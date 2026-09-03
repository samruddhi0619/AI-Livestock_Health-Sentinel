import React from 'react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { User, Bell } from 'lucide-react';

const Navbar = () => {
  const { user } = useAuth();
  const { t } = useLanguage();
  
  if (!user) return null;

  return (
    <header style={{
      height: '70px',
      backgroundColor: '#ffffff',
      borderBottom: '1px solid hsl(var(--border))',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 2rem',
      flexShrink: 0
    }}>
      <div>
        <h2 style={{ fontSize: '1.15rem', fontWeight: 600, color: 'hsl(var(--primary))' }}>
          {t('usp')}
        </h2>
      </div>
      
      <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
        {/* Mock Notification Bell */}
        <div style={{ position: 'relative', cursor: 'pointer', color: 'hsl(var(--text-muted))' }}>
          <Bell size={20} />
          <span style={{
            position: 'absolute',
            top: '-5px',
            right: '-5px',
            backgroundColor: 'hsl(var(--high-risk))',
            color: '#ffffff',
            fontSize: '0.65rem',
            padding: '2px 5px',
            borderRadius: '10px',
            fontWeight: 700
          }}>
            3
          </span>
        </div>

        {/* User Card */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <div style={{
            width: '35px',
            height: '35px',
            borderRadius: '50%',
            backgroundColor: 'hsl(var(--accent-light))',
            color: 'hsl(var(--accent))',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <User size={18} />
          </div>
          <span style={{ fontSize: '0.9rem', fontWeight: 500 }}>
            {user.fullname.split(' ')[0]}
          </span>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
