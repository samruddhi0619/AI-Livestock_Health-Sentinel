import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { useAuth, API_BASE_URL } from '../../context/AuthContext';
import { useLanguage } from '../../context/LanguageContext';
import { 
  Users, 
  Settings, 
  FileText, 
  BarChart, 
  ShieldCheck, 
  RefreshCw, 
  CheckCircle2, 
  AlertCircle 
} from 'lucide-react';

const AdminDashboard = () => {
  const { token } = useAuth();
  const { t } = useLanguage();
  const location = useLocation();
  
  const [activeTab, setActiveTab] = useState('users'); // users, config, audit
  
  useEffect(() => {
    if (location.pathname === '/admin/dashboard' || location.pathname === '/admin/users') {
      setActiveTab('users');
    } else if (location.pathname === '/admin/config') {
      setActiveTab('config');
    } else if (location.pathname === '/admin/audit') {
      setActiveTab('audit');
    }
  }, [location.pathname]);
  const [usersList, setUsersList] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [mlMetrics, setMlMetrics] = useState(null);
  
  // Configuration Settings State
  const [lowRisk, setLowRisk] = useState(40);
  const [highRisk, setHighRisk] = useState(70);
  const [dbscanEps, setDbscanEps] = useState(5.0);
  const [dbscanMin, setDbscanMin] = useState(3);
  
  const [saveSuccess, setSaveSuccess] = useState('');
  const [saveError, setSaveError] = useState('');
  const [saving, setSaving] = useState(false);

  const fetchAdminData = async () => {
    if (!token) return;
    try {
      // 1. Fetch Users List
      const usersRes = await fetch(`${API_BASE_URL}/api/admin/users`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (usersRes.ok) {
        const usersData = await usersRes.json();
        setUsersList(usersData);
      }

      // 2. Fetch General Dashboard / Config details
      const adminDashRes = await fetch(`${API_BASE_URL}/api/dashboard/admin`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (adminDashRes.ok) {
        const dashData = await adminDashRes.json();
        setAuditLogs(dashData.audit_logs || []);
        setMlMetrics(dashData.ml_metrics);
      }

      // 3. Fetch Config
      const configRes = await fetch(`${API_BASE_URL}/api/admin/config`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (configRes.ok) {
        const configData = await configRes.json();
        setLowRisk(configData.low_risk_threshold);
        setHighRisk(configData.high_risk_threshold);
        setDbscanEps(configData.dbscan_eps_km);
        setDbscanMin(configData.dbscan_min_cases);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchAdminData();
  }, [token]);

  const handleSaveConfig = async (e) => {
    e.preventDefault();
    setSaving(true);
    setSaveSuccess('');
    setSaveError('');

    const payload = {
      low_risk_threshold: parseInt(lowRisk),
      high_risk_threshold: parseInt(highRisk),
      dbscan_eps_km: parseFloat(dbscanEps),
      dbscan_min_cases: parseInt(dbscanMin)
    };

    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/config`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        setSaveSuccess('Risk thresholds and DBSCAN parameters updated successfully!');
        fetchAdminData();
      } else {
        const err = await response.json();
        setSaveError(err.detail || 'Failed to save configuration');
      }
    } catch (err) {
      setSaveError('Network error connecting to configuration API.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="page-container">
      {/* Top Tabs */}
      <div style={{ display: 'flex', gap: '1rem', borderBottom: '2px solid hsl(var(--border))', paddingBottom: '1rem', marginBottom: '2rem' }}>
        <button onClick={() => setActiveTab('users')} className={`btn ${activeTab === 'users' ? 'btn-primary' : 'btn-secondary'}`}>
          <Users size={18} /> Accounts Management ({usersList.length})
        </button>
        <button onClick={() => setActiveTab('config')} className={`btn ${activeTab === 'config' ? 'btn-primary' : 'btn-secondary'}`}>
          <Settings size={18} /> Model Configuration
        </button>
        <button onClick={() => setActiveTab('audit')} className={`btn ${activeTab === 'audit' ? 'btn-primary' : 'btn-secondary'}`}>
          <FileText size={18} /> Security Audit Logs
        </button>
      </div>

      {/* TAB 1: ACCOUNTS */}
      {activeTab === 'users' && (
        <div>
          <h3 className="page-title">Sentinel Accounts Directory</h3>
          <p className="page-subtitle">Manage system users, veterinarians, and field officers</p>

          <div className="form-card" style={{ padding: 0, overflow: 'hidden' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
              <thead>
                <tr style={{ backgroundColor: 'hsl(var(--bg-light))', textAlign: 'left', borderBottom: '1px solid hsl(var(--border))' }}>
                  <th style={{ padding: '12px 16px' }}>Full Name</th>
                  <th style={{ padding: '12px 16px' }}>Username</th>
                  <th style={{ padding: '12px 16px' }}>Role</th>
                  <th style={{ padding: '12px 16px' }}>District / Taluka</th>
                  <th style={{ padding: '12px 16px' }}>Status</th>
                </tr>
              </thead>
              <tbody>
                {usersList.map((u, i) => (
                  <tr key={i} style={{ borderBottom: '1px solid hsl(var(--border))' }}>
                    <td style={{ padding: '12px 16px', fontWeight: 600 }}>{u.fullname}</td>
                    <td style={{ padding: '12px 16px', color: 'hsl(var(--text-muted))' }}>{u.username}</td>
                    <td style={{ padding: '12px 16px' }}>
                      <span className="badge" style={{ backgroundColor: '#e2e8f0', color: '#1a202c' }}>{u.role}</span>
                    </td>
                    <td style={{ padding: '12px 16px' }}>{u.district ? `${u.district} / ${u.taluka}` : 'N/A'}</td>
                    <td style={{ padding: '12px 16px', color: 'green', fontWeight: 600 }}>✓ ACTIVE</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 2: CONFIG & ML STATS */}
      {activeTab === 'config' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
          {/* Threshold Configurations */}
          <div className="form-card">
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'hsl(var(--primary))', marginBottom: '1rem' }}>
              Configure Risk Thresholds
            </h3>

            {saveSuccess && (
              <div className="alert-banner" style={{ backgroundColor: 'rgba(16, 124, 65, 0.1)', borderColor: 'green', color: 'green', borderRadius: '8px', marginBottom: '1rem' }}>
                <CheckCircle2 size={16} />
                <span>{saveSuccess}</span>
              </div>
            )}

            {saveError && (
              <div className="alert-banner high-risk" style={{ borderRadius: '8px', marginBottom: '1rem' }}>
                <AlertCircle size={16} />
                <span>{saveError}</span>
              </div>
            )}

            <form onSubmit={handleSaveConfig}>
              <div className="form-group">
                <label className="form-label">Moderate Risk Lower Bound (%)</label>
                <input type="number" className="form-control" value={lowRisk} onChange={(e) => setLowRisk(e.target.value)} />
                <span style={{ fontSize: '0.7rem', color: 'hsl(var(--text-muted))' }}>Predictions below this are classified as LOW RISK.</span>
              </div>

              <div className="form-group">
                <label className="form-label">High Risk Lower Bound (%)</label>
                <input type="number" className="form-control" value={highRisk} onChange={(e) => setHighRisk(e.target.value)} />
                <span style={{ fontSize: '0.7rem', color: 'hsl(var(--text-muted))' }}>Predictions above this are classified as HIGH RISK.</span>
              </div>

              <div style={{ margin: '1.5rem 0', borderBottom: '1px solid hsl(var(--border))' }} />
              <h4 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '0.75rem' }}>DBSCAN Clustering Parameters</h4>

              <div className="form-group">
                <label className="form-label">Clustering Distance (km)</label>
                <input type="number" step="0.1" className="form-control" value={dbscanEps} onChange={(e) => setDbscanEps(e.target.value)} />
              </div>

              <div className="form-group">
                <label className="form-label">Minimum Cases to Form Cluster</label>
                <input type="number" className="form-control" value={dbscanMin} onChange={(e) => setDbscanMin(e.target.value)} />
              </div>

              <button type="submit" className="btn btn-primary" style={{ width: '100%' }} disabled={saving}>
                {saving ? 'Saving Config...' : 'Save Configuration'}
              </button>
            </form>
          </div>

          {/* Model diagnostics logs */}
          <div className="form-card">
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'hsl(var(--primary))', marginBottom: '1rem' }}>
              ML Model Status & Accuracy Metrics
            </h3>

            {mlMetrics ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                <div style={{ borderBottom: '1px solid hsl(var(--border))', paddingBottom: '10px' }}>
                  <h4 style={{ fontWeight: 700, fontSize: '0.95rem', color: 'hsl(var(--primary))' }}>Symptom Classifier (XGBoost Benchmark)</h4>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px', fontSize: '0.85rem', marginTop: '4px' }}>
                    <p><strong>Algorithm:</strong> {mlMetrics.symptom_model.algorithm}</p>
                    <p><strong>Accuracy:</strong> {mlMetrics.symptom_model.accuracy * 100}%</p>
                    <p><strong>Precision:</strong> {mlMetrics.symptom_model.precision * 100}%</p>
                    <p><strong>Recall/F1:</strong> {mlMetrics.symptom_model.f1_score * 100}%</p>
                  </div>
                </div>

                <div style={{ borderBottom: '1px solid hsl(var(--border))', paddingBottom: '10px' }}>
                  <h4 style={{ fontWeight: 700, fontSize: '0.95rem', color: 'hsl(var(--primary))' }}>Anomaly Detector</h4>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px', fontSize: '0.85rem', marginTop: '4px' }}>
                    <p><strong>Algorithm:</strong> {mlMetrics.anomaly_detector.algorithm}</p>
                    <p><strong>Contamination rate:</strong> {mlMetrics.anomaly_detector.contamination_rate * 100}%</p>
                    <p><strong>Status:</strong> {mlMetrics.anomaly_detector.status}</p>
                  </div>
                </div>

                <div>
                  <h4 style={{ fontWeight: 700, fontSize: '0.95rem', color: 'hsl(var(--primary))' }}>Outbreak Detection</h4>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px', fontSize: '0.85rem', marginTop: '4px' }}>
                    <p><strong>Algorithm:</strong> {mlMetrics.outbreak_clustering.algorithm}</p>
                    <p><strong>Default Radius:</strong> {mlMetrics.outbreak_clustering.eps_radius_km} km</p>
                    <p><strong>Min Samples:</strong> {mlMetrics.outbreak_clustering.min_samples} cases</p>
                  </div>
                </div>
              </div>
            ) : (
              <p>ML models not initialized yet. Run training scripts.</p>
            )}
          </div>
        </div>
      )}

      {/* TAB 3: AUDIT TRAIL */}
      {activeTab === 'audit' && (
        <div>
          <h3 className="page-title">System Action Logs</h3>
          <p className="page-subtitle">Chronological record of user-triggered assessment decisions and verifications</p>

          <div className="form-card" style={{ padding: '1rem' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {auditLogs.map((log, idx) => (
                <div key={idx} style={{ 
                  padding: '8px 12px', 
                  backgroundColor: 'hsl(var(--bg-light))', 
                  borderRadius: '6px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  fontSize: '0.85rem'
                }}>
                  <div>
                    <span className="badge" style={{ backgroundColor: 'hsl(var(--primary))', color: '#fff', fontSize: '0.65rem', marginRight: '8px' }}>
                      {log.action}
                    </span>
                    <strong style={{ marginRight: '8px' }}>{log.user}</strong>
                    <span style={{ color: 'hsl(var(--text-muted))' }}>{log.details}</span>
                  </div>
                  <span style={{ color: 'hsl(var(--text-muted))', fontSize: '0.75rem' }}>
                    {new Date(log.timestamp).toLocaleString()}
                  </span>
                </div>
              ))}
              {auditLogs.length === 0 && (
                <p style={{ textAlign: 'center', color: 'hsl(var(--text-muted))' }}>No audit logs recorded.</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;
