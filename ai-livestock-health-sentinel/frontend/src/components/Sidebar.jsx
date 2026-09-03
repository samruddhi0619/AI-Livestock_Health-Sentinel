import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { useSync } from '../context/SyncContext';
import { 
  LayoutDashboard, 
  PlusCircle, 
  Activity, 
  Map, 
  LogOut, 
  Globe, 
  ShieldCheck, 
  FileSpreadsheet, 
  Syringe, 
  Wifi, 
  WifiOff, 
  RefreshCw, 
  AlertTriangle 
} from 'lucide-react';

const Sidebar = () => {
  const { user, logout } = useAuth();
  const { language, setLanguage, t } = useLanguage();
  const { isOnline, pendingCount, syncStatus, syncPendingRecords } = useSync();
  const location = useLocation();
  
  if (!user) return null;
  
  const role = user.role.toUpperCase();
  
  // Custom navigation structure based on role
  const getNavLinks = () => {
    switch(role) {
      case 'FARMER':
        return [
          { name: t('dashboard'), path: '/farmer/dashboard', icon: LayoutDashboard },
          { name: t('animals_list'), path: '/farmer/animals', icon: FileSpreadsheet },
          { name: t('new_assessment'), path: '/farmer/health', icon: PlusCircle },
          { name: t('vaccination_status'), path: '/farmer/vaccinations', icon: Syringe }
        ];
      case 'VETERINARIAN':
        return [
          { name: t('dashboard'), path: '/veterinarian/dashboard', icon: LayoutDashboard },
          { name: t('recent_cases'), path: '/veterinarian/cases', icon: AlertTriangle },
          { name: t('geospatial_map'), path: '/veterinarian/map', icon: Map }
        ];
      case 'OFFICER':
        return [
          { name: t('dashboard'), path: '/officer/dashboard', icon: LayoutDashboard },
          { name: t('geospatial_map'), path: '/officer/map', icon: Map },
          { name: t('trends'), path: '/officer/trends', icon: Activity }
        ];
      case 'ADMIN':
        return [
          { name: 'Accounts Directory', path: '/admin/users', icon: ShieldCheck },
          { name: 'Model Configuration', path: '/admin/config', icon: LayoutDashboard },
          { name: 'Security Audit Logs', path: '/admin/audit', icon: FileSpreadsheet }
        ];
      default:
        return [];
    }
  };

  const navLinks = getNavLinks();

  return (
    <div className="sidebar" style={{
      width: '280px',
      backgroundColor: 'hsl(var(--primary))',
      color: '#ffffff',
      display: 'flex',
      flexDirection: 'column',
      padding: '2rem 1.5rem',
      justifyContent: 'space-between',
      boxShadow: '4px 0 20px rgba(0,0,0,0.05)'
    }}>
      <div>
        {/* Branding */}
        <div className="sidebar-brand" style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', marginBottom: '2.5rem' }}>
          <Activity size={28} className="text-accent" style={{ color: 'hsl(var(--accent))' }} />
          <div>
            <h1 style={{ fontSize: '1.15rem', fontWeight: 700, tracking: '-0.5px', lineHeight: '1.2' }}>
              {t('app_name').split('(')[0]}
            </h1>
            <span style={{ fontSize: '0.65rem', color: 'rgba(255,255,255,0.7)', textTransform: 'uppercase', letterSpacing: '1px' }}>
              Team MetaMinds
            </span>
          </div>
        </div>

        {/* User Info */}
        <div style={{
          background: 'rgba(255,255,255,0.06)',
          padding: '1rem',
          borderRadius: '8px',
          marginBottom: '2rem',
          border: '1px solid rgba(255,255,255,0.1)'
        }}>
          <p style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.6)', textTransform: 'uppercase' }}>
            {t(user.role.toLowerCase())}
          </p>
          <p style={{ fontSize: '0.95rem', fontWeight: 600 }}>{user.fullname}</p>
        </div>

        {/* Navigation links */}
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          {navLinks.map((link) => {
            const Icon = link.icon;
            const isActive = location.pathname === link.path;
            return (
              <Link 
                key={link.path} 
                to={link.path}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.75rem',
                  padding: '0.85rem 1rem',
                  borderRadius: '8px',
                  fontSize: '0.95rem',
                  fontWeight: 500,
                  transition: 'var(--transition)',
                  backgroundColor: isActive ? 'rgba(255,255,255,0.15)' : 'transparent',
                  color: isActive ? '#ffffff' : 'rgba(255,255,255,0.85)'
                }}
                className="nav-link"
              >
                <Icon size={18} />
                <span>{link.name}</span>
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Footer controls: Sync status, Language, Logout */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', marginTop: '2rem' }}>
        
        {/* Offline Sync Status Indicator */}
        <div style={{
          background: 'rgba(0,0,0,0.15)',
          padding: '0.75rem 1rem',
          borderRadius: '8px',
          fontSize: '0.85rem',
          border: '1px solid rgba(255,255,255,0.05)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
            <span style={{ color: 'rgba(255,255,255,0.6)' }}>{t('sync_status')}:</span>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
              {isOnline ? (
                <>
                  <Wifi size={14} className="text-success" style={{ color: '#4ade80' }} />
                  <span style={{ color: '#4ade80', fontWeight: 600 }}>{t('synced')}</span>
                </>
              ) : (
                <>
                  <WifiOff size={14} className="text-danger" style={{ color: '#f87171' }} />
                  <span style={{ color: '#f87171', fontWeight: 600 }}>{t('offline')}</span>
                </>
              )}
            </div>
          </div>
          {pendingCount > 0 && (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '0.25rem' }}>
              <span style={{ fontSize: '0.75rem', color: '#fbbf24' }}>
                {pendingCount} records pending
              </span>
              {isOnline && (
                <button 
                  onClick={syncPendingRecords}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: '#ffffff',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center'
                  }}
                  title="Sync now"
                >
                  <RefreshCw size={12} className={syncStatus === 'SYNCING' ? 'spin' : ''} />
                </button>
              )}
            </div>
          )}
        </div>

        {/* Multilingual Switcher */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', justifyContent: 'center' }}>
          <Globe size={16} style={{ color: 'rgba(255,255,255,0.6)' }} />
          <button 
            onClick={() => setLanguage('en')}
            style={{
              background: 'none',
              border: 'none',
              color: language === 'en' ? 'hsl(var(--accent))' : '#ffffff',
              fontWeight: language === 'en' ? 700 : 400,
              cursor: 'pointer'
            }}
          >
            EN
          </button>
          <span style={{ color: 'rgba(255,255,255,0.4)' }}>|</span>
          <button 
            onClick={() => setLanguage('mr')}
            style={{
              background: 'none',
              border: 'none',
              color: language === 'mr' ? 'hsl(var(--accent))' : '#ffffff',
              fontWeight: language === 'mr' ? 700 : 400,
              cursor: 'pointer'
            }}
          >
            मराठी
          </button>
        </div>

        {/* Logout */}
        <button 
          onClick={logout}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.5rem',
            padding: '0.75rem 1rem',
            backgroundColor: 'rgba(255,255,255,0.08)',
            border: 'none',
            borderRadius: '8px',
            color: '#ffffff',
            fontWeight: 600,
            cursor: 'pointer',
            transition: 'var(--transition)'
          }}
          onMouseOver={(e) => e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.15)'}
          onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.08)'}
        >
          <LogOut size={16} />
          <span>{t('logout')}</span>
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
