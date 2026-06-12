import { useState, useEffect } from 'react'
import { Activity, BarChart2, Map as MapIcon, Play, AlertCircle, CheckCircle2 } from 'lucide-react'

const API_BASE = 'http://localhost:8000/api'
const STATIC_BASE = 'http://localhost:8000'

function App() {
  const [aggLevel, setAggLevel] = useState('daily')
  const [loading, setLoading] = useState(false)
  const [statusMsg, setStatusMsg] = useState('')
  const [error, setError] = useState(false)
  const [results, setResults] = useState(null)

  const fetchResults = async (level) => {
    try {
      const res = await fetch(`${API_BASE}/results?agg_level=${level}`)
      if (res.ok) {
        const data = await res.json()
        setResults(data)
      }
    } catch (err) {
      console.error("Lỗi khi tải kết quả", err)
    }
  }

  // Tải kết quả cũ nếu có khi mới mở app (hoặc khi đổi aggLevel)
  useEffect(() => {
    fetchResults(aggLevel)
  }, [aggLevel])

  const runPipeline = async () => {
    setLoading(true)
    setStatusMsg('Đang chạy Pipeline... quá trình này có thể mất vài phút.')
    setError(false)
    
    try {
      const res = await fetch(`${API_BASE}/run-pipeline`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ agg_level: aggLevel })
      })
      
      const data = await res.json()
      
      if (!res.ok) {
        throw new Error(data.detail || 'Lỗi không xác định')
      }
      
      setStatusMsg('Pipeline hoàn thành thành công!')
      // Đợi 1 chút cho file ghi xong hoàn toàn rồi fetch lại kết quả
      setTimeout(() => fetchResults(aggLevel), 1000)
      
    } catch (err) {
      setError(true)
      setStatusMsg(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-container">
      {/* Sidebar / Controls */}
      <aside className="sidebar">
        <div className="glass-panel">
          <h1>COVID-19 Sentiment</h1>
          <p className="subtitle">
            Phân tích tương quan giữa thái độ trên Twitter/X và số ca nhiễm COVID-19 theo thời gian thực.
          </p>

          {/* Daily / Weekly Toggle */}
          <div className="toggle-group">
            <button
              className={`btn-toggle ${aggLevel === 'daily' ? 'active' : ''}`}
              onClick={() => setAggLevel('daily')}
              disabled={loading}
            >
              Daily
            </button>
            <button
              className={`btn-toggle ${aggLevel === 'weekly' ? 'active' : ''}`}
              onClick={() => setAggLevel('weekly')}
              disabled={loading}
            >
              Weekly
            </button>
          </div>

          <button 
            className="btn-run" 
            onClick={runPipeline} 
            disabled={loading}
          >
            {loading ? <div className="spinner" /> : <Play size={20} />}
            {loading ? 'Processing...' : 'Run Pipeline'}
          </button>
          
          {statusMsg && (
            <div className={`status-text ${error ? 'error' : ''}`}>
              {error ? <AlertCircle size={16} /> : <CheckCircle2 size={16} />}
              <span>{statusMsg}</span>
            </div>
          )}
        </div>
      </aside>

      {/* Main Content / Results */}
      <main className="results-area">
        
        {/* Metric Card */}
        <div className="glass-panel metric-card">
          <div>
            <div className="control-label" style={{marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
              <Activity size={18} color="var(--accent-primary)"/> Global Correlation (r)
            </div>
            <div className="metric-label">Tương quan Pearson trên toàn bộ dataset</div>
          </div>
          <div className="metric-value">
             {results && results.global_correlation && results.global_correlation !== "N/A" 
                ? parseFloat(results.global_correlation.split(': ')[1] || results.global_correlation).toFixed(4) 
                : "---"
             }
          </div>
        </div>

        {/* Charts Grid */}
        <div className="glass-panel">
          <div className="control-label" style={{marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
            <BarChart2 size={18} color="var(--accent-secondary)"/> Temporal Correlation
          </div>
          <div className="chart-container">
            {results && results.temporal_image ? (
              <img src={`${STATIC_BASE}${results.temporal_image}?t=${Date.now()}`} alt="Temporal Correlation" />
            ) : (
              <div className="empty-state">
                <BarChart2 size={48} opacity={0.5} />
                <p>Chưa có dữ liệu biểu đồ. Vui lòng chạy Pipeline.</p>
              </div>
            )}
          </div>
        </div>
        
        <div className="glass-panel">
          <div className="control-label" style={{marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
            <MapIcon size={18} color="var(--success)"/> Spatial Correlation Map (Continental US)
          </div>
          <div className="chart-container">
            {results && results.spatial_image ? (
              <img src={`${STATIC_BASE}${results.spatial_image}?t=${Date.now()}`} alt="Spatial Correlation Map" />
            ) : (
              <div className="empty-state">
                <MapIcon size={48} opacity={0.5} />
                <p>Chưa có bản đồ. Vui lòng chạy Pipeline.</p>
              </div>
            )}
          </div>
        </div>

      </main>
    </div>
  )
}

export default App
