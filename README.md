# LiveKit AI-to-Human Handoff Agent

<p>
  <a href="https://cloud.livekit.io/projects/p_/sandbox"><strong>Deploy a sandbox app</strong></a>
  •
  <a href="https://docs.livekit.io/agents/overview/">LiveKit Agents Docs</a>
  •
  <a href="https://livekit.io/cloud">LiveKit Cloud</a>
  •
  <a href="https://blog.livekit.io/">Blog</a>
</p>

A LiveKit-based AI agent that automatically detects when users request human assistance and seamlessly hands off the call to a human agent with secure join URLs.

## 🚀 Features

- **Automatic Handoff Detection**: Uses LLM function tools to detect human assistance requests
- **Secure URL Generation**: Creates secure LiveKit join URLs with proper authentication
- **Seamless Call Handoff**: Smooth transition from AI to human agent
- **Automatic AI Shutdown**: AI agent gracefully exits when human agent joins
- **Comprehensive Logging**: Tracks all handoff events
- **🎤 Speech-to-Text**: Deepgram Nova-3 model
- **�� LLM**: OpenAI GPT-4o with function tools
- **🔊 Text-to-Speech**: OpenAI TTS
- **🎯 Voice Activity Detection**: Silero VAD

## 📋 Prerequisites

- Python 3.8 or higher
- Virtual environment (recommended)
- LiveKit server instance
- API keys for required services

## ��️ Installation

### 1. Clone and Setup Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install livekit livekit-agents livekit-plugins-openai livekit-plugins-deepgram livekit-plugins-silero python-dotenv
```

### 2. Environment Configuration

Create a `.env.local` file in the project root and add your API keys:

```env
# Required API Keys
LIVEKIT_URL=your_livekit_server_url
LIVEKIT_WS_URL=your_livekit_websocket_url
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
OPENAI_API_KEY=your_openai_api_key
DEEPGRAM_API_KEY=your_deepgram_api_key
```

### 3. Get API Keys

You'll need to sign up for these services and get API keys:

- **LiveKit**: [cloud.livekit.io](https://cloud.livekit.io/) or self-hosted
- **OpenAI**: [platform.openai.com](https://platform.openai.com/)
- **Deepgram**: [console.deepgram.com](https://console.deepgram.com/)

## ⚙️ Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `LIVEKIT_URL` | Your LiveKit server URL | `https://your-livekit-server.com` |
| `LIVEKIT_WS_URL` | LiveKit WebSocket URL | `wss://your-livekit-server.com` |
| `LIVEKIT_API_KEY` | LiveKit API key | `your_api_key_here` |
| `LIVEKIT_API_SECRET` | LiveKit API secret | `your_api_secret_here` |
| `OPENAI_API_KEY` | OpenAI API key for LLM | `sk-...` |
| `DEEPGRAM_API_KEY` | Deepgram API key for STT | `your_deepgram_key` |

## �� How It Works

### 1. **Agent Initialization**
- Creates a `HandoffAgent` with specific instructions for handling human requests
- Sets up LiveKit connection with audio-only subscription
- Initializes LLM (GPT-4o), STT (Deepgram), TTS (OpenAI), and VAD (Silero) plugins

### 2. **Handoff Detection**
The agent uses LLM function tools to detect when users request human assistance. The LLM automatically calls the `transfer_to_human_agent()` function when users say phrases like:
- "I want to speak to a human"
- "Connect me to a manager"
- "I need to talk to a supervisor"
- "Get me a representative"
- And many more variations

### 3. **URL Generation Process**
When handoff is detected:
1. **Token Creation**: Generates a secure LiveKit access token for the human agent with proper grants
2. **URL Assembly**: Creates a complete join URL using `https://meet.livekit.io/custom` with proper parameters
3. **Display**: Shows the URL in the terminal with clear formatting
4. **Logging**: Records the handoff event for tracking

### 4. **Human Agent Handoff**
- Human agent receives the generated URL
- They can join the call using the secure token
- AI agent automatically detects human agent arrival (identity starts with "human-agent-")
- AI agent gracefully shuts down when human joins

## �� Usage

### Running the Agent

```bash
python agent_backup.py
```

### Console Mode (Testing)
For local testing with microphone input:

```bash
python agent_backup.py console
```

**Console Controls:**
- Press `Ctrl+B` to toggle between Text/Audio mode
- Press `Q` to quit
- Speak into your microphone to interact with the agent

## 📁 File Structure
