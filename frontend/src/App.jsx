import { useEffect, useState } from 'react'
import {
  LayoutDashboard, Video, TriangleAlert, BarChart3, Settings, Search,
  Bell, ChevronDown, ShieldCheck, Users, Activity, Camera, CircleCheck,
  HardHat, Zap, Clock, Download, Plus, MoreHorizontal
} from 'lucide-react'

const API = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '')

const demoActivity = [
  { time: '10:42:18', worker: 'Worker #14', site: 'Zone A · Level 3', type: 'Missing helmet', severity: 'High', status: 'New' },
  { time: '10:38:44', worker: 'Worker #07', site: 'Zone C · Loading bay', type: 'Restricted zone entry', severity: 'Critical', status: 'Investigating' },
  { time: '10:31:09', worker: 'Worker #21', site: 'Zone B · North scaffold', type: 'Missing safety vest', severity: 'Medium', status: 'Resolved' },
  { time: '10:24:33', worker: 'Worker #09', site: 'Zone A · Level 2', type: 'Unsafe posture detected', severity: 'Low', status: 'Resolved' },
]

const navItems = [
  [LayoutDashboard, 'Overview', true], [Video, 'Live monitoring', false],
  [TriangleAlert, 'Violations', false], [BarChart3, 'Analytics', false],
  [Settings, 'Settings', false],
]

