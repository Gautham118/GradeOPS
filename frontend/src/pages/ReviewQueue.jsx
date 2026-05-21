import React, { useEffect, useState } from "react"
// TA grading dashboard (main HITL interface)
export default function ReviewQueue({ currentGrade, handleAction, setOverrideScore, overrideScore }) {
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (!currentGrade) return
      if (e.key === "a" || e.key === "A") handleAction("approve")
      if (e.key === "f" || e.key === "F") handleAction("flag")
      if (e.key >= "0" && e.key <= "9") setOverrideScore(parseInt(e.key))
      if (e.key === "Enter" && overrideScore !== null) handleAction("override", overrideScore)
    }
    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [currentGrade, overrideScore])

  return <div>Review Queue</div>
}
