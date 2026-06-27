import { useState } from 'react'
import ReactMarkdown from 'react-markdown'

function App() {
  const [ticker, setTicker] = useState("")
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)

  function handleAnalyze() {
    setLoading(true)
    fetch(`http://localhost:8000/analyze/${ticker}`)
      .then(response => response.json())
      .then(data => {
        console.log(data)
        setResults(data)
        setLoading(false)
      })
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      
      {/* Header */}
      <div className="border-b border-gray-800 px-8 py-5">
        <h1 className="text-2xl font-semibold tracking-tight">Prism<span className="text-purple-500">.</span></h1>
      </div>

      {/* Main content */}
      <div className="max-w-6xl mx-auto px-8 py-10">

        {/* Search */}
        <div className="flex gap-3 mb-8">
          <input
            type="text"
            placeholder="Enter ticker symbol (e.g. AAPL)"
            value={ticker}
            onChange={(e) => setTicker(e.target.value.toUpperCase())}
            className="flex-1 bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500"
          />
          <button
            onClick={handleAnalyze}
            className="bg-purple-600 hover:bg-purple-700 px-6 py-3 rounded-lg font-medium transition-colors"
          >
            Analyze
          </button>
        </div>

        {/* Loading bar */}
        {loading && (
          <div className="mb-8">
            <div className="h-1 bg-gray-800 rounded-full overflow-hidden">
              <div className="h-full bg-purple-500 rounded-full animate-pulse w-3/4"></div>
            </div>
            <p className="text-gray-400 text-sm mt-2">Analyzing {ticker} across 3 AI models...</p>
          </div>
        )}

        {/* Results */}
        {results && (
          <div>

            {/* Stock metrics */}
            <div className="grid grid-cols-4 gap-4 mb-8">
              <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
                <p className="text-gray-400 text-xs mb-1">Price</p>
                <p className="text-xl font-semibold">${results.data.price.results[0].c}</p>
              </div>
              <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
                <p className="text-gray-400 text-xs mb-1">Market cap</p>
                <p className="text-xl font-semibold">${(results.data.details.results.market_cap / 1e12).toFixed(2)}T</p>
              </div>
              <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
                <p className="text-gray-400 text-xs mb-1">Volume</p>
                <p className="text-xl font-semibold">{(results.data.price.results[0].v / 1e6).toFixed(1)}M</p>
              </div>
              <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
                <p className="text-gray-400 text-xs mb-1">Day range</p>
                <p className="text-xl font-semibold">${results.data.price.results[0].l} – ${results.data.price.results[0].h}</p>
              </div>
            </div>

            {/* AI cards */}
            <p className="text-xs text-gray-500 uppercase tracking-widest mb-4">AI analyst perspectives</p>
            <div className="grid grid-cols-3 gap-4 mb-8">
              
              <div className="bg-gray-900 border border-gray-800 rounded-lg p-5">
                <div className="flex items-center gap-2 mb-4">
                  <span className="text-xs bg-emerald-900 text-emerald-400 px-2 py-1 rounded-full">Gemini 3.1 Pro</span>
                </div>
                <ReactMarkdown>{results.gemini}</ReactMarkdown>
              </div>

              <div className="bg-gray-900 border border-gray-800 rounded-lg p-5">
                <div className="flex items-center gap-2 mb-4">
                  <span className="text-xs bg-purple-900 text-purple-400 px-2 py-1 rounded-full">Claude Sonnet</span>
                </div>
                <ReactMarkdown>{results.claude}</ReactMarkdown>
              </div>

              <div className="bg-gray-900 border border-gray-800 rounded-lg p-5">
                <div className="flex items-center gap-2 mb-4">
                  <span className="text-xs bg-green-900 text-green-400 px-2 py-1 rounded-full">GPT-4o</span>
                </div>
                <ReactMarkdown>{results.openai}</ReactMarkdown>
              </div>

            </div>

            {/* Summary */}
            <p className="text-xs text-gray-500 uppercase tracking-widest mb-4">Consensus summary</p>
            <div className="bg-gray-900 border-l-4 border-purple-500 border border-gray-800 rounded-lg p-6">
              <ReactMarkdown>{results.summary}</ReactMarkdown>
            </div>

          </div>
        )}

      </div>
    </div>
  )
}

export default App