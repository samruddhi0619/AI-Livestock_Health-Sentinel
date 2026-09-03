import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { useAuth, API_BASE_URL } from '../../context/AuthContext';
import { useLanguage } from '../../context/LanguageContext';
import DiseaseMap from '../../components/DiseaseMap';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, Cell
} from 'recharts';
import { 
  Activity, 
  Map, 
  Users, 
  ShieldAlert, 
  AlertTriangle, 
  RefreshCw, 
  FileSpreadsheet,
  Globe,
  Info
} from 'lucide-react';

const OfficerDashboard = () => {
  const { token } = useAuth();
  const { t } = useLanguage();
  const location = useLocation();
  
  const [activeTab, setActiveTab] = useState('surveillance'); // surveillance, map, outbreaks
  
  useEffect(() => {
    if (location.pathname === '/officer/dashboard' || location.pathname === '/officer/surveillance') {
      setActiveTab('surveillance');
    } else if (location.pathname === '/officer/map') {
      setActiveTab('map');
    } else if (location.pathname === '/officer/trends') {
      setActiveTab('outbreaks');
    }
  }, [location.pathname]);
  const [stats, setStats] = useState(null);
  const [cases, setCases] = useState([]);
  const [clusters, setClusters] = useState([]);
  const [loadingSync, setLoadingSync] = useState(false);
  const [msg, setMsg] = useState('');

  const fetchOfficerData = async () => {
    if (!token) return;
    try {
      // 1. Fetch dashboard summaries
      const res = await fetch(`${API_BASE_URL}/api/dashboard/officer`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setStats(data);
      }

      // 2. Fetch cases
      const casesRes = await fetch(`${API_BASE_URL}/api/cases`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (casesRes.ok) {
        const casesData = await casesRes.json();
        setCases(casesData);
      }

      // 3. Fetch active clusters
      const clusterRes = await fetch(`${API_BASE_URL}/api/outbreaks`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (clusterRes.ok) {
        const clusterData = await clusterRes.json();
        setClusters(clusterData);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchOfficerData();
  }, [token]);

  // Recalculates outbreak clusters via DBSCAN
  const runOutbreakDetection = async () => {
    setLoadingSync(true);
    setMsg('');
    try {
      const response = await fetch(`${API_BASE_URL}/api/outbreaks/detect`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setMsg(data.message);
        fetchOfficerData();
      } else {
        setMsg('Detection engine error.');
      }
    } catch (err) {
      setMsg('Failed to reach detection engine.');
    } finally {
      setLoadingSync(false);
    }
  };

  if (!stats) {
    return <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}><div className="spinner" /></div>;
  }

  // Format chart data
  const barChartData = Object.keys(stats.disease_distribution || {}).map((k) => ({
    name: k,
    cases: stats.disease_distribution[k]
  }));

  const COLORS = ['#1b4626', '#d49b00', '#dc2626', '#2563eb', '#8b5cf6'];

  return (
    <div className="page-container">
      {/* Top Tabs */}
      <div style={{ display: 'flex', gap: '1rem', borderBottom: '2px solid hsl(var(--border))', paddingBottom: '1rem', marginBottom: '2rem' }}>
        <button onClick={() => setActiveTab('surveillance')} className={`btn ${activeTab === 'surveillance' ? 'btn-primary' : 'btn-secondary'}`}>
          <FileSpreadsheet size={18} /> Statewide Surveillance
        </button>
        <button onClick={() => setActiveTab('map')} className={`btn ${activeTab === 'map' ? 'btn-primary' : 'btn-secondary'}`}>
          <Map size={18} /> Interactive Risk Map
        </button>
        <button onClick={() => setActiveTab('outbreaks')} className={`btn ${activeTab === 'outbreaks' ? 'btn-primary' : 'btn-secondary'}`}>
          <AlertTriangle size={18} /> DBSCAN Cluster Portal
        </button>
      </div>

      {/* TAB 1: SURVEILLANCE */}
      {activeTab === 'surveillance' && (
        <div>
          <h3 className="page-title">Livestock Health & Disease Surveillance</h3>
          <p className="page-subtitle">Administrative oversight of epidemics in Maharashtra</p>

          {/* Cards metrics */}
          <div className="grid-4" style={{ marginBottom: '2rem' }}>
            <div className="stat-card">
              <div className="stat-icon primary"><Activity size={24} /></div>
              <div className="stat-info">
                <h3>Total Animals</h3>
                <p>{stats.total_animals}</p>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon"><Users size={24} /></div>
              <div className="stat-info">
                <h3>Active Farms</h3>
                <p>{stats.total_farms}</p>
              </div>
            </div>
            <div className="stat-card" style={{ borderLeft: '4px solid orange' }}>
              <div className="stat-icon" style={{ color: 'orange', backgroundColor: 'rgba(255,165,0,0.1)' }}><ShieldAlert size={24} /></div>
              <div className="stat-info">
                <h3>Suspected Cases</h3>
                <p>{stats.suspected_cases}</p>
              </div>
            </div>
            <div className="stat-card" style={{ borderLeft: '4px solid red' }}>
              <div className="stat-icon" style={{ color: 'red', backgroundColor: 'rgba(255,0,0,0.1)' }}><AlertTriangle size={24} /></div>
              <div className="stat-info">
                <h3>Active Clusters</h3>
                <p>{stats.active_clusters}</p>
              </div>
            </div>
          </div>

          {/* Charts block */}
          <div className="grid-2" style={{ marginBottom: '2rem' }}>
            {/* Trend line */}
            <div className="form-card">
              <h4 style={{ fontSize: '1.05rem', fontWeight: 700, marginBottom: '1.25rem', color: 'hsl(var(--primary))' }}>
                Epidemiological Trend Line (Past 7 Days)
              </h4>
              <div style={{ width: '100%', height: 260 }}>
                <ResponsiveContainer>
                  <LineChart data={stats.trends}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis allowDecimals={false} />
                    <Tooltip />
                    <Line type="monotone" dataKey="cases" stroke="hsl(var(--primary))" strokeWidth={3} dot={{ r: 5 }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Disease distribution bar chart */}
            <div className="form-card">
              <h4 style={{ fontSize: '1.05rem', fontWeight: 700, marginBottom: '1.25rem', color: 'hsl(var(--primary))' }}>
                Disease Prevalence Distribution
              </h4>
              {barChartData.length > 0 ? (
                <div style={{ width: '100%', height: 260 }}>
                  <ResponsiveContainer>
                    <BarChart data={barChartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis allowDecimals={false} />
                      <Tooltip />
                      <Bar dataKey="cases" fill="hsl(var(--primary))">
                        {barChartData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div style={{ height: 260, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'hsl(var(--text-muted))' }}>
                  No active disease cases reported.
                </div>
              )}
            </div>
          </div>

          {/* Geographical listings */}
          <div className="grid-3">
            <div className="form-card" style={{ padding: '1.25rem' }}>
              <h4 style={{ fontSize: '0.9rem', fontWeight: 700, borderBottom: '1px solid hsl(var(--border))', paddingBottom: '0.5rem', marginBottom: '0.75rem' }}>
                District-Wise Cases
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {Object.keys(stats.district_distribution || {}).map(k => (
                  <div key={k} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem' }}>
                    <strong>{k}</strong>
                    <span>{stats.district_distribution[k]} cases</span>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="form-card" style={{ padding: '1.25rem' }}>
              <h4 style={{ fontSize: '0.9rem', fontWeight: 700, borderBottom: '1px solid hsl(var(--border))', paddingBottom: '0.5rem', marginBottom: '0.75rem' }}>
                Taluka-Wise Cases
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {Object.keys(stats.taluka_distribution || {}).map(k => (
                  <div key={k} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem' }}>
                    <strong>{k}</strong>
                    <span>{stats.taluka_distribution[k]} cases</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="form-card" style={{ padding: '1.25rem' }}>
              <h4 style={{ fontSize: '0.9rem', fontWeight: 700, borderBottom: '1px solid hsl(var(--border))', paddingBottom: '0.5rem', marginBottom: '0.75rem' }}>
                Village-Wise Cases
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {Object.keys(stats.village_distribution || {}).map(k => (
                  <div key={k} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem' }}>
                    <strong>{k}</strong>
                    <span>{stats.village_distribution[k]} cases</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: INTERACTIVE MAP */}
      {activeTab === 'map' && (
        <div>
          <h3 className="page-title">Regional Outbreak & Risk Map</h3>
          <p className="page-subtitle">Live GIS monitoring of Maharashtra farms</p>
          
          <div className="form-card" style={{ padding: '1rem' }}>
            <DiseaseMap cases={cases} clusters={clusters} />
          </div>
        </div>
      )}

      {/* TAB 3: OUTBREAKS PORTAL */}
      {activeTab === 'outbreaks' && (
        <div style={{ maxWidth: '800px', margin: '0 auto' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
            <div>
              <h3 className="page-title">Epidemic Cluster detection (DBSCAN)</h3>
              <p className="page-subtitle">Trigger spatial grouping algorithms over geocoded reports</p>
            </div>
            <button 
              onClick={runOutbreakDetection} 
              className="btn btn-primary"
              disabled={loadingSync}
              style={{ gap: '8px' }}
            >
              <RefreshCw size={18} className={loadingSync ? 'spin' : ''} />
              Re-run DBSCAN Engine
            </button>
          </div>

          {msg && (
            <div className="alert-banner" style={{ backgroundColor: 'rgba(18,70,38,0.1)', color: 'hsl(var(--primary))', borderColor: 'hsl(var(--primary))', borderRadius: '8px' }}>
              <Info size={18} />
              <span>{msg}</span>
            </div>
          )}

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {clusters.map((c, idx) => (
              <div key={idx} className="form-card" style={{ borderLeft: '5px solid red', padding: '1.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <h4 style={{ fontSize: '1.2rem', color: '#dc2626', fontWeight: 800 }}>
                    {c.status}
                  </h4>
                  <span className="badge badge-high">{c.risk_level} RISK</span>
                </div>
                <div style={{ fontSize: '0.9rem', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                  <p><strong>Suspected Disease:</strong> {c.disease}</p>
                  <p><strong>Cases Identified:</strong> {c.cases_count}</p>
                  <p><strong>Warning Radius:</strong> {c.radius} km</p>
                  <p><strong>Affected Farms:</strong> {c.affected_farms?.join(', ')}</p>
                  <p style={{ gridColumn: '1/-1' }}><strong>Cluster Center Point:</strong> Lat: {c.center_location?.latitude.toFixed(5)}, Lng: {c.center_location?.longitude.toFixed(5)}</p>
                </div>
              </div>
            ))}
            {clusters.length === 0 && (
              <div style={{ textAlign: 'center', padding: '3rem', color: 'hsl(var(--text-muted))', border: '2px dashed hsl(var(--border))', borderRadius: '12px' }}>
                <Globe size={40} style={{ color: 'hsl(var(--text-muted))', marginBottom: '1rem' }} />
                <h4>No Disease Clusters Found</h4>
                <p style={{ fontSize: '0.85rem' }}>
                  The regional surveillance grids are clear. Run DBSCAN calculations to check for recent trends.
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default OfficerDashboard;
