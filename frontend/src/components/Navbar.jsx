import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { User, Bell, Shield, Stethoscope, Tractor } from 'lucide-react';

const Navbar = () => {
  const { user, token } = useAuth();
  const { t } = useLanguage();
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    if (!token) return;
    const fetchUnread = async () => {
      try {
        const res = await fetch('/api/alerts/unread-count', {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          setUnreadCount(data.total_unread || 0);
        }
      } catch (e) {
        // Fallback or silent catch
      }
    };
    fetchUnread();
    const interval = setInterval(fetchUnread, 30000); // 30s poll
    return () => clearInterval(interval);
  }, [token]);
  
  if (!user) return null;

  const role = user.role.toUpperCase();
  const alertsPath = role === 'FARMER' ? '/farmer/alerts' : (role === 'ADMIN' || role === 'OFFICER' ? '/admin/alerts' : '/veterinarian/dashboard');

  const getRoleBadge = () => {
    switch(role) {
      case 'FARMER':
        return (
          <span className="flex items-center gap-1 text-xs font-semibold px-2.5 py-1 bg-emerald-100 text-emerald-800 rounded-full">
            <Tractor size={12} /> Farmer
          </span>
        );
      case 'VETERINARIAN':
        return (
          <span className="flex items-center gap-1 text-xs font-semibold px-2.5 py-1 bg-blue-100 text-blue-800 rounded-full">
            <Stethoscope size={12} /> Veterinarian
          </span>
        );
      case 'ADMIN':
      case 'OFFICER':
        return (
          <span className="flex items-center gap-1 text-xs font-semibold px-2.5 py-1 bg-amber-100 text-amber-800 rounded-full">
            <Shield size={12} /> District Officer
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <header className="h-16 bg-white border-b border-slate-200 px-4 sm:px-8 flex items-center justify-between shrink-0 shadow-xs">
      <div className="flex items-center gap-3">
        <h2 className="text-base sm:text-lg font-bold text-slate-800 tracking-tight">
          AI-Livestock Health Sentinel
        </h2>
        <span className="hidden md:inline-block text-xs text-slate-400 font-medium">|</span>
        <span className="hidden md:inline-block text-xs font-medium text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-md border border-emerald-200/60">
          SIH 2026 Sentinel
        </span>
      </div>
      
      <div className="flex items-center gap-4 sm:gap-6">
        {/* Notification Bell */}
        <Link 
          to={alertsPath}
          className="relative p-2 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-xl transition-colors cursor-pointer"
          title="View In-App Alerts"
        >
          <Bell size={20} />
          {unreadCount > 0 && (
            <span className="absolute top-1 right-1 flex items-center justify-center min-w-[18px] h-[18px] bg-red-600 text-white text-[10px] font-bold px-1 rounded-full animate-pulse shadow-xs">
              {unreadCount > 99 ? '99+' : unreadCount}
            </span>
          )}
        </Link>

        {/* Role Badge */}
        <div className="hidden sm:flex">
          {getRoleBadge()}
        </div>

        {/* User Profile Pill */}
        <div className="flex items-center gap-2.5 pl-2 sm:border-l sm:border-slate-200">
          <div className="w-8 h-8 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold text-sm">
            {user.fullname ? user.fullname[0].toUpperCase() : <User size={16} />}
          </div>
          <div className="hidden lg:block text-left">
            <p className="text-xs font-semibold text-slate-800 leading-tight">
              {user.fullname || user.username}
            </p>
            <p className="text-[11px] text-slate-400 leading-tight">
              {user.username}
            </p>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
