import { useState, useEffect, useCallback } from "react"
import { useNavigate } from "react-router-dom"
import { useSession } from "../hooks/useSession"
import { useRealtimeGrades } from "../hooks/useRealtimeGrades"
import { GradeCard } from "../components/GradeCard"
import { KeyboardHints } from "../components/KeyboardHints"
import { supabase } from "../supabaseClient"

const API = import.meta.env.VITE_API_BASE_URL

export default function ReviewQueue() {
  const { session } = useSession()
  const navigate = useNavigate()
  const [exams, setExams] = useState([])
  const [selectedExamId, setSelectedExamId] = useState("")
  const [currentIdx, setCurrentIdx] = useState(0)
  const [overrideScore, setOverrideScore] = useState(null)
  const { grades, setGrades, loading } = useRealtimeGrades(selectedExamId)

  const token = session?.access_token
  const currentGrade = grades[currentIdx] || null

  // Load exams for selector
  useEffect(() => {
    if (!token) return
    fetch(`${API}/exams/`, {
      headers: { "Authorization": `Bearer ${token}` }
    })
      .then(r => r.json())
      .then(data => { setExams(data); if (data.length) setSelectedExamId(data[0].id) })
  }, [token])

  const handleAction = useCallback(async (action, score = null, note = "") => {
    if (!currentGrade) return
    const body = { status: action }
    if (action === "overridden" && score !== null) {
      body.ta_score = score
      body.ta_note = note
    }

    await fetch(`${API}/grades/${currentGrade.id}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify(body)
    })

    // Remove graded card from queue
    setGrades(prev => prev.filter(g => g.id !== currentGrade.id))
    setCurrentIdx(0)
    setOverrideScore(null)
  }, [currentGrade, token, setGrades])

  // Keyboard shortcuts
  useEffect(() => {
    const handleKey = (e) => {
      if (!currentGrade) return
      if (e.key === "a" || e.key === "A") handleAction("approved")
      if (e.key === "f" || e.key === "F") handleAction("flagged")
      if (e.key >= "0" && e.key <= "9") setOverrideScore(parseInt(e.key))
      if (e.key === "Enter" && overrideScore !== null) {
        handleAction("overridden", overrideScore)
      }
    }
    window.addEventListener("keydown", handleKey)
    return () => window.removeEventListener("keydown", handleKey)
  }, [currentGrade, overrideScore, handleAction])

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <nav className="border-b border-gray-800 px-8 py-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button onClick={() => navigate("/dashboard")} className="text-gray-400 hover:text-white">← Back</button>
          <h1 className="text-xl font-bold">Review Queue</h1>
        </div>

        <div className="flex items-center gap-3">
          <select
            className="bg-gray-800 border border-gray-700 text-white rounded-xl px-4 py-2 text-sm"
            value={selectedExamId}
            onChange={e => { setSelectedExamId(e.target.value); setCurrentIdx(0) }}
          >
            {exams.map(e => (
              <option key={e.id} value={e.id}>{e.title}</option>
            ))}
          </select>
          <span className="bg-blue-900 text-blue-300 text-xs px-3 py-1 rounded-full font-medium">
            {grades.length} pending
          </span>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto px-8 py-8">
        {loading ? (
          <div className="text-center text-gray-400 py-20 animate-pulse">Loading grades...</div>
        ) : grades.length === 0 ? (
          <div className="text-center py-20">
            <div className="text-6xl mb-4">🎉</div>
            <p className="text-xl text-white font-semibold">Queue is empty</p>
            <p className="text-gray-400 mt-2">All grades have been reviewed, or upload an exam to get started.</p>
            <button
              onClick={() => navigate("/upload")}
              className="mt-6 bg-blue-600 hover:bg-blue-500 text-white px-6 py-2.5 rounded-xl text-sm transition"
            >Upload an exam</button>
          </div>
        ) : (
          <div>
            {/* Progress bar */}
            <div className="mb-6">
              <div className="flex justify-between text-sm text-gray-400 mb-1">
                <span>Reviewing {currentIdx + 1} of {grades.length}</span>
                <span>{grades.length} remaining</span>
              </div>
              <div className="w-full bg-gray-800 rounded-full h-1.5">
                <div
                  className="bg-blue-500 h-1.5 rounded-full transition-all"
                  style={{ width: `${((currentIdx) / grades.length) * 100}%` }}
                />
              </div>
            </div>

            {currentGrade && (
              <GradeCard
                grade={currentGrade}
                onApprove={(id) => handleAction("approved")}
                onOverride={(id, score, note) => handleAction("overridden", score, note)}
                onFlag={(id) => handleAction("flagged")}
              />
            )}

            {/* Navigation between cards */}
            {grades.length > 1 && (
              <div className="flex justify-center gap-3 mt-6">
                <button
                  onClick={() => setCurrentIdx(Math.max(0, currentIdx - 1))}
                  disabled={currentIdx === 0}
                  className="px-4 py-2 bg-gray-800 rounded-xl text-sm disabled:opacity-30"
                >← Previous</button>
                <button
                  onClick={() => setCurrentIdx(Math.min(grades.length - 1, currentIdx + 1))}
                  disabled={currentIdx === grades.length - 1}
                  className="px-4 py-2 bg-gray-800 rounded-xl text-sm disabled:opacity-30"
                >Next →</button>
              </div>
            )}
          </div>
        )}
      </div>

      <KeyboardHints />
    </div>
  )
}