export default function App() {
  const [summary, setSummary] = useState(null)
  const [health, setHealth] = useState(null)
  const [activeNav, setActiveNav] = useState('Overview')
  const [searchOpen, setSearchOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [cameraModal, setCameraModal] = useState(false)
  const [notificationsOpen, setNotificationsOpen] = useState(false)

  useEffect(() => {
    const loadApiData = async () => {
      const getJson = async (path) => {
        const controller = new AbortController()
        const timeout = setTimeout(() => controller.abort(), 5000)
        try {
          const response = await fetch(`${API}${path}`, { signal: controller.signal })
          if (!response.ok) throw new Error(`API request failed: ${response.status}`)
          return await response.json()
        } catch {
          return null
        } finally {
          clearTimeout(timeout)
        }
      }

      const [summaryData, healthData] = await Promise.all([
        getJson('/api/dashboard/summary'),
        getJson('/api/health'),
      ])
      setSummary(summaryData)
      setHealth(healthData)
    }

    loadApiData()
  }, [])

  const metrics = [
    { label: 'Active workers', value: summary?.total_workers_detected ?? '24', change: '+3 today', icon: Users, tone: 'blue' },
    { label: 'Violations today', value: summary?.violations_today ?? '8', change: '-12% vs yesterday', icon: TriangleAlert, tone: 'amber' },
    { label: 'Active cameras', value: summary?.active_streams ?? '6', change: '2 locations', icon: Camera, tone: 'green' },
    { label: 'Compliance rate', value: '94.2%', change: '+2.4% this week', icon: ShieldCheck, tone: 'purple' },
  ]
  const connected = health?.status === 'healthy'
  const filteredActivity = demoActivity.filter((row) =>
    Object.values(row).join(' ').toLowerCase().includes(searchQuery.toLowerCase())
  )

  const exportReport = () => {
    const header = ['Time', 'Worker', 'Site location', 'Violation', 'Severity', 'Status']
    const rows = demoActivity.map((row) => [row.time, row.worker, row.site, row.type, row.severity, row.status])
    const csv = [header, ...rows].map((row) => row.map((value) => `"${String(value).replaceAll('"', '""')}"`).join(',')).join('\n')
    const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }))
    const link = document.createElement('a')
    link.href = url
    link.download = 'safesite-violations.csv'
    link.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><div className="brand-mark"><HardHat size={22}/></div><span>SafeSite<span>AI</span></span></div>
        <nav>
          <p className="nav-label">WORKSPACE</p>
          {navItems.map(([Icon, label]) => (
            <button key={label} className={activeNav === label ? 'nav-item active' : 'nav-item'} onClick={() => setActiveNav(label)}>
              <Icon size={19}/><span>{label}</span>{label === 'Violations' && <b>8</b>}
            </button>
          ))}
        </nav>
        <div className="sidebar-foot">
          <div className="system-status"><span className={connected ? 'status-dot online' : 'status-dot'}></span><div><strong>{connected ? 'All systems online' : 'Demo mode'}</strong><small>{connected ? 'Last checked just now' : 'Backend not connected'}</small></div></div>
          <div className="profile"><div className="avatar">JD</div><div><strong>Jordan Davis</strong><small>Safety Manager</small></div><ChevronDown size={16}/></div>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div><p className="eyebrow">MONDAY, OCTOBER 28</p><h1>{activeNav}</h1></div>
          <div className="actions"><button className="icon-button" title="Search" onClick={() => setSearchOpen(true)}><Search size={19}/></button><button className="icon-button notification" title="Notifications" onClick={() => setNotificationsOpen(!notificationsOpen)}><Bell size={19}/><i></i></button><button className="primary-button" onClick={() => setCameraModal(true)}><Plus size={17}/> Add camera</button></div>
        </header>

        <div className="content">
          {activeNav === 'Overview' && <>
          <section className="metrics-grid">
            {metrics.map(({ label, value, change, icon: Icon, tone }) => (
              <article className="metric-card" key={label}><div className={`metric-icon ${tone}`}><Icon size={21}/></div><div className="metric-main"><span>{label}</span><strong>{value}</strong><small>{change}</small></div><button className="more"><MoreHorizontal size={18}/></button></article>
            ))}
          </section>

          <section className="dashboard-grid">
            <article className="panel live-panel">
              <div className="panel-head"><div><p className="section-kicker">LIVE FEED</p><h2>Site overview</h2></div><button className="text-button" onClick={() => setActiveNav('Live monitoring')}>View all cameras <span>→</span></button></div>
              <div className="camera-grid">
                <div className="camera-view"><div className="scanline"></div><div className="feed-top"><span><i></i> LIVE</span><b>CAM-01</b></div><div className="worker-box box-one"><span>Worker #14</span><em>NO HELMET</em></div><div className="worker-box box-two"><span>Worker #07</span><em className="safe">SAFE</em></div><div className="feed-bottom"><span>Zone A · Level 3</span><Clock size={14}/> 10:42:18</div></div>
                <div className="camera-stack">
                  <div className="mini-feed feed-two"><div className="feed-top"><span><i></i> LIVE</span><b>CAM-03</b></div><div className="mini-label">Zone B · Loading</div></div>
                  <div className="mini-feed feed-three"><div className="feed-top"><span><i></i> LIVE</span><b>CAM-06</b></div><div className="mini-label">Zone C · Scaffold</div></div>
                </div>
              </div>
            </article>

            <article className="panel alert-panel">
              <div className="panel-head"><div><p className="section-kicker">TODAY</p><h2>Violation breakdown</h2></div><button className="icon-button small"><MoreHorizontal size={18}/></button></div>
              <div className="donut-wrap"><div className="donut"><div><strong>8</strong><span>total alerts</span></div></div></div>
              <div className="legend">
                <div><span><i className="c-red"></i>Missing helmet</span><strong>4</strong></div>
                <div><span><i className="c-orange"></i>Missing vest</span><strong>2</strong></div>
                <div><span><i className="c-yellow"></i>Zone breach</span><strong>1</strong></div>
                <div><span><i className="c-blue"></i>Unsafe posture</span><strong>1</strong></div>
              </div>
            </article>
          </section>

          <section className="panel activity-panel">
            <div className="panel-head"><div><p className="section-kicker">REAL-TIME</p><h2>Recent activity</h2></div><button className="export-button" onClick={exportReport}><Download size={16}/> Export report</button></div>
            <div className="table-wrap"><table><thead><tr><th>TIME</th><th>WORKER</th><th>SITE LOCATION</th><th>VIOLATION</th><th>SEVERITY</th><th>STATUS</th><th></th></tr></thead><tbody>
              {demoActivity.map((row, index) => <tr key={index}><td><Clock size={14}/>{row.time}</td><td><div className="worker-cell"><span>{row.worker.slice(-2)}</span><strong>{row.worker}</strong></div></td><td>{row.site}</td><td>{row.type}</td><td><span className={`severity ${row.severity.toLowerCase()}`}><i></i>{row.severity}</span></td><td><span className={`status ${row.status.toLowerCase().replace(' ', '-')}`}>{row.status}</span></td><td><button className="row-more"><MoreHorizontal size={17}/></button></td></tr>)}
            </tbody></table></div>
          </section>
          </>
          }

          {activeNav === 'Live monitoring' && (
            <section className="page-grid">
              {[1,2,3,4,5,6].map((camera) => (
                <article className="panel camera-card" key={camera}>
                  <div className="camera-card-feed"><div className="feed-top"><span><i></i> LIVE</span><b>CAM-{String(camera).padStart(2, '0')}</b></div><div className="worker-box box-two"><span>Worker #{camera + 4}</span><em className={camera === 1 ? '' : 'safe'}>{camera === 1 ? 'NO HELMET' : 'SAFE'}</em></div></div>
                  <div className="camera-card-info"><strong>Zone {String.fromCharCode(64 + camera % 3 + 1)} · {camera % 2 ? 'Level 3' : 'Loading bay'}</strong><button onClick={() => setActiveNav('Overview')}>Open view</button></div>
                </article>
              ))}
            </section>
          )}

          {activeNav === 'Violations' && (
            <section className="panel activity-panel page-panel">
              <div className="panel-head"><div><p className="section-kicker">ALL RECORDS</p><h2>Safety violations</h2></div><span className="record-count">{filteredActivity.length} records</span></div>
              <div className="table-wrap"><table><thead><tr><th>TIME</th><th>WORKER</th><th>SITE LOCATION</th><th>VIOLATION</th><th>SEVERITY</th><th>STATUS</th><th></th></tr></thead><tbody>
              {filteredActivity.map((row, index) => <tr key={index}><td><Clock size={14}/>{row.time}</td><td><div className="worker-cell"><span>{row.worker.slice(-2)}</span><strong>{row.worker}</strong></div></td><td>{row.site}</td><td>{row.type}</td><td><span className={`severity ${row.severity.toLowerCase()}`}><i></i>{row.severity}</span></td><td><span className={`status ${row.status.toLowerCase().replace(' ', '-')}`}>{row.status}</span></td><td><button className="row-more" title="More options"><MoreHorizontal size={17}/></button></td></tr>)}
              </tbody></table></div>
            </section>
          )}

          {activeNav === 'Analytics' && (
            <section className="analytics-grid">
              <article className="panel analytics-card"><div className="panel-head"><div><p className="section-kicker">WEEKLY</p><h2>Compliance trend</h2></div></div><div className="chart-bars">{[62,68,74,71,82,89,94].map((v,i)=><div key={i}><span style={{height:`${v}%`}}></span><small>{['M','T','W','T','F','S','S'][i]}</small></div>)}</div></article>
              <article className="panel analytics-card"><div className="panel-head"><div><p className="section-kicker">SOURCES</p><h2>Violation types</h2></div></div><div className="analytics-list"><div><span>Missing helmet</span><strong>50%</strong></div><div><span>Missing vest</span><strong>25%</strong></div><div><span>Zone breach</span><strong>12.5%</strong></div><div><span>Unsafe posture</span><strong>12.5%</strong></div></div></article>
            </section>
          )}

          {activeNav === 'Settings' && (
            <section className="panel settings-panel"><div className="panel-head"><div><p className="section-kicker">SYSTEM</p><h2>Detection settings</h2></div></div><form onSubmit={(event) => {event.preventDefault(); alert('Settings saved')}}><label>Detection confidence <input type="number" defaultValue="50" min="0" max="100" />%</label><label>PPE certainty threshold <input type="number" defaultValue="65" min="0" max="100" />%</label><label>Alert cooldown <input type="number" defaultValue="30" min="0" />seconds</label><button className="primary-button" type="submit">Save settings</button></form></section>
          )}
        </div>
      </main>

      {searchOpen && <div className="modal-backdrop" onMouseDown={() => setSearchOpen(false)}><div className="search-modal" onMouseDown={(event)=>event.stopPropagation()}><Search size={18}/><input autoFocus value={searchQuery} onChange={(event)=>setSearchQuery(event.target.value)} placeholder="Search workers, zones, violations..."/><button onClick={()=>{setSearchOpen(false); setActiveNav('Violations')}}>Search</button></div></div>}
      {notificationsOpen && <div className="notification-popover"><strong>Notifications</strong><p><TriangleAlert size={16}/> Missing helmet · Worker #14</p><p><Activity size={16}/> Worker entered restricted zone</p></div>}
      {cameraModal && <div className="modal-backdrop" onMouseDown={() => setCameraModal(false)}><form className="camera-modal" onMouseDown={(event)=>event.stopPropagation()} onSubmit={(event)=>{event.preventDefault(); setCameraModal(false)}}><h2>Add camera</h2><label>Camera name<input required placeholder="CAM-07" /></label><label>Stream URL<input required placeholder="rtsp://camera-ip/stream" /></label><label>Site zone<input required placeholder="Zone D · East gate" /></label><div><button type="button" className="export-button" onClick={()=>setCameraModal(false)}>Cancel</button><button className="primary-button" type="submit">Connect camera</button></div></form></div>}
    </div>
  )
}
