import type { QuestionResponse } from '../../types'

interface Props {
  question: QuestionResponse
  selectedIndex: number | null
  onSelect: (index: number) => void
  disabled: boolean
}

export function QuestionCard({ question, selectedIndex, onSelect, disabled }: Props) {
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
      <div className="flex items-center gap-2 mb-4">
        <span className="text-xs font-medium bg-blue-100 text-blue-700 px-2.5 py-1 rounded-full">
          {question.domain_label}
        </span>
      </div>

      <p className="text-gray-900 font-medium text-base leading-relaxed mb-6">
        {question.question_text}
      </p>

      <div className="space-y-3">
        {question.options.map((option, index) => {
          const isSelected = selectedIndex === index
          return (
            <button
              key={index}
              onClick={() => !disabled && onSelect(index)}
              disabled={disabled}
              className={[
                'w-full text-left px-4 py-3 rounded-xl border text-sm transition-all',
                isSelected
                  ? 'border-blue-500 bg-blue-50 text-blue-800'
                  : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50 text-gray-700',
                disabled && !isSelected ? 'opacity-60 cursor-default' : 'cursor-pointer',
              ].join(' ')}
            >
              {option}
            </button>
          )
        })}
      </div>
    </div>
  )
}
