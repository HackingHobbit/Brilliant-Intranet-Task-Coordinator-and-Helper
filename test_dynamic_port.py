#!/usr/bin/env python3
"""
Simple test to verify the dynamic port system works end-to-end
"""

import time
import subprocess
import requests
import json
from pathlib import Path

def test_dynamic_port_system():
    """Test the complete dynamic port system"""
    print("🧪 Testing Dynamic Port System")
    print("=" * 50)
    
    # Start backend
    print("1. Starting backend with dynamic port...")
    process = subprocess.Popen(
        ['python', 'app.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # Wait for port file to be created
        port_file = Path('.port')
        backend_port = None
        
        for i in range(30):  # Wait up to 30 seconds
            if port_file.exists():
                with open(port_file) as f:
                    backend_port = int(f.read().strip())
                print(f"   ✅ Backend started on port: {backend_port}")
                break
            time.sleep(1)
        
        if not backend_port:
            raise Exception("Backend startup timeout - no port file created")
        
        # Test health endpoint
        print("2. Testing health endpoint...")
        health_url = f"http://localhost:{backend_port}/health"
        
        for i in range(10):  # Wait up to 10 seconds for health check
            try:
                response = requests.get(health_url, timeout=5)
                if response.status_code == 200:
                    health_data = response.json()
                    print(f"   ✅ Health check passed: {health_data['status']}")
                    break
            except requests.exceptions.RequestException:
                if i < 9:
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
            print(f"   ✅ Config endpoint working")
            print(f"   📋 Backend port in config: {config.get('backend_port', 'not set')}")
        else:
            raise Exception("Config endpoint failed")
        
        # Test that port is different from default if 5000 is busy
        if backend_port != 5000:
            print(f"   ✅ Port conflict resolution worked (using {backend_port} instead of 5000)")
        
        print("\n🎉 Dynamic Port System Test PASSED!")
        print(f"\n📊 Results:")
        print(f"   • Backend Port: {backend_port}")
        print(f"   • Health URL: {health_url}")
        print(f"   • Config URL: {config_url}")
        print(f"   • Port File: {port_file} ({'exists' if port_file.exists() else 'missing'})")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test FAILED: {e}")
        return False
        
    finally:
        # Cleanup
        print("\n4. Cleaning up...")
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
        
        # Remove port file
        if Path('.port').exists():
            Path('.port').unlink()
            print("   ✅ Port file cleaned up")

if __name__ == "__main__":
    success = test_dynamic_port_system()
    
    if success:
        print("\n" + "=" * 50)
        print("✅ DYNAMIC PORT SYSTEM IS WORKING!")
        print("=" * 50)
        print("\nYou can now:")
        print("  • Run 'npm start' to start the full application")
        print("  • Run 'python app.py' to start just the backend")
        print("  • The system will automatically find an unused port")
        print("  • No manual port configuration needed!")
    else:
        print("\n" + "=" * 50)
        print("❌ DYNAMIC PORT SYSTEM NEEDS ATTENTION")
        print("=" * 50)
        exit(1)
