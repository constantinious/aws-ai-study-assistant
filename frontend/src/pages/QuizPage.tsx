import { useEffect, useState } from 'react'
import { fetchQuestion, submitAnswer } from '../api/quiz'
import { AnswerFeedback } from '../components/Quiz/AnswerFeedback'
import { QuestionCard } from '../components/Quiz/QuestionCard'
import type { AnswerResult, QuestionResponse } from '../types'

type PageState = 'loading' | 'question' | 'submitting' | 'feedback' | 'error'

export function QuizPage() {
  const [state, setState] = useState<PageState>('loading')
  const [question, setQuestion] = useState<QuestionResponse | null>(null)
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null)
  const [result, setResult] = useState<AnswerResult | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    loadQuestion()
  }, [])

  async function loadQuestion() {
    setState('loading')
    setSelectedIndex(null)
    setResult(null)
    setError('')
    try {
      const q = await fetchQuestion()
      setQuestion(q)
      setState('question')
    } catch {
      setError('Failed to load question. Please try again.')
      setState('error')
    }
  }

  async function handleSubmit() {
    if (selectedIndex === null || !question) return
    setState('submitting')
    try {
      const res = await submitAnswer({
        question_id: question.id,
        answer_token: question.answer_token,
        selected_index: selectedIndex,
        domain: question.domain,
        question_text: question.question_text,
        options: question.options,
      })
      setResult(res)
      setState('feedback')
    } catch {
      setError('Failed to submit answer. Please try again.')
      setState('error')
    }
  }

  if (state === 'loading') {
    return (
      <div className="flex flex-col items-center justify-center py-24 gap-4">
        <div className="animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full" />
        <p className="text-sm text-gray-500">Generating your question…</p>
      </div>
    )
  }

  if (state === 'error') {
    return (
      <div className="max-w-xl mx-auto py-12 px-4 text-center">
        <p className="text-red-600 mb-4">{error}</p>
        <button
          onClick={loadQuestion}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700"
        >
          Try again
        </button>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <div className="mb-6">
        <h1 className="text-xl font-bold text-gray-900">Practice Question</h1>
        <p className="text-sm text-gray-500">AWS Certified AI Practitioner (AIF-C01)</p>
      </div>

      <div className="space-y-4">
        {question && (
          <QuestionCard
            question={question}
            selectedIndex={selectedIndex}
            onSelect={setSelectedIndex}
            disabled={state === 'submitting' || state === 'feedback'}
          />
        )}

        {state === 'question' && (
          <button
            onClick={handleSubmit}
            disabled={selectedIndex === null}
            className="w-full bg-blue-600 text-white rounded-xl py-2.5 text-sm font-medium hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            Submit answer
          </button>
        )}

        {state === 'submitting' && (
          <div className="flex items-center justify-center gap-2 py-4">
            <div className="animate-spin h-5 w-5 border-2 border-blue-600 border-t-transparent rounded-full" />
            <p className="text-sm text-gray-500">Generating explanation…</p>
          </div>
        )}

        {state === 'feedback' && result && question && (
          <AnswerFeedback result={result} question={question} onNext={loadQuestion} />
        )}
      </div>
    </div>
  )
}
