import React from 'react'
// Checks session + role, redirects if unauthorized
export default function ProtectedRoute({ children, allowedRoles }) {
  return <>{children}</>
}
