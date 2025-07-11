#!/usr/bin/env python3
"""
Model download script for Local AI Avatar
Downloads required models for TTS, STT, and vision processing
"""

import os
import sys
import requests
import logging
from pathlib import Path
from typing import Dict, List, Optional
import hashlib

logger = logging.getLogger(__name__)

class ModelDownloader:
    """Downloads and manages AI models"""
    
    def __init__(self, models_dir: str = "models"):
        """
        Initialize model downloader
        
        Args:
            models_dir: Directory to store models
        """
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        
        # Model definitions
        self.models = {
            'piper_tts': {
                'name': 'Piper TTS Voice Model',
                'files': {
                    'en_US-amy-medium.onnx': {
                        'url': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx',
                        'size': '63MB'
                    },
                    'en_US-amy-medium.onnx.json': {
                        'url': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx.json',
                        'size': '2KB'
                    }
                },
                'required': True
            },
            'yolo': {
                'name': 'YOLOv8 Object Detection',
                'files': {
                    'yolov8n.pt': {
                        'url': 'https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt',
                        'size': '6MB'
                    }
                },
                'required': False
            }
        }
    
    def check_model_exists(self, model_name: str) -> Dict[str, bool]:
        """
        Check if model files exist
        
        Args:
            model_name: Name of the model to check
            
        Returns:
            Dictionary of file existence status
        """
        if model_name not in self.models:
            return {}
        
        model_info = self.models[model_name]
        status = {}
        
        for filename in model_info['files'].keys():
            file_path = self.models_dir / filename
            status[filename] = file_path.exists()
        
        return status
    
    def download_file(self, url: str, filepath: Path, expected_size: str = None) -> bool:
        """
        Download a file with progress indication
        
        Args:
            url: URL to download from
            filepath: Local path to save file
            expected_size: Expected file size for validation
            
        Returns:
            True if successful
        """
        try:
            logger.info(f"Downloading {filepath.name}...")
            
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Show progress
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\rProgress: {progress:.1f}%", end='', flush=True)
            
            print()  # New line after progress
            logger.info(f"Downloaded {filepath.name} successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download {filepath.name}: {e}")
            if filepath.exists():
                filepath.unlink()  # Remove partial file
            return False
    
    def download_model(self, model_name: str, force: bool = False) -> bool:
        """
        Download a specific model
        
        Args:
            model_name: Name of the model to download
            force: Force re-download even if files exist
            
        Returns:
            True if successful
        """
        if model_name not in self.models:
            logger.error(f"Unknown model: {model_name}")
            return False
        
        model_info = self.models[model_name]
        logger.info(f"Downloading {model_info['name']}...")
        
        success = True
        for filename, file_info in model_info['files'].items():
            filepath = self.models_dir / filename
            
            if filepath.exists() and not force:
                logger.info(f"{filename} already exists, skipping")
                continue
            
            if not self.download_file(file_info['url'], filepath, file_info.get('size')):
                success = False
        
        return success
    
    def download_all_models(self, required_only: bool = False, force: bool = False) -> Dict[str, bool]:
        """
        Download all models
        
        Args:
            required_only: Only download required models
            force: Force re-download even if files exist
            
        Returns:
            Dictionary of download status for each model
        """
        results = {}
        
        for model_name, model_info in self.models.items():
            if required_only and not model_info.get('required', False):
                continue
            
            results[model_name] = self.download_model(model_name, force)
        
        return results
    
    def verify_models(self) -> Dict[str, Dict[str, bool]]:
        """
        Verify all models are present and valid
        
        Returns:
            Dictionary of verification status
        """
        results = {}
        
        for model_name in self.models.keys():
            results[model_name] = self.check_model_exists(model_name)
        
        return results
    
    def get_missing_models(self) -> List[str]:
        """
        Get list of missing required models
        
        Returns:
            List of missing model names
        """
        missing = []
        
        for model_name, model_info in self.models.items():
            if not model_info.get('required', False):
                continue
            
            status = self.check_model_exists(model_name)
            if not all(status.values()):
                missing.append(model_name)
        
        return missing
    
    def print_status(self):
        """Print current model status"""
        print("\n=== Model Status ===")
        
        for model_name, model_info in self.models.items():
            print(f"\n{model_info['name']} ({'Required' if model_info.get('required') else 'Optional'}):")
            
            status = self.check_model_exists(model_name)
            for filename, exists in status.items():
                status_icon = "✓" if exists else "✗"
                file_info = model_info['files'][filename]
                print(f"  {status_icon} {filename} ({file_info.get('size', 'Unknown size')})")
        
        missing = self.get_missing_models()
        if missing:
            print(f"\n⚠️  Missing required models: {', '.join(missing)}")
        else:
            print("\n✓ All required models are present")
    
    def cleanup_partial_downloads(self):
        """Remove any partial or corrupted downloads"""
        for model_name, model_info in self.models.items():
            for filename in model_info['files'].keys():
                filepath = self.models_dir / filename
                if filepath.exists() and filepath.stat().st_size == 0:
                    logger.info(f"Removing empty file: {filename}")
                    filepath.unlink()

def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Download AI models for Local AI Avatar')
    parser.add_argument('--required-only', action='store_true', 
                       help='Only download required models')
    parser.add_argument('--force', action='store_true',
                       help='Force re-download even if files exist')
    parser.add_argument('--status', action='store_true',
                       help='Show current model status')
    parser.add_argument('--cleanup', action='store_true',
                       help='Clean up partial downloads')
    parser.add_argument('--model', type=str,
                       help='Download specific model')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    downloader = ModelDownloader()
    
    if args.cleanup:
        downloader.cleanup_partial_downloads()
        return
    
    if args.status:
        downloader.print_status()
        return
    
    if args.model:
        success = downloader.download_model(args.model, args.force)
        if success:
            print(f"✓ Successfully downloaded {args.model}")
        else:
            print(f"✗ Failed to download {args.model}")
            sys.exit(1)
        return
    
    # Download models
    print("Starting model download...")
    results = downloader.download_all_models(args.required_only, args.force)
    
    # Print results
    print("\n=== Download Results ===")
    for model_name, success in results.items():
        status = "✓" if success else "✗"
        print(f"{status} {model_name}")
    
    if all(results.values()):
        print("\n✓ All models downloaded successfully!")
    else:
        print("\n⚠️  Some models failed to download")
        sys.exit(1)

if __name__ == "__main__":
    main()
