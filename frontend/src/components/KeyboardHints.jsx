export function KeyboardHints() {
  return (
    <div className="fixed bottom-6 right-6 bg-gray-800 border border-gray-700 
                    rounded-xl p-4 text-xs text-gray-400 space-y-1 shadow-xl">
      <p className="text-gray-300 font-semibold mb-2 text-sm">Keyboard Shortcuts</p>
      <p><kbd className="bg-gray-700 px-2 py-0.5 rounded text-green-400">A</kbd> Approve</p>
      <p><kbd className="bg-gray-700 px-2 py-0.5 rounded text-yellow-400">F</kbd> Flag</p>
      <p><kbd className="bg-gray-700 px-2 py-0.5 rounded text-blue-400">0-9</kbd> Set score</p>
      <p><kbd className="bg-gray-700 px-2 py-0.5 rounded text-purple-400">Enter</kbd> Confirm override</p>
    </div>
  )
}