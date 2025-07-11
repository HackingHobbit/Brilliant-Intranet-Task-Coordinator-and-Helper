#!/usr/bin/env python3
"""
Setup script for Local AI Avatar API keys and credentials
"""

import keyring
import logging
import json
import os
from typing import Dict, List, Optional
import getpass

logger = logging.getLogger(__name__)

class KeyManager:
    """Manages API keys and credentials securely"""
    
    def __init__(self):
        """Initialize key manager"""
        self.required_keys = self._get_required_keys()
        self.logger = logging.getLogger(__name__)
    
    def _get_required_keys(self) -> Dict[str, Dict]:
        """Get list of required API keys and their descriptions"""
        return {
            'alpha_vantage': {
                'api_key': {
                    'description': 'Alpha Vantage API key for financial data',
                    'url': 'https://www.alphavantage.co/support/#api-key',
                    'required': False
                }
            },
            'finnhub': {
                'api_key': {
                    'description': 'Finnhub API key for financial data',
                    'url': 'https://finnhub.io/register',
                    'required': False
                }
            },
            'google': {
                'client_id': {
                    'description': 'Google OAuth client ID for Gmail/Calendar',
                    'url': 'https://console.developers.google.com/',
                    'required': False
                },
                'client_secret': {
                    'description': 'Google OAuth client secret',
                    'url': 'https://console.developers.google.com/',
                    'required': False
                },
                'credentials': {
                    'description': 'Google OAuth credentials JSON',
                    'url': 'https://console.developers.google.com/',
                    'required': False
                }
            },
            'microsoft': {
                'client_id': {
                    'description': 'Microsoft Graph client ID for Outlook',
                    'url': 'https://portal.azure.com/',
                    'required': False
                },
                'client_secret': {
                    'description': 'Microsoft Graph client secret',
                    'url': 'https://portal.azure.com/',
                    'required': False
                }
            },
            'icloud': {
                'username': {
                    'description': 'iCloud email address',
                    'url': 'https://appleid.apple.com/',
                    'required': False
                },
                'password': {
                    'description': 'iCloud app-specific password',
                    'url': 'https://appleid.apple.com/',
                    'required': False,
                    'secure': True
                }
            },
            'openai': {
                'api_key': {
                    'description': 'OpenAI API key (optional, for enhanced features)',
                    'url': 'https://platform.openai.com/api-keys',
                    'required': False
                }
            }
        }
    
    def setup_required_keys(self, interactive: bool = True) -> Dict[str, bool]:
        """
        Setup required API keys
        
        Args:
            interactive: Whether to prompt user for missing keys
            
        Returns:
            Dictionary of setup status for each service
        """
        try:
            setup_status = {}
            
            for service, keys in self.required_keys.items():
                service_status = {}
                
                for key_name, key_info in keys.items():
                    # Check if key exists
                    existing_key = self.get_key(service, key_name)
                    
                    if existing_key:
                        service_status[key_name] = True
                        self.logger.info(f"Found existing key: {service}.{key_name}")
                    else:
                        if key_info.get('required', False):
                            if interactive:
                                # Prompt for required key
                                self._prompt_for_key(service, key_name, key_info)
                                service_status[key_name] = True
                            else:
                                service_status[key_name] = False
                                self.logger.warning(f"Missing required key: {service}.{key_name}")
                        else:
                            # Optional key
                            service_status[key_name] = False
                            self.logger.debug(f"Optional key not set: {service}.{key_name}")
                
                setup_status[service] = all(service_status.values())
            
            return setup_status
            
        except Exception as e:
            self.logger.error(f"Key setup failed: {e}")
            return {}
    
    def _prompt_for_key(self, service: str, key_name: str, key_info: Dict):
        """Prompt user for API key"""
        try:
            print(f"\n=== {service.upper()} - {key_name.upper()} ===")
            print(f"Description: {key_info['description']}")
            print(f"Get key from: {key_info['url']}")
            
            if key_info.get('secure', False):
                # Use getpass for secure input
                value = getpass.getpass(f"Enter {key_name}: ")
            else:
                value = input(f"Enter {key_name}: ")
            
            if value.strip():
                self.set_key(service, key_name, value.strip())
                print(f"✓ {key_name} saved successfully")
            else:
                print(f"✗ {key_name} not provided")
                
        except KeyboardInterrupt:
            print("\nSetup cancelled by user")
            raise
        except Exception as e:
            self.logger.error(f"Failed to prompt for key {service}.{key_name}: {e}")
    
    def get_key(self, service: str, key_name: str) -> Optional[str]:
        """
        Get API key from secure storage
        
        Args:
            service: Service name
            key_name: Key name
            
        Returns:
            API key value or None if not found
        """
        try:
            return keyring.get_password(service, key_name)
        except Exception as e:
            self.logger.error(f"Failed to get key {service}.{key_name}: {e}")
            return None
    
    def set_key(self, service: str, key_name: str, value: str) -> bool:
        """
        Set API key in secure storage
        
        Args:
            service: Service name
            key_name: Key name
            value: Key value
            
        Returns:
            True if successful
        """
        try:
            keyring.set_password(service, key_name, value)
            self.logger.info(f"Key {service}.{key_name} saved successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to set key {service}.{key_name}: {e}")
            return False
    
    def delete_key(self, service: str, key_name: str) -> bool:
        """
        Delete API key from secure storage
        
        Args:
            service: Service name
            key_name: Key name
            
        Returns:
            True if successful
        """
        try:
            keyring.delete_password(service, key_name)
            self.logger.info(f"Key {service}.{key_name} deleted successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete key {service}.{key_name}: {e}")
            return False
    
    def list_keys(self) -> Dict[str, Dict[str, bool]]:
        """
        List all stored keys
        
        Returns:
            Dictionary of services and their key status
        """
        try:
            key_status = {}
            
            for service, keys in self.required_keys.items():
                service_status = {}
                
                for key_name in keys.keys():
                    has_key = self.get_key(service, key_name) is not None
                    service_status[key_name] = has_key
                
                key_status[service] = service_status
            
            return key_status
            
        except Exception as e:
            self.logger.error(f"Failed to list keys: {e}")
            return {}
    
    def export_keys(self, filepath: str) -> bool:
        """
        Export keys to file (for backup purposes)
        
        Args:
            filepath: Output file path
            
        Returns:
            True if successful
        """
        try:
            key_data = {}
            
            for service, keys in self.required_keys.items():
                service_data = {}
                
                for key_name in keys.keys():
                    value = self.get_key(service, key_name)
                    if value:
                        service_data[key_name] = value
                
                if service_data:
                    key_data[service] = service_data
            
            # Save to file
            with open(filepath, 'w') as f:
                json.dump(key_data, f, indent=2)
            
            self.logger.info(f"Keys exported to: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export keys: {e}")
            return False
    
    def import_keys(self, filepath: str) -> bool:
        """
        Import keys from file
        
        Args:
            filepath: Input file path
            
        Returns:
            True if successful
        """
        try:
            if not os.path.exists(filepath):
                self.logger.error(f"Import file not found: {filepath}")
                return False
            
            with open(filepath, 'r') as f:
                key_data = json.load(f)
            
            imported_count = 0
            
            for service, keys in key_data.items():
                for key_name, value in keys.items():
                    if self.set_key(service, key_name, value):
                        imported_count += 1
            
            self.logger.info(f"Imported {imported_count} keys from: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to import keys: {e}")
            return False
    
    def validate_keys(self) -> Dict[str, Dict[str, bool]]:
        """
        Validate stored API keys
        
        Returns:
            Dictionary of validation results
        """
        try:
            validation_results = {}
            
            for service, keys in self.required_keys.items():
                service_results = {}
                
                for key_name in keys.keys():
                    value = self.get_key(service, key_name)
                    if value:
                        # Basic validation (check if key has expected format)
                        is_valid = self._validate_key_format(service, key_name, value)
                        service_results[key_name] = is_valid
                    else:
                        service_results[key_name] = False
                
                validation_results[service] = service_results
            
            return validation_results
            
        except Exception as e:
            self.logger.error(f"Key validation failed: {e}")
            return {}
    
    def _validate_key_format(self, service: str, key_name: str, value: str) -> bool:
        """
        Validate key format (basic checks)
        
        Args:
            service: Service name
            key_name: Key name
            value: Key value
            
        Returns:
            True if format appears valid
        """
        try:
            if not value or len(value.strip()) == 0:
                return False
            
            # Basic format checks based on service
            if service == 'alpha_vantage':
                return len(value) >= 20  # Alpha Vantage keys are typically long
            elif service == 'finnhub':
                return len(value) >= 20  # Finnhub keys are typically long
            elif service == 'google':
                if key_name == 'client_id':
                    return '.apps.googleusercontent.com' in value
                elif key_name == 'client_secret':
                    return len(value) >= 10
            elif service == 'microsoft':
                if key_name == 'client_id':
                    return len(value) >= 20
                elif key_name == 'client_secret':
                    return len(value) >= 10
            elif service == 'icloud':
                if key_name == 'username':
                    return '@' in value
                elif key_name == 'password':
                    return len(value) >= 10  # App-specific passwords are long
            elif service == 'openai':
                return value.startswith('sk-')
            
            # Default validation
            return len(value) >= 5
            
        except Exception as e:
            self.logger.error(f"Key format validation failed: {e}")
            return False
    
    def get_missing_keys(self) -> List[str]:
        """
        Get list of missing required keys
        
        Returns:
            List of missing key identifiers
        """
        try:
            missing_keys = []
            
            for service, keys in self.required_keys.items():
                for key_name, key_info in keys.items():
                    if key_info.get('required', False):
                        if not self.get_key(service, key_name):
                            missing_keys.append(f"{service}.{key_name}")
            
            return missing_keys
            
        except Exception as e:
            self.logger.error(f"Failed to get missing keys: {e}")
            return []
    
    def print_key_status(self):
        """Print current key status"""
        try:
            print("\n=== API Key Status ===")
            
            key_status = self.list_keys()
            
            for service, keys in key_status.items():
                print(f"\n{service.upper()}:")
                
                for key_name, has_key in keys.items():
                    status = "✓" if has_key else "✗"
                    key_info = self.required_keys[service][key_name]
                    required = " (required)" if key_info.get('required', False) else " (optional)"
                    
                    print(f"  {status} {key_name}{required}")
                    if not has_key and key_info.get('required', False):
                        print(f"    Get from: {key_info['url']}")
            
            # Check for missing required keys
            missing_keys = self.get_missing_keys()
            if missing_keys:
                print(f"\n⚠️  Missing required keys: {', '.join(missing_keys)}")
            else:
                print("\n✓ All required keys are configured")
                
        except Exception as e:
            self.logger.error(f"Failed to print key status: {e}")

