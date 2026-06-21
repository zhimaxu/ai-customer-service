<template>
  <el-drawer v-model="open" title="设置" size="360px">
    <el-form label-position="top">
      <el-form-item label="打字速度 (ms/字)">
        <el-slider v-model="speed" :min="10" :max="200" :step="5" show-input />
        <span style="font-size: 12px; color: #999">默认 30ms，越小越快</span>
      </el-form-item>
      <el-form-item label="主题">
        <el-radio-group v-model="theme">
          <el-radio value="light">浅色</el-radio>
          <el-radio value="dark">深色</el-radio>
        </el-radio-group>
      </el-form-item>
    </el-form>
  </el-drawer>
</template>

<script setup>
import { ref } from 'vue'
const open = ref(false)
const speed = ref(parseInt(localStorage.getItem('typewriter-speed') || '30'))
const theme = ref(localStorage.getItem('theme') || 'light')
defineExpose({ open })
</script>
