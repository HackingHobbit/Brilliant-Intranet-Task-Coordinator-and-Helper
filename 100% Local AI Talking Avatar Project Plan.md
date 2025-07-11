# 100% Local AI Talking Avatar Project Plan

## Project Overview

This document provides a complete, detailed, and accuracy-checked plan for developing a 100% local AI talking avatar project. It runs entirely on a MacBook Pro with an M4 Pro chip, replicating talking avatar functionality (listening, responding, lip animation) using a user-provided 2D image (with optional 3D support). All core components are local and offline, with internet access permitted only for specific agentic tasks like web research or API calls. The plan incorporates expansions such as memories, agentic capabilities, image analysis, and a futuristic UI inspired by the provided concept (holographic woman avatar with blue neon glow, chat interface, status indicators).

The project emphasizes:
- Privacy and offline operation.
- Performance optimization for Apple Silicon (Neural Engine, Metal acceleration).
- Modularity for easy extension.

**Key Objectives**:
- Seamless pipeline: Audio input → Transcription → Processing (LLM with memories/agentic tools) → Speech output → Lip sync → Animation.
- Real-time as possible (e.g., streaming where feasible, <1s latency target for animation on M4 Pro).

**Estimated Timeline**: 3 weeks for a solo developer.
**Deliverable**: Standalone Git repository with source code, setup instructions, and assets. You can copy this Markdown content into a file (e.g., plan.md), then convert to PDF using tools like pandoc (`pandoc plan.md -o plan.pdf`) or paste into Microsoft Word for .docx.

Accuracy verified as of July 09, 2025, via web searches: Libraries (e.g., yfinance v0.2.65, pyicloud v1.0+), APIs (Alpha Vantage free tier: 25 requests/day), and macOS Sequoia compatibility (keyring works with Keychain; no major issues reported).

## Project Requirements

The original spec (2D image-based avatar) has been expanded with memories, agentic features, multimodal inputs, and UI elements.

### Core Requirements
1. **Local Language Model**: Ollama with Llama 3 for responses; Node.js API interface.
2. **Local Speech-to-Text**: Whisper.cpp for audio transcription.
3. **Local Text-to-Speech**: Piper for natural audio output.
4. **Lip Sync**: Wawa Lip Sync for real-time viseme generation from audio.
5. **2D Avatar Animation**: User-uploaded image; MediaPipe for landmarks; OpenCV for lip warping; Canvas/Three.js for rendering.
6. **Full Pipeline**: Integrate components for end-to-end flow.
7. **Performance**: Optimize for M4 Pro (e.g., Core ML for ML tasks).

### Added Features
1. **Memories**:
   - Session: Real-time chat history.
   - Agent: User preferences/facts (processed async).
   - Knowledge-base: Async storage for retrieved info (e.g., web results).
2. **Agentic Capabilities**:
   - Local tasks: File organization, calculations.
   - Internet-enabled (on-demand): Web research, API calls (e.g., Google Directions).
   - Expanded tasks: Calendar/email management (configurable: local, Gmail, Outlook, iCloud), document interaction (create/edit spreadsheets/databases), financial queries (real-time/historical via free APIs).
   - Learning: Dynamic API integration via LLM-generated code.
3. **Image Analysis**:
   - Uploaded images: Detect faces/objects.
   - Webcam: On-demand for real-time recognition.
4. **3D Avatar**: Optional toggle; convert 2D to 3D mesh.
5. **UI**: Futuristic design (blue neon glow, holographic avatar, chat dialogue, status indicators like "listening/responding"); settings side panel for configs.

### Compatibility and Constraints
- macOS Sequoia/Apple Silicon compatible (verified: No key issues with keyring, pyicloud auth uses app-specific passwords).
- No cloud AI dependencies; internet for tasks only.
- Free tools/APIs prioritized (e.g., yfinance for financials: free, near-real-time).

## Technologies and Alternatives

Use tables for clarity:

