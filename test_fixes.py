#!/usr/bin/env python3
"""
Test script to verify all fixes are working correctly
"""

import os
import sys
import json
import subprocess
import importlib
import logging
from pathlib import Path
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class FixTester:
    """Test all the fixes that were implemented"""
    
    def __init__(self):
        """Initialize the tester"""
        self.project_root = Path.cwd()
        self.test_results = {}
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def test_python_imports(self) -> bool:
        """Test that all Python imports work correctly"""
        logger.info("Testing Python imports...")
        
        modules_to_test = [
            ('app', 'Flask app imports'),
            ('memory', 'Memory management'),
            ('tools', 'Agentic tools'),
            ('stt', 'Speech-to-text'),
            ('tts', 'Text-to-speech'),
            ('vision', 'Vision processing'),
            ('setup_keys', 'Key management'),
            ('validate_setup', 'Setup validation'),
            ('download_models', 'Model downloader')
        ]
        
        results = {}
        for module_name, description in modules_to_test:
            try:
                module = importlib.import_module(module_name)
                results[module_name] = True
                logger.info(f"✓ {description}")
            except ImportError as e:
                results[module_name] = False
                logger.error(f"✗ {description}: {e}")
        
        self.test_results['python_imports'] = results
        return all(results.values())
    
    def test_flask_cors_fix(self) -> bool:
        """Test that Flask-CORS import is fixed"""
        logger.info("Testing Flask-CORS fix...")
        
        try:
            from flask_cors import CORS
            logger.info("✓ Flask-CORS import successful")
            return True
        except ImportError as e:
            logger.error(f"✗ Flask-CORS import failed: {e}")
            return False
    
    def test_requirements_file(self) -> bool:
        """Test that requirements.txt has all necessary packages"""
        logger.info("Testing requirements.txt...")
        
        requirements_file = self.project_root / 'requirements.txt'
        if not requirements_file.exists():
            logger.error("✗ requirements.txt not found")
            return False
        
        with open(requirements_file) as f:
            content = f.read()
        
        required_packages = [
            'flask-cors',
            'tiktoken',
            'ollama'
        ]
        
        missing = []
        for package in required_packages:
            if package not in content:
                missing.append(package)
        
        if missing:
            logger.error(f"✗ Missing packages in requirements.txt: {missing}")
            return False
        
        logger.info("✓ requirements.txt contains all required packages")
        return True
    
    def test_javascript_fixes(self) -> bool:
        """Test JavaScript fixes"""
        logger.info("Testing JavaScript fixes...")
        
        js_files = ['ui.js', 'avatar.js', 'lipsync.js', 'settings-panel.js']
        results = {}
        
        for js_file in js_files:
            file_path = self.project_root / js_file
            if not file_path.exists():
                results[js_file] = False
                logger.error(f"✗ {js_file} not found")
                continue
            
            with open(file_path) as f:
                content = f.read()
            
            # Check for Node.js require statements (should be removed)
            if 'require(' in content and 'module.exports' in content:
                results[js_file] = False
                logger.error(f"✗ {js_file} still contains Node.js require/exports")
            else:
                results[js_file] = True
                logger.info(f"✓ {js_file} is browser-compatible")
        
        self.test_results['javascript_fixes'] = results
        return all(results.values())
    
    def test_electron_security(self) -> bool:
        """Test Electron security improvements"""
        logger.info("Testing Electron security...")
        
        main_js = self.project_root / 'main.js'
        if not main_js.exists():
            logger.error("✗ main.js not found")
            return False
        
        with open(main_js) as f:
            content = f.read()
        
        # Check for secure settings
        security_checks = [
            ('nodeIntegration: false', 'Node integration disabled'),
            ('contextIsolation: true', 'Context isolation enabled'),
            ('preload:', 'Preload script specified')
        ]
        
        results = {}
        for check, description in security_checks:
            if check in content:
                results[check] = True
                logger.info(f"✓ {description}")
            else:
                results[check] = False
                logger.error(f"✗ {description}")
        
        # Check if preload.js exists
        preload_js = self.project_root / 'preload.js'
        if preload_js.exists():
            logger.info("✓ preload.js exists")
            results['preload_exists'] = True
        else:
            logger.error("✗ preload.js not found")
            results['preload_exists'] = False
        
        self.test_results['electron_security'] = results
        return all(results.values())
    
    def test_config_files(self) -> bool:
        """Test configuration files"""
        logger.info("Testing configuration files...")
        
        config_files = [
            ('config.json', 'Main configuration'),
            ('package.json', 'Node.js configuration'),
            ('requirements.txt', 'Python dependencies')
        ]
        
        results = {}
        for filename, description in config_files:
            file_path = self.project_root / filename
            if file_path.exists():
                results[filename] = True
                logger.info(f"✓ {description} exists")
                
                # Validate JSON files
                if filename.endswith('.json'):
                    try:
                        with open(file_path) as f:
                            json.load(f)
                        logger.info(f"✓ {filename} is valid JSON")
                    except json.JSONDecodeError as e:
                        results[filename] = False
                        logger.error(f"✗ {filename} invalid JSON: {e}")
            else:
                results[filename] = False
                logger.error(f"✗ {description} not found")
        
        self.test_results['config_files'] = results
        return all(results.values())
    
    def test_setup_scripts(self) -> bool:
        """Test setup scripts"""
        logger.info("Testing setup scripts...")
        
        scripts = [
            ('setup.py', 'Main setup script'),
            ('validate_setup.py', 'Validation script'),
            ('download_models.py', 'Model downloader'),
            ('setup_keys.py', 'Key management')
        ]
        
        results = {}
        for script_name, description in scripts:
            script_path = self.project_root / script_name
            if script_path.exists():
                results[script_name] = True
                logger.info(f"✓ {description} exists")
                
                # Test if script is executable
                if os.access(script_path, os.X_OK):
                    logger.info(f"✓ {script_name} is executable")
                else:
                    logger.warning(f"⚠ {script_name} not executable (may need chmod +x)")
            else:
                results[script_name] = False
                logger.error(f"✗ {description} not found")
        
        self.test_results['setup_scripts'] = results
        return all(results.values())
    
    def test_models_directory(self) -> bool:
        """Test models directory setup"""
        logger.info("Testing models directory...")
        
        models_dir = self.project_root / 'models'
        if models_dir.exists() and models_dir.is_dir():
            logger.info("✓ Models directory exists")
            return True
        else:
            logger.error("✗ Models directory not found")
            return False
    
    def test_memory_token_counting(self) -> bool:
        """Test memory token counting fix"""
        logger.info("Testing memory token counting...")
        
        try:
            from memory import MemoryManager
            
            # Create a test instance
            memory_mgr = MemoryManager()
            
            # Test token counting
            test_text = "This is a test sentence for token counting."
            token_count = memory_mgr.count_tokens(test_text)
            
            if isinstance(token_count, int) and token_count > 0:
                logger.info(f"✓ Token counting works: {token_count} tokens")
                return True
            else:
                logger.error("✗ Token counting returned invalid result")
                return False
                
        except Exception as e:
            logger.error(f"✗ Token counting test failed: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all tests"""
        logger.info("Starting comprehensive fix testing...")
        
        tests = [
            ('Python Imports', self.test_python_imports),
            ('Flask-CORS Fix', self.test_flask_cors_fix),
            ('Requirements File', self.test_requirements_file),
            ('JavaScript Fixes', self.test_javascript_fixes),
            ('Electron Security', self.test_electron_security),
            ('Config Files', self.test_config_files),
            ('Setup Scripts', self.test_setup_scripts),
            ('Models Directory', self.test_models_directory),
            ('Memory Token Counting', self.test_memory_token_counting)
        ]
        
        results = {}
        for test_name, test_func in tests:
            print(f"\n{'='*60}")
            print(f"Testing: {test_name}")
            print('='*60)
            
            try:
                results[test_name] = test_func()
            except Exception as e:
                logger.error(f"Test {test_name} failed with exception: {e}")
                results[test_name] = False
        
        return results
    
    def print_summary(self, results: Dict[str, bool]):
        """Print test summary"""
        print(f"\n{'='*60}")
        print("TEST SUMMARY")
        print('='*60)
        
        passed = sum(results.values())
        total = len(results)
        
        for test_name, passed_test in results.items():
            icon = "✅" if passed_test else "❌"
            print(f"{icon} {test_name}")
        
        print(f"\n{passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All fixes are working correctly!")
        else:
            print("⚠️  Some issues remain. Check the logs above.")
            
        return passed == total

def main():
    """Main function"""
    tester = FixTester()
    results = tester.run_all_tests()
    success = tester.print_summary(results)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
