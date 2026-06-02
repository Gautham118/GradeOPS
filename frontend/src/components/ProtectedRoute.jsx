import { Navigate } from "react-router-dom"
import { useSession } from "../hooks/useSession"
import { useRole } from "../hooks/useRole"

export function ProtectedRoute({ children, requiredRole }) {
  const { session, loading: sessionLoading } = useSession()
  const { role, loading: roleLoading } = useRole(session)

  if (sessionLoading || roleLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-950">
        <div className="text-white text-lg animate-pulse">Loading...</div>
      </div>
    )
  }

  if (!session) return <Navigate to="/login" replace />
  if (requiredRole && role !== requiredRole) return <Navigate to="/dashboard" replace />

  return children
}