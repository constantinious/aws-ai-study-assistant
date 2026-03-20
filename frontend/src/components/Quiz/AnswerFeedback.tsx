import { useState } from 'react'
import type { AnswerResult, QuestionResponse } from '../../types'

interface Props {
  result: AnswerResult
  question: QuestionResponse
  onNext: () => void
}

export function AnswerFeedback({ result, question, onNext }: Props) {
  const [showCitations, setShowCitations] = useState(false)

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 space-y-4">
      <div
        className={[
          'flex items-center gap-3 p-4 rounded-xl',
          result.correct ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800',
        ].join(' ')}
      >
        <span className="text-2xl">{result.correct ? '✓' : '✗'}</span>
        <div>
          <p className="font-semibold">{result.correct ? 'Correct!' : 'Not quite'}</p>
          {!result.correct && (
            <p className="text-sm mt-0.5">
              Correct answer: <strong>{question.options[result.correct_index]}</strong>
            </p>
          )}
        </div>
      </div>

      <div className="text-sm text-gray-700 leading-relaxed">
        <p className="font-medium text-gray-900 mb-1">Explanation</p>
        <p>{result.explanation}</p>
      </div>

      {result.citations.length > 0 && (
        <div>
          <button
            onClick={() => setShowCitations(!showCitations)}
            className="text-xs text-blue-600 hover:underline"
          >
            {showCitations ? 'Hide' : 'Show'} source citations ({result.citations.length})
          </button>
          {showCitations && (
            <div className="mt-2 space-y-2">
              {result.citations.map((c, i) => (
                <div key={i} className="text-xs bg-gray-50 rounded-lg p-3 border border-gray-100">
                  <p className="text-gray-600 mb-1 font-medium truncate">{c.source}</p>
                  <p className="text-gray-500 line-clamp-2">{c.text}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      <button
        onClick={onNext}
        className="w-full bg-blue-600 text-white rounded-xl py-2.5 text-sm font-medium hover:bg-blue-700 transition-colors"
      >
        Next question
      </button>
    </div>
  )
}
