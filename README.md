# 100% Local AI Talking Avatar Project

A fully local AI talking avatar application that runs entirely on your MacBook Pro with Apple Silicon (M4 Pro). Features real-time speech-to-text, AI responses, text-to-speech, lip synchronization, and agentic capabilities - all running locally without cloud dependencies.

## 🌟 Features

- **100% Local Operation**: No cloud AI dependencies - everything runs on your machine
- **Real-time Speech Processing**: Whisper.cpp for speech-to-text, Piper for text-to-speech
- **AI Avatar**: 2D/3D avatar with real-time lip synchronization using wawa-lipsync
- **Agentic Capabilities**: Email, calendar, financial data, file operations, web research
- **Memory System**: Session history and knowledge base using SQLite and ChromaDB
- **Futuristic UI**: Neon glow effects, holographic avatar, modern chat interface
- **Apple Silicon Optimized**: MPS acceleration for machine learning tasks

## 🚀 Quick Start

### Prerequisites

- macOS with Apple Silicon (M1/M2/M3/M4)
- Python 3.12+
- Node.js 20+
- Homebrew

### Automated Setup (Recommended)

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Brilliant-Intranet-Task-Coordinator-and-Helper
   ```

2. **Run the automated setup**:
   ```bash
   python setup.py
   ```

   This will automatically:
   - Install all Python and Node.js dependencies
   - Download required AI models
   - Set up Ollama with llama3
   - Create default configuration
   - Validate the installation

3. **Start the application**:
   ```bash
   npm start
   ```

### Manual Installation (Alternative)

If you prefer manual setup or the automated script fails:

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Brilliant-Intranet-Task-Coordinator-and-Helper
   ```

2. **Install Python dependencies**:
   ```bash
   python3 -m venv env
   source env/bin/activate
   pip install -r requirements.txt
   ```

3. **Install Node.js dependencies**:
   ```bash
   npm install
   ```

4. **Install and setup Ollama**:
   ```bash
   # Install Ollama
   curl -fsSL https://ollama.ai/install.sh | sh

   # Pull the Llama 3 model
   ollama pull llama3
   ```

5. **Download required models**:
   ```bash
   python download_models.py --required-only
   ```

6. **Validate setup**:
   ```bash
   python validate_setup.py
   ```

7. **Start the application**:
   ```bash
   npm start
   ```

### Dynamic Port System

The application now uses a **dynamic port allocation system** that automatically finds and uses an available port for the backend:

- **Automatic Port Detection**: The system automatically finds an unused port (starting from 5000)
- **Port Conflict Resolution**: If port 5000 is busy, it automatically tries 5001, 5002, etc.
- **Seamless Integration**: The frontend automatically connects to the correct backend port
- **No Manual Configuration**: No need to manually configure ports

**How it works**:
1. Backend starts and finds an available port
2. Port information is saved to a temporary `.port` file
3. Frontend reads the port file to connect to the correct backend
4. Port file is cleaned up when the application exits

## 📁 Project Structure

```
local-ai-avatar/
├── app.py                 # Flask backend server
├── main.js               # Electron main process
├── index.html            # Main UI
├── styles.css            # Futuristic styling
├── ui.js                 # UI interaction logic
├── avatar.js             # Avatar rendering (Three.js)
├── lipsync.js            # Lip sync with wawa-lipsync
├── settings-panel.js     # Settings management
├── stt.py               # Speech-to-text (Whisper)
├── tts.py               # Text-to-speech (Piper)
├── memory.py            # Memory management
├── tools.py             # Agentic capabilities
├── vision.py            # Image analysis (YOLOv8)
├── landmarks.py         # Facial landmark detection
├── warp.py              # Lip warping for animation
├── setup_keys.py        # API key management
├── config.json          # Application configuration
├── requirements.txt     # Python dependencies
├── package.json         # Node.js dependencies
└── README.md           # This file
```

## 🎮 Usage

### Basic Operation

1. **Launch the app**: `npm start`
2. **Upload an avatar**: Click the camera icon to upload a photo
3. **Start talking**: Click the microphone button and speak
4. **Type messages**: Use the text input for typed conversations
5. **Access settings**: Click the gear icon for configuration

### Agentic Capabilities

The AI can perform various tasks:

- **Email Management**: Send/read emails (Gmail, Outlook, iCloud, local)
- **Calendar**: Add/view events (Google Calendar, Outlook, iCloud, local)
- **Financial Data**: Get real-time stock prices and historical data
- **File Operations**: Organize files, create documents
- **Web Research**: Search the internet for information
- **Image Analysis**: Analyze uploaded images for objects and faces

### Configuration

Access settings via the gear icon to configure:

