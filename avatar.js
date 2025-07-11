class AvatarManager {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.avatarMesh = null;
        this.landmarks = null;
        this.is3D = false;
        this.isAnimating = false;
        this.currentViseme = null;
        this.animationFrame = null;
        
        this.init();
    }

    init() {
        const canvas = document.getElementById('avatar-canvas');
        if (!canvas) {
            console.error('Avatar canvas not found');
            return;
        }

        this.setupRenderer(canvas);
        this.setupScene();
        this.setupCamera();
        this.setupLighting();
        
        // Start render loop
        this.animate();
    }

    setupRenderer(canvas) {
        if (typeof THREE === 'undefined') {
            console.warn('THREE.js not loaded, falling back to 2D canvas');
            this.setup2DCanvas(canvas);
            return;
        }

        this.renderer = new THREE.WebGLRenderer({
            canvas: canvas,
            alpha: true,
            antialias: true
        });

        this.renderer.setSize(canvas.width, canvas.height);
        this.renderer.setClearColor(0x000000, 0);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    }

    setup2DCanvas(canvas) {
        this.ctx = canvas.getContext('2d');
        this.canvas = canvas;
        this.is3D = false;
        this.drawDefault2DAvatar();
    }

    setupScene() {
        if (typeof THREE === 'undefined') return;

        this.scene = new THREE.Scene();
        this.scene.background = null;
    }

    drawDefault2DAvatar() {
        if (!this.ctx) return;

        const centerX = this.canvas.width / 2;
        const centerY = this.canvas.height / 2;
        const radius = 150;

        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw face circle
        this.ctx.beginPath();
        this.ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
        this.ctx.fillStyle = '#1e3a8a';
        this.ctx.fill();

        // Add glow effect
        this.ctx.shadowColor = '#00bfff';
        this.ctx.shadowBlur = 20;
        this.ctx.strokeStyle = '#00bfff';
        this.ctx.lineWidth = 2;
        this.ctx.stroke();
        this.ctx.shadowBlur = 0;

        // Draw eyes
        this.ctx.fillStyle = '#00bfff';
        this.ctx.beginPath();
        this.ctx.arc(centerX - 40, centerY - 30, 8, 0, 2 * Math.PI);
        this.ctx.fill();

        this.ctx.beginPath();
        this.ctx.arc(centerX + 40, centerY - 30, 8, 0, 2 * Math.PI);
        this.ctx.fill();

        // Draw mouth
        this.draw2DMouth(centerX, centerY + 30);
    }

    draw2DMouth(x, y) {
        if (!this.ctx) return;

        this.ctx.strokeStyle = '#00bfff';
        this.ctx.lineWidth = 3;

        const mouthOpen = this.getMouthOpenness(this.currentViseme || 'A');
        const width = 15 + (mouthOpen * 10);
        const height = 5 + (mouthOpen * 8);

        this.ctx.beginPath();
        this.ctx.ellipse(x, y, width, height, 0, 0, 2 * Math.PI);
        this.ctx.stroke();
    }

    setupCamera() {
        if (typeof THREE === 'undefined' || !this.renderer) return;

        const canvas = this.renderer.domElement;
        const aspect = canvas.width / canvas.height;

        this.camera = new THREE.PerspectiveCamera(75, aspect, 0.1, 1000);
        this.camera.position.set(0, 0, 5);
        this.camera.lookAt(0, 0, 0);
    }

    setupLighting() {
        if (typeof THREE === 'undefined' || !this.scene) return;

        // Ambient light
        const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
        this.scene.add(ambientLight);

        // Directional light for shadows
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(5, 5, 5);
        directionalLight.castShadow = true;
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        this.scene.add(directionalLight);

        // Point light for neon glow effect
        const pointLight = new THREE.PointLight(0x00bfff, 1, 10);
        pointLight.position.set(0, 2, 2);
        this.scene.add(pointLight);
    }

    loadAvatar(imagePath, is3D = false) {
        this.is3D = is3D;
        
        if (is3D) {
            this.load3DAvatar(imagePath);
        } else {
            this.load2DAvatar(imagePath);
        }
    }

    load2DAvatar(imagePath) {
        const textureLoader = new THREE.TextureLoader();
        
        textureLoader.load(imagePath, (texture) => {
            // Create plane geometry for 2D avatar
            const geometry = new THREE.PlaneGeometry(3, 3);
            const material = new THREE.MeshBasicMaterial({ 
                map: texture,
                transparent: true,
                side: THREE.DoubleSide
            });
            
            this.avatarMesh = new THREE.Mesh(geometry, material);
            this.avatarMesh.position.set(0, 0, 0);
            this.scene.add(this.avatarMesh);
            
            console.log('2D avatar loaded');
        }, undefined, (error) => {
            console.error('Error loading 2D avatar:', error);
        });
    }

    load3DAvatar(imagePath) {
        // For 3D, we'll create a simple head geometry
        // In a real implementation, you'd load a 3D model
        const geometry = new THREE.SphereGeometry(1.5, 32, 32);
        const material = new THREE.MeshPhongMaterial({ 
            color: 0x00bfff,
            transparent: true,
            opacity: 0.8
        });
        
        this.avatarMesh = new THREE.Mesh(geometry, material);
        this.avatarMesh.position.set(0, 0, 0);
        this.scene.add(this.avatarMesh);
        
        console.log('3D avatar loaded');
    }

    setLandmarks(landmarks) {
        this.landmarks = landmarks;
        console.log('Landmarks set:', landmarks.length);
    }

    startAnimation(viseme) {
        this.isAnimating = true;
        this.currentViseme = viseme;
        
        if (this.avatarMesh && this.landmarks) {
            this.applyViseme(viseme);
        }
    }

    stopAnimation() {
        this.isAnimating = false;
        this.currentViseme = null;
        
        if (this.avatarMesh) {
            // Reset to neutral position
            this.resetToNeutral();
        }
    }

    applyViseme(viseme) {
        if (!this.avatarMesh || !this.landmarks) return;
        
        // Map viseme to mouth shape
        const mouthOpen = this.getMouthOpenness(viseme);
        
        if (this.is3D) {
            // For 3D, scale the mesh
            this.avatarMesh.scale.y = 1 + (mouthOpen * 0.2);
        } else {
            // For 2D, apply texture warping
            this.warpTexture(viseme, mouthOpen);
        }
    }

    getMouthOpenness(viseme) {
        // Map viseme to mouth openness (0-1)
        const visemeMap = {
            'A': 0.8, 'E': 0.6, 'I': 0.4, 'O': 0.7, 'U': 0.5,
            'F': 0.1, 'L': 0.3, 'M': 0.1, 'P': 0.1, 'B': 0.1,
            'V': 0.2, 'W': 0.6, 'Q': 0.4, 'R': 0.3, 'S': 0.2,
            'T': 0.1, 'D': 0.1, 'K': 0.1, 'G': 0.1, 'N': 0.1
        };
        
        return visemeMap[viseme] || 0.3;
    }

    warpTexture(viseme, mouthOpen) {
        // Simple texture warping for 2D avatar
        if (this.avatarMesh.material.map) {
            const texture = this.avatarMesh.material.map;
            
            // Apply simple scaling to simulate mouth movement
            const scale = 1 + (mouthOpen * 0.1);
            this.avatarMesh.scale.set(scale, scale, 1);
        }
    }

    resetToNeutral() {
        if (this.avatarMesh) {
            this.avatarMesh.scale.set(1, 1, 1);
        }
    }

    animate() {
        this.animationFrame = requestAnimationFrame(() => this.animate());

        if (this.ctx) {
            // 2D animation
            this.drawDefault2DAvatar();
        } else if (this.renderer && this.scene && this.camera) {
            // 3D animation
            // Add subtle breathing animation
            if (this.avatarMesh && !this.isAnimating) {
                const time = Date.now() * 0.001;
                const breathing = Math.sin(time * 2) * 0.02;
                this.avatarMesh.scale.setScalar(1 + breathing);
            }

            // Render the scene
            this.renderer.render(this.scene, this.camera);
        }
    }

    toggle3D(enabled) {
        this.is3D = enabled;
        // Reload avatar with new mode
        if (this.avatarMesh) {
            this.scene.remove(this.avatarMesh);
            this.avatarMesh = null;
        }
        
        // Reload with current image
        const currentImage = this.getCurrentImagePath();
        if (currentImage) {
            this.loadAvatar(currentImage, enabled);
        }
    }

    getCurrentImagePath() {
        // Get current avatar image path
        return 'assets/avatar.jpg'; // Default fallback
    }

    dispose() {
        if (this.animationFrame) {
            cancelAnimationFrame(this.animationFrame);
        }
        
        if (this.renderer) {
            this.renderer.dispose();
        }
        
        if (this.avatarMesh) {
            this.avatarMesh.geometry.dispose();
            this.avatarMesh.material.dispose();
        }
    }
}

// Initialize avatar manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.avatarManager = new AvatarManager();
});