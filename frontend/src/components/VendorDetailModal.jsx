import { useState } from 'react'

export default function VendorDetailModal({ assessment, draft, onClose }) {
  const vendor = assessment.vendor || {}
  const signal = assessment.risk_signal || {}
  const band = assessment.risk_band || 'LOW'
  const [copied, setCopied] = useState(null)

  const bandColors = {
    HIGH: { text: 'text-[#B8432B]', bg: 'bg-[#B8432B]', ring: 'ring-[#B8432B]/30' },
    MEDIUM: { text: 'text-[#D97E4A]', bg: 'bg-[#D97E4A]', ring: 'ring-[#D97E4A]/30' },
    LOW: { text: 'text-[#708A74]', bg: 'bg-[#708A74]', ring: 'ring-[#708A74]/30' },
  }
  const colors = bandColors[band] || bandColors.LOW

  const riskSources = [
    { key: 'weather_risk', label: 'Weather', icon: '☁', max: 30, barColor: 'bg-[#708A74]', data: signal.weather_risk },
    { key: 'news_risk', label: 'News / Disruptions', icon: '📰', max: 30, barColor: 'bg-[#D97E4A]', data: signal.news_risk },
    { key: 'commodity_risk', label: 'Commodity Trends', icon: '📈', max: 20, barColor: 'bg-[#C95A3E]', data: signal.commodity_risk },
    { key: 'historical_risk', label: 'Historical Performance', icon: '📊', max: 20, barColor: 'bg-[#B8432B]', data: signal.historical_risk },
  ]

  const handleCopy = async (text, label) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopied(label)
      setTimeout(() => setCopied(null), 2000)
    } catch {
      // Fallback for older browsers
      const ta = document.createElement('textarea')
      ta.value = text
      document.body.appendChild(ta)
      ta.select()
      document.execCommand('copy')
      document.body.removeChild(ta)
      setCopied(label)
      setTimeout(() => setCopied(null), 2000)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="px-6 py-5 border-b border-[#DED9CE]">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-lg font-bold text-[#2E2925]">{vendor.vendor_name}</h2>
              <p className="text-sm text-[#5A524C] mt-0.5">
                {vendor.vendor_id} &middot; {vendor.city}, {vendor.state}
              </p>
            </div>
            <button
              id="modal-close-button"
              onClick={onClose}
              className="text-[#5A524C] hover:text-[#2E2925] transition-colors p-1"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
          </div>

          {/* Score Summary */}
          <div className="mt-4 flex items-center gap-4">
            <div className={`text-3xl font-extrabold ${colors.text}`}>
              {signal.total_score?.toFixed(1)}
            </div>
            <div>
              <span className={`risk-badge risk-badge-${band.toLowerCase()}`}>{band} RISK</span>
              <p className="text-xs text-[#5A524C] mt-1">
                {assessment.action_summary}
              </p>
            </div>
          </div>
        </div>

        {/* Risk Breakdown */}
        <div className="px-6 py-5 space-y-4">
          <h3 className="text-xs font-bold text-[#5A524C] uppercase tracking-wider">Risk Breakdown</h3>
          {riskSources.map((src) => (
            <RiskBar key={src.key} source={src} />
          ))}
        </div>

        {/* Vendor Info */}
        <div className="px-6 py-4 border-t border-[#DED9CE]">
          <h3 className="text-xs font-bold text-[#5A524C] uppercase tracking-wider mb-3">Vendor Details</h3>
          <div className="grid grid-cols-2 gap-x-6 gap-y-2 text-sm">
            <InfoRow label="Commodity" value={vendor.commodity} />
            <InfoRow label="Open PO Value" value={`INR ${(vendor.open_po_value_inr || 0).toLocaleString()}`} />
            <InfoRow label="Lead Time" value={`${vendor.lead_time_days} days`} />
            <InfoRow label="On-time Delivery" value={`${vendor.historical_ontime_pct}%`} />
            {vendor.contact_whatsapp && <InfoRow label="WhatsApp" value={vendor.contact_whatsapp} />}
            {vendor.backup_vendor_id && <InfoRow label="Backup Vendor" value={vendor.backup_vendor_id} />}
          </div>
        </div>

        {/* Procurement Draft */}
        {draft && (
          <div className="px-6 py-5 border-t border-[#DED9CE] bg-[#FAF0E8]">
            <h3 className="text-xs font-bold text-[#B8432B] uppercase tracking-wider mb-3">
              AI Procurement Draft
            </h3>
            <div className="space-y-4">
              <div>
                <p className="text-xs text-[#5A524C] font-semibold mb-1">Risk Summary</p>
                <p className="text-sm text-[#2E2925] font-medium">{draft.risk_summary}</p>
              </div>
              <div>
                <p className="text-xs text-[#5A524C] font-semibold mb-1">Recommended Action</p>
                <p className="text-sm text-[#2E2925] font-medium">{draft.recommended_action}</p>
              </div>
              {draft.alternate_supplier && (
                <div>
                  <p className="text-xs text-[#5A524C] font-semibold mb-1">Alternate Supplier</p>
                  <p className="text-sm text-[#708A74] font-bold">{draft.alternate_supplier} ({draft.alternate_supplier_id})</p>
                </div>
              )}

              {/* Draft PO */}
              <div className="mt-3 p-3 rounded-xl bg-white border border-[#DED9CE]">
                <div className="flex items-center justify-between mb-2 pb-2 border-b border-[#FAF7F2]">
                  <span className="text-xs font-bold text-[#5A524C] uppercase">Draft Purchase Order</span>
                  <button
                    id="copy-po-button"
                    onClick={() => handleCopy(draft.draft_po_text, 'po')}
                    className="btn-ghost text-xs px-2.5 py-1"
                  >
                    {copied === 'po' ? 'Copied!' : 'Copy'}
                  </button>
                </div>
                <pre className="text-xs text-[#2E2925] whitespace-pre-wrap font-mono leading-relaxed bg-[#FAF7F2]/60 p-2.5 rounded-lg">{draft.draft_po_text}</pre>
              </div>

              {/* WhatsApp Message */}
              <div className="p-3 rounded-xl bg-white border border-[#DED9CE]">
                <div className="flex items-center justify-between mb-2 pb-2 border-b border-[#FAF7F2]">
                  <span className="text-xs font-bold text-[#5A524C] uppercase">WhatsApp Alert</span>
                  <button
                    id="copy-whatsapp-button"
                    onClick={() => handleCopy(draft.whatsapp_message, 'wa')}
                    className="btn-ghost text-xs px-2.5 py-1"
                  >
                    {copied === 'wa' ? 'Copied!' : 'Copy'}
                  </button>
                </div>
                <pre className="text-xs text-[#2E2925] whitespace-pre-wrap font-mono leading-relaxed bg-[#FAF7F2]/60 p-2.5 rounded-lg">{draft.whatsapp_message}</pre>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

function RiskBar({ source }) {
  const { label, icon, max, barColor, data } = source
  if (!data) return null
  const pct = Math.min((data.score / max) * 100, 100)

  return (
    <div>
      <div className="flex items-center justify-between mb-1.5">
        <span className="text-sm font-semibold text-[#2E2925]">
          <span className="mr-1.5">{icon}</span>
          {label}
        </span>
        <span className="text-sm font-bold text-[#2E2925]">
          {data.score?.toFixed(1)} <span className="text-[#8F877B] font-normal">/ {max}</span>
        </span>
      </div>
      <div className="progress-bar-track">
        <div className={`progress-bar-fill ${barColor}`} style={{ width: `${pct}%` }} />
      </div>
      {data.evidence && (
        <p className="text-[11px] text-[#5A524C] mt-1 leading-relaxed">{data.evidence}</p>
      )}
    </div>
  )
}

function InfoRow({ label, value }) {
  return (
    <div>
      <span className="text-xs text-[#8F877B] font-bold">{label}</span>
      <p className="text-[#2E2925] text-sm font-medium mt-0.5">{value}</p>
    </div>
  )
}
