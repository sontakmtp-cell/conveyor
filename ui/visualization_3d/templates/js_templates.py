"""
JavaScript Templates for Enhanced 3D Visualization
"""

# Template JavaScript cơ bản
BASIC_JS_TEMPLATE = """
// Basic 3D Conveyor Visualization
class BasicConveyorVisualization {
    constructor(data) {
        this.data = data;
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.clock = new THREE.Clock();
        
        this.init();
    }
    
    init() {
        this.setupScene();
        this.buildConveyor();
        this.animate();
    }
    
    setupScene() {
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
        this.renderer = new THREE.WebGLRenderer();
        
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(this.renderer.domElement);
        
        this.camera.position.set(5, 5, 5);
        this.camera.lookAt(0, 0, 0);
        
        const ambientLight = new THREE.AmbientLight(0x404040);
        this.scene.add(ambientLight);
        
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(10, 10, 5);
        this.scene.add(directionalLight);
    }
    
    buildConveyor() {
        const beltGeometry = new THREE.BoxGeometry(this.data.belt_system.geometry.width, 
                                                 this.data.belt_system.geometry.thickness, 
                                                 this.data.belt_system.geometry.length);
        const beltMaterial = new THREE.MeshStandardMaterial({color: 0x2c3e50});
        const belt = new THREE.Mesh(beltGeometry, beltMaterial);
        belt.position.y = this.data.belt_system.geometry.thickness / 2;
        this.scene.add(belt);
    }
    
    animate() {
        requestAnimationFrame(() => this.animate());
        this.renderer.render(this.scene, this.camera);
    }
}

const visualization = new BasicConveyorVisualization({data});
"""

