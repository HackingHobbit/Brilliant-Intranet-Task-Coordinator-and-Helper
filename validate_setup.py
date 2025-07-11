#!/usr/bin/env python3
"""
Setup validation script for Local AI Avatar
Validates dependencies, models, and configuration
"""

import os
import sys
import json
import subprocess
import importlib
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)

class SetupValidator:
    """Validates project setup and dependencies"""
    
    def __init__(self):
        """Initialize setup validator"""
        self.project_root = Path.cwd()
        self.results = {
            'python_deps': {},
            'node_deps': {},
            'models': {},
            'config': {},
            'system': {}
        }
    
    def check_python_dependencies(self) -> Dict[str, bool]:
        """Check Python dependencies"""
        logger.info("Checking Python dependencies...")
        
        required_packages = [
            'flask', 'flask_cors', 'ollama', 'whisper', 'cv2', 'mediapipe',
            'numpy', 'sentence_transformers', 'chromadb', 'ultralytics',
            'face_recognition', 'pyaudio', 'pydub', 'keyring', 'icalendar',
            'openpyxl', 'pandas', 'sqlalchemy', 'google.auth', 'msal',
            'googlemaps', 'yfinance', 'alpha_vantage', 'finnhub', 'pyicloud',
            'caldav', 'requests', 'torch', 'transformers', 'sklearn', 'tiktoken'
        ]
        
        results = {}
        for package in required_packages:
            try:
                # Handle special cases
                if package == 'cv2':
                    importlib.import_module('cv2')
                elif package == 'google.auth':
                    importlib.import_module('google.auth')
                elif package == 'sklearn':
                    importlib.import_module('sklearn')
                else:
                    importlib.import_module(package)
                results[package] = True
            except ImportError:
                results[package] = False
        
        self.results['python_deps'] = results
        return results
    
    def check_node_dependencies(self) -> Dict[str, bool]:
        """Check Node.js dependencies"""
        logger.info("Checking Node.js dependencies...")
        
        package_json_path = self.project_root / 'package.json'
        if not package_json_path.exists():
            logger.error("package.json not found")
            return {}
        
        try:
            with open(package_json_path) as f:
                package_data = json.load(f)
            
            dependencies = {
                **package_data.get('dependencies', {}),
                **package_data.get('devDependencies', {})
            }
            
            node_modules_path = self.project_root / 'node_modules'
            results = {}
            
            for package in dependencies.keys():
                package_path = node_modules_path / package
                results[package] = package_path.exists()
            
            self.results['node_deps'] = results
            return results
            
        except Exception as e:
            logger.error(f"Failed to check Node.js dependencies: {e}")
            return {}
    
    def check_models(self) -> Dict[str, bool]:
        """Check required models"""
        logger.info("Checking AI models...")
        
        models_dir = self.project_root / 'models'
        required_models = [
            'en_US-amy-medium.onnx',
            'en_US-amy-medium.onnx.json'
        ]
        
        results = {}
        for model in required_models:
            model_path = models_dir / model
            results[model] = model_path.exists()
        
        # Check optional models
        optional_models = ['yolov8n.pt']
        for model in optional_models:
            model_path = models_dir / model
            results[f"{model} (optional)"] = model_path.exists()
        
        self.results['models'] = results
        return results
    
    def check_configuration(self) -> Dict[str, bool]:
        """Check configuration files"""
        logger.info("Checking configuration...")
        
        config_files = [
            'config.json',
            'package.json',
            'requirements.txt',
            'index.html',
            'main.js',
            'app.py'
        ]
        
        results = {}
        for config_file in config_files:
            file_path = self.project_root / config_file
            results[config_file] = file_path.exists()
        
        # Validate config.json content
        config_path = self.project_root / 'config.json'
        if config_path.exists():
            try:
                with open(config_path) as f:
                    config_data = json.load(f)
                
                required_keys = [
                    'email_mode', 'calendar_mode', 'financial_api',
                    'enable_3d', 'llm_model', 'stt_model', 'tts_voice'
                ]
                
                for key in required_keys:
                    results[f"config.{key}"] = key in config_data
                    
            except Exception as e:
                logger.error(f"Failed to validate config.json: {e}")
                results['config.json (valid)'] = False
        
        self.results['config'] = results
        return results
    
    def check_system_requirements(self) -> Dict[str, bool]:
        """Check system requirements"""
        logger.info("Checking system requirements...")
        
        results = {}
        
        # Check Python version
        python_version = sys.version_info
        results['Python 3.8+'] = python_version >= (3, 8)
        
        # Check Node.js
        try:
            result = subprocess.run(['node', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                version_str = result.stdout.strip().lstrip('v')
                major_version = int(version_str.split('.')[0])
                results['Node.js 16+'] = major_version >= 16
            else:
                results['Node.js 16+'] = False
        except Exception:
            results['Node.js 16+'] = False
        
        # Check npm
        try:
            result = subprocess.run(['npm', '--version'], 
                                  capture_output=True, text=True)
            results['npm'] = result.returncode == 0
        except Exception:
            results['npm'] = False
        
        # Check Ollama
        try:
            result = subprocess.run(['ollama', '--version'], 
                                  capture_output=True, text=True)
            results['Ollama'] = result.returncode == 0
        except Exception:
            results['Ollama'] = False
        
        # Check available models in Ollama
        try:
            result = subprocess.run(['ollama', 'list'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                models_output = result.stdout
                results['Ollama llama3'] = 'llama3' in models_output
            else:
                results['Ollama llama3'] = False
        except Exception:
            results['Ollama llama3'] = False
        
        self.results['system'] = results
        return results
    
    def run_full_validation(self) -> Dict[str, Dict[str, bool]]:
        """Run complete validation"""
        logger.info("Starting full setup validation...")
        
        self.check_system_requirements()
        self.check_python_dependencies()
        self.check_node_dependencies()
        self.check_models()
        self.check_configuration()
        
        return self.results
    
    def print_results(self):
        """Print validation results"""
        print("\n" + "="*60)
        print("LOCAL AI AVATAR - SETUP VALIDATION RESULTS")
        print("="*60)
        
        for category, checks in self.results.items():
            if not checks:
                continue
                
            category_name = category.replace('_', ' ').title()
            print(f"\n{category_name}:")
            print("-" * len(category_name))
            
            for item, status in checks.items():
                icon = "✓" if status else "✗"
                color = "\033[92m" if status else "\033[91m"  # Green/Red
                reset = "\033[0m"
                print(f"  {color}{icon}{reset} {item}")
        
        # Summary
        total_checks = sum(len(checks) for checks in self.results.values())
        passed_checks = sum(sum(checks.values()) for checks in self.results.values())
        
        print(f"\n{'='*60}")
        print(f"SUMMARY: {passed_checks}/{total_checks} checks passed")
        
        if passed_checks == total_checks:
            print("🎉 All checks passed! Your setup is ready.")
        else:
            print("⚠️  Some checks failed. Please address the issues above.")
            
            # Provide specific guidance
            self.print_guidance()
    
    def print_guidance(self):
        """Print guidance for failed checks"""
        print(f"\n{'='*60}")
        print("SETUP GUIDANCE")
        print("="*60)
        
        # Python dependencies
        failed_python = [pkg for pkg, status in self.results.get('python_deps', {}).items() if not status]
        if failed_python:
            print(f"\n📦 Install missing Python packages:")
            print(f"   pip install {' '.join(failed_python)}")
        
        # Node dependencies
        failed_node = [pkg for pkg, status in self.results.get('node_deps', {}).items() if not status]
        if failed_node:
            print(f"\n📦 Install missing Node.js packages:")
            print(f"   npm install")
        
        # Models
        failed_models = [model for model, status in self.results.get('models', {}).items() if not status and 'optional' not in model]
        if failed_models:
            print(f"\n🤖 Download missing models:")
            print(f"   python download_models.py --required-only")
        
        # System requirements
        system_issues = [item for item, status in self.results.get('system', {}).items() if not status]
        if system_issues:
            print(f"\n🔧 System requirements:")
            for issue in system_issues:
                if 'Python' in issue:
                    print(f"   - Install Python 3.8 or higher")
                elif 'Node.js' in issue:
                    print(f"   - Install Node.js 16 or higher")
                elif 'Ollama' in issue and 'llama3' not in issue:
                    print(f"   - Install Ollama: https://ollama.ai/")
                elif 'llama3' in issue:
                    print(f"   - Download llama3 model: ollama pull llama3")
    
    def get_failed_checks(self) -> List[str]:
        """Get list of failed checks"""
        failed = []
        for category, checks in self.results.items():
            for item, status in checks.items():
                if not status:
                    failed.append(f"{category}.{item}")
        return failed

def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate Local AI Avatar setup')
    parser.add_argument('--quiet', action='store_true',
                       help='Only show summary')
    parser.add_argument('--json', action='store_true',
                       help='Output results as JSON')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.WARNING if args.quiet else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    validator = SetupValidator()
    results = validator.run_full_validation()
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        validator.print_results()
    
    # Exit with error code if validation failed
    failed_checks = validator.get_failed_checks()
    if failed_checks:
        sys.exit(1)

if __name__ == "__main__":
    main()
