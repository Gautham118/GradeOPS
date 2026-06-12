import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { useSession } from "../hooks/useSession"
import { RubricEditor } from "../components/RubricEditor"

const API = import.meta.env.VITE_API_BASE_URL

export default function ExamUpload() {
  const { session } = useSession()
  const navigate = useNavigate()

  const [title, setTitle] = useState("")
  const [subject, setSubject] = useState("")
  const [rubricJson, setRubricJson] = useState({ questions: [] })
  const [files, setFiles] = useState([])
  const [studentNames, setStudentNames] = useState("")
  const [loading, setLoading] = useState(false)
  const [step, setStep] = useState(1)  // 1=exam details, 2=upload PDFs
  const [createdExamId, setCreatedExamId] = useState(null)
  const [message, setMessage] = useState("")
  const [uploaded, setUploaded] = useState(false)
  const [fileInputKey, setFileInputKey] = useState(0)

  const token = session?.access_token

  const createExam = async () => {
    if (!title || !rubricJson.questions.length) {
      setMessage("Please fill in exam title and at least one question.")
      return
    }
    setLoading(true)
    try {
      const res = await fetch(`${API}/exams/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ title, subject, rubric_json: rubricJson })
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail)
      setCreatedExamId(data.id)
      setMessage(`Exam created! ID: ${data.id}`)
      setStep(2)
    } catch (err) {
      setMessage(`Error: ${err.message}`)
    }
    setLoading(false)
  }

  const uploadSubmissions = async () => {
    if (!files.length || !studentNames.trim()) {
      setMessage("Please select PDF files and enter student names.")
      return
    }
    setLoading(true)
    try {
      const formData = new FormData()
      formData.append("exam_id", createdExamId)
      formData.append("student_names", studentNames)
      Array.from(files).forEach(f => formData.append("files", f))

      const res = await fetch(`${API}/submissions/bulk`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${token}` },
        body: formData
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail)
      setMessage(`✅ ${data.message}. Processing started!`)
      setUploaded(true)
    } catch (err) {
      setMessage(`Error: ${err.message}`)
    }
    setLoading(false)
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <nav className="border-b border-gray-800 px-8 py-4 flex items-center gap-4">
        <button onClick={() => navigate("/dashboard")} className="text-gray-400 hover:text-white">← Back</button>
        <h1 className="text-xl font-bold">Upload Exam</h1>
      </nav>

      <div className="max-w-3xl mx-auto px-8 py-10">
        {/* Step indicator */}
        <div className="flex items-center gap-3 mb-10">
          {["Exam Details & Rubric", "Upload PDFs"].map((label, i) => (
            <div key={i} className="flex items-center gap-2">
              <div className={`w-7 h-7 rounded-full flex items-center justify-center text-sm font-bold
                ${step > i + 1 ? "bg-green-600" : step === i + 1 ? "bg-blue-600" : "bg-gray-700"}`}>
                {step > i + 1 ? "✓" : i + 1}
              </div>
              <span className={`text-sm ${step === i + 1 ? "text-white" : "text-gray-500"}`}>{label}</span>
              {i < 1 && <div className="w-8 h-px bg-gray-700 mx-1" />}
            </div>
          ))}
        </div>

        {/* Step 1 */}
        {step === 1 && (
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm text-gray-400 block mb-1">Exam title *</label>
                <input
                  className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-2.5 text-white"
                  placeholder="Mid Semester Exam"
                  value={title}
                  onChange={e => setTitle(e.target.value)}
                />
              </div>
              <div>
                <label className="text-sm text-gray-400 block mb-1">Subject</label>
                <input
                  className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-2.5 text-white"
                  placeholder="Physics"
                  value={subject}
                  onChange={e => setSubject(e.target.value)}
                />
              </div>
            </div>

            <div>
              <label className="text-sm text-gray-400 block mb-3">Rubric builder</label>
              <RubricEditor onChange={setRubricJson} />
            </div>

            <button
              onClick={createExam}
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-50 
                         text-white py-3 rounded-xl font-medium transition"
            >{loading ? "Creating..." : "Create Exam & Continue →"}</button>
          </div>
        )}

        {/* Step 2 */}
        {step === 2 && (
          <div className="space-y-6">
            <div className="bg-green-900/30 border border-green-700 rounded-xl p-4 text-green-300 text-sm">
              ✅ Exam created — ID: <code className="text-xs">{createdExamId}</code>
            </div>

            <div>
              <label className="text-sm text-gray-400 block mb-1">Student names</label>
              <input
                className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-2.5 text-white"
                placeholder="Alice (one name per PDF file)"
                value={studentNames}
                onChange={e => setStudentNames(e.target.value)}
              />
              <p className="text-xs text-gray-500 mt-1">
                Single file: just one name. Multiple files: separate with commas (Alice, Bob, Charlie)
              </p>
            </div>

            <div>
              <label className="text-sm text-gray-400 block mb-1">PDF files</label>
              <input
                key={fileInputKey}
                type="file"
                accept=".pdf"
                multiple
                onChange={e => setFiles(e.target.files)}
                className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-2.5 
                           text-white file:mr-4 file:py-1 file:px-3 file:rounded-lg 
                           file:border-0 file:bg-blue-600 file:text-white file:text-sm cursor-pointer"
              />
              {files.length > 0 && (
                <p className="text-xs text-gray-400 mt-1">{files.length} file(s) selected</p>
              )}
            </div>

            {!uploaded ? (
              <button
                onClick={uploadSubmissions}
                disabled={loading}
                className="w-full bg-purple-600 hover:bg-purple-500 disabled:opacity-50 
                           text-white py-3 rounded-xl font-medium transition"
              >{loading ? "Uploading..." : "Upload & Start Grading 🚀"}</button>
            ) : (
              <div className="flex gap-3">
                <button
                  onClick={() => {
                    setUploaded(false)
                    setFiles([])
                    setStudentNames("")
                    setMessage("")
                    setFileInputKey(k => k + 1)
                  }}
                  className="flex-1 border border-blue-500 text-blue-400 hover:bg-blue-900/30 
                             py-3 rounded-xl font-medium transition text-sm"
                >+ Upload More PDFs to This Exam</button>
                <button
                  onClick={() => navigate("/review")}
                  className="flex-1 bg-green-700 hover:bg-green-600 
                             text-white py-3 rounded-xl font-medium transition text-sm"
                >Go to Review Queue →</button>
              </div>
            )}
          </div>
        )}

        {message && (
          <div className={`mt-4 p-4 rounded-xl text-sm border ${
            message.startsWith("Error")
              ? "bg-red-900/30 border-red-700 text-red-300"
              : "bg-blue-900/30 border-blue-700 text-blue-300"
          }`}>{message}</div>
        )}
      </div>
    </div>
  )
}