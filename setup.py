#!/usr/bin/env python3
"""
Complete setup script for Local AI Avatar
Handles installation, configuration, and validation
"""

import os
import sys
import subprocess
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
import platform

# Import our validation and download modules
try:
    from validate_setup import SetupValidator
    from download_models import ModelDownloader
    from setup_keys import KeyManager
except ImportError as e:
    print(f"Error importing setup modules: {e}")
    print("Please ensure all setup files are in the same directory")
    sys.exit(1)

logger = logging.getLogger(__name__)

class ProjectSetup:
    """Complete project setup manager"""
    
    def __init__(self):
        """Initialize setup manager"""
        self.project_root = Path.cwd()
        self.platform = platform.system().lower()
        self.validator = SetupValidator()
        self.model_downloader = ModelDownloader()
        self.key_manager = KeyManager()
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def check_system_requirements(self) -> bool:
        """Check basic system requirements"""
        logger.info("Checking system requirements...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            logger.error("Python 3.8 or higher is required")
            return False
        
        # Check if we're in the right directory
        required_files = ['package.json', 'app.py', 'main.js', 'index.html']
        missing_files = [f for f in required_files if not (self.project_root / f).exists()]
        
        if missing_files:
            logger.error(f"Missing required files: {missing_files}")
            logger.error("Please run this script from the project root directory")
            return False
        
        return True
    
    def install_python_dependencies(self) -> bool:
        """Install Python dependencies"""
        logger.info("Installing Python dependencies...")
        
        requirements_file = self.project_root / 'requirements.txt'
        if not requirements_file.exists():
            logger.error("requirements.txt not found")
            return False
        
        try:
            # Upgrade pip first
            subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                         check=True, capture_output=True)
            
            # Install requirements
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)], 
                         check=True, capture_output=True)
            
            logger.info("Python dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install Python dependencies: {e}")
            return False
    
    def install_node_dependencies(self) -> bool:
        """Install Node.js dependencies"""
        logger.info("Installing Node.js dependencies...")
        
        try:
            # Check if npm is available
            subprocess.run(['npm', '--version'], check=True, capture_output=True)
            
            # Install dependencies
            subprocess.run(['npm', 'install'], check=True, capture_output=True, 
                         cwd=self.project_root)
            
            logger.info("Node.js dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install Node.js dependencies: {e}")
            return False
        except FileNotFoundError:
            logger.error("npm not found. Please install Node.js first")
            return False
    
    def setup_ollama(self) -> bool:
        """Setup Ollama and download required models"""
        logger.info("Setting up Ollama...")
        
        try:
            # Check if Ollama is installed
            subprocess.run(['ollama', '--version'], check=True, capture_output=True)
            
            # Check if llama3 model is available
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            if 'llama3' not in result.stdout:
                logger.info("Downloading llama3 model (this may take a while)...")
                subprocess.run(['ollama', 'pull', 'llama3'], check=True)
            
            logger.info("Ollama setup completed")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to setup Ollama: {e}")
            return False
        except FileNotFoundError:
            logger.error("Ollama not found. Please install Ollama first: https://ollama.ai/")
            return False
    
    def download_ai_models(self) -> bool:
        """Download required AI models"""
        logger.info("Downloading AI models...")
        
        try:
            results = self.model_downloader.download_all_models(required_only=True)
            
            if all(results.values()):
                logger.info("All required models downloaded successfully")
                return True
            else:
                logger.error("Some models failed to download")
                return False
                
        except Exception as e:
            logger.error(f"Failed to download models: {e}")
            return False
    
    def create_default_config(self) -> bool:
        """Create default configuration file"""
        logger.info("Creating default configuration...")
        
        config_path = self.project_root / 'config.json'
        
        default_config = {
            "email_mode": "local",
            "calendar_mode": "local",
            "financial_api": "yfinance",
            "enable_3d": False,
            "avatar_path": "assets/avatar.jpg",
            "llm_model": "llama3",
            "stt_model": "whisper-small",
            "tts_voice": "en_US-amy-medium",
            "neon_glow_color": "#00bfff",
            "ui_theme": "futuristic",
            "performance_mode": "optimized",
            "memory_enabled": True,
            "agentic_tools_enabled": True,
            "vision_enabled": True,
            "webcam_enabled": False,
            "auto_save_session": True,
            "max_session_history": 50,
            "api_keys": {}
        }
        
        try:
            if config_path.exists():
                # Load existing config and merge with defaults
                with open(config_path) as f:
                    existing_config = json.load(f)
                
                # Update with any missing keys
                for key, value in default_config.items():
                    if key not in existing_config:
                        existing_config[key] = value
                
                config = existing_config
            else:
                config = default_config
            
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info("Configuration file created/updated")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create config: {e}")
            return False
    
    def setup_api_keys(self, interactive: bool = True) -> bool:
        """Setup API keys"""
        logger.info("Setting up API keys...")
        
        try:
            if interactive:
                print("\n" + "="*60)
                print("API KEY SETUP")
                print("="*60)
                print("You can set up API keys now or skip and configure them later")
                print("through the settings panel in the application.")
                
                setup_keys = input("\nWould you like to set up API keys now? (y/N): ").lower().strip()
                
                if setup_keys == 'y':
                    self.key_manager.setup_required_keys(interactive=True)
                else:
                    print("Skipping API key setup. You can configure them later.")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup API keys: {e}")
            return False
    
    def run_validation(self) -> bool:
        """Run final validation"""
        logger.info("Running final validation...")
        
        results = self.validator.run_full_validation()
        
        # Check critical components
        critical_checks = [
            ('system', 'Python 3.8+'),
            ('python_deps', 'flask'),
            ('python_deps', 'flask_cors'),
            ('config', 'config.json'),
            ('models', 'en_US-amy-medium.onnx')
        ]
        
        failed_critical = []
        for category, check in critical_checks:
            if not results.get(category, {}).get(check, False):
                failed_critical.append(f"{category}.{check}")
        
        if failed_critical:
            logger.error(f"Critical validation failures: {failed_critical}")
            return False
        
        logger.info("Validation completed successfully")
        return True
    
    def print_completion_message(self):
        """Print setup completion message"""
        print("\n" + "="*60)
        print("🎉 LOCAL AI AVATAR SETUP COMPLETED!")
        print("="*60)
        print("\nYour Local AI Avatar is now ready to use!")
        print("\nTo start the application:")
        print("  npm start")
        print("\nTo run validation anytime:")
        print("  python validate_setup.py")
        print("\nTo download additional models:")
        print("  python download_models.py")
        print("\nTo configure API keys:")
        print("  python setup_keys.py")
        print("\nFor help and documentation:")
        print("  See README.md")
        print("\n" + "="*60)
    
    def run_complete_setup(self, interactive: bool = True) -> bool:
        """Run complete setup process"""
        logger.info("Starting Local AI Avatar setup...")
        
        steps = [
            ("Checking system requirements", self.check_system_requirements),
            ("Installing Python dependencies", self.install_python_dependencies),
            ("Installing Node.js dependencies", self.install_node_dependencies),
            ("Setting up Ollama", self.setup_ollama),
            ("Downloading AI models", self.download_ai_models),
            ("Creating configuration", self.create_default_config),
            ("Setting up API keys", lambda: self.setup_api_keys(interactive)),
            ("Running validation", self.run_validation)
        ]
        
        for step_name, step_func in steps:
            print(f"\n📋 {step_name}...")
            
            try:
                if not step_func():
                    logger.error(f"Setup failed at: {step_name}")
                    return False
                print(f"✓ {step_name} completed")
                
            except KeyboardInterrupt:
                print(f"\n❌ Setup cancelled by user during: {step_name}")
                return False
            except Exception as e:
                logger.error(f"Unexpected error during {step_name}: {e}")
                return False
        
        self.print_completion_message()
        return True

def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Setup Local AI Avatar project')
    parser.add_argument('--non-interactive', action='store_true',
                       help='Run setup without interactive prompts')
    parser.add_argument('--skip-models', action='store_true',
                       help='Skip model downloads')
    parser.add_argument('--skip-ollama', action='store_true',
                       help='Skip Ollama setup')
    parser.add_argument('--validate-only', action='store_true',
                       help='Only run validation')
    
    args = parser.parse_args()
    
    setup = ProjectSetup()
    
    if args.validate_only:
        success = setup.run_validation()
        setup.validator.print_results()
        sys.exit(0 if success else 1)
    
    # Run complete setup
    interactive = not args.non_interactive
    success = setup.run_complete_setup(interactive)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
