export default function VendorCard({ assessment, onClick, style }) {
  const vendor = assessment.vendor || {}
  const signal = assessment.risk_signal || {}
  const band = assessment.risk_band || 'LOW'
  const score = signal.total_score ?? 0

  const borderClass = {
    HIGH: 'risk-border-high',
    MEDIUM: 'risk-border-medium',
    LOW: 'risk-border-low',
  }[band]

  const badgeClass = {
    HIGH: 'risk-badge-high',
    MEDIUM: 'risk-badge-medium',
    LOW: 'risk-badge-low',
  }[band]

  const scoreColor = {
    HIGH: 'text-[#B8432B]',
    MEDIUM: 'text-[#D97E4A]',
    LOW: 'text-[#708A74]',
  }[band]

  return (
    <div
      id={`vendor-card-${vendor.vendor_id}`}
      className={`glass-card ${borderClass} px-4 py-3.5 cursor-pointer animate-fade-in`}
      onClick={onClick}
      style={style}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && onClick()}
    >
      <div className="flex items-start justify-between mb-2">
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-bold text-[#2E2925] truncate">{vendor.vendor_name}</h3>
          <p className="text-xs text-[#5A524C] mt-0.5">
            {vendor.city}, {vendor.state} &middot; {vendor.commodity}
          </p>
        </div>
        <span className={`risk-badge ${badgeClass} ml-2 flex-shrink-0`}>{band}</span>
      </div>

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div>
            <span className={`text-xl font-black ${scoreColor}`}>{score.toFixed(1)}</span>
            <span className="text-xs text-[#5A524C] ml-1">/100</span>
          </div>
          {/* Mini bar chart for the 4 risk categories */}
          <div className="flex items-end gap-0.5 h-5">
            <MiniBar value={signal.weather_risk?.score} max={30} color="bg-[#708A74]" />
            <MiniBar value={signal.news_risk?.score} max={30} color="bg-[#D97E4A]" />
            <MiniBar value={signal.commodity_risk?.score} max={20} color="bg-[#C95A3E]" />
            <MiniBar value={signal.historical_risk?.score} max={20} color="bg-[#B8432B]" />
          </div>
        </div>
        <div className="text-xs font-semibold text-[#5A524C]">
          PO: ₹{(vendor.open_po_value_inr / 100000).toFixed(1)}L
        </div>
      </div>
    </div>
  )
}

function MiniBar({ value = 0, max = 30, color }) {
  const pct = Math.min((value / max) * 100, 100)
  return (
    <div className="w-1.5 bg-[#DED9CE] rounded-full h-5 overflow-hidden flex flex-col-reverse">
      <div
        className={`${color} rounded-full transition-all duration-500`}
        style={{ height: `${pct}%` }}
      />
    </div>
  )
}
