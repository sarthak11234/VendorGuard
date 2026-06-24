import { useState } from 'react'

export default function ScanTrigger({ onTrigger, isScanning }) {
  const [input, setInput] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!input.trim() && !isScanning) {
      // Trigger with empty input to use default CSV fallback
      onTrigger('', '')
      return
    }
    const val = input.trim()
    if (val.startsWith('http://') || val.startsWith('https://')) {
      onTrigger(val, '')
    } else {
      onTrigger('', val)
    }
  }

  return (
    <form onSubmit={handleSubmit} id="scan-trigger-form" className="glass-card p-5">
      <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-end">
        <div className="flex-1 w-full">
          <label htmlFor="vendor-source-input" className="block text-xs font-bold text-[#5A524C] uppercase tracking-wider mb-2">
            Vendor Register Source
          </label>
          <input
            id="vendor-source-input"
            type="text"
            placeholder="Google Sheet URL, CSV path, or leave empty for demo data"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isScanning}
            className="w-full px-4 py-2.5 rounded-xl bg-white border border-[#DED9CE]
                       text-[#2E2925] text-sm placeholder-[#8F877B]
                       focus:outline-none focus:ring-2 focus:ring-[#C95A3E]/30 focus:border-[#C95A3E]
                       disabled:opacity-50 transition-all duration-200"
          />
        </div>
        <button
          id="scan-trigger-button"
          type="submit"
          disabled={isScanning}
          className="btn-primary whitespace-nowrap flex items-center gap-2"
        >
          {isScanning ? (
            <>
              <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
              Scanning...
            </>
          ) : (
            <>
              <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
              </svg>
              Run Risk Scan
            </>
          )}
        </button>
      </div>
    </form>
  )
}
