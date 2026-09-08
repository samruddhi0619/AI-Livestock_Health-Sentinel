import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { useAuth, API_BASE_URL } from '../../context/AuthContext';
import { useLanguage } from '../../context/LanguageContext';
import { useSync } from '../../context/SyncContext';
import { 
  PlusCircle, 
  FileText, 
  Syringe, 
  Bell, 
  Upload, 
  MapPin, 
  AlertTriangle, 
  CheckCircle2, 
  Info, 
  HelpCircle,
  BarChart2,
  Trash2,
  Activity,
  WifiOff
} from 'lucide-react';

const FarmerDashboard = () => {
  const { token, user } = useAuth();
  const { t, language } = useLanguage();
  const { isOnline, saveOfflineRecord, syncPendingRecords, pendingCount } = useSync();
  const location = useLocation();

  const [activeTab, setActiveTab] = useState('animals'); // animals, register, assessment, alerts
  
  useEffect(() => {
    if (location.pathname === '/farmer/dashboard' || location.pathname === '/farmer/animals') {
      setActiveTab('animals');
    } else if (location.pathname === '/farmer/health') {
      setActiveTab('assessment');
    } else if (location.pathname === '/farmer/vaccinations') {
      setActiveTab('alerts');
    }
  }, [location.pathname]);
  const [animals, setAnimals] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  // Animal registration form state
  const [breed, setBreed] = useState('');
  const [age, setAge] = useState('');
  const [gender, setGender] = useState('Female');
  const [healthHistory, setHealthHistory] = useState('None');
  const [lat, setLat] = useState('18.5204');
  const [lng, setLng] = useState('73.8567');
  const [village, setVillage] = useState('Wadgaon');
  const [taluka, setTaluka] = useState('Haveli');
  const [district, setDistrict] = useState('Pune');
  const [regSuccess, setRegSuccess] = useState('');

  // Assessment form state
  const [selectedAnimalId, setSelectedAnimalId] = useState('');
  const [selectedSymptoms, setSelectedSymptoms] = useState([]);
  const [temp, setTemp] = useState(38.5);
  const [appetite, setAppetite] = useState(1); // 0=None, 1=Normal, 2=High
  const [milk, setMilk] = useState(15.0);
  const [activity, setActivity] = useState(1); // 0=Low, 1=Normal, 2=High
  const [obs, setObs] = useState('');
  const [imageFile, setImageFile] = useState(null);
  
  // Assessment results
  const [imgUploading, setImgUploading] = useState(false);
  const [imgUrl, setImgUrl] = useState(null);
  const [imgQualityError, setImgQualityError] = useState('');
  const [cvResult, setCvResult] = useState(null);
  const [aiResult, setAiResult] = useState(null);
  const [offlineSaved, setOfflineSaved] = useState(false);

  // Alerts & Notifications
  const [alerts, setAlerts] = useState([]);

  // Fetch farmer data
  const fetchData = async () => {
    if (!token) return;
    setLoading(true);
    try {
      // 1. Fetch Animals
      const animRes = await fetch(`${API_BASE_URL}/api/animals`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (animRes.ok) {
        const animData = await animRes.ok ? await animRes.json() : [];
        setAnimals(animData);
        if (animData.length > 0) setSelectedAnimalId(animData[0]._id);
      }

      // 2. Fetch Farmer alerts / notifications
      const alertRes = await fetch(`${API_BASE_URL}/api/dashboard/farmer`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (alertRes.ok) {
        const dashboardData = await alertRes.json();
        setAlerts(dashboardData.alerts || []);
      }
    } catch (err) {
      console.error(err);
      setError('Connection to backend failed. Operating in Offline Sandbox mode.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [token]);

  // Capture GPS using browser geolocation
  const captureGPS = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLat(position.coords.latitude.toFixed(5));
          setLng(position.coords.longitude.toFixed(5));
        },
        (err) => {
          alert('GPS capture failed. Using default Pune coordinates.');
        }
      );
    } else {
      alert('Geolocation not supported by this browser.');
    }
  };

  // Register animal handler
  const handleRegisterAnimal = async (e) => {
    e.preventDefault();
    setRegSuccess('');
    setError('');

    const newAnimal = {
      species: 'Cattle',
      breed,
      age: parseFloat(age),
      gender,
      health_history: healthHistory,
      farm_id: user?.username || 'farmer_a',
      latitude: parseFloat(lat),
      longitude: parseFloat(lng),
      village,
      taluka,
      district
    };

    if (!isOnline) {
      // Mock local register for demo
      const mockId = `ANM-OFF-${Math.floor(100 + Math.random() * 900)}`;
      setAnimals([...animals, { ...newAnimal, _id: mockId, sync_status: 'PENDING' }]);
      setRegSuccess('Animal saved locally in browser cache. Sync pending connectivity.');
      setBreed(''); setAge('');
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/animals`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(newAnimal)
      });
      
      if (response.ok) {
        setRegSuccess('Cattle registered successfully!');
        setBreed(''); setAge('');
        fetchData();
      } else {
        const err = await response.json();
        setError(err.detail || 'Registration failed');
      }
    } catch (err) {
      setError('Failed to connect to backend.');
    }
  };

  // Symptom checklist helper
  const toggleSymptom = (symptom) => {
    if (selectedSymptoms.includes(symptom)) {
      setSelectedSymptoms(selectedSymptoms.filter(s => s !== symptom));
    } else {
      setSelectedSymptoms([...selectedSymptoms, symptom]);
    }
  };

  // Handle Photo upload with OpenCV quality check
  const handleImageUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    setImgUploading(true);
    setImgQualityError('');
    setCvResult(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_BASE_URL}/api/assessment/image`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      const resData = await response.json();
      if (response.ok && resData.success) {
        setImgUrl(resData.image_url);
        setCvResult(resData.cv_result);
      } else {
        setImgQualityError(resData.error || 'Poor image quality. Please upload a clearer photo.');
      }
    } catch (err) {
      setImgQualityError('Offline Mode: Image quality validation deferred until online.');
      // Create local object URL for display
      setImgUrl(URL.createObjectURL(file));
    } finally {
      setImgUploading(false);
    }
  };

  // Handle assessment submit
  const handleRunAssessment = async (e) => {
    e.preventDefault();
    setAiResult(null);
    setOfflineSaved(false);
    setError('');

    const payload = {
      symptoms: selectedSymptoms,
      temperature: parseFloat(temp),
      appetite: parseFloat(appetite),
      milk_production: parseFloat(milk),
      activity: parseFloat(activity),
      observations: obs,
      image_url: imgUrl,
      latitude: parseFloat(lat),
      longitude: parseFloat(lng)
    };

    if (!isOnline) {
      // Offline scenario - save in IndexedDB
      await saveOfflineRecord(selectedAnimalId, payload);
      setOfflineSaved(true);
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/assessment/submit/${selectedAnimalId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        const result = await response.json();
        setAiResult(result);
        fetchData(); // reload alerts
      } else {
        const err = await response.json();
        setError(err.detail || 'Assessment failed');
      }
    } catch (err) {
      setError('Connection lost. Saving to offline storage.');
      await saveOfflineRecord(selectedAnimalId, payload);
      setOfflineSaved(true);
    }
  };

  return (
    <div className="page-container">
      {/* Tab Switcher */}
      <div style={{ display: 'flex', gap: '1rem', borderBottom: '2px solid hsl(var(--border))', paddingBottom: '1rem', marginBottom: '2rem' }}>
        <button onClick={() => setActiveTab('animals')} className={`btn ${activeTab === 'animals' ? 'btn-primary' : 'btn-secondary'}`}>
          <FileText size={18} /> {t('animals_list')}
        </button>
        <button onClick={() => setActiveTab('register')} className={`btn ${activeTab === 'register' ? 'btn-primary' : 'btn-secondary'}`}>
          <PlusCircle size={18} /> {t('new_assessment').split(' ')[0]} Cattle
        </button>
        <button onClick={() => setActiveTab('assessment')} className={`btn ${activeTab === 'assessment' ? 'btn-primary' : 'btn-secondary'}`}>
          <Activity size={18} /> {t('new_assessment')}
        </button>
        <button onClick={() => setActiveTab('alerts')} className={`btn ${activeTab === 'alerts' ? 'btn-primary' : 'btn-secondary'}`}>
          <Bell size={18} /> {t('notifications')}
        </button>
      </div>

      {/* ERROR / WARNING BOARD */}
      {error && (
        <div className="alert-banner high-risk" style={{ borderRadius: '8px' }}>
          <AlertTriangle size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* TAB 1: ANIMAL LIST */}
      {activeTab === 'animals' && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
            <h3 className="page-title">{t('animals_list')}</h3>
            <span style={{ fontSize: '0.85rem', color: 'hsl(var(--text-muted))' }}>Total: {animals.length} cattle registered</span>
          </div>

          <div className="grid-3">
            {animals.map((a) => (
              <div key={a._id} className="form-card" style={{ padding: '1.5rem', position: 'relative' }}>
                {a.sync_status === 'PENDING' && (
                  <span className="badge badge-moderate" style={{ position: 'absolute', top: '15px', right: '15px', fontSize: '0.65rem' }}>
                    PENDING SYNC
                  </span>
                )}
                <h4 style={{ fontSize: '1.15rem', color: 'hsl(var(--primary))', fontWeight: 700 }}>{a.breed} (Cattle)</h4>
                <div style={{ margin: '0.75rem 0', fontSize: '0.9rem', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  <p><strong>Tag ID:</strong> {a._id}</p>
                  <p><strong>Age:</strong> {a.age} years</p>
                  <p><strong>Gender:</strong> {a.gender}</p>
                  <p><strong>Location:</strong> {a.village}, {a.taluka}</p>
                </div>
                <button 
                  onClick={() => { setSelectedAnimalId(a._id); setActiveTab('assessment'); }} 
                  className="btn btn-secondary" 
                  style={{ width: '100%', padding: '0.5rem', fontSize: '0.85rem' }}
                >
                  Diagnose Health
                </button>
              </div>
            ))}
            {animals.length === 0 && (
              <div style={{ gridColumn: '1/-1', textAlign: 'center', padding: '3rem', color: 'hsl(var(--text-muted))' }}>
                <Info size={36} style={{ marginBottom: '1rem' }} />
                <p>No animals registered yet. Register your cattle to perform health checks.</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 2: REGISTER CATTLE */}
      {activeTab === 'register' && (
        <div style={{ maxWidth: '600px', margin: '0 auto' }}>
          <h3 className="page-title">Register New Cattle</h3>
          <p className="page-subtitle">Add livestock details and spatial location to database</p>

          {regSuccess && (
            <div className="alert-banner" style={{ backgroundColor: 'rgba(16, 124, 65, 0.1)', borderColor: 'green', color: 'green', borderRadius: '8px' }}>
              <CheckCircle2 size={18} />
              <span>{regSuccess}</span>
            </div>
          )}

          <form onSubmit={handleRegisterAnimal} className="form-card">
            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">{t('breed')}</label>
                <select className="form-control" value={breed} onChange={(e) => setBreed(e.target.value)} required>
                  <option value="">Select Breed</option>
                  <option value="Gir">Gir</option>
                  <option value="Sahiwal">Sahiwal</option>
                  <option value="Holstein Friesian">Holstein Friesian</option>
                  <option value="Jersey">Jersey</option>
                  <option value="Indigenous">Indigenous</option>
                  <option value="Other">Other</option>
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">{t('age')}</label>
                <input type="number" step="0.1" className="form-control" placeholder="Age in years" value={age} onChange={(e) => setAge(e.target.value)} required />
              </div>
            </div>

            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">{t('gender')}</label>
                <select className="form-control" value={gender} onChange={(e) => setGender(e.target.value)}>
                  <option value="Female">{t('female')}</option>
                  <option value="Male">{t('male')}</option>
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">{t('health_history')}</label>
                <select className="form-control" value={healthHistory} onChange={(e) => setHealthHistory(e.target.value)}>
                  <option value="None">{t('vaccinated')} (Standard)</option>
                  <option value="Previous Illness">{t('previous_illness')}</option>
                  <option value="Chronic">{t('chronic_disease')}</option>
                </select>
              </div>
            </div>

            {/* Location block */}
            <div style={{ backgroundColor: 'rgba(0,0,0,0.02)', padding: '1rem', borderRadius: '8px', border: '1px solid hsl(var(--border))', marginBottom: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                <h4 style={{ fontSize: '0.85rem', fontWeight: 700 }}>Geospatial Positioning</h4>
                <button type="button" onClick={captureGPS} className="btn btn-secondary" style={{ padding: '4px 8px', fontSize: '0.75rem' }}>
                  <MapPin size={12} /> {t('get_gps')}
                </button>
              </div>
              <div className="grid-2" style={{ gap: '0.5rem', marginBottom: '0.75rem' }}>
                <div>
                  <label style={{ fontSize: '0.75rem', color: 'hsl(var(--text-muted))' }}>Latitude</label>
                  <input type="text" className="form-control" value={lat} onChange={(e) => setLat(e.target.value)} />
                </div>
                <div>
                  <label style={{ fontSize: '0.75rem', color: 'hsl(var(--text-muted))' }}>Longitude</label>
                  <input type="text" className="form-control" value={lng} onChange={(e) => setLng(e.target.value)} />
                </div>
              </div>
              <div className="grid-3" style={{ gap: '0.5rem' }}>
                <div>
                  <label style={{ fontSize: '0.75rem', color: 'hsl(var(--text-muted))' }}>{t('village')}</label>
                  <input type="text" className="form-control" value={village} onChange={(e) => setVillage(e.target.value)} />
                </div>
                <div>
                  <label style={{ fontSize: '0.75rem', color: 'hsl(var(--text-muted))' }}>{t('taluka')}</label>
                  <input type="text" className="form-control" value={taluka} onChange={(e) => setTaluka(e.target.value)} />
                </div>
                <div>
                  <label style={{ fontSize: '0.75rem', color: 'hsl(var(--text-muted))' }}>{t('district')}</label>
                  <input type="text" className="form-control" value={district} onChange={(e) => setDistrict(e.target.value)} />
                </div>
              </div>
            </div>

            <button type="submit" className="btn btn-primary" style={{ width: '100%' }}>Register Cattle</button>
          </form>
        </div>
      )}

      {/* TAB 3: DIAGNOSTIC SCANNER */}
      {activeTab === 'assessment' && (
        <div>
          <h3 className="page-title">{t('run_assessment')}</h3>
          <p className="page-subtitle">Submit physical symptoms and hide images for Hybrid validation</p>

          <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '2rem' }}>
            {/* Form */}
            <form onSubmit={handleRunAssessment} className="form-card">
              <div className="form-group">
                <label className="form-label">Select Registered Cattle</label>
                <select className="form-control" value={selectedAnimalId} onChange={(e) => setSelectedAnimalId(e.target.value)} required>
                  {animals.map(a => (
                    <option key={a._id} value={a._id}>{a.breed} (Tag: {a._id})</option>
                  ))}
                  {animals.length === 0 && <option value="">No cattle registered</option>}
                </select>
              </div>

              {/* Symptoms Checklist */}
              <div className="form-group">
                <label className="form-label">{t('symptoms')}</label>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px', padding: '0.5rem 0' }}>
                  {[
                    { id: 'fever', label: t('fever') },
                    { id: 'cough', label: t('cough') },
                    { id: 'loss_of_appetite', label: t('loss_of_appetite') },
                    { id: 'reduced_milk_production', label: t('reduced_milk_production') },
                    { id: 'nasal_discharge', label: t('nasal_discharge') },
                    { id: 'diarrhea', label: t('diarrhea') },
                    { id: 'breathing_difficulty', label: t('breathing_difficulty') },
                    { id: 'skin_abnormalities', label: t('skin_abnormalities') },
                    { id: 'swelling', label: t('swelling') },
                    { id: 'reduced_activity', label: t('reduced_activity') }
                  ].map((s) => (
                    <label key={s.id} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem', cursor: 'pointer' }}>
                      <input 
                        type="checkbox" 
                        checked={selectedSymptoms.includes(s.id)}
                        onChange={() => toggleSymptom(s.id)}
                      />
                      <span>{s.label}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Vitals inputs */}
              <div className="grid-2">
                <div className="form-group">
                  <label className="form-label">Body Temperature (°C)</label>
                  <input type="number" step="0.1" className="form-control" value={temp} onChange={(e) => setTemp(e.target.value)} />
                  <span style={{ fontSize: '0.7rem', color: 'hsl(var(--text-muted))' }}>Normal: 38.0 - 39.5°C</span>
                </div>
                <div className="form-group">
                  <label className="form-label">Milk Yield (Liters/day)</label>
                  <input type="number" step="0.5" className="form-control" value={milk} onChange={(e) => setMilk(e.target.value)} />
                </div>
              </div>

              <div className="grid-2">
                <div className="form-group">
                  <label className="form-label">Appetite Status</label>
                  <select className="form-control" value={appetite} onChange={(e) => setAppetite(e.target.value)}>
                    <option value="1">Normal</option>
                    <option value="2">High</option>
                    <option value="0">Reduced/Loss of Appetite</option>
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">Activity Status</label>
                  <select className="form-control" value={activity} onChange={(e) => setActivity(e.target.value)}>
                    <option value="1">Normal</option>
                    <option value="2">High</option>
                    <option value="0">Lethargic / Reduced Activity</option>
                  </select>
                </div>
              </div>

              {/* Image Upload Block */}
              <div className="form-group" style={{ border: '1px dashed hsl(var(--border))', padding: '1.25rem', borderRadius: '8px', textAlign: 'center' }}>
                <label className="form-label" style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                  <Upload size={16} /> {t('upload_image')}
                  <input type="file" accept="image/*" onChange={handleImageUpload} style={{ display: 'none' }} />
                </label>
                
                {imgUploading && <p style={{ fontSize: '0.8rem', color: 'hsl(var(--primary))', marginTop: '4px' }}>Running CV quality checks...</p>}
                {imgQualityError && <p style={{ fontSize: '0.8rem', color: 'hsl(var(--high-risk))', marginTop: '4px' }}>⚠️ {imgQualityError}</p>}
                
                {imgUrl && !imgQualityError && (
                  <div style={{ marginTop: '0.5rem' }}>
                    <p style={{ fontSize: '0.75rem', color: 'green', fontWeight: 600 }}>✓ Image validation passed</p>
                    <img src={imgUrl.startsWith('blob:') ? imgUrl : `${API_BASE_URL}${imgUrl}`} alt="symptom preview" style={{ height: '80px', borderRadius: '4px', marginTop: '4px', objectFit: 'cover' }} />
                  </div>
                )}
              </div>

              <button type="submit" className="btn btn-primary" style={{ width: '100%', gap: '8px' }}>
                <Activity size={18} /> {t('run_assessment')}
              </button>
            </form>

            {/* Results Column */}
            <div>
              {/* DISCLAIMER FOOTER */}
              <div style={{
                background: '#fffae6',
                border: '1px solid #ffe58f',
                padding: '1rem',
                borderRadius: '8px',
                fontSize: '0.8rem',
                color: '#d46b08',
                marginBottom: '1.5rem',
                lineHeight: '1.4'
              }}>
                <Info size={16} style={{ float: 'left', marginRight: '6px', marginTop: '2px' }} />
                <strong>Disclaimer:</strong> {t('disclaimer')}
              </div>

              {/* OFFLINE SAVED BANNER */}
              {offlineSaved && (
                <div style={{ backgroundColor: 'rgba(204,153,0,0.1)', border: '1px solid #cc9900', padding: '1.5rem', borderRadius: '12px', textAlign: 'center' }}>
                  <WifiOff size={40} style={{ color: '#cc9900', marginBottom: '0.5rem' }} />
                  <h4 style={{ fontWeight: 700 }}>Offline Mode Activated</h4>
                  <p style={{ fontSize: '0.85rem', color: 'hsl(var(--text-muted))', margin: '4px 0 1rem 0' }}>
                    Health record saved locally in IndexedDB storage. It will synchronize automatically once connectivity returns.
                  </p>
                  <span className="badge badge-moderate">Sync Pending</span>
                </div>
              )}

              {/* RENDER DIAGNOSIS */}
              {aiResult && (
                <div className="form-card" style={{ border: '2px solid hsl(var(--primary))' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                    <div>
                      <h4 style={{ fontSize: '0.8rem', color: 'hsl(var(--text-muted))', textTransform: 'uppercase' }}>AI Predicted Status</h4>
                      <h3 style={{ fontSize: '1.35rem', fontWeight: 800, color: 'hsl(var(--primary))' }}>{aiResult.assessment.possible_disease}</h3>
                    </div>
                    <span className={`badge badge-${aiResult.assessment.risk_level.toLowerCase()}`}>
                      {aiResult.assessment.risk_level} RISK
                    </span>
                  </div>

                  <div className="grid-2" style={{ marginBottom: '1rem' }}>
                    <div style={{ backgroundColor: 'hsl(var(--bg-light))', padding: '8px 12px', borderRadius: '6px' }}>
                      <span style={{ fontSize: '0.75rem', color: 'hsl(var(--text-muted))' }}>Risk Score</span>
                      <p style={{ fontSize: '1.2rem', fontWeight: 700 }}>{aiResult.assessment.risk_score}%</p>
                    </div>
                    <div style={{ backgroundColor: 'hsl(var(--bg-light))', padding: '8px 12px', borderRadius: '6px' }}>
                      <span style={{ fontSize: '0.75rem', color: 'hsl(var(--text-muted))' }}>Severity</span>
                      <p style={{ fontSize: '1.2rem', fontWeight: 700 }}>{aiResult.assessment.severity}</p>
                    </div>
                  </div>

                  {aiResult.assessment.is_anomaly && (
                    <div className="alert-banner high-risk" style={{ padding: '8px', fontSize: '0.8rem', marginBottom: '1rem' }}>
                      <AlertTriangle size={14} />
                      <span><strong>Warning:</strong> Anomalous vitals pattern detected by Anomaly Engine!</span>
                    </div>
                  )}

                  {/* SHAP graph breakdown */}
                  <div style={{ marginBottom: '1rem' }}>
                    <h5 style={{ fontSize: '0.85rem', fontWeight: 600, marginBottom: '6px' }}>{t('important_drivers')}</h5>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                      {aiResult.drivers.map((d, i) => (
                        <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.8rem' }}>
                          <span style={{ color: 'hsl(var(--text-muted))' }}>{d.feature}</span>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flex: 1, justifyContent: 'flex-end', marginLeft: '2rem' }}>
                            <div style={{ height: '6px', backgroundColor: '#e2e8f0', borderRadius: '3px', width: '80px', position: 'relative', overflow: 'hidden' }}>
                              <div style={{ height: '100%', backgroundColor: d.contribution >= 0 ? '#ef4444' : '#4ade80', width: `${Math.min(100, Math.abs(d.contribution) * 150)}%` }}></div>
                            </div>
                            <span style={{ fontWeight: 600, width: '40px', textAlign: 'right' }}>
                              {d.contribution >= 0 ? '+' : ''}{Math.round(d.contribution * 100)}%
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* CV details if any */}
                  {cvResult && (
                    <div style={{ backgroundColor: 'rgba(18,70,38,0.03)', padding: '10px', borderRadius: '6px', border: '1px solid hsl(var(--border))', fontSize: '0.8rem', marginBottom: '1rem' }}>
                      <strong style={{ display: 'block', color: 'hsl(var(--primary))', marginBottom: '2px' }}>Computer Vision Hide Scanner:</strong>
                      <p>{cvResult.visual_findings}</p>
                    </div>
                  )}

                  {/* Recommendations */}
                  <div>
                    <h5 style={{ fontSize: '0.85rem', fontWeight: 600, marginBottom: '4px' }}>{t('preventive_guidance')}</h5>
                    <ul style={{ fontSize: '0.8rem', color: 'hsl(var(--text-muted))', paddingLeft: '1.25rem', lineHeight: '1.4' }}>
                      {aiResult.guidance.map((g, idx) => (
                        <li key={idx} style={{ marginBottom: '2px' }}>{g}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* TAB 4: ALERTS */}
      {activeTab === 'alerts' && (
        <div>
          <h3 className="page-title">{t('notifications')}</h3>
          <p className="page-subtitle">Veterinary advice, alerts, and sync updates</p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', maxWidth: '800px' }}>
            {alerts.map((a, i) => (
              <div key={i} className="stat-card" style={{ gap: '1rem', borderLeft: `4px solid ${a.type === 'OUTBREAK_ALERT' ? '#ef4444' : 'hsl(var(--primary))'}` }}>
                <div style={{ color: a.type === 'OUTBREAK_ALERT' ? '#ef4444' : 'hsl(var(--primary))' }}>
                  <AlertTriangle size={24} />
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'hsl(var(--text-muted))' }}>{a.type}</span>
                    <span style={{ fontSize: '0.75rem', color: 'hsl(var(--text-muted))' }}>{new Date(a.created_at).toLocaleDateString()}</span>
                  </div>
                  <p style={{ fontSize: '0.9rem', marginTop: '2px', fontWeight: 500 }}>{a.message}</p>
                </div>
              </div>
            ))}
            {alerts.length === 0 && (
              <div style={{ textAlign: 'center', padding: '3rem', color: 'hsl(var(--text-muted))' }}>
                <CheckCircle2 size={36} style={{ color: 'green', marginBottom: '1rem' }} />
                <p>No active alerts. Your cattle are in a low-risk surveillance grid.</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default FarmerDashboard;
