import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { useAuth, API_BASE_URL } from '../../context/AuthContext';
import { useLanguage } from '../../context/LanguageContext';
import DiseaseMap from '../../components/DiseaseMap';
import { 
  AlertTriangle, 
  CheckCircle, 
  Map, 
  ClipboardList, 
  User, 
  FileText, 
  Thermometer, 
  Activity,
  AlertCircle 
} from 'lucide-react';

const VetDashboard = () => {
  const { token } = useAuth();
  const { t } = useLanguage();
  const location = useLocation();
  
  const [activeTab, setActiveTab] = useState('cases'); // cases, map
  
  useEffect(() => {
    if (location.pathname === '/veterinarian/dashboard' || location.pathname === '/veterinarian/cases') {
      setActiveTab('cases');
    } else if (location.pathname === '/veterinarian/map') {
      setActiveTab('map');
    }
  }, [location.pathname]);
  const [pendingCases, setPendingCases] = useState([]);
  const [allCases, setAllCases] = useState([]);
  const [clusters, setClusters] = useState([]);
  
  const [selectedCase, setSelectedCase] = useState(null);
  
  // Verification Form State
  const [statusVal, setStatusVal] = useState('VERIFIED'); // VERIFIED or REJECTED
  const [diagnosis, setDiagnosis] = useState('');
  const [treatment, setTreatment] = useState('');
  const [followUp, setFollowUp] = useState('');
  const [submitSuccess, setSubmitSuccess] = useState('');
  const [submitError, setSubmitError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const fetchDashboardData = async () => {
    if (!token) return;
    try {
      // 1. Fetch Vet dashboard stats and cases
      const res = await fetch(`${API_BASE_URL}/api/dashboard/vet`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setPendingCases(data.pending_cases || []);
      }

      // 2. Fetch all cases (both suspected and verified for map rendering)
      const casesRes = await fetch(`${API_BASE_URL}/api/cases`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (casesRes.ok) {
        const casesData = await casesRes.json();
        setAllCases(casesData);
      }

      // 3. Fetch outbreak clusters
      const clusterRes = await fetch(`${API_BASE_URL}/api/outbreaks`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (clusterRes.ok) {
        const clusterData = await clusterRes.json();
        setClusters(clusterData);
      }
    } catch (err) {
      console.error("Failed to load vet dashboard data", err);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [token]);

  const handleSelectCase = async (c) => {
    setSelectedCase(c);
    setSubmitSuccess('');
    setSubmitError('');
    setDiagnosis('');
    setTreatment('');
    setFollowUp('');
  };

  const handleVerifySubmit = async (e) => {
    e.preventDefault();
    if (!selectedCase) return;

    setSubmitting(true);
    setSubmitSuccess('');
    setSubmitError('');

    const payload = {
      status: statusVal,
      diagnosis,
      treatment,
      follow_up: followUp
    };

    try {
      const response = await fetch(`${API_BASE_URL}/api/cases/${selectedCase._id}/verify`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        setSubmitSuccess('Case verification logged successfully!');
        setSelectedCase(null);
        fetchDashboardData();
      } else {
        const err = await response.json();
        setSubmitError(err.detail || 'Verification request failed');
      }
    } catch (err) {
      setSubmitError('Backend network connection error.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="page-container">
      {/* Top Tabs */}
      <div style={{ display: 'flex', gap: '1rem', borderBottom: '2px solid hsl(var(--border))', paddingBottom: '1rem', marginBottom: '2rem' }}>
        <button onClick={() => setActiveTab('cases')} className={`btn ${activeTab === 'cases' ? 'btn-primary' : 'btn-secondary'}`}>
          <ClipboardList size={18} /> Review Queue ({pendingCases.length})
        </button>
        <button onClick={() => setActiveTab('map')} className={`btn ${activeTab === 'map' ? 'btn-primary' : 'btn-secondary'}`}>
          <Map size={18} /> Regional Map Overview
        </button>
      </div>

      {/* TAB 1: REVIEW QUEUE */}
      {activeTab === 'cases' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.2fr', gap: '2rem' }}>
          
          {/* List panel */}
          <div>
            <h3 className="page-title">Cases Pending Verification</h3>
            <p className="page-subtitle">Prioritized list of AI flagged high-risk symptoms</p>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {pendingCases.map((c) => (
                <div 
                  key={c._id} 
                  onClick={() => handleSelectCase(c)}
                  className="form-card" 
                  style={{ 
                    padding: '1.25rem', 
                    cursor: 'pointer',
                    borderColor: selectedCase?._id === c._id ? 'hsl(var(--primary))' : 'hsl(var(--border))',
                    borderLeft: `5px solid ${c.risk_level === 'HIGH' ? 'red' : 'orange'}`,
                    transition: 'var(--transition)'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                    <h4 style={{ color: 'hsl(var(--primary))', fontWeight: 700 }}>{c.disease}</h4>
                    <span className={`badge badge-${c.risk_level.toLowerCase()}`}>{c.risk_level}</span>
                  </div>
                  <div style={{ fontSize: '0.85rem', color: 'hsl(var(--text-muted))' }}>
                    <p><strong>Animal Tag:</strong> {c.animal_id} ({c.animal_details?.breed})</p>
                    <p><strong>Location:</strong> {c.village}, {c.taluka}</p>
                    <p><strong>Reported:</strong> {new Date(c.detected_at).toLocaleDateString()}</p>
                  </div>
                </div>
              ))}

              {pendingCases.length === 0 && (
                <div style={{ textAlign: 'center', padding: '3rem', color: 'hsl(var(--text-muted))' }}>
                  <CheckCircle size={36} style={{ color: 'green', marginBottom: '1rem' }} />
                  <p>All clear! No pending suspected livestock cases requiring review.</p>
                </div>
              )}
            </div>
          </div>

          {/* Details & verification form panel */}
          <div>
            {selectedCase ? (
              <div className="form-card" style={{ border: '2px solid hsl(var(--border))' }}>
                <h3 style={{ fontSize: '1.3rem', fontWeight: 700, color: 'hsl(var(--primary))', marginBottom: '0.5rem' }}>
                  Evaluate Diagnostic Case
                </h3>
                
                {submitError && (
                  <div className="alert-banner high-risk" style={{ borderRadius: '8px' }}>
                    <AlertCircle size={16} />
                    <span>{submitError}</span>
                  </div>
                )}

                {/* Case overview */}
                <div style={{ 
                  backgroundColor: 'hsl(var(--bg-light))', 
                  padding: '1rem', 
                  borderRadius: '8px', 
                  marginBottom: '1.5rem',
                  fontSize: '0.85rem',
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  gap: '8px'
                }}>
                  <p><strong>Animal Breed:</strong> {selectedCase.animal_details?.breed}</p>
                  <p><strong>Age / Gender:</strong> {selectedCase.animal_details?.age} yrs / {selectedCase.animal_details?.gender}</p>
                  <p><strong>Reporter Village:</strong> {selectedCase.village}</p>
                  <p><strong>Coordinates:</strong> {selectedCase.location?.latitude.toFixed(4)}, {selectedCase.location?.longitude.toFixed(4)}</p>
                </div>

                {/* Form */}
                <form onSubmit={handleVerifySubmit}>
                  <div className="form-group">
                    <label className="form-label">Audit Assessment Action</label>
                    <select 
                      className="form-control" 
                      value={statusVal} 
                      onChange={(e) => setStatusVal(e.target.value)}
                    >
                      <option value="VERIFIED">Approve & Confirm Diagnosis (VERIFIED)</option>
                      <option value="REJECTED">Dismiss Case Flag (REJECTED)</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label className="form-label">{t('diagnosis')}</label>
                    <input 
                      type="text" 
                      className="form-control" 
                      placeholder="e.g. Confirmed Lumpy Skin Disease with mild skin lesions"
                      value={diagnosis}
                      onChange={(e) => setDiagnosis(e.target.value)}
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">{t('treatment_plan')}</label>
                    <textarea 
                      className="form-control" 
                      rows="3" 
                      placeholder="Input clinical prescription, hygiene rules, quarantine guidelines..."
                      value={treatment}
                      onChange={(e) => setTreatment(e.target.value)}
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">{t('follow_up')}</label>
                    <input 
                      type="text" 
                      className="form-control" 
                      placeholder="e.g. Inspect herd in 7 days, check for secondary lesions"
                      value={followUp}
                      onChange={(e) => setFollowUp(e.target.value)}
                    />
                  </div>

                  <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem' }}>
                    <button 
                      type="submit" 
                      className="btn btn-primary" 
                      style={{ flex: 1 }}
                      disabled={submitting}
                    >
                      {submitting ? 'Saving...' : 'Submit Verification'}
                    </button>
                    <button 
                      type="button" 
                      onClick={() => setSelectedCase(null)} 
                      className="btn btn-secondary"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              </div>
            ) : (
              <div style={{ 
                height: '100%', 
                display: 'flex', 
                flexDirection: 'column', 
                alignItems: 'center', 
                justifyContent: 'center',
                padding: '4rem',
                border: '2px dashed hsl(var(--border))',
                borderRadius: '12px',
                color: 'hsl(var(--text-muted))',
                textAlign: 'center'
              }}>
                <FileText size={48} style={{ marginBottom: '1rem' }} />
                <h4>Select a Case from the Review Queue</h4>
                <p style={{ fontSize: '0.85rem', maxWidth: '300px', margin: '4px 0' }}>
                  Click on any card to evaluate vital trends, verify predicted risk levels, and write treatment plans.
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 2: MAP */}
      {activeTab === 'map' && (
        <div>
          <h3 className="page-title">Geospatial Surveillance Map</h3>
          <p className="page-subtitle">Pune Region Case Locations & Active Outbreak Clusters Overlay</p>
          
          <div className="form-card" style={{ padding: '1rem' }}>
            <DiseaseMap cases={allCases} clusters={clusters} />
          </div>
        </div>
      )}
    </div>
  );
};

export default VetDashboard;
