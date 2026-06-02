import React from "react"
import ReactDOM from "react-dom/client"
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import { ProtectedRoute } from "./components/ProtectedRoute"
import Login from "./pages/Login"
import Dashboard from "./pages/Dashboard"
import ExamUpload from "./pages/ExamUpload"
import ReviewQueue from "./pages/ReviewQueue"
import "./index.css"

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={
          <ProtectedRoute><Dashboard /></ProtectedRoute>
        } />
        <Route path="/upload" element={
          <ProtectedRoute requiredRole="instructor"><ExamUpload /></ProtectedRoute>
        } />
        <Route path="/review" element={
          <ProtectedRoute><ReviewQueue /></ProtectedRoute>
        } />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
)