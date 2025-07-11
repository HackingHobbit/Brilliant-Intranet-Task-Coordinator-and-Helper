const { contextBridge, ipcRenderer } = require('electron');
const fs = require('fs');
const path = require('path');

// Function to read backend port from file
function getBackendUrl() {
  try {
    const portFile = path.join(process.cwd(), '.port');
    if (fs.existsSync(portFile)) {
      const port = fs.readFileSync(portFile, 'utf8').trim();
      return `http://localhost:${port}`;
    }
  } catch (error) {
    console.warn('Could not read port file:', error);
  }

  // Fallback to default port
  return 'http://localhost:5000';
}

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // Configuration methods
  getConfig: () => ipcRenderer.invoke('get-config'),
  updateConfig: (config) => ipcRenderer.invoke('update-config', config),

  // File operations
  selectFile: (options) => ipcRenderer.invoke('select-file', options),

  // System information
  getSystemInfo: () => ipcRenderer.invoke('get-system-info'),

  // Backend communication helpers
  getBackendUrl: getBackendUrl,

  // Utility functions
  platform: process.platform,

  // Event listeners
  onConfigUpdate: (callback) => {
    ipcRenderer.on('config-updated', callback);
  },

  removeAllListeners: (channel) => {
    ipcRenderer.removeAllListeners(channel);
  }
});

// Expose a limited set of Node.js APIs
contextBridge.exposeInMainWorld('nodeAPI', {
  path: {
    join: (...args) => require('path').join(...args),
    dirname: (path) => require('path').dirname(path),
    basename: (path) => require('path').basename(path)
  }
});