- **Email/Calendar Modes**: Choose between local, Gmail, Outlook, or iCloud
- **Financial API**: Select between Yahoo Finance, Alpha Vantage, or Finnhub
- **Avatar Settings**: Toggle 3D mode, adjust performance settings
- **API Keys**: Securely store API keys for external services

## 🔧 Configuration

### API Keys Setup

For full functionality, you may need to set up API keys:

1. **Alpha Vantage** (Financial data):
   - Sign up at: https://www.alphavantage.co/
   - Free tier: 25 requests/day

2. **Google Maps** (Location services):
   - Create project at: https://console.cloud.google.com/
   - Enable Maps JavaScript API

3. **iCloud** (Email/Calendar):
   - Generate app-specific password at: https://appleid.apple.com/
   - Use your Apple ID email and the app-specific password

### Performance Optimization

For optimal performance on Apple Silicon:

1. **Enable MPS acceleration**: The app automatically uses Metal Performance Shaders when available
2. **Adjust performance mode**: Choose between Optimized, Balanced, or High Quality
3. **3D Avatar**: Disable for better performance on older devices

## 🛠️ Development

### Running in Development Mode

```bash
npm run dev
```

### Backend API Endpoints

The Flask backend provides these endpoints:

- `GET /health` - Health check
- `POST /transcribe` - Speech-to-text
- `POST /generate_response` - AI response generation
- `POST /tts` - Text-to-speech
- `POST /analyze_image` - Image analysis
- `POST /landmarks` - Facial landmark detection
- `POST /warp` - Lip warping
- `POST /update_config` - Update configuration
- `POST /set_key` - Store API key
- `GET /get_config` - Get current configuration

### Adding New Tools

To add new agentic capabilities:

1. **Add tool class** in `tools.py`:
   ```python
   class NewTool(BaseTool):
       name = 'New Tool'
       description = 'Description of what this tool does'
       
       def _run(self, *args, **kwargs):
           # Tool implementation
           return result
   ```

2. **Register tool** in `AgentTools.get_all_tools()`:
   ```python
   def get_all_tools(self):
       return [
           # ... existing tools
           self.new_tool()
       ]
   ```

3. **Update UI** if needed for user interaction

## 🐛 Troubleshooting

### Common Issues

**Ollama not running**:
```bash
ollama serve
```

**Audio recording issues**:
- Check microphone permissions in System Preferences
- Ensure microphone is not being used by other applications

**Model download issues**:
- Check internet connection
- Verify model paths in configuration
- Some models may need manual download

**Performance issues**:
- Disable 3D avatar mode
- Reduce performance mode to "Balanced"
- Close other resource-intensive applications

**API key errors**:
- Verify API keys are correctly entered
- Check API service status
- Ensure proper permissions for the service

### Setup Script Issues

**Setup script fails**:
```bash
# Run validation to see what's missing
python validate_setup.py

# Download models manually if needed
python download_models.py --required-only

# Setup API keys manually
python setup_keys.py
```

**Permission errors**:
```bash
# Make scripts executable
chmod +x setup.py validate_setup.py download_models.py

# Run with proper permissions
sudo python setup.py  # Only if needed
```

### Debug Mode

Enable debug logging:

```bash
# Set environment variable
export DEBUG=true

# Or modify config.json
{
  "debug_mode": true
}
```

### Logs

Check logs in:
- **Electron**: Developer Tools Console (Cmd+Option+I)
- **Flask**: Terminal where you ran `npm start`

## 📊 Performance

### Benchmarks (M4 Pro)

- **Speech-to-Text**: ~200ms latency
- **Text-to-Speech**: ~500ms generation time
- **Avatar Animation**: 30+ FPS
- **Memory Retrieval**: <50ms
- **Image Analysis**: ~1-2 seconds

### Optimization Tips

1. **Use SSD storage** for faster model loading
2. **Close unnecessary applications** to free up memory
3. **Use wired internet** for API calls when needed
4. **Regularly restart** the application for optimal performance

## 🔒 Privacy & Security

- **100% Local**: No data sent to cloud services unless explicitly requested
- **Secure Storage**: API keys stored in macOS Keychain
- **No Telemetry**: No usage data collection
- **Open Source**: Full transparency of code

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- **Ollama** for local LLM inference
- **Whisper.cpp** for speech recognition
- **Piper** for text-to-speech
- **wawa-lipsync** for real-time lip synchronization
- **Three.js** for 3D rendering
- **MediaPipe** for facial landmarks
- **CrewAI** for agentic capabilities

## 📞 Support

For issues and questions:

1. Check the troubleshooting section above
2. Search existing issues
3. Create a new issue with detailed information
4. Include system information and error logs

---

**Note**: This project is designed for macOS with Apple Silicon. While it may work on other platforms, optimal performance is achieved on M-series Macs.
