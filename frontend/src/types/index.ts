export type ExamDomain =
  | 'ai_ml_fundamentals'
  | 'generative_ai_fundamentals'
  | 'foundation_models'
  | 'responsible_ai'
  | 'security_governance'

export const DOMAIN_LABELS: Record<ExamDomain, string> = {
  ai_ml_fundamentals: 'Fundamentals of AI and ML',
  generative_ai_fundamentals: 'Fundamentals of Generative AI',
  foundation_models: 'Applications of Foundation Models',
  responsible_ai: 'Guidelines for Responsible AI',
  security_governance: 'Security, Compliance, and Governance',
}

export interface QuestionResponse {
  id: string
  domain: ExamDomain
  domain_label: string
  question_text: string
  options: string[]
  answer_token: string
}

export interface AnswerSubmission {
  question_id: string
  answer_token: string
  selected_index: number
  domain: ExamDomain
  question_text: string
  options: string[]
}

export interface SourceCitation {
  text: string
  source: string
}

export interface AnswerResult {
  question_id: string
  correct: boolean
  correct_index: number
  selected_index: number
  explanation: string
  citations: SourceCitation[]
}

export interface DomainProgress {
  domain: ExamDomain
  domain_label: string
  correct_count: number
  total_count: number
  accuracy: number
  last_answered_at: string | null
}

export interface HistoryEntry {
  question_id: string
  domain: ExamDomain
  correct: boolean
  answered_at: string
}

export interface UserProgressSummary {
  domains: DomainProgress[]
  overall_accuracy: number
  total_answered: number
  current_streak: number
  recent_history: HistoryEntry[]
}
