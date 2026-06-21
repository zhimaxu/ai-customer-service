<template>
  <canvas ref="canvasRef" class="particle-canvas"></canvas>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const canvasRef = ref(null)
let animationId = null
let particles = []

const PARTICLE_COUNT = 70
const CONNECTION_DISTANCE = 150
const MOUSE_RADIUS = 120

class Particle {
  constructor(w, h) {
    this.x = Math.random() * w
    this.y = Math.random() * h
    this.vx = (Math.random() - 0.5) * 0.6
    this.vy = (Math.random() - 0.5) * 0.6
    this.radius = Math.random() * 1.5 + 0.5
    this.opacity = Math.random() * 0.5 + 0.3
    this.pulseSpeed = Math.random() * 0.02 + 0.005
    this.pulseOffset = Math.random() * Math.PI * 2
  }

  update(time, w, h) {
    this.x += this.vx
    this.y += this.vy

    if (this.x < 0 || this.x > w) this.vx *= -1
    if (this.y < 0 || this.y > h) this.vy *= -1

    this.currentOpacity = this.opacity * (0.7 + 0.3 * Math.sin(time * this.pulseSpeed + this.pulseOffset))
  }

  draw(ctx) {
    ctx.beginPath()
    ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2)
    ctx.fillStyle = `rgba(255, 107, 53, ${this.currentOpacity})`
    ctx.fill()
  }
}

function init(canvas) {
  const w = (canvas.width = canvas.offsetWidth)
  const h = (canvas.height = canvas.offsetHeight)
  particles = []
  for (let i = 0; i < PARTICLE_COUNT; i++) {
    particles.push(new Particle(w, h))
  }
}

function drawConnections(ctx, w, h, time) {
  for (let i = 0; i < particles.length; i++) {
    for (let j = i + 1; j < particles.length; j++) {
      const dx = particles[i].x - particles[j].x
      const dy = particles[i].y - particles[j].y
      const dist = Math.sqrt(dx * dx + dy * dy)
      if (dist < CONNECTION_DISTANCE) {
        const alpha = (1 - dist / CONNECTION_DISTANCE) * 0.15
        ctx.beginPath()
        ctx.moveTo(particles[i].x, particles[i].y)
        ctx.lineTo(particles[j].x, particles[j].y)
        ctx.strokeStyle = `rgba(255, 107, 53, ${alpha})`
        ctx.lineWidth = 0.5
        ctx.stroke()
      }
    }
  }
}

function animate(time) {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  const w = canvas.width
  const h = canvas.height

  ctx.clearRect(0, 0, w, h)

  particles.forEach((p) => {
    p.update(time, w, h)
    p.draw(ctx)
  })

  drawConnections(ctx, w, h, time)

  animationId = requestAnimationFrame(animate)
}

onMounted(() => {
  const canvas = canvasRef.value
  if (!canvas) return
  init(canvas)
  window.addEventListener('resize', () => init(canvas))
  animationId = requestAnimationFrame(animate)
})

onBeforeUnmount(() => {
  if (animationId) cancelAnimationFrame(animationId)
})
</script>

<style scoped>
.particle-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
}
</style>
