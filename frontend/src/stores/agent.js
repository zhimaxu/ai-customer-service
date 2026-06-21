import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import request from '../api/request'

export const useAgentStore = defineStore('agent', () => {
  // State
  const sessions = ref([])
  const activeSessions = ref([])
  const currentSession = ref(null)
  const ws = ref(null)
  const wsConnected = ref(false)
  const quickReplies = ref([
    '您好，有什么可以帮您？',
    '请稍等，我为您查询一下',
    '感谢您的耐心等待',
    '请问还有其他问题吗？',
    '祝您生活愉快，再见！',
  ])

  // Computed
  const unreadCount = computed(() => {
    let count = 0
    for (const s of sessions.value) {
      count += s.unread || 0
    }
    return count
  })

  // API Methods
  async function fetchSessions(filters = {}) {
    const params = new URLSearchParams(filters)
    const data = await request.get(`/agent/sessions?${params}`)
    sessions.value = data || []
    return sessions.value
  }

  async function fetchSessionMessages(sessionId) {
    return await request.get(`/agent/sessions/${sessionId}/messages`)
  }

  async function replyToSession(sessionId, message) {
    return await request.post(`/agent/sessions/${sessionId}/reply`, { message })
  }

  async function quickReplyToSession(sessionId, message) {
    return await request.post(`/agent/sessions/${sessionId}/quick-reply`, {
      message,
      agent_id: 'current-agent',
    })
  }

  async function takeoverSession(sessionId, agentId) {
    return await request.post(`/agent/sessions/${sessionId}/takeover`, {
      agent_id: agentId || 'current-agent',
    })
  }

  async function closeSession(sessionId) {
    await request.post(`/agent/sessions/${sessionId}/close`)
    await fetchSessions({ status: 'active' })
  }

  // WebSocket Methods
  function connectToSession(sessionId) {
    if (ws.value) {
      ws.value.close()
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}/ws/chat/${sessionId}`

    const socket = new WebSocket(wsUrl)

    socket.onopen = () => {
      wsConnected.value = true
      startHeartbeat(socket)
    }

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        handleWSMessage(data)
      } catch (e) {
        console.error('WS parse error:', e)
      }
    }

    socket.onclose = () => {
      wsConnected.value = false
      ws.value = null
    }

    socket.onerror = () => {
      wsConnected.value = false
    }

    ws.value = socket
    currentSession.value = sessionId
    return socket
  }

  function handleWSMessage(data) {
    if (data.type === 'pong') return

    if (data.type === 'message') {
      console.log('New message from WS:', data)
    } else if (data.type === 'notification') {
      console.log('Notification:', data.content)
    }
  }

  function sendWSMessage(sessionId, message) {
    if (ws.value && ws.value.readyState === WebSocket.OPEN) {
      ws.value.send(JSON.stringify(message))
    }
  }

  function disconnect() {
    if (ws.value) {
      ws.value.close()
      ws.value = null
      wsConnected.value = false
    }
  }

  function startHeartbeat(socket) {
    const interval = setInterval(() => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ type: 'heartbeat' }))
      } else {
        clearInterval(interval)
      }
    }, 20000)
  }

  return {
    sessions,
    activeSessions,
    currentSession,
    ws,
    wsConnected,
    quickReplies,
    unreadCount,
    fetchSessions,
    fetchSessionMessages,
    replyToSession,
    quickReplyToSession,
    takeoverSession,
    closeSession,
    connectToSession,
    sendWSMessage,
    disconnect,
  }
})
