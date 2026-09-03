import React from 'react';
import { Link } from 'react-router-dom';
import { Activity, ShieldAlert, MapPin, Award, CheckCircle } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

const LandingPage = () => {
  const { t } = useLanguage();

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: 'hsl(var(--bg-light))', fontFamily: "'Outfit', sans-serif" }}>
      {/* Navbar */}
      <nav style={{ height: '80px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0 4rem', backgroundColor: '#ffffff', borderBottom: '1px solid hsl(var(--border))' }}>
        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <Activity size={32} style={{ color: 'hsl(var(--primary))' }} />
          <div>
            <h1 style={{ fontSize: '1.4rem', fontWeight: 800, color: 'hsl(var(--primary))', lineHeight: '1.1' }}>
              {t('app_name').split('(')[0]}
            </h1>
            <span style={{ fontSize: '0.7rem', color: 'hsl(var(--text-muted))', fontWeight: 600 }}>SIH 2026 PROTOTYPE</span>
          </div>
        </div>
        <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'center' }}>
          <Link to="/login" className="btn btn-secondary" style={{ padding: '0.5rem 1.25rem', fontSize: '0.9rem' }}>
            {t('login')}
          </Link>
          <Link to="/register" className="btn btn-primary" style={{ padding: '0.5rem 1.25rem', fontSize: '0.9rem' }}>
            {t('register')}
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section style={{
        flex: 1,
        padding: '5rem 4rem',
        background: 'linear-gradient(135deg, rgba(18,70,38,0.05) 0%, rgba(204,153,0,0.05) 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '4rem'
      }}>
        <div style={{ maxWidth: '600px' }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.5rem',
            backgroundColor: 'hsl(var(--accent-light))',
            color: 'hsl(var(--accent))',
            padding: '0.35rem 1rem',
            borderRadius: '20px',
            fontSize: '0.8rem',
            fontWeight: 700,
            textTransform: 'uppercase',
            marginBottom: '1.5rem'
          }}>
            <Award size={14} /> Smart India Hackathon 2026 (SIH26128)
          </div>
          <h2 style={{ fontSize: '3rem', fontWeight: 800, color: 'hsl(var(--primary))', lineHeight: '1.1', marginBottom: '1.5rem' }}>
            {t('app_name')}
          </h2>
          <p style={{ fontSize: '1.2rem', color: 'hsl(var(--text-main))', fontWeight: 500, marginBottom: '0.5rem' }}>
            {t('usp')}
          </p>
          <p style={{ fontSize: '1rem', color: 'hsl(var(--text-muted))', lineHeight: '1.6', marginBottom: '2.5rem' }}>
            "We are not building just a livestock disease prediction system; we are building an integrated early-warning and health-management platform that connects animal-level risk assessment with farm-level and regional disease surveillance."
          </p>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <Link to="/register" className="btn btn-primary" style={{ padding: '1rem 2rem', fontSize: '1.05rem', borderRadius: '10px' }}>
              Create Account
            </Link>
            <Link to="/login" className="btn btn-secondary" style={{ padding: '1rem 2rem', fontSize: '1.05rem', borderRadius: '10px' }}>
              Access Dashboard
            </Link>
          </div>
        </div>
        
        {/* Decorative Grid */}
        <div style={{
          backgroundColor: '#ffffff',
          borderRadius: '24px',
          boxShadow: '0 25px 50px -12px rgba(18, 38, 24, 0.15)',
          padding: '2.5rem',
          border: '1px solid hsl(var(--border))',
          width: '450px',
          display: 'flex',
          flexDirection: 'column',
          gap: '1.5rem'
        }}>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, borderBottom: '2px solid hsl(var(--accent-light))', paddingBottom: '0.5rem', color: 'hsl(var(--primary))' }}>
            Core Capabilities
          </h3>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
            <div style={{ padding: '0.5rem', borderRadius: '8px', backgroundColor: 'rgba(18,70,38,0.1)', color: 'hsl(var(--primary))' }}>
              <CheckCircle size={20} />
            </div>
            <div>
              <h4 style={{ fontWeight: 600, fontSize: '0.95rem' }}>Dual AI-Engine Diagnostic Validation</h4>
              <p style={{ fontSize: '0.85rem', color: 'hsl(var(--text-muted))' }}>Combines symptom-based XGBoost with custom OpenCV hide scanning.</p>
            </div>
          </div>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
            <div style={{ padding: '0.5rem', borderRadius: '8px', backgroundColor: 'rgba(18,70,38,0.1)', color: 'hsl(var(--primary))' }}>
              <ShieldAlert size={20} />
            </div>
            <div>
              <h4 style={{ fontWeight: 600, fontSize: '0.95rem' }}>Isolation Forest Anomaly Checking</h4>
              <p style={{ fontSize: '0.85rem', color: 'hsl(var(--text-muted))' }}>Flags unusual milk-production or body-temperature drops automatically.</p>
            </div>
          </div>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
            <div style={{ padding: '0.5rem', borderRadius: '8px', backgroundColor: 'rgba(18,70,38,0.1)', color: 'hsl(var(--primary))' }}>
              <MapPin size={20} />
            </div>
            <div>
              <h4 style={{ fontWeight: 600, fontSize: '0.95rem' }}>DBSCAN Outbreak Clustering</h4>
              <p style={{ fontSize: '0.85rem', color: 'hsl(var(--text-muted))' }}>Identifies active disease clusters inside rural grids using geolocations.</p>
            </div>
          </div>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
            <div style={{ padding: '0.5rem', borderRadius: '8px', backgroundColor: 'rgba(18,70,38,0.1)', color: 'hsl(var(--primary))' }}>
              <Award size={20} />
            </div>
            <div>
              <h4 style={{ fontWeight: 600, fontSize: '0.95rem' }}>Offline Capture & Automatic Sync</h4>
              <p style={{ fontSize: '0.85rem', color: 'hsl(var(--text-muted))' }}>IndexedDB browser database stores assessments during zero connectivity.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Info Footnote */}
      <footer style={{ backgroundColor: 'hsl(var(--primary))', color: 'rgba(255,255,255,0.8)', padding: '2rem 4rem', fontSize: '0.85rem', borderTop: '4px solid hsl(var(--accent))' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <p><strong>Government Sponsor:</strong> Department of Animal Husbandry, Government of Maharashtra</p>
            <p><strong>Development Team:</strong> MetaMinds (SIH26128 Prototype)</p>
          </div>
          <div style={{ textAlign: 'right' }}>
            <p>Official References: <a href="https://dahd.gov.in" target="_blank" style={{ color: 'hsl(var(--accent))', fontWeight: 600 }}>dahd.gov.in</a> | <a href="https://icar.org.in" target="_blank" style={{ color: 'hsl(var(--accent))', fontWeight: 600 }}>icar.org.in</a></p>
            <p>© 2026 AI-Livestock Health Sentinel. All Rights Reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
