import { defineStore } from 'pinia'
import { ref } from 'vue'
import request from '../api/request'

export const useSessionStore = defineStore('session', () => {
  const sessions = ref([])
  const currentSession = ref(null)
  const messages = ref([])

  async function fetchSessions(params = {}) {
    const data = await request.get('/chat/sessions', { params })
    sessions.value = data.sessions || []
    return sessions.value
  }

  async function fetchSessionDetail(sessionId) {
    const data = await request.get(`/chat/sessions/${sessionId}`)
    currentSession.value = data.session
    messages.value = data.messages || []
    return data
  }

  async function createSession() {
    const data = await request.post('/chat', {
      message: '',
      user_id: 'current-user',
      tenant_id: 'default',
    })
    await fetchSessions()
    currentSession.value = { id: data.session_id }
    messages.value = []
    return data
  }

  async function closeSession(sessionId) {
    await request.delete(`/chat/sessions/${sessionId}`)
    await fetchSessions()
    if (currentSession.value?.id === sessionId) {
      currentSession.value = null
      messages.value = []
    }
  }

  function addMessage(msg) {
    messages.value.push(msg)
  }

  function clearMessages() {
    messages.value = []
  }

  return {
    sessions,
    currentSession,
    messages,
    fetchSessions,
    fetchSessionDetail,
    createSession,
    closeSession,
    addMessage,
    clearMessages,
  }
})
