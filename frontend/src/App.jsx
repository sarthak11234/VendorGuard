import { useState, useEffect, useCallback, useRef } from 'react'
import ScanTrigger from './components/ScanTrigger'
import ScanStatusBar from './components/ScanStatusBar'
import VendorHeatMap from './components/VendorHeatMap'
import VendorDetailModal from './components/VendorDetailModal'
import AlertsPanel from './components/AlertsPanel'
import Home from './components/Home'

function App() {
  const [activeTab, setActiveTab] = useState('home')
  const [scanId, setScanId] = useState(null)
  const [scanStatus, setScanStatus] = useState(null)
  const [vendors, setVendors] = useState([])
  const [alerts, setAlerts] = useState([])
  const [activeVendorId, setActiveVendorId] = useState(null)
  const [isScanning, setIsScanning] = useState(false)
  const [error, setError] = useState(null)
  const pollRef = useRef(null)

  // Trigger a new scan
  const handleTriggerScan = useCallback(async (sheetUrl, csvPath) => {
    setError(null)
    setVendors([])
    setAlerts([])
    setScanStatus(null)
    setActiveVendorId(null)

    try {
      const body = {}
      if (sheetUrl) body.sheet_url = sheetUrl
      if (csvPath) body.csv_path = csvPath

      const res = await fetch('/api/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      if (!res.ok) throw new Error(`Scan trigger failed (${res.status})`)

      const data = await res.json()
      setScanId(data.scan_id)
      setIsScanning(true)
    } catch (err) {
      setError(err.message)
    }
  }, [])

  // Poll scan status
  useEffect(() => {
    if (!scanId || !isScanning) return

    const poll = async () => {
      try {
        const res = await fetch(`/api/scan/${scanId}`)
        if (!res.ok) throw new Error(`Status poll failed (${res.status})`)
        const data = await res.json()
        setScanStatus(data)

        if (data.status === 'COMPLETE') {
          setIsScanning(false)
          // Fetch results
          const [vendorsRes, alertsRes] = await Promise.all([
            fetch('/api/vendors'),
            fetch('/api/alerts'),
          ])
          if (vendorsRes.ok) setVendors(await vendorsRes.json())
          if (alertsRes.ok) setAlerts(await alertsRes.json())
        } else if (data.status === 'FAILED') {
          setIsScanning(false)
          setError(data.error || 'Scan failed.')
        }
      } catch (err) {
        setError(err.message)
        setIsScanning(false)
      }
    }

    poll() // Immediately poll once
    pollRef.current = setInterval(poll, 3000)
    return () => clearInterval(pollRef.current)
  }, [scanId, isScanning])

  // Find details for selected vendor
  const selectedAssessment = vendors.find(
    (v) => v.vendor?.vendor_id === activeVendorId
  )
  const selectedDraft = alerts.find(
    (a) => a.vendor_id === activeVendorId
  )

  // Summary stats
  const highCount = vendors.filter((v) => v.risk_band === 'HIGH').length
  const mediumCount = vendors.filter((v) => v.risk_band === 'MEDIUM').length
  const lowCount = vendors.filter((v) => v.risk_band === 'LOW').length

  return (
    <div className="min-h-screen flex flex-col bg-[#FAF7F2] text-[#2E2925]">
      {/* Header */}
      <header className="border-b border-[#DED9CE] px-6 py-4 bg-white/70 backdrop-blur-md sticky top-0 z-50">
        <div className="w-full flex items-center justify-between">
          <div className="flex items-center gap-6">
            <div onClick={() => setActiveTab('home')} className="flex items-center cursor-pointer hover:opacity-95 transition-all">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 160" className="h-11 w-auto">
                {/* The 'Guard' Architectural Arch */}
                <path d="M 30,30 Q 80,0 130,30 L 115,45 Q 80,20 45,45 Z" fill="#81B29A" />
                
                {/* The Base Shield / Gateway */}
                <polygon points="30,40 80,135 130,40 112,40 80,100 48,40" fill="#3D3835" />

                {/* The 'Vendor' V-Shape moving through the gateway */}
                <polygon points="55,30 80,95 105,30 85,30 80,70 75,30" fill="#E07A5F" />
                
                {/* Typography */}
                <text x="160" y="95" fontFamily="'Helvetica Neue', Helvetica, Arial, sans-serif" fontWeight="800" fontSize="64" fill="#3D3835" letterSpacing="-2">Vendor</text>
                <text x="395" y="95" fontFamily="'Helvetica Neue', Helvetica, Arial, sans-serif" fontWeight="300" fontSize="64" fill="#81B29A" letterSpacing="-1">Guard</text>
                
                {/* Tagline */}
                <text x="165" y="125" fontFamily="'Helvetica Neue', Helvetica, Arial, sans-serif" fontWeight="500" fontSize="16" fill="#E07A5F" letterSpacing="4">THE AI TRUST GATEWAY</text>
              </svg>
            </div>

            {/* Navigation Switcher */}
            <nav className="flex items-center gap-1 bg-[#F5F2EB] p-1 rounded-xl border border-[#DED9CE]">
              <button
                onClick={() => setActiveTab('home')}
                className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${
                  activeTab === 'home'
                    ? 'bg-[#C95A3E] text-white shadow-md shadow-[#C95A3E]/10'
                    : 'text-[#5A524C] hover:text-[#2E2925]'
                }`}
              >
                Home
              </button>
              <button
                onClick={() => setActiveTab('dashboard')}
                className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${
                  activeTab === 'dashboard'
                    ? 'bg-[#C95A3E] text-white shadow-md shadow-[#C95A3E]/10'
                    : 'text-[#5A524C] hover:text-[#2E2925]'
                }`}
              >
                Dashboard
              </button>
            </nav>
          </div>

          {scanStatus?.status === 'COMPLETE' && (
            <div className="text-xs text-[#5A524C] hidden sm:block">
              Last scan: {new Date(scanStatus.completed_at).toLocaleString()} &middot; {scanStatus.elapsed_seconds}s
            </div>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 px-6 py-8">
        <div className="w-full">
          {activeTab === 'home' ? (
            <Home onNavigate={setActiveTab} />
          ) : (
            <div className="space-y-6 animate-fade-in">
              {/* Scan Trigger */}
              <ScanTrigger onTrigger={handleTriggerScan} isScanning={isScanning} />

              {/* Error Banner */}
              {error && (
                <div className="glass-card border-red-500/50 bg-red-900/20 px-4 py-3 flex items-center gap-3">
                  <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5 text-red-400 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
                  <span className="text-red-300 text-sm">{error}</span>
                  <button onClick={() => setError(null)} className="ml-auto text-red-400 hover:text-red-300 text-xs">Dismiss</button>
                </div>
              )}

              {/* Scan Progress Bar */}
              {scanStatus && isScanning && (
                <ScanStatusBar status={scanStatus} />
              )}

              {/* Stats Row */}
              {vendors.length > 0 && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 animate-fade-in">
                  <StatCard label="Total Vendors" value={vendors.length} color="text-[#2E2925]" />
                  <StatCard label="High Risk" value={highCount} color="text-[#B8432B]" />
                  <StatCard label="Medium Risk" value={mediumCount} color="text-[#D97E4A]" />
                  <StatCard label="Low Risk" value={lowCount} color="text-[#708A74]" />
                </div>
              )}

              {/* Vendor Grid + Alerts */}
              {vendors.length > 0 && (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-fade-in">
                  <div className="lg:col-span-2">
                    <VendorHeatMap vendors={vendors} onSelect={setActiveVendorId} />
                  </div>
                  <div>
                    <AlertsPanel alerts={alerts} onSelect={setActiveVendorId} />
                  </div>
                </div>
              )}

              {/* Empty State */}
              {!isScanning && vendors.length === 0 && !error && (
                <div className="text-center py-24 animate-fade-in">
                  <div className="w-16 h-16 rounded-full bg-[#F5F2EB] border border-[#DED9CE] flex items-center justify-center mx-auto mb-5">
                    <svg xmlns="http://www.w3.org/2000/svg" className="w-8 h-8 text-[#8F877B]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                    </svg>
                  </div>
                  <h2 className="text-xl font-bold text-[#2E2925] mb-2">Ready to Scan</h2>
                  <p className="text-sm text-[#5A524C] max-w-md mx-auto">
                    Enter your vendor register URL above and trigger a scan to analyze supply chain risk across weather, news, commodity, and historical data sources.
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </main>

      {/* Vendor Detail Modal */}
      {activeVendorId && selectedAssessment && (
        <VendorDetailModal
          assessment={selectedAssessment}
          draft={selectedDraft}
          onClose={() => setActiveVendorId(null)}
        />
      )}

      {/* Footer */}
      <footer className="border-t border-[#DED9CE] px-6 py-3">
        <div className="w-full flex items-center justify-between text-xs text-[#8F877B]">
          <span>VendorGuard v1.0 &middot; Kaggle AI Agents Capstone 2026</span>
          <span>Powered by Google ADK + Gemini</span>
        </div>
      </footer>
    </div>
  )
}

function StatCard({ label, value, color }) {
  return (
    <div className="glass-card px-4 py-3">
      <div className="text-xs text-[#5A524C] uppercase tracking-wider mb-1">{label}</div>
      <div className={`text-2xl font-bold ${color}`}>{value}</div>
    </div>
  )
}

export default App
