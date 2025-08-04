from __future__ import annotations

import logging
import os
import json
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from urllib.parse import urlencode

# Use the 'livekit-api' package for server-side token generation.
from livekit import api

# Main LiveKit Agents imports
from livekit.agents import (
    Agent,
    JobContext,
    WorkerOptions,
    cli,
    tts,
    AutoSubscribe,
    AgentSession,
    get_job_context,
)
# The correct decorator for creating tools for the LLM.
from livekit.agents.llm import function_tool
from livekit.agents.voice import ErrorEvent

from livekit.plugins import openai, deepgram, silero

# Load environment variables from a .env.local file.
load_dotenv('.env.local')

# --- CONFIGURATION & SETUP ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("escalation-agent")

# Load all required API keys and URLs from the environment.
LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_WS_URL = os.getenv("LIVEKIT_WS_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

# Validate that all required environment variables are set.
missing_vars = [
    var for var in ["LIVEKIT_URL", "LIVEKIT_WS_URL", "LIVEKIT_API_KEY", "LIVEKIT_API_SECRET", "OPENAI_API_KEY", "DEEPGRAM_API_KEY"] if not globals()[var]
]
if missing_vars:
    raise EnvironmentError(f"Missing required environment variables in .env.local: {', '.join(missing_vars)}")


# --- THE AGENT IMPLEMENTATION ---

class EscalationAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="""
                You are a friendly and helpful customer support agent.
                Your primary goal is to assist the user with their questions.
                If the user indicates they want to speak to a human, use the
                'transfer_to_human_agent' function. Do not try to answer
                the question yourself if they ask for a human. Always be polite.
            """
        )
        self.escalation_log_file = "escalation_log.txt"


    @function_tool
    async def transfer_to_human_agent(self):
        """
        Call this function ONLY when the user explicitly asks to speak to a human,
        a person, a manager, a supervisor, or a live representative.
        """
        context = get_job_context()
        logger.info(f"LLM triggered 'transfer_to_human_agent' for room: {context.room.name}")

        token = (
            api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
            .with_identity(f"human-agent-{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            .with_name("Human Support Agent")
            .with_grants(
                api.VideoGrants(
                    room_join=True,
                    room=context.room.name,
                    can_publish=True,
                    can_subscribe=True,
                )
            )
            .to_jwt()
        )

        query_params = urlencode({
            "liveKitUrl": LIVEKIT_WS_URL,
            "token": token,
        })
        join_url = f"https://meet.livekit.io/custom?{query_params}"

        self._display_and_log_url(context.room.name, join_url)
        return "Of course. I am generating a secure link for a human representative to join our call. Please hold on a moment."

    def _display_and_log_url(self, room_name: str, join_url: str):
        """Helper function to display the generated URL in the terminal and log it."""
        print("\n" + "="*80)
        print("🚨 HUMAN INTERVENTION REQUESTED 🚨")
        print("="*80)
        print(f"Room: {room_name}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M%S')}")
        print("-" * 80)
        print("🔗 REAL JOIN URL FOR HUMAN AGENT:")
        print(join_url)
        print("-" * 80)
        print("📋 Share this URL with a human agent to join the call.")
        print("=" * 80 + "\n")


# --- AGENT ENTRYPOINT ---

async def entrypoint(ctx: JobContext):
    logger.info(f"Agent starting for room {ctx.room.name}...")

    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    agent_finished_event = asyncio.Event()

    llm_plugin = openai.LLM(model='gpt-4o', api_key=OPENAI_API_KEY)
    stt = deepgram.STT(api_key=DEEPGRAM_API_KEY)
    tts_plugin = openai.TTS(api_key=OPENAI_API_KEY)
    vad = silero.VAD.load()

    session = AgentSession(
        llm=llm_plugin,
        stt=stt,
        tts=tts_plugin,
        vad=vad,
    )

    @session.on("error")
    def on_error(error: ErrorEvent):
        logger.error(f"An error occurred during the session: {error.error}")
        agent_finished_event.set()

    agent = EscalationAgent()

    await session.start(
        room=ctx.room,
        agent=agent
    )

    @ctx.room.on("participant_connected")
    def on_human_join(participant):
        if participant.identity.startswith("human-agent-"):
            logger.info(f"Human agent '{participant.identity}' has joined. Signaling agent to shut down.")
            agent_finished_event.set()

    logger.info("Agent session connected and running. Waiting for human handover...")
    
    await agent_finished_event.wait()

    # --- THE FINAL CORRECTION ---
    # Use 'aclose()' for the asynchronous cleanup of the session.
    logger.info("Shutdown signaled. Closing agent session immediately.")
    await session.aclose()
    
    logger.info("Agent job is finished. The agent will now disconnect.")


# --- MAIN EXECUTION BLOCK ---

if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(entrypoint_fnc=entrypoint)
    )
