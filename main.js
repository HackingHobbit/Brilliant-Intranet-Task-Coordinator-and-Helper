const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');
const http = require('http');

let mainWindow;
let flaskProcess;
let backendPort = null;

async function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, 'assets', 'avatar.jpg'), // Use existing avatar image as icon
    titleBarStyle: 'hiddenInset',
    show: false
  });

  // Start Flask backend first
  await startFlaskBackend();

  mainWindow.loadFile('index.html');

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  mainWindow.on('closed', () => {
    if (flaskProcess) {
      flaskProcess.kill();
    }
    cleanupPortFile();
    mainWindow = null;
  });

  // Handle window close
  app.on('before-quit', () => {
    if (flaskProcess) {
      flaskProcess.kill();
    }
    cleanupPortFile();
  });
}

async function startFlaskBackend() {
  return new Promise((resolve, reject) => {
    const pythonPath = process.platform === 'win32' ? 'python' : 'python3';

    console.log('Starting Flask backend...');
    flaskProcess = spawn(pythonPath, ['app.py'], {
      stdio: ['pipe', 'pipe', 'pipe']
    });

    let backendStarted = false;

    flaskProcess.stdout.on('data', (data) => {
      const output = data.toString();
      console.log(`Flask: ${output}`);

      // Look for backend URL in output
      const urlMatch = output.match(/Backend will be available at (http:\/\/localhost:\d+)/);
      if (urlMatch && !backendStarted) {
        const backendUrl = urlMatch[1];
        const portMatch = backendUrl.match(/:(\d+)/);
        if (portMatch) {
          backendPort = parseInt(portMatch[1]);
          console.log(`Backend started on port ${backendPort}`);

          // Wait for backend to be ready
          waitForBackend(backendPort).then(() => {
            backendStarted = true;
            resolve();
          }).catch(reject);
        }
      }
    });

    flaskProcess.stderr.on('data', (data) => {
      console.error(`Flask Error: ${data}`);
    });

    flaskProcess.on('close', (code) => {
      console.log(`Flask process exited with code ${code}`);
      if (!backendStarted) {
        reject(new Error(`Flask process exited with code ${code}`));
      }
    });

    flaskProcess.on('error', (err) => {
      console.error('Failed to start Flask backend:', err);
      reject(err);
    });

    // Timeout after 30 seconds
    setTimeout(() => {
      if (!backendStarted) {
        reject(new Error('Backend startup timeout'));
      }
    }, 30000);
  });
}

// Helper function to wait for backend to be ready
async function waitForBackend(port, maxAttempts = 30) {
  return new Promise((resolve, reject) => {
    let attempts = 0;

    const checkBackend = () => {
      attempts++;

      const req = http.get(`http://localhost:${port}/health`, (res) => {
        if (res.statusCode === 200) {
          console.log('Backend is ready!');
          resolve();
        } else {
          if (attempts < maxAttempts) {
            setTimeout(checkBackend, 1000);
          } else {
            reject(new Error('Backend health check failed'));
          }
        }
      });

      req.on('error', (err) => {
        if (attempts < maxAttempts) {
          setTimeout(checkBackend, 1000);
        } else {
          reject(new Error(`Backend not responding: ${err.message}`));
        }
      });

      req.setTimeout(5000, () => {
        req.destroy();
        if (attempts < maxAttempts) {
          setTimeout(checkBackend, 1000);
        } else {
          reject(new Error('Backend health check timeout'));
        }
      });
    };

    checkBackend();
  });
}

// Helper function to read backend port from file
function getBackendPort() {
  try {
    const portFile = path.join(__dirname, '.port');
    if (fs.existsSync(portFile)) {
      const port = parseInt(fs.readFileSync(portFile, 'utf8').trim());
      return port;
    }
  } catch (error) {
    console.warn('Could not read port file:', error);
  }
  return 5000; // fallback
}

// Helper function to cleanup port file
function cleanupPortFile() {
  try {
    const portFile = path.join(__dirname, '.port');
    if (fs.existsSync(portFile)) {
      fs.unlinkSync(portFile);
      console.log('Cleaned up port file');
    }
  } catch (error) {
    console.warn('Could not cleanup port file:', error);
  }
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// IPC handlers for communication between main and renderer processes
ipcMain.handle('get-config', async () => {
  try {
    const fs = require('fs');
    const config = JSON.parse(fs.readFileSync('config.json', 'utf8'));
    return config;
  } catch (error) {
    console.error('Error reading config:', error);
    return {};
  }
});

ipcMain.handle('update-config', async (event, newConfig) => {
  try {
    const fs = require('fs');
    fs.writeFileSync('config.json', JSON.stringify(newConfig, null, 2));
    return { success: true };
  } catch (error) {
    console.error('Error updating config:', error);
    return { success: false, error: error.message };
  }
}); 