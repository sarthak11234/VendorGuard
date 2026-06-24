import { useState } from 'react'

export default function Home({ onNavigate }) {
  const [activeInstructionTab, setActiveInstructionTab] = useState(0)

  const instructions = [
    {
      step: "01",
      title: "Provide Vendor Registry",
      desc: "Enter a public Google Sheets URL or local CSV path. The registry must include fields like vendor_id, vendor_name, city, open_po_value_inr, and historical_ontime_pct.",
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6 text-[#708A74]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      )
    },
    {
      step: "02",
      title: "Activate AI Agent Scan",
      desc: "Click 'Analyze Risk' to trigger our 4-agent system. The coordinator orchestrates parallel worker agents to fetch weather, news, commodity trends, and logistics prices.",
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6 text-[#D97E4A]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
          <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      )
    },
    {
      step: "03",
      title: "Evaluate Risk Heatmap",
      desc: "Examine the color-coded interactive grid (Low, Medium, High risk bands) to instantly isolate which purchase orders and suppliers are at danger.",
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6 text-[#C95A3E]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 002 2h2a2 2 0 002-2z" />
        </svg>
      )
    },
    {
      step: "04",
      title: "Deploy Automated Actions",
      desc: "Open any card to view detailed risk factors, weather warnings, and copy ready-to-send WhatsApp messages or PO drafts to alternate suppliers.",
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6 text-[#B8432B]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
          <path strokeLinecap="round" strokeLinejoin="round" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
        </svg>
      )
    }
  ]

  const features = [
    {
      title: "Real-time Weather Risk",
      desc: "Connects with OpenWeatherMap to calculate weather scores (0-30 pts) for monsoon floodings, storms, and extreme heatwaves.",
      color: "border-[#708A74]/20 group-hover:border-[#708A74]/40",
      iconColor: "text-[#708A74] bg-[#708A74]/10"
    },
    {
      title: "Logistics Disruption News",
      desc: "Monitors Newscatcher feeds and web search logs for strike events, highway blockages, and industrial closures in India.",
      color: "border-[#D97E4A]/20 group-hover:border-[#D97E4A]/40",
      iconColor: "text-[#D97E4A] bg-[#D97E4A]/10"
    },
    {
      title: "Commodity Trends Analysis",
      desc: "Queries Google Trends indices for price spikes in key production raw materials (steel, copper, aluminum).",
      color: "border-[#C95A3E]/20 group-hover:border-[#C95A3E]/40",
      iconColor: "text-[#C95A3E] bg-[#C95A3E]/10"
    },
    {
      title: "Fuel Logistics Pricing",
      desc: "BS4 custom web-scraper parses diesel updates directly from PPAC India to evaluate freight pricing escalation.",
      color: "border-[#B8432B]/20 group-hover:border-[#B8432B]/40",
      iconColor: "text-[#B8432B] bg-[#B8432B]/10"
    }
  ]

  return (
    <div className="space-y-20 pb-20 animate-fade-in">
      {/* Hero Banner */}
      <section className="relative rounded-3xl overflow-hidden bg-white/60 border border-[#DED9CE] p-8 md:p-16 flex flex-col items-center text-center space-y-6 backdrop-blur-md">
        <div className="absolute inset-0 bg-gradient-to-tr from-[#C95A3E]/10 via-transparent to-[#708A74]/5 pointer-events-none" />
        
        {/* Badge */}
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#708A74]/10 border border-[#708A74]/20 text-xs font-semibold text-[#708A74] animate-pulse">
          <span className="w-1.5 h-1.5 rounded-full bg-[#708A74]" />
          System Active • Live Risk Feeds Connected
        </div>

        <h1 className="text-4xl md:text-6xl font-black tracking-tight max-w-4xl leading-tight text-[#2E2925]">
          AI-Powered Supply Chain <br />
          <span className="text-gradient">Risk Control</span> for SMEs
        </h1>

        <p className="text-[#5A524C] text-lg max-w-2xl mx-auto leading-relaxed">
          Empowering Indian SME manufacturers with real-time risk intelligence, multi-agent AI scanning, and automated procurement drafting to secure raw material supply.
        </p>

        <div className="pt-4 flex flex-col sm:flex-row gap-4 justify-center">
          <button
            onClick={() => onNavigate('dashboard')}
            className="px-8 py-3.5 rounded-xl bg-[#C95A3E] hover:bg-[#B34C32] text-white font-bold transition-all shadow-lg shadow-[#C95A3E]/20 flex items-center justify-center gap-2"
          >
            Open Dashboard
            <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
              <path strokeLinecap="round" strokeLinejoin="round" d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          </button>
          <a
            href="#instructions"
            className="px-8 py-3.5 rounded-xl bg-transparent border border-[#DED9CE] text-[#2E2925] hover:bg-[#F5F2EB] font-bold transition-all flex items-center justify-center gap-2"
          >
            How it Works
          </a>
        </div>
      </section>

      {/* About Section */}
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 glass-card p-8 flex flex-col justify-between relative overflow-hidden group">
          <div className="absolute right-0 bottom-0 translate-x-12 translate-y-12 opacity-5 pointer-events-none transition-transform duration-500 group-hover:scale-110">
            <svg xmlns="http://www.w3.org/2000/svg" className="w-96 h-96 text-[#F5F2EB]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.5">
              <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 12c0-1.232-.046-2.453-.138-3.662a4.006 4.006 0 00-3.7-3.7 48.678 48.678 0 00-7.324 0 4.006 4.006 0 00-3.7 3.7c-.017.22-.032.441-.046.662M19.5 12l3-3m-3 3l-3-3m-12 3c0 1.232.046 2.453.138 3.662a4.006 4.006 0 003.7 3.7 48.656 48.656 0 007.324 0 4.006 4.006 0 003.7-3.7c.017-.22.032-.441.046-.662M7.5 12l3 3m-3-3l-3 3m12-3l-3-3m-3 3l3 3" />
            </svg>
          </div>
          <div className="space-y-4">
            <h2 className="text-2xl font-bold tracking-tight text-[#2E2925]">Indian SME Focus</h2>
            <p className="text-[#5A524C] leading-relaxed text-base">
              Monsoon washouts, logistics strikes, and commodity volatility disproportionately hurt SME manufacturers.
              <strong> VendorGuard</strong> acts as a predictive firewall—fusing local operations data with real-time risk feeds to safeguard inventory pipelines.
            </p>
          </div>
          <div className="grid grid-cols-3 gap-4 pt-8">
            <div className="border-l-2 border-[#708A74] pl-3">
              <div className="text-xl font-bold text-[#2E2925]">Monsoon</div>
              <div className="text-xs text-[#8F877B]">Route Blockage Scan</div>
            </div>
            <div className="border-l-2 border-[#D97E4A] pl-3">
              <div className="text-xl font-bold text-[#2E2925]">Shortage</div>
              <div className="text-xs text-[#8F877B]">Price Trend Tracking</div>
            </div>
            <div className="border-l-2 border-[#B8432B] pl-3">
              <div className="text-xl font-bold text-[#2E2925]">Logistics</div>
              <div className="text-xs text-[#8F877B]">PPAC Scraped Fuel Impact</div>
            </div>
          </div>
        </div>

        <div className="glass-card p-8 flex flex-col justify-between">
          <div className="space-y-4">
            <h3 className="text-lg font-bold text-[#2E2925]">System Parameters</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 rounded-xl bg-[#FAF7F2] border border-[#DED9CE]">
                <span className="text-sm text-[#5A524C]">Scan Pipeline</span>
                <span className="text-xs font-semibold text-[#708A74] bg-[#708A74]/10 px-2.5 py-0.5 rounded-full border border-[#708A74]/20">6-Stage Live</span>
              </div>
              <div className="flex items-center justify-between p-3 rounded-xl bg-[#FAF7F2] border border-[#DED9CE]">
                <span className="text-sm text-[#5A524C]">Risk Threshold</span>
                <span className="text-xs font-semibold text-[#D97E4A] bg-[#D97E4A]/10 px-2.5 py-0.5 rounded-full border border-[#D97E4A]/20">Score &gt; 65 (HIGH)</span>
              </div>
              <div className="flex items-center justify-between p-3 rounded-xl bg-[#FAF7F2] border border-[#DED9CE]">
                <span className="text-sm text-[#5A524C]">Draft PO Output</span>
                <span className="text-xs font-semibold text-[#B8432B] bg-[#B8432B]/10 px-2.5 py-0.5 rounded-full border border-[#B8432B]/20">Gemini 1.5 Pro</span>
              </div>
            </div>
          </div>
          <button
            onClick={() => onNavigate('dashboard')}
            className="w-full mt-6 py-2.5 rounded-xl bg-transparent border border-[#DED9CE] text-[#2E2925] hover:bg-[#F5F2EB] text-sm font-semibold transition-all"
          >
            Manage Vendors &rarr;
          </button>
        </div>
      </section>

      {/* Features Grid */}
      <section className="space-y-8">
        <div className="text-center space-y-2">
          <h2 className="text-3xl font-extrabold tracking-tight">Real-Time Risk Monitoring</h2>
          <p className="text-[#5A524C] max-w-xl mx-auto text-sm">
            Our multi-agent system uses specialized tools to monitor external risk variables in real-time.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((f, i) => (
            <div key={i} className={`glass-card p-6 flex flex-col gap-4 border transition-all duration-300 group hover:-translate-y-1 ${f.color}`}>
              <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${f.iconColor}`}>
                {i === 0 && (
                  <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z" />
                  </svg>
                )}
                {i === 1 && (
                  <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                  </svg>
                )}
                {i === 2 && (
                  <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                )}
                {i === 3 && (
                  <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                )}
              </div>
              <div className="space-y-1">
                <h3 className="text-base font-bold text-[#2E2925]">{f.title}</h3>
                <p className="text-[#5A524C] text-xs leading-relaxed">{f.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Instructions & Interactive Tab */}
      <section id="instructions" className="space-y-8 w-full scroll-mt-24">
        <div className="text-center space-y-2">
          <h2 className="text-3xl font-extrabold tracking-tight">Step-by-Step Instructions</h2>
          <p className="text-[#5A524C] text-sm">
            Learn how to use VendorGuard to scan registers and analyze risk factors in seconds.
          </p>
        </div>

        {/* Tab Controls */}
        <div className="flex justify-center border-b border-[#DED9CE] pb-px">
          <div className="flex gap-2">
            {instructions.map((step, idx) => (
              <button
                key={idx}
                onClick={() => setActiveInstructionTab(idx)}
                className={`pb-4 px-4 text-sm font-semibold border-b-2 transition-all relative ${
                  activeInstructionTab === idx
                    ? 'border-[#C95A3E] text-[#C95A3E]'
                    : 'border-transparent text-[#8F877B] hover:text-[#5A524C]'
                }`}
              >
                Step {step.step}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content Card */}
        <div className="glass-card p-8 flex flex-col md:flex-row items-start gap-6 animate-fade-in">
          <div className="p-4 rounded-2xl bg-[#FAF7F2] border border-[#DED9CE] flex-shrink-0">
            {instructions[activeInstructionTab].icon}
          </div>
          <div className="space-y-3">
            <div className="text-xs font-bold tracking-widest text-[#C95A3E] uppercase">
              Step {instructions[activeInstructionTab].step} of 04
            </div>
            <h3 className="text-xl font-bold text-[#2E2925]">{instructions[activeInstructionTab].title}</h3>
            <p className="text-[#5A524C] text-sm leading-relaxed">{instructions[activeInstructionTab].desc}</p>
          </div>
        </div>
      </section>

      {/* Bottom CTA */}
      <section className="text-center space-y-6 max-w-2xl mx-auto py-10">
        <h2 className="text-3xl font-extrabold">Ready to evaluate your supplier risk?</h2>
        <p className="text-[#5A524C] text-sm leading-relaxed">
          Navigate to the dashboard, input your spreadsheet link, and run our live multi-agent pipeline immediately.
        </p>
        <button
          onClick={() => onNavigate('dashboard')}
          className="px-8 py-3 rounded-xl bg-[#C95A3E] hover:bg-[#B34C32] text-white font-bold transition-all shadow-lg shadow-[#C95A3E]/20"
        >
          Access Dashboard Now
        </button>
      </section>
    </div>
  )
}
