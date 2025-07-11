#!/usr/bin/env python3
"""
Test script for the dynamic port system
"""

import time
import subprocess
import requests
import logging
from pathlib import Path
from port_manager import PortManager

logger = logging.getLogger(__name__)

def test_port_manager():
    """Test the PortManager functionality"""
    print("Testing PortManager...")
    
    manager = PortManager()
    
    # Test port availability checking
    print("1. Testing port availability checking...")
    for port in [5000, 5001, 5002]:
        available = manager.is_port_available(port)
        print(f"   Port {port}: {'Available' if available else 'Busy'}")
    
    # Test finding available port
    print("\n2. Testing available port finding...")
    port = manager.find_available_port()
    print(f"   Found available port: {port}")
    
    # Test saving to config
    print("\n3. Testing config save/load...")
    manager.save_port_to_config(port)
    loaded_port = manager.get_configured_port()
    print(f"   Saved port: {port}, Loaded port: {loaded_port}")
    assert port == loaded_port, "Port save/load failed"
    
    # Test port file operations
    print("\n4. Testing port file operations...")
    manager.create_port_file(port)
    file_port = manager.read_port_file()
    print(f"   Port file port: {file_port}")
    assert port == file_port, "Port file operations failed"
    
    # Test backend URL generation
    print("\n5. Testing backend URL generation...")
    url = manager.get_backend_url(port)
    print(f"   Backend URL: {url}")
    assert f":{port}" in url, "Backend URL generation failed"
    
    manager.cleanup_port_file()
    print("✅ PortManager tests passed!")

def test_backend_startup():
    """Test backend startup with dynamic port"""
    print("\nTesting backend startup...")
    
    # Start the backend
    print("1. Starting Flask backend...")
    process = subprocess.Popen(
        ['python', 'app.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # Wait for startup and capture port
        backend_port = None
        start_time = time.time()
        timeout = 30
        
        while time.time() - start_time < timeout:
            # Check if port file exists
            manager = PortManager()
            port = manager.read_port_file()
            
            if port:
                backend_port = port
                print(f"   Backend started on port: {backend_port}")
                break
            
            time.sleep(1)
        
        if not backend_port:
            raise Exception("Backend startup timeout")
        
        # Test health check
        print("2. Testing health check...")
        health_url = f"http://localhost:{backend_port}/health"
        
        for attempt in range(10):
            try:
                response = requests.get(health_url, timeout=5)
                if response.status_code == 200:
                    health_data = response.json()
                    print(f"   Health check passed: {health_data['status']}")
                    break
            except requests.exceptions.RequestException:
                if attempt < 9:
                    time.sleep(1)
                    continue
                else:
                    raise Exception("Health check failed")
        
        # Test config endpoint
        print("3. Testing config endpoint...")
        config_url = f"http://localhost:{backend_port}/get_config"
        response = requests.get(config_url, timeout=5)
        
        if response.status_code == 200:
            config = response.json()
            print(f"   Config endpoint working, backend_port: {config.get('backend_port')}")
        else:
            raise Exception("Config endpoint failed")
        
        print("✅ Backend startup tests passed!")
        
    finally:
        # Cleanup
        print("4. Cleaning up...")
        process.terminate()
        process.wait(timeout=10)
        
        # Cleanup port file
        manager = PortManager()
        manager.cleanup_port_file()

def test_port_conflict_resolution():
    """Test port conflict resolution"""
    print("\nTesting port conflict resolution...")
    
    # Start a dummy server on port 5000
    import socket
    import threading
    
    def dummy_server():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(('localhost', 5000))
            sock.listen(1)
            print("   Dummy server started on port 5000")
            
            # Keep server running for a bit
            sock.settimeout(10)
            try:
                conn, addr = sock.accept()
                conn.close()
            except socket.timeout:
                pass
        except Exception as e:
            print(f"   Dummy server error: {e}")
        finally:
            sock.close()
    
    # Start dummy server in background
    server_thread = threading.Thread(target=dummy_server)
    server_thread.daemon = True
    server_thread.start()
    
    time.sleep(1)  # Let server start
    
    # Test port manager finds alternative
    manager = PortManager()
    port = manager.find_available_port(5000)
    
    print(f"   Found alternative port: {port}")
    assert port != 5000, "Should have found alternative to busy port 5000"
    
    print("✅ Port conflict resolution tests passed!")

def main():
    """Run all tests"""
    logging.basicConfig(level=logging.INFO)
    
    print("🧪 Testing Dynamic Port System")
    print("=" * 50)
    
    try:
        test_port_manager()
        test_port_conflict_resolution()
        test_backend_startup()
        
        print("\n🎉 All tests passed!")
        print("\nThe dynamic port system is working correctly!")
        print("\nUsage:")
        print("  npm start          # Start with Electron (auto port)")
        print("  python app.py      # Start backend only (auto port)")
        print("  npm run test-port  # Test port manager")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
