const STAGES = [
  { key: 'QUEUED', label: 'Queued' },
  { key: 'INGESTING', label: 'Ingesting' },
  { key: 'MONITORING', label: 'Monitoring' },
  { key: 'PREDICTING', label: 'Predicting' },
  { key: 'DRAFTING', label: 'Drafting' },
  { key: 'COMPLETE', label: 'Complete' },
]

export default function ScanStatusBar({ status }) {
  const currentIdx = STAGES.findIndex((s) => s.key === status.status)
  const progress = Math.max(0, ((currentIdx + 1) / STAGES.length) * 100)

  return (
    <div id="scan-status-bar" className="glass-card p-5 animate-fade-in">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-bold text-[#2E2925]">Scan Progress</h3>
        <div className="flex items-center gap-2 text-xs text-[#5A524C]">
          {status.vendor_count && <span>{status.vendor_count} vendors</span>}
          {status.elapsed_seconds && <span>&middot; {status.elapsed_seconds}s</span>}
        </div>
      </div>

      {/* Progress Bar */}
      <div className="progress-bar-track mb-4 bg-retro-bone">
        <div
          className="progress-bar-fill bg-[#C95A3E]"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Stage Indicators */}
      <div className="flex justify-between">
        {STAGES.map((stage, idx) => {
          const isActive = idx === currentIdx
          const isDone = idx < currentIdx
          return (
            <div key={stage.key} className="flex flex-col items-center gap-1.5">
              <div
                className={`w-3 h-3 rounded-full border-2 transition-all duration-300 ${
                  isDone
                    ? 'bg-[#C95A3E] border-[#C95A3E]'
                    : isActive
                    ? 'bg-[#C95A3E] border-[#C95A3E] shadow-md shadow-[#C95A3E]/30 animate-pulse-slow'
                    : 'bg-transparent border-[#C7C0B4]'
                }`}
              />
              <span
                className={`text-[10px] font-bold transition-colors duration-300 ${
                  isDone ? 'text-[#C95A3E]' : isActive ? 'text-[#C95A3E] font-extrabold' : 'text-[#8F877B]'
                }`}
              >
                {stage.label}
              </span>
            </div>
          )
        })}
      </div>

      {/* Stage Message */}
      {status.stage_message && (
        <p className="text-xs text-[#5A524C] mt-3 text-center italic">{status.stage_message}</p>
      )}
    </div>
  )
}
