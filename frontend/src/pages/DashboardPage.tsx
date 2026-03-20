import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchProgress } from '../api/progress'
import { AccuracyRadar } from '../components/Dashboard/AccuracyRadar'
import { DomainScoreCard } from '../components/Dashboard/DomainScoreCard'
import type { UserProgressSummary } from '../types'

export function DashboardPage() {
  const [summary, setSummary] = useState<UserProgressSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchProgress()
      .then(setSummary)
      .catch(() => setError('Failed to load progress.'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-24">
        <div className="animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full" />
      </div>
    )
  }

  if (error || !summary) {
    return (
      <div className="text-center py-12 text-red-600">{error || 'No data available.'}</div>
    )
  }

  const overallPct = Math.round(summary.overall_accuracy * 100)

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-8">
      <div>
        <h1 className="text-xl font-bold text-gray-900">Your Progress</h1>
        <p className="text-sm text-gray-500">AIF-C01 exam readiness overview</p>
      </div>

      {/* Top stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white rounded-xl border border-gray-100 p-4 text-center">
          <p className="text-3xl font-bold text-gray-900">{summary.total_answered}</p>
          <p className="text-xs text-gray-500 mt-1">Questions answered</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-100 p-4 text-center">
          <p className="text-3xl font-bold text-blue-600">{overallPct}%</p>
          <p className="text-xs text-gray-500 mt-1">Overall accuracy</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-100 p-4 text-center">
          <p className="text-3xl font-bold text-orange-500">{summary.current_streak}</p>
          <p className="text-xs text-gray-500 mt-1">Current streak</p>
        </div>
      </div>

      {/* Domain scores */}
      <div>
        <h2 className="text-sm font-semibold text-gray-700 mb-3">Domain Breakdown</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {summary.domains.map((d) => (
            <DomainScoreCard key={d.domain} domain={d} />
          ))}
        </div>
      </div>

      {/* Radar chart */}
      <AccuracyRadar domains={summary.domains} />

      {/* CTA */}
      {summary.total_answered === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-500 mb-4">No questions answered yet. Start practising!</p>
          <Link
            to="/quiz"
            className="bg-blue-600 text-white px-6 py-2.5 rounded-xl text-sm font-medium hover:bg-blue-700 transition-colors"
          >
            Start quiz
          </Link>
        </div>
      ) : (
        <div className="text-center">
          <Link
            to="/quiz"
            className="bg-blue-600 text-white px-6 py-2.5 rounded-xl text-sm font-medium hover:bg-blue-700 transition-colors"
          >
            Continue practising
          </Link>
        </div>
      )}
    </div>
  )
}
