<template>
  <div class="file-upload" @drop.prevent="handleDrop" @dragover.prevent>
    <el-tooltip content="拖拽或点击上传文件" placement="top">
      <el-button :icon="Upload" circle @click="$refs.fileInput.click()" />
    </el-tooltip>
    <input
      ref="fileInput"
      type="file"
      accept=".md,.txt,.csv,.pdf,.docx,.xlsx,.png,.jpg,.jpeg,.webp"
      style="display: none"
      @change="handleFile"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Upload } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const emit = defineEmits(['uploaded'])
const fileInput = ref(null)

async function handleFile(event) {
  const file = event.target.files[0]
  if (!file) return
  await processFile(file)
}

async function handleDrop(event) {
  const file = event.dataTransfer.files[0]
  if (!file) return
  await processFile(file)
}

async function processFile(file) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('tenant_id', 'default')

  try {
    const resp = await fetch('/api/knowledge/upload', {
      method: 'POST',
      headers: { Authorization: 'Bearer ' + localStorage.getItem('token') },
      body: formData,
    })
    const data = await resp.json()
    if (data.id) {
      ElMessage.success('文件上传成功')
      emit('uploaded', data.title)
    }
  } catch (error) {
    ElMessage.error('上传失败: ' + error)
  }
}
</script>
