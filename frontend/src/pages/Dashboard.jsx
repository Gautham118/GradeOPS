import { useNavigate } from "react-router-dom"
import { useSession } from "../hooks/useSession"
import { useRole } from "../hooks/useRole"
import { supabase } from "../supabaseClient"

export default function Dashboard() {
  const { session } = useSession()
  const { role } = useRole(session)
  const navigate = useNavigate()

  const handleLogout = async () => {
    await supabase.auth.signOut()
    navigate("/login")
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <nav className="border-b border-gray-800 px-8 py-4 flex items-center justify-between">
        <h1 className="text-xl font-bold text-white">GradeOps</h1>
        <div className="flex items-center gap-4">
          <span className={`text-xs px-3 py-1 rounded-full font-medium ${
            role === "instructor"
              ? "bg-purple-900 text-purple-300"
              : "bg-blue-900 text-blue-300"
          }`}>{role}</span>
          <button
            onClick={handleLogout}
            className="text-gray-400 hover:text-white text-sm transition"
          >Sign out</button>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-8 py-16">
        <h2 className="text-3xl font-bold mb-2">
          Welcome back{session?.user?.email ? `, ${session.user.email.split("@")[0]}` : ""}
        </h2>
        <p className="text-gray-400 mb-10">What would you like to do?</p>

        <div className="grid grid-cols-2 gap-6">
          {role === "instructor" && (
            <button
              onClick={() => navigate("/upload")}
              className="bg-gray-800 hover:bg-gray-750 border border-gray-700 hover:border-purple-500 
                         rounded-2xl p-8 text-left transition group"
            >
              <div className="text-4xl mb-4">📄</div>
              <h3 className="text-xl font-semibold mb-1 group-hover:text-purple-300">Upload Exam</h3>
              <p className="text-gray-400 text-sm">Create rubric and upload student PDFs for grading</p>
            </button>
          )}

          <button
            onClick={() => navigate("/review")}
            className="bg-gray-800 hover:bg-gray-750 border border-gray-700 hover:border-blue-500 
                       rounded-2xl p-8 text-left transition group"
          >
            <div className="text-4xl mb-4">✅</div>
            <h3 className="text-xl font-semibold mb-1 group-hover:text-blue-300">Review Queue</h3>
            <p className="text-gray-400 text-sm">Review and approve AI-generated grades</p>
          </button>
        </div>
      </div>
    </div>
  )
}