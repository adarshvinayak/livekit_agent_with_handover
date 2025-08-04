# LiveKit AI-to-Human Handoff Agent

<p>
  <a h<p>
  <a href="https://cloud.livekit.io/projects/p_/sandbox"><strong>Deploy a sandbox app</strong></a>
  •
  <a href="https://docs.livekit.io/agents/overview/">LiveKit Agents Docs</a>
  •
  <a href="https://livekit.io/cloud">LiveKit Cloud</a>
  •
  <a href="https://blog.livekit.io/">Blog</a>
</p>

A LiveKit-based AI agent that automatically detects when users request human assistance and generates secure join URLs for human agents to join ongoing calls.

## 🚀 Features

- **Automatic Escalation Detection**: Uses LLM function tools to detect human assistance requests
- **Secure URL Generation**: Creates secure LiveKit join URLs with proper authentication
- **Real-time Call Handover**: Seamless transition from AI to human agent
- **Automatic Shutdown**: AI agent gracefully exits when human agent joins
- **Comprehensive Logging**: Tracks all escalation events
- **🎤 Speech-to-Text**: Deepgram Nova-3 model
- **🧠 LLM**: OpenAI GPT-4o with function tools
- **🔊 Text-to-Speech**: OpenAI TTS
- **🎯 Voice Activity Detection**: Silero VAD

## 📋 Prerequisites

- Python 3.8 or higher
- Virtual environment (recommended)
- LiveKit server instance
- API keys for required services

## ️ Installation

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

##  How It Works

### 1. **Agent Initialization**
- Creates an `EscalationAgent` with specific instructions for handling human requests
- Sets up LiveKit connection with audio-only subscription
- Initializes LLM (GPT-4o), STT (Deepgram), TTS (OpenAI), and VAD (Silero) plugins

### 2. **Escalation Detection**
The agent uses LLM function tools to detect when users request human assistance. The LLM automatically calls the `transfer_to_human_agent()` function when users say phrases like:
- "I want to speak to a human"
- "Connect me to a manager"
- "I need to talk to a supervisor"
- "Get me a representative"
- And many more variations

### 3. **URL Generation Process**
When escalation is detected:
1. **Token Creation**: Generates a secure LiveKit access token for the human agent with proper grants
2. **URL Assembly**: Creates a complete join URL using `https://meet.livekit.io/custom` with proper parameters
3. **Display**: Shows the URL in the terminal with clear formatting
4. **Logging**: Records the escalation event for tracking

### 4. **Human Agent Handover**
- Human agent receives the generated URL
- They can join the call using the secure token
- AI agent automatically detects human agent arrival (identity starts with "human-agent-")
- AI agent gracefully shuts down when human joins

##  Usage

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

```
lk-agent-avatar-custom/
├── agent_backup.py         # Main escalation agent implementation
├── agent.py               # Original agent with avatar integration
├── requirements.txt       # Python dependencies
├── .env.local            # Environment variables (create this)
├── escalation_log.txt    # Generated escalation logs (auto-created)
├── README.md             # This file
└── venv/                 # Virtual environment
```

## 🔧 Key Components

### EscalationAgent Class
- **Purpose**: Main agent class with escalation detection using LLM function tools
- **Key Methods**:
  - `transfer_to_human_agent()`: Function tool for LLM to trigger escalation
  - `_display_and_log_url()`: Helper for URL display and logging

### Function Tools
- Uses `@function_tool` decorator to create callable functions for the LLM
- LLM can automatically call `transfer_to_human_agent()` when escalation is needed
- This is the key innovation that makes escalation detection work reliably

### Session Management
- **AgentSession**: Manages LLM, STT, TTS, and VAD integration
- **Event Handling**: Monitors for errors and human agent connections
- **Graceful Shutdown**: Proper cleanup when human agent joins using `aclose()`

## 🔐 Security Features

- **Secure Token Generation**: Uses LiveKit's AccessToken with proper grants
- **Time-limited Tokens**: Tokens include timestamps for security
- **Room-specific Access**: Human agents only get access to the specific room
- **Proper Permissions**: Human agents get publish/subscribe permissions
- **Identity Management**: Human agents get unique identities with "human-agent-" prefix

## 📊 Logging and Monitoring

### Escalation Events
All escalation events are logged with:
- Timestamp
- Room name
- Generated join URL
- Escalation type

### Console Output
Real-time display of:
- Agent status and connections
- Escalation triggers
- Generated URLs with clear formatting
- Human agent connections
- Graceful shutdown messages

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**:
   - Ensure all LiveKit packages are installed
   - Check Python version compatibility

2. **API Key Errors**:
   - Verify all environment variables are set in `.env.local`
   - Check API key validity and permissions

3. **Connection Issues**:
   - Verify LiveKit server URLs are correct
   - Check network connectivity

4. **Token Generation Errors**:
   - Ensure LiveKit API key and secret are correct
   - Check LiveKit server configuration

### Debug Mode
Enable detailed logging by modifying the logging level in the code:
```python
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
```

##  Workflow Example

1. **User joins call** → AI agent greets them
2. **User asks for human** → LLM detects escalation keywords and calls function tool
3. **Function tool triggered** → `transfer_to_human_agent()` is called
4. **URL is generated** → Secure join URL created and displayed
5. **Human agent joins** → Uses URL to connect to the call
6. **AI agent exits** → Graceful handover completed

## 📝 Key Innovations

### LLM Function Tools
The main innovation in this implementation is using LiveKit's `@function_tool` decorator, which allows the LLM to automatically call the escalation function when it detects human assistance requests. This is much more reliable than keyword matching.

### Proper LiveKit Integration
- Uses `livekit.api` for server-side token generation
- Proper event handling for participant connections
- Graceful session management with `aclose()`

### Real URL Generation
Unlike placeholder implementations, this generates actual working LiveKit join URLs that human agents can use to join the call.

## Frontend Integration

This agent can work with:
- LiveKit's [Agents Playground](https://agents.livekit.io/)
- Custom web/mobile frontends using LiveKit SDKs
- Telephony integration via LiveKit SIP

## Documentation

- [LiveKit Agents Documentation](https://docs.livekit.io/agents/)
- [LiveKit Python SDK](https://docs.livekit.io/realtime/client/python/)
- [LiveKit API Documentation](https://docs.livekit.io/reference/)

## Support

For issues and questions:
- [LiveKit Community Slack](https://livekit.io/join-slack)
- [GitHub Issues](https://github.com/livekit/agents/issues)

---

**Note**: This agent is designed for production use with proper LiveKit server setup and API keys. Always test in a development environment first.

