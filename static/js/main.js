// Gree.do JavaScript - Dynamic animations and API interactions

class GreedoApp {
    constructor() {
        this.logoElement = null;
        this.timestampData = null;
        this.updateInterval = null;
        this.spaceGun = null;
        this.logoContainer = null;
        
        this.init();
    }
    
    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }
    
    setup() {
        console.log('🚀 Initializing Gree.do...');
        
        this.logoElement = document.getElementById('logo');
        
        // Start logo animations
        this.startLogoAnimations();
        
        // Load initial data
        this.loadTimestampData();
        
        // Set up auto-refresh
        this.startAutoRefresh();
        
        // Set up controls
        this.setupControls();
        
        // Set up dropdown navigation
        this.setupDropdown();
        
        // Add some sparkle effects
        this.addSparkleEffects();
        
        // Add ambient sparkles around logo
        this.startAmbientSparkles();
        
        // Start continuous floating sparkles
        this.startFloatingSparkles();
        
        // Setup space gun cursor
        this.setupSpaceGun();
        
        console.log('✨ Gree.do initialized successfully!');
    }
    
    startLogoAnimations() {
        if (!this.logoElement) return;
        
        // Always use combined animation
        this.logoElement.classList.add('logo-combined');
        console.log('🎭 Applied combined animation (all effects)');
    }
    
    
    async loadTimestampData() {
        try {
            this.showLoading();
            
            const response = await fetch('/api/v1/greedo');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            this.timestampData = await response.json();
            this.displayTimestampData();
            this.hideLoading();
            
            console.log('📊 Timestamp data loaded:', this.timestampData);
            
        } catch (error) {
            console.error('❌ Failed to load timestamp data:', error);
            this.showError('Failed to load timestamp data');
            this.hideLoading();
        }
    }
    
    displayTimestampData() {
        if (!this.timestampData) return;
        
        // Update fact
        this.updateElement('fact', this.timestampData.fact);
        
        // Update quote if available
        if (this.timestampData.quote) {
            this.updateElement('quote', `"${this.timestampData.quote}"`);
            this.showElement('quote-section');
        } else {
            this.hideElement('quote-section');
        }
        
        // Update time data
        if (this.timestampData.time) {
            const utcDate = new Date(this.timestampData.time.utc);
            const localDate = new Date(this.timestampData.time.local);
            
            this.updateElement('utc-time', this.formatDateTime(utcDate, 'UTC'));
            this.updateElement('local-time', this.formatDateTime(localDate, this.timestampData.time.tz));
            this.updateElement('unix-time', this.timestampData.unix.toString());
        }
        
        // Update Star Wars time
        if (this.timestampData.sw) {
            this.updateElement('swet-time', this.timestampData.sw.swet.toString());
            this.updateElement('cgt-time', this.timestampData.sw.cgt_str);
            this.updateElement('gsc-year', this.timestampData.sw.gsc_year.toString());
            this.showElement('star-wars-section');
        }
        
        // Update request ID
        if (this.timestampData.request_id) {
            this.updateElement('request-id', this.timestampData.request_id);
        }
        
        // Add fade-in animation to updated content
        this.animateContent();
    }
    
    formatDateTime(date, timezone) {
        const options = {
            weekday: 'short',
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            timeZoneName: 'short'
        };
        
        try {
            return new Intl.DateTimeFormat('en-US', options).format(date) + ` ${timezone}`;
        } catch (error) {
            return date.toISOString();
        }
    }
    
    updateElement(id, content) {
        const element = document.getElementById(id);
        if (element && content !== undefined) {
            element.textContent = content;
            element.classList.add('fade-in');
        }
    }
    
    showElement(id) {
        const element = document.getElementById(id);
        if (element) {
            element.style.display = 'block';
        }
    }
    
    hideElement(id) {
        const element = document.getElementById(id);
        if (element) {
            element.style.display = 'none';
        }
    }
    
    animateContent() {
        const elements = document.querySelectorAll('.timestamp-data, .sidebar');
        elements.forEach((el, index) => {
            setTimeout(() => {
                el.classList.remove('fade-in');
                el.offsetHeight; // Force reflow
                el.classList.add('fade-in');
            }, index * 100);
        });
    }
    
    startAutoRefresh() {
        // Refresh every 30 seconds
        this.updateInterval = setInterval(() => {
            this.loadTimestampData();
        }, 30000);
        
        console.log('⏰ Auto-refresh enabled (30s interval)');
    }
    
    setupControls() {
        // Add click handlers for nav links with sparkle effects
        document.querySelectorAll('.nav-link, .btn').forEach(link => {
            link.addEventListener('click', (e) => {
                this.createSparkles(e.target);
            });
        });
        
        // Get logo container for space gun area
        this.logoContainer = document.querySelector('.logo-container');
    }
    
    setupSpaceGun() {
        // Create space gun cursor element
        this.spaceGun = document.createElement('div');
        this.spaceGun.className = 'space-gun';
        document.body.appendChild(this.spaceGun);
        
        // Hide space gun initially
        this.spaceGun.style.display = 'none';
        
        if (this.logoContainer) {
            // Show space gun when hovering over logo area
            this.logoContainer.addEventListener('mouseenter', () => {
                this.logoContainer.classList.add('space-gun-cursor');
                this.spaceGun.style.display = 'block';
            });
            
            // Hide space gun when leaving logo area
            this.logoContainer.addEventListener('mouseleave', () => {
                this.logoContainer.classList.remove('space-gun-cursor');
                this.spaceGun.style.display = 'none';
            });
            
            // Update space gun position on mouse move
            this.logoContainer.addEventListener('mousemove', (e) => {
                this.spaceGun.style.left = e.clientX + 'px';
                this.spaceGun.style.top = e.clientY + 'px';
            });
            
            // Shooting effect on click
            this.logoContainer.addEventListener('click', (e) => {
                this.shootSpaceGun(e);
            });
        }
    }
    
    shootSpaceGun(e) {
        // Add shooting effect
        this.spaceGun.classList.add('shooting');
        
        // Create blast sparkles at click location
        this.createBlastEffect(e.clientX, e.clientY);
        
        // Remove shooting class after animation
        setTimeout(() => {
            this.spaceGun.classList.remove('shooting');
        }, 300);
    }
    
    createBlastEffect(x, y) {
        // Create multiple sparkles for blast effect
        for (let i = 0; i < 8; i++) {
            setTimeout(() => {
                this.createBlastSparkle(x, y, i);
            }, i * 20);
        }
    }
    
    createBlastSparkle(x, y, index) {
        const sparkle = document.createElement('div');
        const colors = ['#10b981', '#14b8a6', '#8b5a2b', '#34d399', '#ffffff'];
        const color = colors[index % colors.length];
        
        sparkle.style.cssText = `
            position: fixed;
            width: 8px;
            height: 8px;
            background: ${color};
            border-radius: 50%;
            pointer-events: none;
            z-index: 1000;
            left: ${x}px;
            top: ${y}px;
            box-shadow: 0 0 8px ${color};
        `;
        
        document.body.appendChild(sparkle);
        
        // Explosive animation
        const angle = (index * 45) * (Math.PI / 180);
        const distance = 40 + Math.random() * 80;
        const duration = 600 + Math.random() * 400;
        
        sparkle.animate([
            {
                transform: 'translate(0, 0) scale(1) rotate(0deg)',
                opacity: 1,
                filter: 'brightness(2)'
            },
            {
                transform: `translate(${Math.cos(angle) * distance}px, ${Math.sin(angle) * distance}px) scale(0) rotate(720deg)`,
                opacity: 0,
                filter: 'brightness(0)'
            }
        ], {
            duration: duration,
            easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)'
        }).addEventListener('finish', () => {
            sparkle.remove();
        });
    }
    
    startFloatingSparkles() {
        // Create floating sparkles continuously - MORE SPARKLES!
        setInterval(() => {
            this.createFloatingSparkle();
        }, 400); // Doubled frequency
        
        // Create star sparkles around logo
        setInterval(() => {
            this.createStarSparkles();
        }, 1000);
        
        // Create initial batch
        for (let i = 0; i < 8; i++) {
            setTimeout(() => {
                this.createFloatingSparkle();
            }, i * 100);
        }
    }
    
    createStarSparkles() {
        if (!this.logoElement) return;
        
        // Create sparkles in star pattern around logo
        const logoRect = this.logoElement.getBoundingClientRect();
        const centerX = logoRect.left + logoRect.width / 2;
        const centerY = logoRect.top + logoRect.height / 2;
        
        // Create 5-pointed star pattern
        for (let i = 0; i < 5; i++) {
            const angle = (i * 72) * (Math.PI / 180); // 72 degrees apart
            const radius = logoRect.width / 2 + 30 + Math.random() * 20;
            const x = centerX + Math.cos(angle) * radius;
            const y = centerY + Math.sin(angle) * radius;
            
            setTimeout(() => {
                this.createStarSparkle(x, y);
            }, i * 100);
        }
    }
    
    createStarSparkle(x, y) {
        const sparkle = document.createElement('div');
        sparkle.style.cssText = `
            position: fixed;
            width: 8px;
            height: 8px;
            background: #ffff00;
            border-radius: 50%;
            pointer-events: none;
            z-index: 100;
            left: ${x}px;
            top: ${y}px;
            opacity: 0;
            box-shadow: 0 0 10px #ffff00, 0 0 20px #ffff00;
        `;
        
        document.body.appendChild(sparkle);
        
        sparkle.animate([
            {
                opacity: 0,
                transform: 'scale(0) rotate(0deg)'
            },
            {
                opacity: 1,
                transform: 'scale(1.5) rotate(180deg)'
            },
            {
                opacity: 0,
                transform: 'scale(0) rotate(360deg)'
            }
        ], {
            duration: 2000,
            easing: 'ease-in-out'
        }).addEventListener('finish', () => {
            sparkle.remove();
        });
    }
    
    createFloatingSparkle() {
        const sparkle = document.createElement('div');
        sparkle.className = 'floating-sparkle';
        
        // Random horizontal position
        const startX = Math.random() * window.innerWidth;
        sparkle.style.left = startX + 'px';
        
        // Random size variation
        const size = 3 + Math.random() * 4;
        sparkle.style.width = size + 'px';
        sparkle.style.height = size + 'px';
        
        // Random delay for staggered effect
        sparkle.style.animationDelay = Math.random() * 2 + 's';
        
        document.body.appendChild(sparkle);
        
        // Remove after animation completes
        setTimeout(() => {
            if (sparkle.parentNode) {
                sparkle.remove();
            }
        }, 12000 + Math.random() * 2000);
    }
    
    setupDropdown() {
        const dropdownBtn = document.getElementById('nav-dropdown');
        const dropdown = dropdownBtn?.parentElement;
        const dropdownContent = document.getElementById('dropdown-content');
        
        if (!dropdownBtn || !dropdown) return;
        
        dropdownBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            dropdown.classList.toggle('active');
            this.createSparkles(dropdownBtn);
            
            // Add sparkle burst when opening
            if (dropdown.classList.contains('active')) {
                this.createSparkleburst(dropdownBtn);
            }
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!dropdown.contains(e.target)) {
                dropdown.classList.remove('active');
            }
        });
        
        // Close dropdown when pressing escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                dropdown.classList.remove('active');
            }
        });
        
        // Add sparkles to dropdown links
        dropdownContent?.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                this.createSparkles(link);
                dropdown.classList.remove('active');
            });
        });
    }
    
    showLoading() {
        const loadingElements = document.querySelectorAll('.loading');
        loadingElements.forEach(el => el.style.display = 'inline-block');
    }
    
    hideLoading() {
        const loadingElements = document.querySelectorAll('.loading');
        loadingElements.forEach(el => el.style.display = 'none');
    }
    
    showError(message) {
        // Create or update error display
        let errorEl = document.getElementById('error-message');
        if (!errorEl) {
            errorEl = document.createElement('div');
            errorEl.id = 'error-message';
            errorEl.className = 'status-indicator status-error';
            errorEl.style.position = 'fixed';
            errorEl.style.top = '20px';
            errorEl.style.right = '20px';
            errorEl.style.zIndex = '1000';
            document.body.appendChild(errorEl);
        }
        
        errorEl.textContent = message;
        errorEl.style.display = 'flex';
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            errorEl.style.display = 'none';
        }, 5000);
    }
    
    addSparkleEffects() {
        // Add hover effects to interactive elements
        document.querySelectorAll('.btn, .nav-link').forEach(el => {
            el.addEventListener('mouseenter', (e) => {
                this.addGlowEffect(e.target);
            });
            
            el.addEventListener('mouseleave', (e) => {
                this.removeGlowEffect(e.target);
            });
        });
    }
    
    addGlowEffect(element) {
        element.style.filter = 'drop-shadow(0 0 10px rgba(16, 185, 129, 0.5))';
        element.style.transition = 'all 0.3s ease';
    }
    
    removeGlowEffect(element) {
        element.style.filter = '';
    }
    
    createSparkles(element) {
        const rect = element.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;
        
        for (let i = 0; i < 6; i++) {
            setTimeout(() => {
                this.createSparkle(centerX, centerY);
            }, i * 50);
        }
    }
    
    createSparkle(x, y) {
        const sparkle = document.createElement('div');
        sparkle.style.cssText = `
            position: fixed;
            width: 4px;
            height: 4px;
            background: var(--primary-green);
            border-radius: 50%;
            pointer-events: none;
            z-index: 1000;
            left: ${x}px;
            top: ${y}px;
        `;
        
        document.body.appendChild(sparkle);
        
        // Animate sparkle
        const angle = Math.random() * Math.PI * 2;
        const distance = 30 + Math.random() * 40;
        const duration = 800 + Math.random() * 400;
        
        sparkle.animate([
            {
                transform: 'translate(0, 0) scale(1)',
                opacity: 1
            },
            {
                transform: `translate(${Math.cos(angle) * distance}px, ${Math.sin(angle) * distance}px) scale(0)`,
                opacity: 0
            }
        ], {
            duration: duration,
            easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)'
        }).addEventListener('finish', () => {
            sparkle.remove();
        });
    }
    
    createSparkleburst(element) {
        const rect = element.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;
        
        // Create a burst of 12 sparkles
        for (let i = 0; i < 12; i++) {
            setTimeout(() => {
                this.createEnhancedSparkle(centerX, centerY, i);
            }, i * 30);
        }
    }
    
    createEnhancedSparkle(x, y, index) {
        const sparkle = document.createElement('div');
        const colors = ['#10b981', '#14b8a6', '#8b5a2b', '#34d399'];
        const color = colors[index % colors.length];
        
        sparkle.style.cssText = `
            position: fixed;
            width: 6px;
            height: 6px;
            background: ${color};
            border-radius: 50%;
            pointer-events: none;
            z-index: 1000;
            left: ${x}px;
            top: ${y}px;
            box-shadow: 0 0 6px ${color};
        `;
        
        document.body.appendChild(sparkle);
        
        // More dramatic animation
        const angle = (index * 30) * (Math.PI / 180); // Spread evenly in circle
        const distance = 60 + Math.random() * 60;
        const duration = 1200 + Math.random() * 800;
        
        sparkle.animate([
            {
                transform: 'translate(0, 0) scale(1) rotate(0deg)',
                opacity: 1,
                filter: 'brightness(1.5)'
            },
            {
                transform: `translate(${Math.cos(angle) * distance}px, ${Math.sin(angle) * distance}px) scale(0) rotate(360deg)`,
                opacity: 0,
                filter: 'brightness(3)'
            }
        ], {
            duration: duration,
            easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)'
        }).addEventListener('finish', () => {
            sparkle.remove();
        });
    }
    
    startAmbientSparkles() {
        // Create subtle sparkles around the logo periodically
        setInterval(() => {
            if (this.logoElement && Math.random() < 0.3) {
                this.createAmbientSparkle();
            }
        }, 2000);
    }
    
    createAmbientSparkle() {
        const logoRect = this.logoElement.getBoundingClientRect();
        const centerX = logoRect.left + logoRect.width / 2;
        const centerY = logoRect.top + logoRect.height / 2;
        
        // Random position around logo
        const angle = Math.random() * Math.PI * 2;
        const radius = logoRect.width / 2 + 20 + Math.random() * 40;
        const x = centerX + Math.cos(angle) * radius;
        const y = centerY + Math.sin(angle) * radius;
        
        const sparkle = document.createElement('div');
        sparkle.style.cssText = `
            position: fixed;
            width: 3px;
            height: 3px;
            background: var(--primary-green);
            border-radius: 50%;
            pointer-events: none;
            z-index: 100;
            left: ${x}px;
            top: ${y}px;
            opacity: 0;
        `;
        
        document.body.appendChild(sparkle);
        
        sparkle.animate([
            {
                opacity: 0,
                transform: 'scale(0)'
            },
            {
                opacity: 0.6,
                transform: 'scale(1)'
            },
            {
                opacity: 0,
                transform: 'scale(0)'
            }
        ], {
            duration: 3000,
            easing: 'ease-in-out'
        }).addEventListener('finish', () => {
            sparkle.remove();
        });
    }
    
    // Health check functionality
    async checkHealth() {
        try {
            const response = await fetch('/api/health');
            const health = await response.json();
            
            console.log('🏥 Health check:', health);
            return health;
        } catch (error) {
            console.error('❌ Health check failed:', error);
            return { status: 'unhealthy', error: error.message };
        }
    }
    
    // Utility method to copy API endpoints to clipboard
    async copyToClipboard(text, button) {
        try {
            await navigator.clipboard.writeText(text);
            
            const originalText = button.textContent;
            button.textContent = '✅ Copied!';
            button.style.background = 'var(--success)';
            
            setTimeout(() => {
                button.textContent = originalText;
                button.style.background = '';
            }, 2000);
            
            this.createSparkles(button);
        } catch (error) {
            console.error('Failed to copy to clipboard:', error);
        }
    }
    
    // Easter eggs and fun interactions
    initEasterEggs() {
        // Konami code easter egg
        let konamiCode = [];
        const konami = [38, 38, 40, 40, 37, 39, 37, 39, 66, 65]; // ↑↑↓↓←→←→BA
        
        document.addEventListener('keydown', (e) => {
            konamiCode.push(e.keyCode);
            if (konamiCode.length > 10) konamiCode.shift();
            
            if (konamiCode.join(',') === konami.join(',')) {
                this.activateEasterEgg();
                konamiCode = [];
            }
        });
        
        // Double-click logo for surprise
        if (this.logoElement) {
            this.logoElement.addEventListener('dblclick', () => {
                this.logoSurprise();
            });
        }
    }
    
    activateEasterEgg() {
        // Temporary disco mode
        document.body.style.animation = 'discoFlash 0.5s ease-in-out 6';
        console.log('🕺 DISCO MODE ACTIVATED!');
        
        setTimeout(() => {
            document.body.style.animation = '';
        }, 3000);
    }
    
    logoSurprise() {
        if (!this.logoElement) return;
        
        // Rapid cycle through all animations
        this.animations.forEach((anim, index) => {
            setTimeout(() => {
                this.logoElement.className = 'logo-image ' + anim;
            }, index * 200);
        });
        
        // Return to normal after surprise
        setTimeout(() => {
            this.applyLogoAnimation();
        }, this.animations.length * 200 + 1000);
    }
}

// Initialize the app when the page loads
const greedoApp = new GreedoApp();

// Add CSS for disco mode easter egg
const style = document.createElement('style');
style.textContent = `
    @keyframes discoFlash {
        0%, 100% { background: var(--background); }
        25% { background: linear-gradient(45deg, var(--primary-green), var(--secondary-teal)); }
        50% { background: linear-gradient(135deg, var(--accent-brown), var(--primary-green)); }
        75% { background: linear-gradient(225deg, var(--secondary-teal), var(--accent-brown)); }
    }
`;
document.head.appendChild(style);

// Global utilities
window.GreedoApp = GreedoApp;
window.greedoApp = greedoApp;

// Console message for developers
console.log(`
🌟 Welcome to Gree.do! 🌟

This is a Star Wars Holonet Timestamp System.
Built with love, JavaScript, and a touch of galactic magic.

Try the Konami code: ↑↑↓↓←→←→BA
Or double-click the logo for a surprise!

Remember: Han shot first! 🚀

API Endpoints:
- JSON: /api/v1/greedo
- Text: /curl/v1/greedo
- Health: /api/health
`);