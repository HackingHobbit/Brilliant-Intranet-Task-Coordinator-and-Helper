# Brilliant Intranet Task Coordinator and Helper

In the spirit of J.A.R.V.I.S., a 100% local AI talking avatar assistant running on MacBook Pro M4 Pro.

## Setup
1. Install Homebrew, Python 3.12, Node.js.
2. Create venv: `python -m venv env; source env/bin/activate`.
3. `pip install -r requirements.txt` (create with plan deps).
4. `npm install`.
5. Run `python download_models.py`.
6. Launch: `npm start`.

## Features
- Local LLM, STT, TTS.
- Memories, agentic tools (file org, research, calendar/email with modes: local/Gmail/Outlook/iCloud, financial real-time/historical).
- Image analysis (uploaded/webcam).
- 2D/3D avatar with Wawa lip sync.
- Futuristic UI with settings panel.

## Troubleshooting
- Ollama: `ollama serve`.
- iCloud: Generate app-specific password.
- Perf: Use MPS for Torch.

See plan.md for details.