class SettingsPanel {
    constructor() {
        this.isOpen = false;
        this.config = {};
        this.panel = null;
        this.overlay = null;
        
        this.init();
    }

    init() {
        this.createPanel();
        this.loadConfig();
        this.setupEventListeners();
    }

    createPanel() {
        // Create overlay
        this.overlay = document.createElement('div');
        this.overlay.className = 'settings-overlay';
        this.overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            z-index: 1000;
            display: none;
        `;

        // Create panel
        this.panel = document.createElement('div');
        this.panel.className = 'settings-panel';
        this.panel.style.cssText = `
            position: fixed;
            top: 0;
            right: -400px;
            width: 400px;
            height: 100%;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border-left: 2px solid #00bfff;
            box-shadow: -5px 0 20px rgba(0, 191, 255, 0.3);
            z-index: 1001;
            overflow-y: auto;
            transition: right 0.3s ease;
            padding: 20px;
            color: white;
        `;

        // Add content
        this.panel.innerHTML = this.getSettingsHTML();
        
        // Add to DOM
        document.body.appendChild(this.overlay);
        document.body.appendChild(this.panel);
    }

    getSettingsHTML() {
        return `
            <div class="settings-header">
                <h2 style="margin: 0 0 20px 0; color: #00bfff; font-family: 'Orbitron', sans-serif;">
                    ⚙️ Settings
                </h2>
                <button id="close-settings" style="
                    position: absolute;
                    top: 20px;
                    right: 20px;
                    background: none;
                    border: none;
                    color: #00bfff;
                    font-size: 24px;
                    cursor: pointer;
                ">×</button>
            </div>

            <form id="settings-form">
                <div class="settings-section">
                    <h3 style="color: #00bfff; margin-bottom: 15px;">Email Configuration</h3>
                    <div class="form-group">
                        <label for="email_mode">Email Mode:</label>
                        <select name="email_mode" id="email_mode" style="
                            width: 100%;
                            padding: 8px;
                            background: #2a2a3e;
                            border: 1px solid #00bfff;
                            color: white;
                            border-radius: 4px;
                        ">
                            <option value="local">Local Mail</option>
                            <option value="gmail">Gmail</option>
                            <option value="outlook">Outlook</option>
                            <option value="icloud">iCloud</option>
                        </select>
                    </div>
                </div>

                <div class="settings-section">
                    <h3 style="color: #00bfff; margin-bottom: 15px;">Calendar Configuration</h3>
                    <div class="form-group">
                        <label for="calendar_mode">Calendar Mode:</label>
                        <select name="calendar_mode" id="calendar_mode" style="
                            width: 100%;
                            padding: 8px;
                            background: #2a2a3e;
                            border: 1px solid #00bfff;
                            color: white;
                            border-radius: 4px;
                        ">
                            <option value="local">Local Calendar</option>
                            <option value="gmail">Google Calendar</option>
                            <option value="outlook">Outlook Calendar</option>
                            <option value="icloud">iCloud Calendar</option>
                        </select>
                    </div>
                </div>

                <div class="settings-section">
                    <h3 style="color: #00bfff; margin-bottom: 15px;">Financial API</h3>
                    <div class="form-group">
                        <label for="financial_api">Financial Data Source:</label>
                        <select name="financial_api" id="financial_api" style="
                            width: 100%;
                            padding: 8px;
                            background: #2a2a3e;
                            border: 1px solid #00bfff;
                            color: white;
                            border-radius: 4px;
                        ">
                            <option value="yfinance">Yahoo Finance (Free)</option>
                            <option value="alpha_vantage">Alpha Vantage (25 req/day)</option>
                            <option value="finnhub">Finnhub (60 req/min)</option>
                        </select>
                    </div>
                </div>

                <div class="settings-section">
                    <h3 style="color: #00bfff; margin-bottom: 15px;">Avatar Settings</h3>
                    <div class="form-group">
                        <label style="display: flex; align-items: center; cursor: pointer;">
                            <input type="checkbox" name="enable_3d" id="enable_3d" style="margin-right: 8px;">
                            Enable 3D Avatar
                        </label>
                    </div>
                </div>

                <div class="settings-section">
                    <h3 style="color: #00bfff; margin-bottom: 15px;">API Keys</h3>
                    <div class="form-group">
                        <label for="alpha_vantage_key">Alpha Vantage API Key:</label>
                        <input type="password" name="alpha_vantage_key" id="alpha_vantage_key" placeholder="Enter API key" style="
                            width: 100%;
                            padding: 8px;
                            background: #2a2a3e;
                            border: 1px solid #00bfff;
                            color: white;
                            border-radius: 4px;
                        ">
                    </div>
                    <div class="form-group">
                        <label for="googlemaps_key">Google Maps API Key:</label>
                        <input type="password" name="googlemaps_key" id="googlemaps_key" placeholder="Enter API key" style="
                            width: 100%;
                            padding: 8px;
                            background: #2a2a3e;
                            border: 1px solid #00bfff;
                            color: white;
                            border-radius: 4px;
                        ">
                    </div>
                    <div class="form-group">
                        <label for="icloud_username">iCloud Username:</label>
                        <input type="email" name="icloud_username" id="icloud_username" placeholder="Apple ID email" style="
                            width: 100%;
                            padding: 8px;
                            background: #2a2a3e;
                            border: 1px solid #00bfff;
                            color: white;
                            border-radius: 4px;
                        ">
                    </div>
                    <div class="form-group">
                        <label for="icloud_password">iCloud App-Specific Password:</label>
                        <input type="password" name="icloud_password" id="icloud_password" placeholder="App-specific password" style="
                            width: 100%;
                            padding: 8px;
                            background: #2a2a3e;
                            border: 1px solid #00bfff;
                            color: white;
                            border-radius: 4px;
                        ">
                    </div>
                </div>

                <div class="settings-section">
                    <h3 style="color: #00bfff; margin-bottom: 15px;">Performance</h3>
                    <div class="form-group">
                        <label for="performance_mode">Performance Mode:</label>
                        <select name="performance_mode" id="performance_mode" style="
                            width: 100%;
                            padding: 8px;
                            background: #2a2a3e;
                            border: 1px solid #00bfff;
                            color: white;
                            border-radius: 4px;
                        ">
                            <option value="optimized">Optimized (Recommended)</option>
                            <option value="balanced">Balanced</option>
                            <option value="quality">High Quality</option>
                        </select>
                    </div>
                </div>

                <div style="margin-top: 30px; text-align: center;">
                    <button type="submit" style="
                        background: linear-gradient(45deg, #00bfff, #0080ff);
                        border: none;
                        color: white;
                        padding: 12px 30px;
                        border-radius: 6px;
                        cursor: pointer;
                        font-weight: bold;
                        transition: all 0.3s ease;
                    " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                        💾 Save Settings
                    </button>
                </div>
            </form>
        `;
    }

    setupEventListeners() {
        // Close button
        const closeBtn = this.panel.querySelector('#close-settings');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                this.close();
            });
        }

        // Overlay click to close
        this.overlay.addEventListener('click', () => {
            this.close();
        });

        // Form submission
        const form = this.panel.querySelector('#settings-form');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.saveSettings();
            });
        }

        // Escape key to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.close();
            }
        });
    }

    async loadConfig() {
        try {
            // Try Electron API first
            if (window.electronAPI) {
                this.config = await window.electronAPI.getConfig();
            } else {
                // Fallback to HTTP API - get dynamic backend URL
                const backendUrl = window.electronAPI ? window.electronAPI.getBackendUrl() : 'http://localhost:5000';
                const response = await fetch(`${backendUrl}/get_config`);
                if (response.ok) {
                    this.config = await response.json();
                } else {
                    throw new Error(`HTTP ${response.status}`);
                }
            }
            this.populateForm();
        } catch (error) {
            console.error('Failed to load config:', error);
        }
    }

    populateForm() {
        const form = this.panel.querySelector('#settings-form');
        if (!form) return;

        // Populate form fields with current config
        for (const [key, value] of Object.entries(this.config)) {
            const field = form.querySelector(`[name="${key}"]`);
            if (field) {
                if (field.type === 'checkbox') {
                    field.checked = value;
                } else {
                    field.value = value;
                }
            }
        }
    }

    async saveSettings() {
        try {
            const form = this.panel.querySelector('#settings-form');
            const formData = new FormData(form);
            const settings = Object.fromEntries(formData);

            // Convert checkbox values
            const checkboxes = form.querySelectorAll('input[type="checkbox"]');
            checkboxes.forEach(checkbox => {
                settings[checkbox.name] = checkbox.checked;
            });

            // Update config
            let configSuccess = false;
            if (window.electronAPI) {
                const result = await window.electronAPI.updateConfig(settings);
                configSuccess = result.success;
            } else {
                const backendUrl = window.electronAPI ? window.electronAPI.getBackendUrl() : 'http://localhost:5000';
                const response = await fetch(`${backendUrl}/update_config`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(settings)
                });
                configSuccess = response.ok;
            }

            if (!configSuccess) {
                throw new Error('Failed to update config');
            }

            // Save API keys separately
            const apiKeys = {
                alpha_vantage_key: formData.get('alpha_vantage_key'),
                googlemaps_key: formData.get('googlemaps_key'),
                icloud_username: formData.get('icloud_username'),
                icloud_password: formData.get('icloud_password')
            };

            const backendUrl = window.electronAPI ? window.electronAPI.getBackendUrl() : 'http://localhost:5000';
            for (const [service, key] of Object.entries(apiKeys)) {
                if (key && key.trim()) {
                    try {
                        const response = await fetch(`${backendUrl}/set_key`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({
                                service: service.split('_')[0],
                                key: service.split('_')[1] || 'api_key',
                                value: key.trim()
                            })
                        });

                        if (!response.ok) {
                            console.warn(`Failed to save ${service}`);
                        }
                    } catch (error) {
                        console.error(`Error saving ${service}:`, error);
                    }
                }
            }

            // Update local config
            this.config = { ...this.config, ...settings };

            // Show success message
            this.showMessage('Settings saved successfully!', 'success');
            
            // Close panel after a short delay
            setTimeout(() => {
                this.close();
            }, 1500);

        } catch (error) {
            console.error('Failed to save settings:', error);
            this.showMessage('Failed to save settings. Please try again.', 'error');
        }
    }

    showMessage(message, type = 'info') {
        // Create message element
        const messageEl = document.createElement('div');
        messageEl.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 6px;
            color: white;
            font-weight: bold;
            z-index: 1002;
            animation: slideIn 0.3s ease;
        `;

        if (type === 'success') {
            messageEl.style.background = 'linear-gradient(45deg, #00ff88, #00cc6a)';
        } else if (type === 'error') {
            messageEl.style.background = 'linear-gradient(45deg, #ff4444, #cc3333)';
        } else {
            messageEl.style.background = 'linear-gradient(45deg, #00bfff, #0080ff)';
        }

        messageEl.textContent = message;
        document.body.appendChild(messageEl);

        // Remove after 3 seconds
        setTimeout(() => {
            if (messageEl.parentNode) {
                messageEl.parentNode.removeChild(messageEl);
            }
        }, 3000);
    }

    open() {
        this.isOpen = true;
        this.overlay.style.display = 'block';
        this.panel.style.right = '0';
        
        // Load latest config
        this.loadConfig();
    }

    close() {
        this.isOpen = false;
        this.overlay.style.display = 'none';
        this.panel.style.right = '-400px';
    }

    // Public method to open settings
    openSettings() {
        this.open();
    }
}

// Initialize settings panel when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.settingsPanel = new SettingsPanel();
});