import { useEffect, useState } from "react"
import { supabase } from "../supabaseClient"

export function useRole(session) {
  const [role, setRole] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!session) { setLoading(false); return }

    supabase
      .from("profiles")
      .select("role")
      .eq("id", session.user.id)
      .single()
      .then(({ data }) => {
        setRole(data?.role || null)
        setLoading(false)
      })
  }, [session])

  return { role, loading }
}