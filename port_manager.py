#!/usr/bin/env python3
"""
Port management utility for Local AI Avatar
Finds and manages unused ports for the Flask backend
"""

import socket
import json
import logging
import os
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

class PortManager:
    """Manages port allocation for the application"""
    
    def __init__(self, config_file: str = "config.json"):
        """
        Initialize port manager
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = Path(config_file)
        self.default_port = 5000
        self.port_range = (5000, 5100)  # Search in this range
        
    def is_port_available(self, port: int) -> bool:
        """
        Check if a port is available
        
        Args:
            port: Port number to check
            
        Returns:
            True if port is available
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                return result != 0  # Port is available if connection fails
        except Exception as e:
            logger.warning(f"Error checking port {port}: {e}")
            return False
    
    def find_available_port(self, start_port: Optional[int] = None) -> int:
        """
        Find an available port starting from start_port
        
        Args:
            start_port: Port to start searching from
            
        Returns:
            Available port number
            
        Raises:
            RuntimeError: If no available port found
        """
        if start_port is None:
            start_port = self.default_port
        
        # First try the requested port
        if self.is_port_available(start_port):
            logger.info(f"Port {start_port} is available")
            return start_port
        
        # Search in the defined range
        logger.info(f"Port {start_port} is busy, searching for alternative...")
        
        for port in range(self.port_range[0], self.port_range[1] + 1):
            if port == start_port:
                continue  # Already tried this one
                
            if self.is_port_available(port):
                logger.info(f"Found available port: {port}")
                return port
        
        # If no port found in range, try system-assigned port
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.bind(('localhost', 0))
                port = sock.getsockname()[1]
                logger.info(f"Using system-assigned port: {port}")
                return port
        except Exception as e:
            raise RuntimeError(f"Could not find any available port: {e}")
    
    def get_configured_port(self) -> int:
        """
        Get port from configuration file
        
        Returns:
            Configured port or default port
        """
        try:
            if self.config_file.exists():
                with open(self.config_file) as f:
                    config = json.load(f)
                return config.get('backend_port', self.default_port)
        except Exception as e:
            logger.warning(f"Could not read port from config: {e}")
        
        return self.default_port
    
    def save_port_to_config(self, port: int) -> bool:
        """
        Save port to configuration file
        
        Args:
            port: Port number to save
            
        Returns:
            True if successful
        """
        try:
            config = {}
            
            # Load existing config
            if self.config_file.exists():
                with open(self.config_file) as f:
                    config = json.load(f)
            
            # Update port
            config['backend_port'] = port
            
            # Save config
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"Saved port {port} to configuration")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save port to config: {e}")
            return False
    
    def allocate_port(self, preferred_port: Optional[int] = None) -> int:
        """
        Allocate an available port and save to config
        
        Args:
            preferred_port: Preferred port number
            
        Returns:
            Allocated port number
        """
        if preferred_port is None:
            preferred_port = self.get_configured_port()
        
        port = self.find_available_port(preferred_port)
        self.save_port_to_config(port)
        
        return port
    
    def create_port_file(self, port: int) -> bool:
        """
        Create a temporary file with the current port for other processes
        
        Args:
            port: Port number to write
            
        Returns:
            True if successful
        """
        try:
            port_file = Path('.port')
            with open(port_file, 'w') as f:
                f.write(str(port))
            
            logger.info(f"Created port file with port {port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create port file: {e}")
            return False
    
    def read_port_file(self) -> Optional[int]:
        """
        Read port from temporary port file
        
        Returns:
            Port number or None if file doesn't exist
        """
        try:
            port_file = Path('.port')
            if port_file.exists():
                with open(port_file) as f:
                    port = int(f.read().strip())
                return port
        except Exception as e:
            logger.warning(f"Could not read port file: {e}")
        
        return None
    
    def cleanup_port_file(self):
        """Remove temporary port file"""
        try:
            port_file = Path('.port')
            if port_file.exists():
                port_file.unlink()
                logger.info("Cleaned up port file")
        except Exception as e:
            logger.warning(f"Could not cleanup port file: {e}")
    
    def get_backend_url(self, port: Optional[int] = None) -> str:
        """
        Get the backend URL
        
        Args:
            port: Port number (if None, reads from config/file)
            
        Returns:
            Backend URL
        """
        if port is None:
            # Try to read from port file first
            port = self.read_port_file()
            
            # Fallback to config
            if port is None:
                port = self.get_configured_port()
        
        return f"http://localhost:{port}"

def get_available_port(preferred_port: int = 5000) -> int:
    """
    Convenience function to get an available port
    
    Args:
        preferred_port: Preferred port number
        
    Returns:
        Available port number
    """
    manager = PortManager()
    return manager.find_available_port(preferred_port)

def setup_backend_port() -> Tuple[int, str]:
    """
    Setup backend port and return port and URL
    
    Returns:
        Tuple of (port, url)
    """
    manager = PortManager()
    port = manager.allocate_port()
    manager.create_port_file(port)
    url = manager.get_backend_url(port)
    
    return port, url

if __name__ == "__main__":
    # Test the port manager
    logging.basicConfig(level=logging.INFO)
    
    manager = PortManager()
    
    print("Testing port availability...")
    for test_port in [5000, 5001, 5002]:
        available = manager.is_port_available(test_port)
        print(f"Port {test_port}: {'Available' if available else 'Busy'}")
    
    print("\nFinding available port...")
    port = manager.find_available_port()
    print(f"Found port: {port}")
    
    print(f"Backend URL: {manager.get_backend_url(port)}")
