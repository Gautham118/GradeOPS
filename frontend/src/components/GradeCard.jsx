import { useEffect, useState } from "react"
import { supabase } from "../supabaseClient"

export function GradeCard({ grade, onApprove, onOverride, onFlag }) {
  const [cropUrl, setCropUrl] = useState(null)
  const [overrideScore, setOverrideScore] = useState("")
  const [note, setNote] = useState("")
  const [showOverride, setShowOverride] = useState(false)

  useEffect(() => {
    if (!grade.crop_url) return
    supabase.storage
      .from("answer-crops")
      .createSignedUrl(grade.crop_url, 3600)
      .then(({ data }) => { if (data) setCropUrl(data.signedUrl) })
  }, [grade.crop_url])

  const studentName = grade.submissions?.student_name || "Unknown"
  const plagiarism = grade.plagiarism_flag

  return (
    <div className={`bg-gray-800 rounded-2xl border ${plagiarism ? "border-red-500" : "border-gray-700"} overflow-hidden`}>
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-3 bg-gray-750 border-b border-gray-700">
        <div>
          <p className="text-white font-semibold">{studentName}</p>
          <p className="text-gray-400 text-xs">Question {grade.question_id}</p>
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold text-white">
            {grade.ai_score ?? "—"}
            <span className="text-gray-400 text-base font-normal">/{grade.max_marks}</span>
          </p>
          {plagiarism && (
            <span className="text-xs bg-red-900 text-red-300 px-2 py-0.5 rounded-full">
              ⚠ Plagiarism flagged
            </span>
          )}
        </div>
      </div>

      <div className="p-5 grid grid-cols-2 gap-5">
        {/* Left — crop image */}
        <div>
          <p className="text-xs text-gray-400 uppercase tracking-wide mb-2">Answer scan</p>
          {cropUrl ? (
            <img src={cropUrl} alt="Answer crop" className="rounded-lg border border-gray-600 w-full" />
          ) : (
            <div className="rounded-lg border border-gray-600 h-40 flex items-center justify-center text-gray-500 text-sm">
              {grade.crop_url ? "Loading image..." : "No image yet"}
            </div>
          )}
          <div className="mt-3">
            <p className="text-xs text-gray-400 uppercase tracking-wide mb-1">Transcription</p>
            <p className="text-gray-300 text-sm bg-gray-900 rounded-lg p-3 leading-relaxed">
              {grade.transcription || "Pending..."}
            </p>
          </div>
        </div>

        {/* Right — AI breakdown */}
        <div>
          <p className="text-xs text-gray-400 uppercase tracking-wide mb-2">AI breakdown</p>
          <div className="space-y-2 mb-3">
            {(grade.breakdown || []).map((b, i) => (
              <div key={i} className={`rounded-lg p-2.5 text-xs border ${b.awarded
                ? "bg-green-900/30 border-green-700/50 text-green-300"
                : "bg-red-900/30 border-red-700/50 text-red-300"}`}>
                <div className="flex justify-between font-medium mb-0.5">
                  <span>{b.condition}</span>
                  <span>{b.marks_given}/{b.marks_given > 0 ? b.marks_given : "0"}</span>
                </div>
                <p className="text-gray-400">{b.reason}</p>
              </div>
            ))}
          </div>
          {grade.justification && (
            <p className="text-gray-400 text-xs bg-gray-900 rounded-lg p-3">
              {grade.justification}
            </p>
          )}
        </div>
      </div>

      {/* Override input */}
      {showOverride && (
        <div className="px-5 pb-3 flex gap-2">
          <input
            type="number"
            className="w-24 bg-gray-700 text-white rounded-lg px-3 py-2 text-sm"
            placeholder="Score"
            value={overrideScore}
            onChange={e => setOverrideScore(e.target.value)}
            min={0} max={grade.max_marks}
          />
          <input
            className="flex-1 bg-gray-700 text-white rounded-lg px-3 py-2 text-sm"
            placeholder="Note (optional)"
            value={note}
            onChange={e => setNote(e.target.value)}
          />
          <button
            onClick={() => { onOverride(grade.id, parseInt(overrideScore), note); setShowOverride(false) }}
            className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg text-sm"
          >Confirm</button>
        </div>
      )}

      {/* Action buttons */}
      <div className="flex gap-2 px-5 pb-5">
        <button
          onClick={() => onApprove(grade.id)}
          className="flex-1 bg-green-700 hover:bg-green-600 text-white py-2 rounded-xl text-sm font-medium transition"
        >✓ Approve (A)</button>
        <button
          onClick={() => setShowOverride(!showOverride)}
          className="flex-1 bg-blue-700 hover:bg-blue-600 text-white py-2 rounded-xl text-sm font-medium transition"
        >✎ Override</button>
        <button
          onClick={() => onFlag(grade.id)}
          className="flex-1 bg-yellow-700 hover:bg-yellow-600 text-white py-2 rounded-xl text-sm font-medium transition"
        >⚑ Flag (F)</button>
      </div>
    </div>
  )
}