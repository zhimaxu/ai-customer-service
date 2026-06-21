import request from './request'

export function getOverview() {
  return request.get('/stats/overview')
}

export function getChatStats(period) {
  return request.get('/stats/chat', { params: { period: period || 'day' } })
}

export function getSatisfactionStats() {
  return request.get('/stats/satisfaction')
}

export function getEfficiencyStats() {
  return request.get('/stats/efficiency')
}

export function getAllStats(period) {
  return request.get('/stats/all', { params: { period: period || 'day' } })
}
