<template>
  <div class="homepage" :class="{ 'dark-mode': isDarkMode }">
    <!-- Navigation Header -->
    <nav class="navbar">
      <div class="nav-container">
        <div class="nav-logo">
          <h2>🅿️ CyberPark</h2>
        </div>
        <div class="nav-links">
          <button @click="scrollToSection('features')" class="nav-link">Features</button>
          <button @click="scrollToSection('how-it-works')" class="nav-link">How It Works</button>
          <button @click="scrollToSection('testimonials')" class="nav-link">Reviews</button>
          <button @click="scrollToSection('faq')" class="nav-link">FAQ</button>
          <button @click="scrollToSection('contact')" class="nav-link">Contact</button>
          <button @click="toggleTheme" class="theme-toggle" :title="isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'">
            {{ isDarkMode ? '☀️' : '🌙' }}
          </button>
          <button @click="goToLogin" class="btn-login">Login</button>
          <button @click="goToRegister" class="btn-register">Register</button>
        </div>
      </div>
    </nav>

    <!-- Hero Section with Three.js Background -->
    <section class="hero" id="hero">
      <div class="three-container" ref="threeContainer"></div>
      <div class="hero-content">
        <h1 class="hero-title">Smart Parking Made Simple</h1>
        <p class="hero-subtitle">Find, book, and manage parking spots with ease using our intelligent parking management system</p>
        <div class="hero-buttons">
          <button @click="goToRegister" class="btn-primary">Get Started</button>
          <button @click="scrollToSection('how-it-works')" class="btn-secondary">Learn More</button>
        </div>
      </div>
      <div class="scroll-indicator" @click="scrollToSection('features')">
        <div class="scroll-arrow">↓</div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features" id="features">
      <div class="container">
        <h2 class="section-title">Why Choose CyberPark?</h2>
        <div class="features-grid">
          <div class="feature-card" v-for="feature in features" :key="feature.id">
            <div class="feature-icon">{{ feature.icon }}</div>
            <h3>{{ feature.title }}</h3>
            <p>{{ feature.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- How It Works Section -->
    <section class="how-it-works" id="how-it-works">
      <div class="container">
        <h2 class="section-title">How It Works</h2>
        <div class="steps-container">
          <div class="step" v-for="(step, index) in steps" :key="step.id">
            <div class="step-number">{{ index + 1 }}</div>
            <div class="step-content">
              <h3>{{ step.title }}</h3>
              <p>{{ step.description }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Statistics Section -->
    <section class="statistics" id="statistics">
      <div class="container">
        <h2 class="section-title">Trusted by Thousands</h2>
        <div class="stats-grid">
          <div class="stat-card" v-for="stat in statistics" :key="stat.id">
            <div class="stat-number">{{ stat.number }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- FAQ Section -->
    <section class="faq" id="faq">
      <div class="container">
        <h2 class="section-title">Frequently Asked Questions</h2>
        <div class="faq-container">
          <div class="faq-item" v-for="faq in faqs" :key="faq.id">
            <button class="faq-question" @click="toggleFaq(faq.id)"
                    :class="{ active: activeFaq === faq.id }">
              <span>{{ faq.question }}</span>
              <span class="faq-icon">{{ activeFaq === faq.id ? '−' : '+' }}</span>
            </button>
            <div class="faq-answer" :class="{ active: activeFaq === faq.id }">
              <p>{{ faq.answer }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Contact Section -->
    <section class="contact" id="contact">
      <div class="container">
        <h2 class="section-title">Get In Touch</h2>
        <div class="contact-content">
          <div class="contact-info">
            <h3>Ready to revolutionize your parking experience?</h3>
            <p>Join thousands of users who have already made parking hassle-free with CyberPark.</p>
            <div class="contact-buttons">
              <button @click="goToRegister" class="btn-primary">Start Now</button>
              <button @click="goToLogin" class="btn-outline">Already a member?</button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="footer">
      <div class="container">
        <div class="footer-content">
          <div class="footer-logo">
            <h3>🅿️ CyberPark</h3>
            <p>Smart parking solutions for modern cities</p>
            <div class="social-links">
              <a href="#" class="social-link" title="Facebook">📘</a>
              <a href="#" class="social-link" title="Twitter">🐦</a>
              <a href="#" class="social-link" title="Instagram">📷</a>
              <a href="#" class="social-link" title="LinkedIn">💼</a>
            </div>
          </div>
          <div class="footer-links">
            <div class="footer-section">
              <h4>Product</h4>
              <a href="#features">Features</a>
              <a href="#how-it-works">How It Works</a>
              <a href="#statistics">Statistics</a>
            </div>
            <div class="footer-section">
              <h4>Support</h4>
              <a href="#contact">Contact</a>
              <a href="#faq">FAQ</a>
              <a href="#testimonials">Reviews</a>
            </div>
          </div>
        </div>
        <div class="footer-bottom">
          <p>&copy; 2024 CyberPark. All rights reserved.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
import * as THREE from 'three'

export default {
  name: 'Homepage',
  created() {
    // Initialize Three.js objects as non-reactive to prevent Vue proxy issues
    this.scene = null
    this.camera = null
    this.renderer = null
    this.cars = []
    this.trafficLights = []
    this.particleSystem = null
    this.morphingShapes = []
    this.glowOrbs = []
    this.shootingStars = []
    this.waveMesh = null
    this.energyRings = []
    this.clock = null
  },
  data() {
    return {
      isDarkMode: false,
      mouse: { x: 0, y: 0 },
      scrollY: 0,
      features: [
        {
          id: 1,
          icon: '🔍',
          title: 'Find Spots Instantly',
          description: 'Locate available parking spots in real-time with our smart search system'
        },
        {
          id: 2,
          icon: '📱',
          title: 'Book on the Go',
          description: 'Reserve your parking spot from anywhere using our mobile-friendly interface'
        },
        {
          id: 3,
          icon: '💳',
          title: 'Secure Payments',
          description: 'Pay safely with our integrated payment system and loyalty rewards'
        },
        {
          id: 4,
          icon: '⭐',
          title: 'Loyalty Points',
          description: 'Earn points with every booking and get discounts on future reservations'
        },
        {
          id: 5,
          icon: '📊',
          title: 'Smart Analytics',
          description: 'Track your parking history and optimize your parking habits'
        },
        {
          id: 6,
          icon: '🔧',
          title: 'Admin Dashboard',
          description: 'Comprehensive management tools for parking lot operators'
        }
      ],
      steps: [
        {
          id: 1,
          title: 'Create Account',
          description: 'Sign up for free and set up your profile in minutes'
        },
        {
          id: 2,
          title: 'Find Parking',
          description: 'Search for available spots near your destination'
        },
        {
          id: 3,
          title: 'Book & Pay',
          description: 'Reserve your spot and pay securely through the app'
        },
        {
          id: 4,
          title: 'Park & Go',
          description: 'Arrive at your reserved spot and start your parking session'
        }
      ],
      statistics: [
        {
          id: 1,
          number: '1,000+',
          label: 'Happy Users'
        },
        {
          id: 2,
          number: '50+',
          label: 'Parking Locations'
        },
        {
          id: 3,
          number: '99.9%',
          label: 'Uptime'
        },
        {
          id: 4,
          number: '24/7',
          label: 'Support'
        }
      ],
      testimonials: [
        {
          id: 1,
          content: 'CyberPark has completely transformed how I handle parking in the city. No more circling around looking for spots!',
          name: 'Sarah Johnson',
          role: 'Business Professional',
          avatar: '👩‍💼'
        },
        {
          id: 2,
          content: 'The loyalty points system is amazing. I\'ve saved so much money on parking fees. Highly recommended!',
          name: 'Mike Chen',
          role: 'Daily Commuter',
          avatar: '👨‍💻'
        },
        {
          id: 3,
          content: 'As a parking lot owner, the admin dashboard gives me complete control and insights into my business.',
          name: 'Emma Rodriguez',
          role: 'Parking Lot Owner',
          avatar: '👩‍💼'
        }
      ],
      currentTestimonial: 1,
      faqs: [
        {
          id: 1,
          question: 'How do I book a parking spot?',
          answer: 'Simply create an account, search for available spots near your destination, select your preferred spot, and complete the booking with secure payment.'
        },
        {
          id: 2,
          question: 'Can I cancel my booking?',
          answer: 'Yes, you can cancel your booking up to 30 minutes before your reserved time. Cancellation fees may apply depending on the timing.'
        },
        {
          id: 3,
          question: 'How do loyalty points work?',
          answer: 'You earn 2 points for every hour of parking. Points can be redeemed for discounts on future bookings at a rate of $0.10 per point.'
        },
        {
          id: 4,
          question: 'Is my payment information secure?',
          answer: 'Absolutely! We use industry-standard encryption and secure payment gateways to protect all your financial information.'
        },
        {
          id: 5,
          question: 'What if I can\'t find my reserved spot?',
          answer: 'Contact our 24/7 support team immediately. We\'ll help you locate your spot or find an alternative solution.'
        }
      ],
      activeFaq: null
    }
  },
  mounted() {
    this.initTheme()
    this.initThreeJS()
    this.startTestimonialRotation()
    // Use nextTick to ensure DOM is fully rendered before setting up animations
    this.$nextTick(() => {
      setTimeout(() => {
        this.addScrollAnimations()
      }, 100)
    })
  },
  beforeUnmount() {
    if (this.renderer) {
      this.renderer.dispose()
    }

    // Clean up event listeners
    window.removeEventListener('resize', this.onWindowResize)
    window.removeEventListener('mousemove', this.onMouseMove)
    window.removeEventListener('scroll', this.onScroll)
  },
  methods: {
    initThreeJS() {
      try {
        // Initialize clock for animations
        this.clock = new THREE.Clock()
        
        // Scene setup
        this.scene = new THREE.Scene()
        this.scene.background = new THREE.Color(this.isDarkMode ? 0x050510 : 0x0a0a1a)
        
        // Add fog for depth
        this.scene.fog = new THREE.Fog(this.isDarkMode ? 0x050510 : 0x0a0a1a, 10, 50)

        // Camera setup
        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000)
        this.camera.position.z = 15

        // Renderer setup with enhanced settings
        this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
        this.renderer.setSize(window.innerWidth, window.innerHeight)
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))

        if (this.$refs.threeContainer) {
          this.$refs.threeContainer.appendChild(this.renderer.domElement)
        } else {
          console.error('threeContainer ref not found!')
          return
        }

        // Create all animations
        this.createMorphingShapes()
        this.createGlowOrbs()
        this.createShootingStars()
        this.createWaveEffect()
        this.createEnergyRings()
        this.createCars()

        // Enhanced lighting
        const ambientLight = new THREE.AmbientLight(0x4040ff, 0.3)
        this.scene.add(ambientLight)

        const pointLight1 = new THREE.PointLight(0x4ecdc4, 2, 50)
        pointLight1.position.set(10, 10, 10)
        this.scene.add(pointLight1)

        const pointLight2 = new THREE.PointLight(0xff6b6b, 2, 50)
        pointLight2.position.set(-10, -10, 10)
        this.scene.add(pointLight2)

        const pointLight3 = new THREE.PointLight(0x45b7d1, 1.5, 40)
        pointLight3.position.set(0, 15, 5)
        this.scene.add(pointLight3)

        // Start animation
        this.animate()

        // Handle window resize
        window.addEventListener('resize', this.onWindowResize)

        // Add mouse interaction
        window.addEventListener('mousemove', this.onMouseMove)

        // Add scroll interaction
        window.addEventListener('scroll', this.onScroll)
      } catch (error) {
        console.error('Error initializing Three.js:', error)
      }
    },
    createCars() {
      const colors = [0xff6b6b, 0x4ecdc4, 0x45b7d1, 0x96ceb4, 0xfeca57, 0xff9ff3]

      for (let i = 0; i < 12; i++) {
        // Create more detailed car
        const carGroup = new THREE.Group()

        // Car body
        const bodyGeometry = new THREE.BoxGeometry(1.2, 0.4, 0.6)
        const bodyMaterial = new THREE.MeshLambertMaterial({
          color: colors[Math.floor(Math.random() * colors.length)]
        })
        const body = new THREE.Mesh(bodyGeometry, bodyMaterial)
        body.position.y = 0.2
        carGroup.add(body)

        // Car roof
        const roofGeometry = new THREE.BoxGeometry(0.8, 0.3, 0.5)
        const roofMaterial = new THREE.MeshLambertMaterial({
          color: colors[Math.floor(Math.random() * colors.length)]
        })
        const roof = new THREE.Mesh(roofGeometry, roofMaterial)
        roof.position.y = 0.55
        carGroup.add(roof)

        // Wheels
        const wheelGeometry = new THREE.CylinderGeometry(0.15, 0.15, 0.1, 8)
        const wheelMaterial = new THREE.MeshLambertMaterial({ color: 0x333333 })

        const wheels = []
        const wheelPositions = [
          [-0.4, -0.1, 0.35],
          [0.4, -0.1, 0.35],
          [-0.4, -0.1, -0.35],
          [0.4, -0.1, -0.35]
        ]

        wheelPositions.forEach(pos => {
          const wheel = new THREE.Mesh(wheelGeometry, wheelMaterial)
          wheel.position.set(pos[0], pos[1], pos[2])
          wheel.rotation.z = Math.PI / 2
          carGroup.add(wheel)
          wheels.push(wheel)
        })

        // Position cars in a more organized pattern
        const angle = (i / 12) * Math.PI * 2
        const radius = 8 + Math.random() * 4
        carGroup.position.x = Math.cos(angle) * radius
        carGroup.position.z = Math.sin(angle) * radius
        carGroup.position.y = (Math.random() - 0.5) * 6

        // Random rotation
        carGroup.rotation.y = Math.random() * Math.PI * 2

        // Store movement data
        carGroup.userData = {
          angle: angle,
          radius: radius,
          speed: 0.005 + Math.random() * 0.01,
          verticalSpeed: (Math.random() - 0.5) * 0.005,
          rotationSpeed: (Math.random() - 0.5) * 0.02,
          wheels: wheels,
          originalY: carGroup.position.y
        }

        this.cars.push(carGroup)
        this.scene.add(carGroup)
      }

      // Add parking lot structures
      this.createParkingStructures()

      // Add traffic lights
      this.createTrafficLights()

      // Add particle effects
      this.createParticleEffects()
    },
    createParkingStructures() {
      // Create parking lot buildings
      for (let i = 0; i < 4; i++) {
        const buildingGroup = new THREE.Group()

        // Main building
        const buildingGeometry = new THREE.BoxGeometry(3, 2, 2)
        const buildingMaterial = new THREE.MeshLambertMaterial({
          color: this.isDarkMode ? 0x2a2a2a : 0x8a8a8a
        })
        const building = new THREE.Mesh(buildingGeometry, buildingMaterial)
        building.position.y = 1
        buildingGroup.add(building)

        // Parking spots (visual indicators)
        for (let j = 0; j < 6; j++) {
          const spotGeometry = new THREE.PlaneGeometry(0.8, 1.2)
          const spotMaterial = new THREE.MeshLambertMaterial({
            color: 0xffffff,
            transparent: true,
            opacity: 0.3
          })
          const spot = new THREE.Mesh(spotGeometry, spotMaterial)
          spot.rotation.x = -Math.PI / 2
          spot.position.set(
            (j % 3 - 1) * 1.2,
            0.01,
            Math.floor(j / 3) * 1.5 - 0.75
          )
          buildingGroup.add(spot)
        }

        // Position buildings around the scene
        const angle = (i / 4) * Math.PI * 2
        buildingGroup.position.x = Math.cos(angle) * 15
        buildingGroup.position.z = Math.sin(angle) * 15
        buildingGroup.position.y = -2

        this.scene.add(buildingGroup)
      }
    },
    createTrafficLights() {
      for (let i = 0; i < 6; i++) {
        const trafficLightGroup = new THREE.Group()

        // Pole
        const poleGeometry = new THREE.CylinderGeometry(0.05, 0.05, 3, 8)
        const poleMaterial = new THREE.MeshLambertMaterial({ color: 0x444444 })
        const pole = new THREE.Mesh(poleGeometry, poleMaterial)
        pole.position.y = 1.5
        trafficLightGroup.add(pole)

        // Light box
        const boxGeometry = new THREE.BoxGeometry(0.3, 0.8, 0.2)
        const boxMaterial = new THREE.MeshLambertMaterial({ color: 0x222222 })
        const box = new THREE.Mesh(boxGeometry, boxMaterial)
        box.position.y = 3.2
        trafficLightGroup.add(box)

        // Lights
        const lightColors = [0xff0000, 0xffff00, 0x00ff00]
        const lights = []

        lightColors.forEach((color, index) => {
          const lightGeometry = new THREE.SphereGeometry(0.08, 8, 8)
          const lightMaterial = new THREE.MeshLambertMaterial({
            color: color,
            emissive: color,
            emissiveIntensity: 0.2
          })
          const light = new THREE.Mesh(lightGeometry, lightMaterial)
          light.position.set(0, 3.5 - index * 0.25, 0.11)
          trafficLightGroup.add(light)
          lights.push(light)
        })

        // Position traffic lights
        const angle = (i / 6) * Math.PI * 2
        trafficLightGroup.position.x = Math.cos(angle) * 12
        trafficLightGroup.position.z = Math.sin(angle) * 12

        trafficLightGroup.userData = {
          lights: lights,
          currentLight: Math.floor(Math.random() * 3),
          timer: Math.random() * 3000
        }

        this.scene.add(trafficLightGroup)
        this.trafficLights = this.trafficLights || []
        this.trafficLights.push(trafficLightGroup)
      }
    },
    createParticleEffects() {
      // Create floating particles for ambiance
      const particleCount = 100
      const particles = new THREE.BufferGeometry()
      const positions = new Float32Array(particleCount * 3)
      const colors = new Float32Array(particleCount * 3)

      for (let i = 0; i < particleCount; i++) {
        positions[i * 3] = (Math.random() - 0.5) * 50
        positions[i * 3 + 1] = Math.random() * 20
        positions[i * 3 + 2] = (Math.random() - 0.5) * 50

        const color = new THREE.Color()
        color.setHSL(Math.random(), 0.5, 0.5)
        colors[i * 3] = color.r
        colors[i * 3 + 1] = color.g
        colors[i * 3 + 2] = color.b
      }

      particles.setAttribute('position', new THREE.BufferAttribute(positions, 3))
      particles.setAttribute('color', new THREE.BufferAttribute(colors, 3))

      const particleMaterial = new THREE.PointsMaterial({
        size: 0.1,
        vertexColors: true,
        transparent: true,
        opacity: 0.6
      })

      this.particleSystem = new THREE.Points(particles, particleMaterial)
      this.scene.add(this.particleSystem)
    },
    createMorphingShapes() {
      const geometries = [
        new THREE.IcosahedronGeometry(1.5, 0),
        new THREE.OctahedronGeometry(1.5, 0),
        new THREE.TetrahedronGeometry(1.5, 0),
        new THREE.DodecahedronGeometry(1.2, 0)
      ]
      const colors = [0x4ecdc4, 0xff6b6b, 0x45b7d1, 0xfeca57, 0xff9ff3, 0x96ceb4]
      
      for (let i = 0; i < 8; i++) {
        const geo = geometries[i % geometries.length]
        const material = new THREE.MeshPhongMaterial({
          color: colors[i % colors.length],
          transparent: true,
          opacity: 0.7,
          wireframe: Math.random() > 0.5,
          emissive: colors[i % colors.length],
          emissiveIntensity: 0.3
        })
        
        const mesh = new THREE.Mesh(geo.clone(), material)
        mesh.position.set(
          (Math.random() - 0.5) * 40,
          (Math.random() - 0.5) * 20,
          (Math.random() - 0.5) * 30 - 10
        )
        mesh.userData = {
          rotationSpeed: { x: Math.random() * 0.02, y: Math.random() * 0.02, z: Math.random() * 0.01 },
          floatSpeed: 0.5 + Math.random() * 1,
          floatOffset: Math.random() * Math.PI * 2,
          pulseSpeed: 1 + Math.random() * 2,
          originalScale: 0.5 + Math.random() * 1
        }
        mesh.scale.setScalar(mesh.userData.originalScale)
        this.morphingShapes.push(mesh)
        this.scene.add(mesh)
      }
    },
    createGlowOrbs() {
      for (let i = 0; i < 12; i++) {
        const geometry = new THREE.SphereGeometry(0.3 + Math.random() * 0.5, 32, 32)
        const hue = Math.random()
        const material = new THREE.MeshBasicMaterial({
          color: new THREE.Color().setHSL(hue, 0.8, 0.6),
          transparent: true,
          opacity: 0.8
        })
        
        const orb = new THREE.Mesh(geometry, material)
        orb.position.set(
          (Math.random() - 0.5) * 50,
          (Math.random() - 0.5) * 25,
          (Math.random() - 0.5) * 40 - 5
        )
        orb.userData = {
          baseHue: hue,
          speed: 0.3 + Math.random() * 0.7,
          amplitude: 2 + Math.random() * 4,
          phase: Math.random() * Math.PI * 2,
          orbitRadius: 5 + Math.random() * 15,
          orbitSpeed: 0.2 + Math.random() * 0.5,
          orbitAngle: Math.random() * Math.PI * 2
        }
        this.glowOrbs.push(orb)
        this.scene.add(orb)
      }
    },
    createShootingStars() {
      for (let i = 0; i < 6; i++) {
        const curve = new THREE.CatmullRomCurve3([
          new THREE.Vector3(0, 0, 0),
          new THREE.Vector3(-2, 0, 0),
          new THREE.Vector3(-5, 0, 0)
        ])
        const geometry = new THREE.TubeGeometry(curve, 20, 0.05, 8, false)
        const material = new THREE.MeshBasicMaterial({
          color: 0xffffff,
          transparent: true,
          opacity: 0.9
        })
        
        const star = new THREE.Mesh(geometry, material)
        star.position.set(50, Math.random() * 30 - 15, -20 - Math.random() * 20)
        star.userData = {
          speed: 0.8 + Math.random() * 1.2,
          active: false,
          delay: Math.random() * 5000,
          lastTrigger: 0
        }
        star.visible = false
        this.shootingStars.push(star)
        this.scene.add(star)
      }
    },
    createWaveEffect() {
      const geometry = new THREE.PlaneGeometry(80, 80, 50, 50)
      const material = new THREE.MeshPhongMaterial({
        color: 0x4ecdc4,
        transparent: true,
        opacity: 0.15,
        wireframe: true,
        side: THREE.DoubleSide
      })
      
      this.waveMesh = new THREE.Mesh(geometry, material)
      this.waveMesh.rotation.x = -Math.PI / 2
      this.waveMesh.position.y = -8
      this.waveMesh.position.z = -10
      this.scene.add(this.waveMesh)
    },
    createEnergyRings() {
      const colors = [0x4ecdc4, 0xff6b6b, 0x45b7d1]
      
      for (let i = 0; i < 5; i++) {
        const geometry = new THREE.TorusGeometry(3 + i * 1.5, 0.05, 16, 100)
        const material = new THREE.MeshBasicMaterial({
          color: colors[i % colors.length],
          transparent: true,
          opacity: 0.6
        })
        
        const ring = new THREE.Mesh(geometry, material)
        ring.position.set(0, 0, -15)
        ring.userData = {
          rotationSpeed: 0.01 + i * 0.005,
          wobbleSpeed: 0.5 + i * 0.2,
          wobbleAmount: 0.1 + i * 0.05
        }
        this.energyRings.push(ring)
        this.scene.add(ring)
      }
    },
    animate() {
      requestAnimationFrame(this.animate)

      const time = Date.now() * 0.001

      // Animate cars in circular motion
      this.cars.forEach(car => {
        car.userData.angle += car.userData.speed
        car.position.x = Math.cos(car.userData.angle) * car.userData.radius
        car.position.z = Math.sin(car.userData.angle) * car.userData.radius

        // Gentle vertical movement
        car.position.y = car.userData.originalY + Math.sin(time + car.userData.angle) * 0.5

        // Rotate car
        car.rotation.y += car.userData.rotationSpeed

        // Animate wheels
        if (car.userData.wheels) {
          car.userData.wheels.forEach(wheel => {
            wheel.rotation.x += car.userData.speed * 10
          })
        }
      })

      // Animate traffic lights
      if (this.trafficLights) {
        this.trafficLights.forEach(trafficLight => {
          trafficLight.userData.timer += 16 // ~60fps
          if (trafficLight.userData.timer > 2000) { // Change every 2 seconds
            trafficLight.userData.timer = 0

            // Turn off current light
            trafficLight.userData.lights.forEach(light => {
              light.material.emissiveIntensity = 0.1
            })

            // Turn on next light
            trafficLight.userData.currentLight = (trafficLight.userData.currentLight + 1) % 3
            const currentLight = trafficLight.userData.lights[trafficLight.userData.currentLight]
            currentLight.material.emissiveIntensity = 0.8
          }
        })
      }

      // Animate particles
      if (this.particleSystem) {
        this.particleSystem.rotation.y += 0.001
        const positions = this.particleSystem.geometry.attributes.position.array
        for (let i = 1; i < positions.length; i += 3) {
          positions[i] += Math.sin(time + i) * 0.01
        }
        this.particleSystem.geometry.attributes.position.needsUpdate = true
      }

      // Animate morphing shapes
      this.morphingShapes.forEach(shape => {
        shape.rotation.x += shape.userData.rotationSpeed.x
        shape.rotation.y += shape.userData.rotationSpeed.y
        shape.rotation.z += shape.userData.rotationSpeed.z
        
        // Floating motion
        shape.position.y += Math.sin(time * shape.userData.floatSpeed + shape.userData.floatOffset) * 0.02
        
        // Pulsing scale
        const pulse = 1 + Math.sin(time * shape.userData.pulseSpeed) * 0.15
        shape.scale.setScalar(shape.userData.originalScale * pulse)
        
        // Color shift
        if (shape.material.emissive) {
          const hue = (time * 0.1 + shape.userData.floatOffset) % 1
          shape.material.emissive.setHSL(hue, 0.8, 0.3)
        }
      })

      // Animate glow orbs
      this.glowOrbs.forEach(orb => {
        orb.userData.orbitAngle += orb.userData.orbitSpeed * 0.01
        orb.position.x += Math.sin(time * orb.userData.speed + orb.userData.phase) * 0.03
        orb.position.y += Math.cos(time * orb.userData.speed * 0.7 + orb.userData.phase) * 0.02
        
        // Color cycling
        const hue = (orb.userData.baseHue + time * 0.05) % 1
        orb.material.color.setHSL(hue, 0.8, 0.6)
        
        // Pulsing opacity
        orb.material.opacity = 0.5 + Math.sin(time * 2 + orb.userData.phase) * 0.3
      })

      // Animate shooting stars
      const now = Date.now()
      this.shootingStars.forEach(star => {
        if (!star.userData.active) {
          if (now - star.userData.lastTrigger > star.userData.delay) {
            star.userData.active = true
            star.visible = true
            star.position.x = 40
            star.position.y = Math.random() * 20 - 10
            star.userData.lastTrigger = now
          }
        } else {
          star.position.x -= star.userData.speed * 2
          star.material.opacity = Math.max(0, 1 - Math.abs(star.position.x) / 80)
          
          if (star.position.x < -50) {
            star.userData.active = false
            star.visible = false
            star.userData.delay = 3000 + Math.random() * 7000
          }
        }
      })

      // Animate wave mesh
      if (this.waveMesh) {
        const positions = this.waveMesh.geometry.attributes.position.array
        for (let i = 0; i < positions.length; i += 3) {
          const x = positions[i]
          const z = positions[i + 2]
          positions[i + 1] = Math.sin(x * 0.1 + time) * Math.cos(z * 0.1 + time) * 1.5
        }
        this.waveMesh.geometry.attributes.position.needsUpdate = true
      }

      // Animate energy rings
      this.energyRings.forEach((ring, index) => {
        ring.rotation.x = time * ring.userData.rotationSpeed + index * 0.5
        ring.rotation.y = time * ring.userData.rotationSpeed * 1.5
        ring.rotation.z = Math.sin(time * ring.userData.wobbleSpeed) * ring.userData.wobbleAmount
        
        // Pulsing opacity
        ring.material.opacity = 0.3 + Math.sin(time * 2 + index) * 0.2
      })

      // Dynamic camera movement with mouse interaction
      const mouseInfluence = 0.8
      this.camera.position.x = Math.sin(time * 0.15) * 3 + this.mouse.x * mouseInfluence * 3
      this.camera.position.y = 2 + Math.cos(time * 0.1) * 2 + this.mouse.y * mouseInfluence * 2
      this.camera.position.z = 15 + Math.sin(time * 0.08) * 3 - (this.scrollY * 0.005)

      // Look at center with slight mouse influence
      const lookAtX = this.mouse.x * 3
      const lookAtY = this.mouse.y * 2
      this.camera.lookAt(lookAtX, lookAtY, -5)

      this.renderer.render(this.scene, this.camera)
    },
    onWindowResize() {
      this.camera.aspect = window.innerWidth / window.innerHeight
      this.camera.updateProjectionMatrix()
      this.renderer.setSize(window.innerWidth, window.innerHeight)
    },
    addScrollAnimations() {
      // Add intersection observer for scroll animations
      const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
      }
      
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('animate-in')
          }
        })
      }, observerOptions)
      
      // Observe all sections
      document.querySelectorAll('.features, .how-it-works, .statistics, .testimonials, .faq, .contact').forEach(section => {
        observer.observe(section)
      })
    },
    scrollToSection(sectionId) {
      const element = document.getElementById(sectionId)
      if (element) {
        element.scrollIntoView({ 
          behavior: 'smooth',
          block: 'start'
        })
      }
    },
    goToLogin() {
      this.$router.push('/login')
    },
    goToRegister() {
      this.$router.push('/login')
    },
    initTheme() {
      // Load theme preference from localStorage
      const savedTheme = localStorage.getItem('cyberpark-theme')
      this.isDarkMode = savedTheme === 'dark'
      
      // Set body class and background on initial load
      document.body.classList.toggle('dark-mode', this.isDarkMode)
      document.body.style.backgroundColor = this.isDarkMode ? '#0a0a0a' : '#ffffff'
    },
    toggleTheme() {
      this.isDarkMode = !this.isDarkMode
      localStorage.setItem('cyberpark-theme', this.isDarkMode ? 'dark' : 'light')

      // Update document body for proper theme sync
      document.body.classList.toggle('dark-mode', this.isDarkMode)
      document.body.style.backgroundColor = this.isDarkMode ? '#0a0a0a' : '#ffffff'

      // Update Three.js scene background and fog
      if (this.scene) {
        const bgColor = this.isDarkMode ? 0x050510 : 0x0a0a1a
        this.scene.background = new THREE.Color(bgColor)
        
        if (this.scene.fog) {
          this.scene.fog.color = new THREE.Color(bgColor)
        }

        // Update building materials
        this.scene.traverse((child) => {
          if (child.isMesh && child.material.color) {
            // Update building colors based on theme
            if (child.geometry.type === 'BoxGeometry' && child.position.y > 0.5) {
              child.material.color.setHex(this.isDarkMode ? 0x2a2a2a : 0x8a8a8a)
            }
          }
        })

        // Update particle opacity based on theme
        if (this.particleSystem) {
          this.particleSystem.material.opacity = this.isDarkMode ? 0.9 : 0.5
        }

        // Update wave mesh color
        if (this.waveMesh) {
          this.waveMesh.material.color.setHex(this.isDarkMode ? 0x4ecdc4 : 0x45b7d1)
          this.waveMesh.material.opacity = this.isDarkMode ? 0.2 : 0.12
        }

        // Update energy rings brightness
        this.energyRings.forEach(ring => {
          ring.material.opacity = this.isDarkMode ? 0.7 : 0.5
        })

        // Update glow orbs brightness
        this.glowOrbs.forEach(orb => {
          orb.material.opacity = this.isDarkMode ? 0.9 : 0.7
        })
      }
    },
    toggleFaq(faqId) {
      this.activeFaq = this.activeFaq === faqId ? null : faqId
    },
    startTestimonialRotation() {
      setInterval(() => {
        const nextId = this.currentTestimonial >= this.testimonials.length ? 1 : this.currentTestimonial + 1
        this.currentTestimonial = nextId
      }, 5000) // Rotate every 5 seconds
    },
    onMouseMove(event) {
      this.mouse.x = (event.clientX / window.innerWidth) * 2 - 1
      this.mouse.y = -(event.clientY / window.innerHeight) * 2 + 1
    },
    onScroll() {
      this.scrollY = window.scrollY
    }
  }
}
</script>

