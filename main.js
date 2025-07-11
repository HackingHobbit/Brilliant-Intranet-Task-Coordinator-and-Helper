const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let win, flaskProcess;

function createWindow() {
  win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: { nodeIntegration: true, contextIsolation: false }
  });
  win.loadFile('index.html');

  flaskProcess = spawn('python', ['app.py']);
  flaskProcess.on('data', data => console.log(`Flask: ${data}`));
  flaskProcess.on('error', err => console.error(`Flask Error: ${err}`));

  win.on('closed', () => {
    flaskProcess.kill();
    win = null;
  });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});