| Component | Primary Technology | Alternatives | Rationale/Notes (as of July 09, 2025) |
|-----------|--------------------|--------------|---------------------------------------|
| **LLM** | Ollama (Llama 3) + Node.js API | LM Studio, vLLM | Local inference; Llama 3 for quality. |
| **STT** | Whisper.cpp | MacWhisper, Aiko | Optimized for Apple Silicon (Core ML). |
| **TTS** | Piper | Coqui TTS, macOS 'say' | Natural voices; low latency. |
| **Lip Sync** | Wawa Lip Sync (v2) | MuseTalk, Rhubarb, Wav2Lip | Real-time JS; browser-native for UI. |
| **Facial Landmarks** | MediaPipe | Dlib, OpenFace | 468 points; efficient on M4. |
| **Image Warping/Rendering** | OpenCV + Canvas/Three.js (2D) | scikit-image, PixiJS; Babylon.js (3D) | Warping for lips; holographic effects via CSS. |
| **3D Conversion** | InstantMesh | Ready Player Me SDK | Optional; low-poly for perf (~30-60 FPS). |
| **Memories** | SQLite (session/agent), Chroma (knowledge-base) | Mem0, Faiss | Local DB; async processing. |
| **Agent Framework** | CrewAI | LangChain, AutoGen | Tool-calling; dynamic learning. |
| **File Ops** | os/shutil | - | Local FS management. |
| **Web Research** | requests | Selenium (if needed) | On-demand fetches. |
| **Calendar/Email** | osascript (local), google-api-python-client (Gmail), msal (Outlook), pyicloud/caldav/imaplib/smtplib (iCloud) | Radicale (self-hosted) | Configurable modes; iCloud uses app-specific passwords (verified working). |
| **Financial APIs** | yfinance (v0.2.65, default) | Alpha Vantage (25 req/day free), Finnhub (60/min free tier) | Real-time (.info) & historical (.history); free/near-real-time. |
| **Documents** | openpyxl (Excel), Pandas/SQLAlchemy (DBs) | docx, pptx | Local creation/editing. |
| **Image Analysis** | YOLOv8 (objects), Dlib/face_recognition (faces) | Apple's Vision Framework | Local CV; webcam via OpenCV/JS. |
| **UI/App** | Electron + Tailwind CSS | React for components | Desktop app; neon styling. |
| **Settings Panel** | react-sliding-pane | Pure CSS | Slide-out form. |
| **Secure Storage** | keyring (macOS Keychain) | cryptography Fernet | Encrypted API keys; compatible with Sequoia. |
| **Audio** | PyAudio/pydub | SoX | Handling/recording. |

All installable locally; no pip beyond listed (verified compatibility).

## Detailed Granular Plan

### Phase 1: Environment Setup (1-2 days)
1. **Install Tools**:
   - Homebrew: Run installation script.
   - Python 3.12, Node.js 20+, Electron.
2. **Virtual Environment**: Create and activate Python venv.
3. **Dependencies**:
   - Pip: List from above (e.g., ollama, whisper-cpp, piper-tts, etc.).
   - NPM: wawa-lipsync, tailwindcss, etc.
4. **Models/Downloads**:
   - Ollama: `ollama pull llama3`.
   - Whisper.cpp: Compile from GitHub; small.en model.
   - YOLOv8n via Ultralytics.
5. **Project Structure**:
   - Folders: src (python/js), assets (sample avatar.jpg - futuristic woman with blue glow), memory, tools, vision, ui.
   - Files: config.json (modes/toggles), setup_keys.py (prompt/store keys in keyring).
6. **Initial Config**: Set defaults (e.g., email_mode: 'local', financial_api: 'yfinance').
7. **Verification**: Run `python -m pip list` to confirm installs; test keyring with sample code.

### Phase 2: Implement Individual Components (5-7 days)
1. **Local LLM**:
   - Setup: Node.js server for Ollama API.
   - Integration: CrewAI chain for tool/memory calls.
   - Code Snippet: app.js - POST /query endpoint.
   - Test: Send prompt, get response.

2. **Local STT/TTS**:
   - STT: `stt.py` - Record mic, transcribe with Whisper.cpp.
   - TTS: `tts.py` - Text to WAV via Piper.
   - Test: Transcribe sample audio; play TTS output.

3. **Lip Sync**:
   - `lipsync.js`: Use Wawa to process TTS audio for visemes (real-time).
   - Test: Feed sample audio, output mouth shapes.

4. **Avatar Animation**:
   - Upload/Landmarks: `landmarks.py` - MediaPipe on image.
   - Warping: `warp.py` - OpenCV lip deformation per viseme.
   - Rendering: `avatar.js` - Canvas for 2D; Babylon.js branch for 3D (toggle in config).
   - Styling: CSS for blue neon glow (box-shadow, filters).
   - Test: Warp sample image; render sequence.

5. **Memories**:
   - `memory.py`: SQLite setup for agent/session; Chroma for vector embeddings.
   - Async Update: Post-session LLM extraction to knowledge-base.
   - Integration: Retrieve in LLM prompts.
   - Test: Store/retrieve fact.