<style>
/* Global styles to prevent white margins */
html, body {
  margin: 0;
  padding: 0;
  width: 100%;
  overflow-x: hidden;
}

body {
  transition: background-color 0.5s ease;
  background-color: #ffffff;
}

body.dark-mode {
  background-color: #0a0a0a;
}
</style>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.homepage {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  line-height: 1.6;
  color: #333;
  transition: background-color 0.5s ease, color 0.5s ease;
  overflow-x: hidden;
  min-height: 100vh;
  width: 100%;
}

/* Navigation */
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: rgba(10, 10, 10, 0.95);
  backdrop-filter: blur(10px);
  z-index: 1000;
  padding: 1rem 0;
  transition: all 0.3s ease;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 2rem;
}

.nav-logo h2 {
  color: #4ecdc4;
  font-size: 1.5rem;
  font-weight: bold;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.nav-link {
  background: none;
  border: none;
  color: #fff;
  cursor: pointer;
  font-size: 1rem;
  transition: color 0.3s ease;
}

.nav-link:hover {
  color: #4ecdc4;
}

.btn-login, .btn-register {
  padding: 0.5rem 1.5rem;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-login {
  background: transparent;
  color: #fff;
  border: 2px solid #4ecdc4;
}

.btn-login:hover {
  background: #4ecdc4;
  color: #0a0a0a;
}

.btn-register {
  background: #4ecdc4;
  color: #0a0a0a;
}

.btn-register:hover {
  background: #45b7d1;
  transform: translateY(-2px);
}

.theme-toggle {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 50%;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
}

.theme-toggle:hover {
  background: rgba(78, 205, 196, 0.2);
  transform: scale(1.1);
}

/* Hero Section */
.hero {
  position: relative;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.three-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

.hero-content {
  position: relative;
  z-index: 2;
  text-align: center;
  color: #fff;
  max-width: 800px;
  padding: 0 2rem;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
  background: linear-gradient(135deg, #4ecdc4, #45b7d1);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: fadeInUp 1s ease-out;
}

.hero-subtitle {
  font-size: 1.3rem;
  margin-bottom: 2rem;
  opacity: 0.9;
  animation: fadeInUp 1s ease-out 0.3s both;
}

.hero-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
  animation: fadeInUp 1s ease-out 0.6s both;
}

.btn-primary, .btn-secondary {
  padding: 1rem 2rem;
  border: none;
  border-radius: 30px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: linear-gradient(135deg, #4ecdc4, #45b7d1);
  color: #fff;
}

.btn-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 25px rgba(78, 205, 196, 0.3);
}

.btn-secondary {
  background: transparent;
  color: #fff;
  border: 2px solid #fff;
}

.btn-secondary:hover {
  background: #fff;
  color: #0a0a0a;
}

.scroll-indicator {
  position: absolute;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
  cursor: pointer;
  z-index: 2;
  animation: bounce 2s infinite;
}

.scroll-arrow {
  color: #4ecdc4;
  font-size: 2rem;
  font-weight: bold;
}

/* Sections */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

.section-title {
  text-align: center;
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 3rem;
  color: #333;
}

/* Features Section */
.features {
  padding: 5rem 0;
  background: #f8f9fa;
  opacity: 1;
  transform: translateY(0);
  transition: all 0.8s ease;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.feature-card {
  background: #fff;
  padding: 2rem;
  border-radius: 15px;
  text-align: center;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.15);
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.feature-card h3 {
  font-size: 1.3rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #333;
}

.feature-card p {
  color: #666;
  line-height: 1.6;
}

/* How It Works Section */
.how-it-works {
  padding: 5rem 0;
  background: #fff;
  opacity: 1;
  transform: translateY(0);
  transition: all 0.8s ease;
}

.steps-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 3rem;
}

.step {
  text-align: center;
  position: relative;
}

.step-number {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #4ecdc4, #45b7d1);
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: bold;
  margin: 0 auto 1.5rem;
}

.step h3 {
  font-size: 1.3rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #333;
}

.step p {
  color: #666;
  line-height: 1.6;
}

/* Contact Section */
.contact {
  padding: 5rem 0;
  background: linear-gradient(135deg, #4ecdc4, #45b7d1);
  color: #fff;
  opacity: 1;
  transform: translateY(0);
  transition: all 0.8s ease;
}

.contact .section-title {
  color: #fff;
}

.contact-content {
  text-align: center;
}

.contact-info h3 {
  font-size: 1.8rem;
  margin-bottom: 1rem;
}

.contact-info p {
  font-size: 1.1rem;
  margin-bottom: 2rem;
  opacity: 0.9;
}

.contact-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.btn-outline {
  padding: 1rem 2rem;
  background: transparent;
  color: #fff;
  border: 2px solid #fff;
  border-radius: 30px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-outline:hover {
  background: #fff;
  color: #4ecdc4;
}

/* Footer */
.footer {
  background: #0a0a0a;
  color: #fff;
  padding: 3rem 0 1rem;
}

.footer-content {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 3rem;
  margin-bottom: 2rem;
}

.footer-logo h3 {
  color: #4ecdc4;
  margin-bottom: 0.5rem;
}

.footer-logo p {
  opacity: 0.7;
}

.footer-links {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 2rem;
}

.footer-section h4 {
  margin-bottom: 1rem;
  color: #4ecdc4;
}

.footer-section a {
  display: block;
  color: #ccc;
  text-decoration: none;
  margin-bottom: 0.5rem;
  transition: color 0.3s ease;
}

.footer-section a:hover {
  color: #4ecdc4;
}

.footer-bottom {
  border-top: 1px solid #333;
  padding-top: 1rem;
  text-align: center;
  opacity: 0.7;
}

.social-links {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.social-link {
  display: inline-block;
  font-size: 1.5rem;
  text-decoration: none;
  transition: transform 0.3s ease;
}

.social-link:hover {
  transform: scale(1.2);
}

/* Statistics Section */
.statistics {
  padding: 5rem 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2rem;
}

.stat-card {
  text-align: center;
  padding: 2rem;
}

.stat-number {
  font-size: 3rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
  background: linear-gradient(135deg, #fff, #f0f0f0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-label {
  font-size: 1.1rem;
  opacity: 0.9;
}

/* Testimonials Section */
.testimonials {
  padding: 5rem 0;
  background: #f8f9fa;
}

.testimonials-container {
  position: relative;
  max-width: 800px;
  margin: 0 auto;
  height: 300px;
  overflow: hidden;
}

.testimonial-card {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  opacity: 0;
  transform: translateX(100px);
  transition: all 0.5s ease;
}

.testimonial-card.active {
  opacity: 1;
  transform: translateX(0);
}

.testimonial-content {
  background: #fff;
  padding: 3rem;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.testimonial-content p {
  font-size: 1.2rem;
  font-style: italic;
  margin-bottom: 2rem;
  color: #333;
  line-height: 1.6;
}

.testimonial-author {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}

.author-avatar {
  font-size: 3rem;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #4ecdc4, #45b7d1);
  border-radius: 50%;
}

.author-info h4 {
  margin: 0;
  color: #333;
  font-weight: 600;
}

.author-info span {
  color: #666;
  font-size: 0.9rem;
}

.testimonial-dots {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 2rem;
}

.testimonial-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: none;
  background: #ccc;
  cursor: pointer;
  transition: all 0.3s ease;
}

.testimonial-dot.active {
  background: #4ecdc4;
  transform: scale(1.2);
}

/* FAQ Section */
.faq {
  padding: 5rem 0;
  background: #fff;
}

.faq-container {
  max-width: 800px;
  margin: 0 auto;
}

.faq-item {
  border-bottom: 1px solid #eee;
  margin-bottom: 1rem;
}

.faq-question {
  width: 100%;
  padding: 1.5rem 0;
  background: none;
  border: none;
  text-align: left;
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: color 0.3s ease;
}

.faq-question:hover {
  color: #4ecdc4;
}

.faq-question.active {
  color: #4ecdc4;
}

.faq-icon {
  font-size: 1.5rem;
  font-weight: bold;
  transition: transform 0.3s ease;
}

.faq-question.active .faq-icon {
  transform: rotate(180deg);
}

.faq-answer {
  max-height: 0;
  overflow: hidden;
  transition: all 0.3s ease;
  padding: 0;
}

.faq-answer.active {
  max-height: 200px;
  padding: 0 0 1.5rem 0;
}

.faq-answer p {
  color: #666;
  line-height: 1.6;
  margin: 0;
}

/* Animations */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateX(-50%) translateY(0);
  }
  40% {
    transform: translateX(-50%) translateY(-10px);
  }
  60% {
    transform: translateX(-50%) translateY(-5px);
  }
}

/* Responsive Design */
@media (max-width: 768px) {
  .nav-links {
    gap: 1rem;
  }

  .nav-link {
    display: none;
  }

  .hero-title {
    font-size: 2.5rem;
  }

  .hero-subtitle {
    font-size: 1.1rem;
  }

  .hero-buttons {
    flex-direction: column;
    align-items: center;
  }

  .btn-primary, .btn-secondary {
    width: 100%;
    max-width: 300px;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }

  .steps-container {
    grid-template-columns: 1fr;
  }

  .contact-buttons {
    flex-direction: column;
    align-items: center;
  }

  .btn-outline {
    width: 100%;
    max-width: 300px;
  }

  .footer-content {
    grid-template-columns: 1fr;
    text-align: center;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .testimonials-container {
    height: auto;
    min-height: 300px;
  }

  .testimonial-content {
    padding: 2rem;
  }

  .testimonial-author {
    flex-direction: column;
    text-align: center;
  }
}

@media (max-width: 480px) {
  .nav-container {
    padding: 0 1rem;
  }

  .hero-content {
    padding: 0 1rem;
  }

  .container {
    padding: 0 1rem;
  }

  .hero-title {
    font-size: 2rem;
  }

  .section-title {
    font-size: 2rem;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .stat-number {
    font-size: 2.5rem;
  }

  .testimonial-content {
    padding: 1.5rem;
  }

  .testimonial-content p {
    font-size: 1rem;
  }

  .social-links {
    justify-content: center;
  }
}

/* Dark Mode Styles */
.homepage.dark-mode {
  background: #0a0a0a;
  color: #e0e0e0;
}

.homepage.dark-mode .navbar {
  background: rgba(0, 0, 0, 0.95);
}

.homepage.dark-mode .nav-logo h2 {
  color: #4ecdc4;
}

.homepage.dark-mode .nav-link {
  color: #e0e0e0;
}

.homepage.dark-mode .nav-link:hover {
  color: #4ecdc4;
}

.homepage.dark-mode .btn-login {
  color: #e0e0e0;
  border-color: #4ecdc4;
}

.homepage.dark-mode .btn-login:hover {
  background: #4ecdc4;
  color: #0a0a0a;
}

.homepage.dark-mode .hero-title {
  background: linear-gradient(135deg, #4ecdc4, #45b7d1);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.homepage.dark-mode .hero-subtitle {
  color: #b0b0b0;
}

.homepage.dark-mode .btn-secondary {
  color: #e0e0e0;
  border-color: #e0e0e0;
}

.homepage.dark-mode .btn-secondary:hover {
  background: #e0e0e0;
  color: #0a0a0a;
}

.homepage.dark-mode .scroll-arrow {
  color: #4ecdc4;
}

.homepage.dark-mode .features {
  background: #1a1a1a;
}

.homepage.dark-mode .section-title {
  color: #e0e0e0;
}

.homepage.dark-mode .feature-card {
  background: #2a2a2a;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
}

.homepage.dark-mode .feature-card:hover {
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.4);
}

.homepage.dark-mode .feature-card h3 {
  color: #e0e0e0;
}

.homepage.dark-mode .feature-card p {
  color: #b0b0b0;
}

.homepage.dark-mode .how-it-works {
  background: #0f0f0f;
}

.homepage.dark-mode .step h3 {
  color: #e0e0e0;
}

.homepage.dark-mode .step p {
  color: #b0b0b0;
}

.homepage.dark-mode .footer {
  background: #000;
}

.homepage.dark-mode .footer-logo h3 {
  color: #4ecdc4;
}

.homepage.dark-mode .footer-logo p {
  color: #b0b0b0;
}

.homepage.dark-mode .footer-section h4 {
  color: #4ecdc4;
}

.homepage.dark-mode .footer-section a {
  color: #b0b0b0;
}

.homepage.dark-mode .footer-section a:hover {
  color: #4ecdc4;
}

.homepage.dark-mode .footer-bottom {
  border-top-color: #333;
  color: #b0b0b0;
}

.homepage.dark-mode .theme-toggle:hover {
  background: rgba(78, 205, 196, 0.3);
}

/* Dark Mode - New Sections */
.homepage.dark-mode .statistics {
  background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
}

.homepage.dark-mode .testimonials {
  background: #1a1a1a;
}

.homepage.dark-mode .testimonial-content {
  background: #2a2a2a;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.homepage.dark-mode .testimonial-content p {
  color: #e0e0e0;
}

.homepage.dark-mode .author-info h4 {
  color: #e0e0e0;
}

.homepage.dark-mode .author-info span {
  color: #b0b0b0;
}

.homepage.dark-mode .testimonial-dot {
  background: #555;
}

.homepage.dark-mode .testimonial-dot.active {
  background: #4ecdc4;
}

.homepage.dark-mode .faq {
  background: #0f0f0f;
}

.homepage.dark-mode .faq-item {
  border-bottom-color: #333;
}

.homepage.dark-mode .faq-question {
  color: #e0e0e0;
}

.homepage.dark-mode .faq-question:hover,
.homepage.dark-mode .faq-question.active {
  color: #4ecdc4;
}

.homepage.dark-mode .faq-answer p {
  color: #b0b0b0;
}

.homepage.dark-mode .social-link {
  opacity: 0.8;
}

.homepage.dark-mode .social-link:hover {
  opacity: 1;
}

/* Enhanced section transitions */
.features,
.how-it-works,
.statistics,
.testimonials,
.faq,
.contact {
  transition: background-color 0.5s ease, transform 0.8s ease, opacity 0.8s ease;
}

/* Neon glow effects */
@keyframes neonPulse {
  0%, 100% {
    text-shadow: 0 0 5px #4ecdc4, 0 0 10px #4ecdc4, 0 0 20px #4ecdc4;
  }
  50% {
    text-shadow: 0 0 10px #4ecdc4, 0 0 20px #4ecdc4, 0 0 40px #4ecdc4, 0 0 80px #4ecdc4;
  }
}

@keyframes glowBox {
  0%, 100% {
    box-shadow: 0 0 10px rgba(78, 205, 196, 0.3), 0 0 20px rgba(78, 205, 196, 0.2);
  }
  50% {
    box-shadow: 0 0 20px rgba(78, 205, 196, 0.5), 0 0 40px rgba(78, 205, 196, 0.3), 0 0 60px rgba(78, 205, 196, 0.2);
  }
}

@keyframes float3D {
  0%, 100% {
    transform: translateY(0) rotateX(0deg);
  }
  25% {
    transform: translateY(-10px) rotateX(5deg);
  }
  50% {
    transform: translateY(-5px) rotateX(0deg);
  }
  75% {
    transform: translateY(-15px) rotateX(-5deg);
  }
}

@keyframes shimmer {
  0% {
    background-position: -200% center;
  }
  100% {
    background-position: 200% center;
  }
}

/* Apply animations to elements */
.homepage.dark-mode .hero-title {
  animation: neonPulse 3s ease-in-out infinite, fadeInUp 1s ease-out;
}

.homepage.dark-mode .feature-card {
  animation: float3D 6s ease-in-out infinite;
  animation-delay: var(--delay, 0s);
}

.homepage.dark-mode .feature-card:nth-child(1) { --delay: 0s; }
.homepage.dark-mode .feature-card:nth-child(2) { --delay: 0.5s; }
.homepage.dark-mode .feature-card:nth-child(3) { --delay: 1s; }
.homepage.dark-mode .feature-card:nth-child(4) { --delay: 1.5s; }
.homepage.dark-mode .feature-card:nth-child(5) { --delay: 2s; }
.homepage.dark-mode .feature-card:nth-child(6) { --delay: 2.5s; }

.homepage.dark-mode .feature-card:hover {
  animation: glowBox 1.5s ease-in-out infinite;
  border: 1px solid rgba(78, 205, 196, 0.5);
}

.homepage.dark-mode .step-number {
  animation: neonPulse 2s ease-in-out infinite;
}

.homepage.dark-mode .btn-primary {
  position: relative;
  overflow: hidden;
}

.homepage.dark-mode .btn-primary::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
  animation: shimmer 3s infinite;
}

/* Enhanced scroll indicator */
.scroll-indicator {
  animation: bounce 2s infinite, neonPulse 2s ease-in-out infinite;
}

/* Three.js container effects */
.three-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  filter: saturate(1.2) contrast(1.1);
}

.homepage.dark-mode .three-container {
  filter: saturate(1.4) contrast(1.2) brightness(1.1);
}

/* Light mode specific adjustments */
.homepage:not(.dark-mode) .three-container {
  filter: saturate(1.1) brightness(0.95);
}

.homepage:not(.dark-mode) .navbar {
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
}

.homepage:not(.dark-mode) .nav-link {
  color: #333;
}

.homepage:not(.dark-mode) .btn-login {
  color: #333;
}
</style>
