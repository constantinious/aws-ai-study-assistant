import type { UserProgressSummary } from '../types'
import { apiClient } from './client'

export async function fetchProgress(): Promise<UserProgressSummary> {
  const { data } = await apiClient.get<UserProgressSummary>('/progress')
  return data
}
