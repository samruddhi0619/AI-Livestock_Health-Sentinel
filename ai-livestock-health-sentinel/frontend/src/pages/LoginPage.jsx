import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { Activity, Lock, User, AlertCircle } from 'lucide-react';

const LoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const { t } = useLanguage();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = await login(username, password);
      const role = data.role.toUpperCase();
      if (role === 'FARMER') {
        navigate('/farmer/dashboard');
      } else if (role === 'VETERINARIAN') {
        navigate('/veterinarian/dashboard');
      } else if (role === 'OFFICER') {
        navigate('/officer/dashboard');
      } else if (role === 'ADMIN') {
        navigate('/admin/dashboard');
      } else {
        navigate('/');
      }
    } catch (err) {
      setError(err.message || 'Invalid username or password');
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
      padding: '1.5rem'
    }}>
      <div style={{
        maxWidth: '420px',
        width: '100%',
        backgroundColor: '#ffffff',
        padding: '2.5rem',
        borderRadius: '16px',
        boxShadow: '0 20px 40px -8px rgba(18, 38, 24, 0.1)',
        border: '1px solid hsl(var(--border))'
      }}>
        {/* Branding header */}
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '54px',
            height: '54px',
            borderRadius: '12px',
            backgroundColor: 'rgba(18,70,38,0.1)',
            color: 'hsl(var(--primary))',
            marginBottom: '1rem'
          }}>
            <Activity size={32} />
          </div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: 'hsl(var(--primary))' }}>
            {t('login')}
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'hsl(var(--text-muted))', marginTop: '0.25rem' }}>
            {t('app_name')}
          </p>
        </div>

        {error && (
          <div className="alert-banner high-risk" style={{ marginBottom: '1.5rem', borderRadius: '8px' }}>
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label" htmlFor="username">Username</label>
            <div style={{ position: 'relative' }}>
              <User size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'hsl(var(--text-muted))' }} />
              <input 
                id="username"
                type="text" 
                className="form-control" 
                style={{ paddingLeft: '36px' }}
                placeholder="Enter username" 
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>
          </div>

          <div className="form-group" style={{ marginBottom: '2rem' }}>
            <label className="form-label" htmlFor="password">Password</label>
            <div style={{ position: 'relative' }}>
              <Lock size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'hsl(var(--text-muted))' }} />
              <input 
                id="password"
                type="password" 
                className="form-control" 
                style={{ paddingLeft: '36px' }}
                placeholder="Enter password" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
          </div>

          <button 
            type="submit" 
            className="btn btn-primary" 
            style={{ width: '100%', padding: '0.85rem', borderRadius: '8px', fontSize: '1rem' }}
            disabled={loading}
          >
            {loading ? 'Logging in...' : t('login')}
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.85rem', color: 'hsl(var(--text-muted))' }}>
          Don't have an account?{' '}
          <Link to="/register" style={{ color: 'hsl(var(--primary))', fontWeight: 600 }}>
            {t('register')}
          </Link>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