# Global instance for convenience
_key_manager = None

def get_key_manager() -> KeyManager:
    """Get global key manager instance"""
    global _key_manager
    if _key_manager is None:
        _key_manager = KeyManager()
    return _key_manager

def setup_required_keys(interactive: bool = True) -> Dict[str, bool]:
    """
    Setup required API keys
    
    Args:
        interactive: Whether to prompt user for missing keys
        
    Returns:
        Dictionary of setup status for each service
    """
    manager = get_key_manager()
    return manager.setup_required_keys(interactive)

def get_key(service: str, key_name: str) -> Optional[str]:
    """
    Get API key from secure storage
    
    Args:
        service: Service name
        key_name: Key name
        
    Returns:
        API key value or None if not found
    """
    manager = get_key_manager()
    return manager.get_key(service, key_name)

def set_key(service: str, key_name: str, value: str) -> bool:
    """
    Set API key in secure storage
    
    Args:
        service: Service name
        key_name: Key name
        value: Key value
        
    Returns:
        True if successful
    """
    manager = get_key_manager()
    return manager.set_key(service, key_name, value)

if __name__ == "__main__":
    # Test key manager
    manager = KeyManager()
    
    # Print current status
    manager.print_key_status()
    
    # Setup keys interactively
    print("\nSetting up keys...")
    setup_status = manager.setup_required_keys(interactive=True)
    
    print(f"\nSetup status: {setup_status}")
    
    # Print final status
    manager.print_key_status() 