# Template JavaScript nâng cao
ENHANCED_JS_TEMPLATE = """
// Enhanced 3D Conveyor Visualization
class EnhancedConveyorVisualization {
    constructor(data) {
        this.data = data;
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.clock = new THREE.Clock();
        this.components = {};
        this.animations = {};
        this.isPlaying = true;
        this.animationSpeed = 1.0;
        
        this.init();
    }
    
    async init() {
        await this.setupScene();
        await this.buildConveyor();
        this.setupAnimations();
        this.setupControls();
        this.animate();
    }
    
    setupScene() {
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(60, window.innerWidth/window.innerHeight, 0.1, 5000);
        this.renderer = new THREE.WebGLRenderer({antialias: true});
        
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(this.renderer.domElement);
        
        this.camera.position.set(10, 10, 10);
        this.camera.lookAt(0, 0, 0);
        
        const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
        this.scene.add(ambientLight);
        
        const directionalLight = new THREE.DirectionalLight(0xffffff, 1.0);
        directionalLight.position.set(10, 15, 10);
        this.scene.add(directionalLight);
    }
    
    async buildConveyor() {
        await this.buildBeltSystem();
        await this.buildDriveSystem();
        await this.buildSupportStructure();
    }
    
    async buildBeltSystem() {
        const beltData = this.data.belt_system;
        const geo = beltData.geometry;
        
        const geometry = new THREE.BoxGeometry(geo.width, geo.thickness, geo.length);
        const material = new THREE.MeshStandardMaterial({color: 0x2c3e50});
        
        this.components.belt = new THREE.Mesh(geometry, material);
        this.components.belt.position.set(geo.length/2, geo.thickness/2, 0);
        this.scene.add(this.components.belt);
    }
    
    async buildDriveSystem() {
        // Tạo hệ truyền động
        const driveData = this.data.drive_system;
        
        if (driveData.motor) {
            this.components.motor = this.createMotor(driveData.motor);
            this.scene.add(this.components.motor);
        }
    }
    
    async buildSupportStructure() {
        // Tạo khung đỡ
        const supportData = this.data.support_structure;
        
        if (supportData.main_frame) {
            this.components.mainFrame = this.createMainFrame(supportData.main_frame);
            this.scene.add(this.components.mainFrame);
        }
    }
    
    createMotor(motorData) {
        const geometry = new THREE.CylinderGeometry(
            motorData.parameters.radiusTop,
            motorData.parameters.radiusBottom,
            motorData.parameters.height,
            motorData.parameters.radialSegments
        );
        
        const material = new THREE.MeshStandardMaterial({
            color: motorData.material.parameters.color,
            roughness: motorData.material.parameters.roughness,
            metalness: motorData.material.parameters.metalness
        });
        
        const motor = new THREE.Mesh(geometry, material);
        motor.position.set(...motorData.position);
        
        return motor;
    }
    
    createMainFrame(frameData) {
        const geometry = new THREE.BoxGeometry(
            frameData.parameters.width,
            frameData.parameters.height,
            frameData.parameters.depth
        );
        
        const material = new THREE.MeshStandardMaterial({
            color: frameData.material.parameters.color,
            roughness: frameData.material.parameters.roughness,
            metalness: frameData.material.parameters.metalness
        });
        
        const frame = new THREE.Mesh(geometry, material);
        frame.position.set(...frameData.position);
        
        return frame;
    }
    
    setupAnimations() {
        this.animations.belt = this.createBeltAnimation();
        this.animations.drive = this.createDriveAnimation();
    }
    
    createBeltAnimation() {
        const belt = this.components.belt;
        const speed = this.data.belt_speed_mps || 2.0;
        
        return {
            update: (deltaTime) => {
                if (belt.material.map) {
                    belt.material.map.offset.x += speed * deltaTime * 0.1;
                }
            }
        };
    }
    
    createDriveAnimation() {
        const motor = this.components.motor;
        const motorRpm = this.data.drive_system?.motor?.rpm || 1450;
        
        return {
            update: (deltaTime) => {
                if (motor) {
                    motor.rotation.y += (motorRpm / 60) * Math.PI * 2 * deltaTime;
                }
            }
        };
    }
    
    setupControls() {
        this.setupAnimationControls();
        this.setupCameraControls();
    }
    
    setupAnimationControls() {
        const playPauseBtn = document.getElementById('play-pause');
        if (playPauseBtn) {
            playPauseBtn.addEventListener('click', () => {
                this.isPlaying = !this.isPlaying;
                playPauseBtn.textContent = this.isPlaying ? '⏸️' : '▶️';
            });
        }
        
        const speedSlider = document.getElementById('speed-slider');
        if (speedSlider) {
            speedSlider.addEventListener('input', (e) => {
                this.animationSpeed = parseFloat(e.target.value);
            });
        }
    }
    
    setupCameraControls() {
        const cameraPreset = document.getElementById('camera-preset');
        if (cameraPreset) {
            cameraPreset.addEventListener('change', (e) => {
                this.setCameraPreset(e.target.value);
            });
        }
    }
    
    setCameraPreset(preset) {
        const beltLength = this.data.belt_system.geometry.length;
        
        switch (preset) {
            case 'overview':
                this.camera.position.set(beltLength * 1.5, beltLength * 1.2, beltLength * 1.5);
                this.camera.lookAt(beltLength / 2, 0, 0);
                break;
            case 'drive':
                this.camera.position.set(0, 2, 3);
                this.camera.lookAt(0, 0, 0);
                break;
            case 'belt':
                this.camera.position.set(beltLength / 2, 1, 0);
                this.camera.lookAt(beltLength / 2, 0, 0);
                break;
        }
    }
    
    animate() {
        requestAnimationFrame(() => this.animate());
        
        if (this.isPlaying) {
            const deltaTime = this.clock.getDelta() * this.animationSpeed;
            
            Object.values(this.animations).forEach(anim => {
                if (anim.update) anim.update(deltaTime);
            });
        }
        
        this.renderer.render(this.scene, this.camera);
    }
}

const visualization = new EnhancedConveyorVisualization({data});
"""

# Template JavaScript cho chế độ đơn giản
SIMPLE_JS_TEMPLATE = """
// Simple 3D Conveyor Visualization
class SimpleConveyorVisualization {
    constructor(data) {
        this.data = data;
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        
        this.init();
    }
    
    init() {
        this.setupScene();
        this.buildConveyor();
        this.animate();
    }
    
    setupScene() {
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
        this.renderer = new THREE.WebGLRenderer();
        
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(this.renderer.domElement);
        
        this.camera.position.set(5, 5, 5);
        this.camera.lookAt(0, 0, 0);
        
        const ambientLight = new THREE.AmbientLight(0x404040);
        this.scene.add(ambientLight);
    }
    
    buildConveyor() {
        const beltGeometry = new THREE.BoxGeometry(this.data.belt_system.geometry.width, 
                                                 this.data.belt_system.geometry.thickness, 
                                                 this.data.belt_system.geometry.length);
        const beltMaterial = new THREE.MeshStandardMaterial({color: 0x2c3e50});
        const belt = new THREE.Mesh(beltGeometry, beltMaterial);
        belt.position.y = this.data.belt_system.geometry.thickness / 2;
        this.scene.add(belt);
    }
    
    animate() {
        requestAnimationFrame(() => this.animate());
        this.renderer.render(this.scene, this.camera);
    }
}

const visualization = new SimpleConveyorVisualization({data});
"""
