import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { ProtectedRoute } from './components/Auth/ProtectedRoute'
import { LoginPage } from './components/Auth/LoginPage'
import { SignUpPage } from './components/Auth/SignUpPage'
import { Navbar } from './components/Layout/Navbar'
import { DashboardPage } from './pages/DashboardPage'
import { QuizPage } from './pages/QuizPage'

function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main>{children}</main>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignUpPage />} />
        <Route
          path="/quiz"
          element={
            <ProtectedRoute>
              <AppLayout>
                <QuizPage />
              </AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <AppLayout>
                <DashboardPage />
              </AppLayout>
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/quiz" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
