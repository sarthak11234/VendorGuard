import VendorCard from './VendorCard'

export default function VendorHeatMap({ vendors, onSelect }) {
  // Sort: HIGH first, then MEDIUM, then LOW. Within each band, by score desc.
  const sorted = [...vendors].sort((a, b) => {
    const bandOrder = { HIGH: 0, MEDIUM: 1, LOW: 2 }
    const bandA = bandOrder[a.risk_band] ?? 2
    const bandB = bandOrder[b.risk_band] ?? 2
    if (bandA !== bandB) return bandA - bandB
    return (b.risk_signal?.total_score || 0) - (a.risk_signal?.total_score || 0)
  })

  return (
    <div>
      <h2 className="text-sm font-semibold text-[#5A524C] uppercase tracking-wider mb-3">
        Vendor Risk Heatmap
      </h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {sorted.map((assessment, idx) => (
          <VendorCard
            key={assessment.vendor?.vendor_id || idx}
            assessment={assessment}
            onClick={() => onSelect(assessment.vendor?.vendor_id)}
            style={{ animationDelay: `${idx * 60}ms` }}
          />
        ))}
      </div>
    </div>
  )
}
