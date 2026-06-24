export default function AlertsPanel({ alerts, onSelect }) {
  if (!alerts || alerts.length === 0) {
    return (
      <div>
        <h2 className="text-sm font-bold text-[#5A524C] uppercase tracking-wider mb-3">
          Action Alerts
        </h2>
        <div className="glass-card px-4 py-6 text-center">
          <div className="w-10 h-10 rounded-full bg-[#EAEFEA] border border-[#708A74]/20 flex items-center justify-center mx-auto mb-3">
            <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5 text-[#708A74]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M22 11.08V12a10 10 0 11-5.93-9.14"/>
              <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
          </div>
          <p className="text-sm text-[#5A524C]">No high-risk alerts</p>
          <p className="text-xs text-[#8F877B] mt-1">All vendors within acceptable thresholds</p>
        </div>
      </div>
    )
  }

  return (
    <div>
      <h2 className="text-sm font-bold text-[#B8432B] uppercase tracking-wider mb-3 flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-[#B8432B] animate-pulse-slow" />
        Action Alerts ({alerts.length})
      </h2>
      <div className="space-y-3">
        {alerts.map((draft, idx) => (
          <AlertItem
            key={draft.vendor_id}
            draft={draft}
            index={idx}
            onClick={() => onSelect(draft.vendor_id)}
          />
        ))}
      </div>
    </div>
  )
}

function AlertItem({ draft, index, onClick }) {
  return (
    <div
      id={`alert-item-${draft.vendor_id}`}
      className="glass-card risk-border-high px-4 py-3 cursor-pointer animate-fade-in"
      style={{ animationDelay: `${index * 80}ms` }}
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && onClick()}
    >
      <div className="flex items-start justify-between mb-1.5">
        <div>
          <h3 className="text-sm font-bold text-[#2E2925]">{draft.vendor_name}</h3>
          <span className="risk-badge risk-badge-high text-[10px] mt-1 inline-block">{draft.urgency}</span>
        </div>
        <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4 text-[#5A524C] flex-shrink-0 mt-1" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="9 18 15 12 9 6"/>
        </svg>
      </div>
      <p className="text-xs text-[#5A524C] line-clamp-2">{draft.risk_summary}</p>
      {draft.alternate_supplier && (
        <p className="text-xs text-[#708A74] font-bold mt-1.5">
          Alt: {draft.alternate_supplier}
        </p>
      )}
    </div>
  )
}
