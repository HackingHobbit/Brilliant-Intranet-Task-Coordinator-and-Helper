#!/bin/bash

# Local AI Avatar Setup Script
# This script helps set up the 100% Local AI Talking Avatar project

set -e

echo "🚀 Setting up Local AI Avatar Project..."
echo "========================================"

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This project is optimized for macOS with Apple Silicon"
    echo "   While it may work on other platforms, optimal performance is on M-series Macs"
    exit 1
fi

# Check for Apple Silicon
if [[ $(uname -m) != "arm64" ]]; then
    echo "⚠️  Warning: This project is optimized for Apple Silicon (M1/M2/M3/M4)"
    echo "   Performance may be suboptimal on Intel Macs"
fi

# Check for Homebrew
if ! command -v brew &> /dev/null; then
    echo "📦 Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "✅ Homebrew already installed"
fi

# Install Python 3.12
echo "🐍 Installing Python 3.12..."
brew install python@3.12

# Install Node.js
echo "📦 Installing Node.js..."
brew install node

# Install Ollama
echo "🤖 Installing Ollama..."
if ! command -v ollama &> /dev/null; then
    curl -fsSL https://ollama.ai/install.sh | sh
else
    echo "✅ Ollama already installed"
fi

# Create virtual environment
echo "🔧 Setting up Python virtual environment..."
python3 -m venv env
source env/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
npm install

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p models
mkdir -p voices
mkdir -p assets

# Download Ollama model
echo "🤖 Downloading Llama 3 model (this may take a while)..."
ollama pull llama3

# Create sample avatar if none exists
if [ ! -f "assets/avatar.jpg" ]; then
    echo "📸 Creating sample avatar placeholder..."
    # Create a simple colored square as placeholder
    convert -size 400x400 xc:#00bfff -fill white -pointsize 48 -gravity center -annotate +0+0 "AI\nAvatar" assets/avatar.jpg 2>/dev/null || echo "⚠️  Could not create sample avatar (ImageMagick not installed)"
fi

# Setup API keys (optional)
echo ""
echo "🔑 API Keys Setup (Optional)"
echo "============================"
echo "For full functionality, you may want to set up API keys:"
echo ""
echo "1. Alpha Vantage (Financial data):"
echo "   - Sign up at: https://www.alphavantage.co/"
echo "   - Free tier: 25 requests/day"
echo ""
echo "2. Google Maps (Location services):"
echo "   - Create project at: https://console.cloud.google.com/"
echo "   - Enable Maps JavaScript API"
echo ""
echo "3. iCloud (Email/Calendar):"
echo "   - Generate app-specific password at: https://appleid.apple.com/"
echo "   - Use your Apple ID email and the app-specific password"
echo ""

# Check for required models
echo "📋 Model Requirements"
echo "===================="
echo "You'll need to download these models manually:"
echo ""
echo "1. Whisper model:"
echo "   - Download ggml-small.en.bin from OpenAI"
echo "   - Place in models/ directory"
echo ""
echo "2. Piper voice model:"
echo "   - Download from: https://huggingface.co/rhasspy/piper-voices"
echo "   - Example: en_US-amy-medium.onnx"
echo "   - Place in voices/ directory"
echo ""

# Test setup
echo "🧪 Testing setup..."
echo ""

# Test Python environment
if python3 -c "import torch; print('✅ PyTorch:', torch.__version__)" 2>/dev/null; then
    echo "✅ Python environment ready"
else
    echo "❌ Python environment issues detected"
fi

# Test Node.js
if node --version &>/dev/null; then
    echo "✅ Node.js ready"
else
    echo "❌ Node.js not found"
fi

# Test Ollama
if ollama list | grep -q llama3; then
    echo "✅ Ollama with Llama 3 ready"
else
    echo "❌ Ollama model not found"
fi

echo ""
echo "🎉 Setup complete!"
echo "=================="
echo ""
echo "To start the application:"
echo "  npm start"
echo ""
echo "For development mode:"
echo "  npm run dev"
echo ""
echo "Troubleshooting:"
echo "- If you encounter issues, check the README.md file"
echo "- Ensure all models are downloaded to the correct directories"
echo "- Check microphone permissions in System Preferences"
echo ""
echo "Happy coding! 🤖✨" 