import { useState } from "react"

export function RubricEditor({ onChange }) {
  const [questions, setQuestions] = useState([
    { id: "q1", text: "", max_marks: 10, conditions: [{ description: "", marks: 0 }] }
  ])

  const updateQuestion = (qIdx, field, value) => {
    const updated = questions.map((q, i) =>
      i === qIdx ? { ...q, [field]: value } : q
    )
    setQuestions(updated)
    onChange({ questions: updated })
  }

  const updateCondition = (qIdx, cIdx, field, value) => {
    const updated = questions.map((q, i) => {
      if (i !== qIdx) return q
      const conditions = q.conditions.map((c, j) =>
        j === cIdx ? { ...c, [field]: value } : c
      )
      return { ...q, conditions }
    })
    setQuestions(updated)
    onChange({ questions: updated })
  }

  const addQuestion = () => {
    const updated = [...questions, {
      id: `q${questions.length + 1}`,
      text: "", max_marks: 10,
      conditions: [{ description: "", marks: 0 }]
    }]
    setQuestions(updated)
    onChange({ questions: updated })
  }

  const addCondition = (qIdx) => {
    const updated = questions.map((q, i) =>
      i === qIdx
        ? { ...q, conditions: [...q.conditions, { description: "", marks: 0 }] }
        : q
    )
    setQuestions(updated)
    onChange({ questions: updated })
  }

  const removeCondition = (qIdx, cIdx) => {
    const updated = questions.map((q, i) =>
      i === qIdx
        ? { ...q, conditions: q.conditions.filter((_, j) => j !== cIdx) }
        : q
    )
    setQuestions(updated)
    onChange({ questions: updated })
  }

  return (
    <div className="space-y-6">
      {questions.map((q, qIdx) => (
        <div key={qIdx} className="bg-gray-800 rounded-xl p-5 border border-gray-700">
          <div className="flex gap-3 mb-4">
            <input
              className="flex-1 bg-gray-700 text-white rounded-lg px-3 py-2 text-sm"
              placeholder={`Question ${qIdx + 1} text`}
              value={q.text}
              onChange={e => updateQuestion(qIdx, "text", e.target.value)}
            />
            <input
              type="number"
              className="w-24 bg-gray-700 text-white rounded-lg px-3 py-2 text-sm"
              placeholder="Max marks"
              value={q.max_marks}
              onChange={e => updateQuestion(qIdx, "max_marks", parseInt(e.target.value))}
            />
          </div>

          <p className="text-xs text-gray-400 mb-2 uppercase tracking-wide">Rubric conditions</p>
          {q.conditions.map((c, cIdx) => (
            <div key={cIdx} className="flex gap-2 mb-2">
              <input
                className="flex-1 bg-gray-700 text-white rounded-lg px-3 py-2 text-sm"
                placeholder="Condition description"
                value={c.description}
                onChange={e => updateCondition(qIdx, cIdx, "description", e.target.value)}
              />
              <input
                type="number"
                className="w-20 bg-gray-700 text-white rounded-lg px-3 py-2 text-sm"
                placeholder="Marks"
                value={c.marks}
                onChange={e => updateCondition(qIdx, cIdx, "marks", parseInt(e.target.value))}
              />
              <button
                onClick={() => removeCondition(qIdx, cIdx)}
                className="text-red-400 hover:text-red-300 px-2 text-lg"
              >×</button>
            </div>
          ))}

          <button
            onClick={() => addCondition(qIdx)}
            className="text-xs text-blue-400 hover:text-blue-300 mt-1"
          >+ Add condition</button>
        </div>
      ))}

      <button
        onClick={addQuestion}
        className="w-full border border-dashed border-gray-600 text-gray-400 
                   hover:border-blue-500 hover:text-blue-400 rounded-xl py-3 text-sm transition"
      >+ Add Question</button>
    </div>
  )
}