6. **Agentic Capabilities**:
   - Tools in `tools.py`: Define CrewAI tools with config switches.
     - File: shutil-based organization.
     - Research: requests.get + summarize.
     - Calendar/Email: Mode-based (e.g., iCloud: pyicloud.login(username, keyring.get_password); caldav for events; imaplib for email read).
     - Financial: Parse query (regex for 'historical'); yfinance.Ticker(symbol).info or .history().
     - Documents: openpyxl.Workbook() for spreadsheets; sqlalchemy for DBs.
     - APIs: googlemaps.Client(key); dynamic: LLM generates function.
     - Image: `vision.py` - YOLO.detect(); face_recognition.compare_faces(); webcam stream.
   - Key Handling: Retrieve from keyring; prompt if missing.
   - Test: Enumerate scenarios per mode (e.g., "Get historical AAPL via Alpha Vantage" - verify 25/day limit).

7. **Main UI**:
   - `main-ui.html/js`: Center avatar div (glow CSS), chat scrollable div, input bar with mic button, glowing status text (e.g., "Pondering..." from image tags).
   - Theming: Futuristic (Orbitron font, gradients).
   - Integration: Update chat with responses; avatar animates on TTS.
   - Test: Load, interact.

8. **Settings Panel**:
   - `settings-panel.js`: Gear button triggers slide (from right).
   - Form: Dropdowns (modes: local/gmail/outlook/icloud), toggles (3D), key inputs (password type → keyring).
   - Submit: Update config.json; reload if needed.
   - Test: Change mode, verify in tool calls.

### Phase 3: Full Pipeline Integration (3-4 days)
1. **Orchestration**: Electron main process - Mic capture → STT Flask → Memory retrieve → CrewAI agent (tools if detected) → LLM → TTS → Wawa → Avatar render + UI update.
2. **Branching Logic**: If query needs tools (e.g., "directions" → googlemaps), route async; internet confirm prompt.
3. **Real-Time Enhancements**: WebSockets for partial responses; status indicators during steps.
4. **Shortcuts**: Integrate SadTalker for avatar if needed; CrewAI examples for agents.
5. **Error Handling**: Fallbacks (e.g., offline → cached knowledge); validation (e.g., face in image).
6. **Test**: End-to-end: Upload image, ask agentic query (e.g., "Add iCloud event and analyze photo"), verify UI/animation.

### Phase 4: Optimization and Testing (2-3 days)
1. **Optimization**:
   - Use MPS (torch) for ML on M4.
   - Cache API results in knowledge-base.
   - Profile: Instruments.app for FPS (target 30+); batch warping.
2. **Testing**:
   - Unit: Pytest for Python (e.g., test_tools.py per mode).
   - Integration: Manual scenarios in README (e.g., "Toggle 3D, check perf"; "Historical financial query").
   - Edge Cases: Noisy audio, missing keys (prompt), offline (use local modes).
   - UI: Verify panel slide, glow effects don't lag.
3. **Coverage**: 80%+ for core; focus on agentic variations.

### Phase 5: Packaging and Delivery (1 day)
1. **Bundle**:
   - Git repo: All code, requirements.txt, package.json.
   - Scripts: setup.sh (install deps), run.sh (electron .).
2. **Assets/Docs**:
   - Sample avatar.jpg (matching UI concept).
   - README.md: Step-by-step setup/run, troubleshooting (e.g., iCloud: "Generate app-specific password at appleid.apple.com"), screenshots.
   - Appendix: Tool lists, accuracy notes (e.g., Alpha Vantage limits: 25/day).
3. **Distribution**: Zip repo; user can build Electron app or run via Node.

## Appendix: Accuracy and Verification
- **Library Versions/Compat**: pyicloud v1.0+ (GitHub active, auth issues resolvable); yfinance v0.2.65 (PyPI Jul 2025); keyring compatible with macOS Sequoia (no reported bugs in Keychain).
- **API Limits**: Alpha Vantage free: 25 req/day; Finnhub: 60/min; yfinance unlimited (Yahoo-based).
- **Potential Issues**: iCloud requires app-specific passwords; monitor for Yahoo Finance changes (yfinance issues ongoing but functional).
- **Sources**: Verified via web searches on PyPI/GitHub/Apple Support.

This plan is self-contained and ready for implementation. For PDF/Word, copy to Markdown file and convert.