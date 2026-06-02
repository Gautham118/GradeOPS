import { Auth } from "@supabase/auth-ui-react"
import { ThemeSupa } from "@supabase/auth-ui-shared"
import { supabase } from "../supabaseClient"
import { useNavigate } from "react-router-dom"
import { useEffect } from "react"
import { useSession } from "../hooks/useSession"

export default function Login() {
  const { session } = useSession()
  const navigate = useNavigate()

  useEffect(() => {
    if (session) navigate("/dashboard")
  }, [session])

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white">GradeOps</h1>
          <p className="text-gray-400 mt-2">AI-powered exam grading pipeline</p>
        </div>
        <div className="bg-gray-800 rounded-2xl p-6 border border-gray-700">
          <Auth
            supabaseClient={supabase}
            appearance={{ theme: ThemeSupa }}
            theme="dark"
            providers={[]}
            redirectTo={window.location.origin + "/dashboard"}
          />
        </div>
      </div>
    </div>
  )
}