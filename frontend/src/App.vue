<template>
  <div class="app-layout">
    <SidebarNav />
    <transition name="fade-slide" mode="out-in">
      <main class="app-main">
        <router-view />
      </main>
    </transition>
  </div>
</template>

<script setup>
import SidebarNav from './components/SidebarNav.vue'
</script>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
}

.app-main {
  margin-left: 64px;
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--bg-deep);
  transition: margin-left var(--transition-slow);
  min-height: 100vh;
  overflow: auto;
}
</style>
