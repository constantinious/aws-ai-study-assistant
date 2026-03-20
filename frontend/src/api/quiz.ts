import type { AnswerResult, AnswerSubmission, ExamDomain, QuestionResponse } from '../types'
import { apiClient } from './client'

export async function fetchQuestion(domain?: ExamDomain): Promise<QuestionResponse> {
  const params = domain ? { domain } : {}
  const { data } = await apiClient.get<QuestionResponse>('/quiz/question', { params })
  return data
}

export async function submitAnswer(submission: AnswerSubmission): Promise<AnswerResult> {
  const { data } = await apiClient.post<AnswerResult>('/quiz/answer', submission)
  return data
}
