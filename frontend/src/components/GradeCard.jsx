import React from 'react'

// Crop image + AI score + breakdown accordion + action buttons
export default function GradeCard({ grade, onApprove, onOverride, onFlag }) {
  return (
    <div className="grade-card">
      {/* Implementation details based on CLAUDE.md interface */}
      <h3>Student: {grade?.submissions?.student_name}</h3>
      <p>AI Score: {grade?.ai_score} / {grade?.max_marks}</p>
    </div>
  )
}
