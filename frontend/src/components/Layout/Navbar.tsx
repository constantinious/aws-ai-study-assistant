import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'

export function Navbar() {
  const { email, signOut } = useAuth()
  const location = useLocation()

  const linkClass = (path: string) =>
    [
      'text-sm font-medium px-3 py-1.5 rounded-lg transition-colors',
      location.pathname === path
        ? 'bg-blue-50 text-blue-700'
        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100',
    ].join(' ')

  return (
    <nav className="border-b border-gray-100 bg-white px-4 py-3 flex items-center justify-between">
      <div className="flex items-center gap-1">
        <span className="text-lg font-bold text-gray-900 mr-4">AIF Study</span>
        <Link to="/quiz" className={linkClass('/quiz')}>
          Quiz
        </Link>
        <Link to="/dashboard" className={linkClass('/dashboard')}>
          Dashboard
        </Link>
      </div>
      <div className="flex items-center gap-3">
        <span className="text-xs text-gray-400 hidden sm:block">{email}</span>
        <button
          onClick={signOut}
          className="text-sm text-gray-500 hover:text-gray-900 transition-colors"
        >
          Sign out
        </button>
      </div>
    </nav>
  )
}
