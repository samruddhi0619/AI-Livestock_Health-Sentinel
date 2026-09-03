import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { Activity, User, Lock, Phone, MapPin, AlertCircle, CheckCircle } from 'lucide-react';

const RegisterPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [fullname, setFullname] = useState('');
  const [role, setRole] = useState('FARMER');
  const [phone, setPhone] = useState('');
  const [village, setVillage] = useState('');
  const [taluka, setTaluka] = useState('');
  const [district, setDistrict] = useState('');
  
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);
  
  const { register } = useAuth();
  const { t } = useLanguage();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess(false);
    setLoading(true);

    const payload = {
      username,
      password,
      fullname,
      role,
      phone,
      village: role === 'FARMER' ? village : '',
      taluka: role === 'FARMER' ? taluka : '',
      district: role === 'FARMER' ? district : ''
    };

    try {
      await register(payload);
      setSuccess(true);
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (err) {
      setError(err.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, rgba(18,70,38,0.08) 0%, rgba(204,153,0,0.08) 100%)',
      fontFamily: "'Outfit', sans-serif",
      padding: '2.5rem 1.5rem'
    }}>
      <div style={{
        maxWidth: '500px',
        width: '100%',
        backgroundColor: '#ffffff',
        padding: '2.5rem',
        borderRadius: '16px',
        boxShadow: '0 20px 40px -8px rgba(18, 38, 24, 0.1)',
        border: '1px solid hsl(var(--border))'
      }}>
        <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '50px',
            height: '50px',
            borderRadius: '12px',
            backgroundColor: 'rgba(18,70,38,0.1)',
            color: 'hsl(var(--primary))',
            marginBottom: '0.75rem'
          }}>
            <Activity size={28} />
          </div>
          <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: 'hsl(var(--primary))' }}>
            {t('register')}
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'hsl(var(--text-muted))' }}>
            {t('app_name')}
          </p>
        </div>

        {error && (
          <div className="alert-banner high-risk" style={{ borderRadius: '8px' }}>
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        {success && (
          <div className="alert-banner" style={{ backgroundColor: 'rgba(16, 124, 65, 0.1)', borderColor: 'green', color: 'green', borderRadius: '8px' }}>
            <CheckCircle size={16} />
            <span>Registration successful! Redirecting to login...</span>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label" htmlFor="fullname">Full Name</label>
            <input 
              id="fullname"
              type="text" 
              className="form-control" 
              placeholder="e.g. Ramesh Patil"
              value={fullname}
              onChange={(e) => setFullname(e.target.value)}
              required
            />
          </div>

          <div className="grid-2">
            <div className="form-group">
              <label className="form-label" htmlFor="username">Username</label>
              <input 
                id="username"
                type="text" 
                className="form-control" 
                placeholder="Choose username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="password">Password</label>
              <input 
                id="password"
                type="password" 
                className="form-control" 
                placeholder="Choose password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="role">User Role</label>
            <select 
              id="role"
              className="form-control"
              value={role}
              onChange={(e) => setRole(e.target.value)}
            >
              <option value="FARMER">{t('farmer')}</option>
              <option value="VETERINARIAN">{t('veterinarian')}</option>
              <option value="OFFICER">{t('officer')}</option>
              <option value="ADMIN">{t('admin')}</option>
            </select>
          </div>

          {role === 'FARMER' && (
            <div style={{
              background: 'rgba(18,70,38,0.03)',
              padding: '1.25rem',
              borderRadius: '8px',
              border: '1px solid hsl(var(--border))',
              marginBottom: '1.5rem'
            }}>
              <h3 style={{ fontSize: '0.85rem', fontWeight: 700, textTransform: 'uppercase', marginBottom: '0.75rem', color: 'hsl(var(--primary))' }}>
                Farm Location Details
              </h3>
              
              <div className="form-group">
                <label className="form-label" htmlFor="phone">Phone Number</label>
                <div style={{ position: 'relative' }}>
                  <Phone size={14} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'hsl(var(--text-muted))' }} />
                  <input 
                    id="phone"
                    type="tel" 
                    className="form-control" 
                    style={{ paddingLeft: '32px' }}
                    placeholder="+91 XXXXX XXXXX"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    required
                  />
                </div>
              </div>

              <div className="grid-3" style={{ gap: '0.75rem' }}>
                <div className="form-group">
                  <label className="form-label" htmlFor="village">{t('village')}</label>
                  <input 
                    id="village"
                    type="text" 
                    className="form-control" 
                    placeholder="Village" 
                    value={village}
                    onChange={(e) => setVillage(e.target.value)}
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="form-label" htmlFor="taluka">{t('taluka')}</label>
                  <input 
                    id="taluka"
                    type="text" 
                    className="form-control" 
                    placeholder="Taluka"
                    value={taluka}
                    onChange={(e) => setTaluka(e.target.value)}
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="form-label" htmlFor="district">{t('district')}</label>
                  <input 
                    id="district"
                    type="text" 
                    className="form-control" 
                    placeholder="Pune"
                    value={district}
                    onChange={(e) => setDistrict(e.target.value)}
                    required
                  />
                </div>
              </div>
            </div>
          )}

          <button 
            type="submit" 
            className="btn btn-primary" 
            style={{ width: '100%', padding: '0.85rem', borderRadius: '8px', fontSize: '1rem', marginTop: '1rem' }}
            disabled={loading}
          >
            {loading ? 'Creating Account...' : t('register')}
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.85rem', color: 'hsl(var(--text-muted))' }}>
          Already have an account?{' '}
          <Link to="/login" style={{ color: 'hsl(var(--primary))', fontWeight: 600 }}>
            {t('login')}
          </Link>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
