import {
  PolarAngleAxis,
  PolarGrid,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
} from 'recharts'
import type { DomainProgress } from '../../types'

interface Props {
  domains: DomainProgress[]
}

export function AccuracyRadar({ domains }: Props) {
  const data = domains.map((d) => ({
    domain: d.domain_label.split(' ').slice(0, 3).join(' '),
    accuracy: Math.round(d.accuracy * 100),
    fullMark: 100,
  }))

  return (
    <div className="bg-white rounded-2xl border border-gray-100 p-6">
      <h3 className="text-sm font-semibold text-gray-700 mb-4">Accuracy by Domain</h3>
      <ResponsiveContainer width="100%" height={260}>
        <RadarChart data={data}>
          <PolarGrid stroke="#e5e7eb" />
          <PolarAngleAxis dataKey="domain" tick={{ fontSize: 11, fill: '#6b7280' }} />
          <Radar
            name="Accuracy"
            dataKey="accuracy"
            stroke="#3b82f6"
            fill="#3b82f6"
            fillOpacity={0.2}
          />
          <Tooltip formatter={(val) => [`${val}%`, 'Accuracy']} />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  )
}
