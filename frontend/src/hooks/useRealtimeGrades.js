import { useEffect, useState } from "react"
import { supabase } from "../supabaseClient"

export function useRealtimeGrades(examId) {
  const [grades, setGrades] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!examId) return

    // Initial fetch
    supabase
      .from("grades")
      .select("*, submissions(student_name)")
      .eq("exam_id", examId)
      .eq("status", "pending_review")
      .order("created_at", { ascending: true })
      .then(({ data, error }) => {
        if (!error) setGrades(data || [])
        setLoading(false)
      })

    // Live subscription — new grades arrive from grading worker
    const channel = supabase
      .channel(`grades-${examId}`)
      .on("postgres_changes", {
        event: "INSERT",
        schema: "public",
        table: "grades",
        filter: `exam_id=eq.${examId}`
      }, (payload) => {
        if (payload.new.status === "pending_review") {
          setGrades(prev => [...prev, payload.new])
        }
      })
      .subscribe()

    return () => supabase.removeChannel(channel)
  }, [examId])

  return { grades, setGrades, loading }
}