import type { DomainProgress } from '../../types'

interface Props {
  domain: DomainProgress
}

function accuracyColor(accuracy: number): string {
  if (accuracy >= 0.75) return 'text-green-600 bg-green-50 border-green-200'
  if (accuracy >= 0.5) return 'text-yellow-600 bg-yellow-50 border-yellow-200'
  return 'text-red-600 bg-red-50 border-red-200'
}

function accuracyBar(accuracy: number): string {
  if (accuracy >= 0.75) return 'bg-green-500'
  if (accuracy >= 0.5) return 'bg-yellow-400'
  return 'bg-red-400'
}

export function DomainScoreCard({ domain }: Props) {
  const pct = Math.round(domain.accuracy * 100)

  return (
    <div className={`rounded-xl border p-4 ${accuracyColor(domain.accuracy)}`}>
      <p className="text-xs font-medium uppercase tracking-wide opacity-70 mb-1">
        {domain.domain_label}
      </p>
      <div className="flex items-end justify-between mb-2">
        <span className="text-2xl font-bold">{domain.total_count > 0 ? `${pct}%` : '—'}</span>
        <span className="text-xs opacity-70">
          {domain.correct_count}/{domain.total_count} correct
        </span>
      </div>
      <div className="h-1.5 bg-black/10 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all ${accuracyBar(domain.accuracy)}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}
