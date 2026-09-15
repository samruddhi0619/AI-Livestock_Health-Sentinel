import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { useSync } from '../context/SyncContext';
import { useSidebar } from '../context/SidebarContext';
import { 
  LayoutDashboard, 
  PlusCircle, 
  Activity, 
  Map, 
  LogOut, 
  Globe, 
  ShieldCheck, 
  ListOrdered, 
  Syringe, 
  Wifi, 
  WifiOff, 
  RefreshCw, 
  AlertTriangle,
  Camera,
  FileText,
  Bell,
  Stethoscope,
  Layers,
  BarChart3,
  X
} from 'lucide-react';

const Sidebar = () => {
  const { user, logout } = useAuth();
  const { language, setLanguage, t } = useLanguage();
  const { isOnline, pendingCount, syncStatus, syncPendingRecords } = useSync();
  const { isSidebarOpen, closeSidebar } = useSidebar();
  const location = useLocation();
  
  if (!user) return null;
  
  const role = user.role.toUpperCase();
  
  // Custom navigation structure based on role
  const getNavLinks = () => {
    switch(role) {
      case 'FARMER':
        return [
          { name: t('nav_dashboard'), path: '/farmer/dashboard', icon: LayoutDashboard },
          { name: t('nav_my_animals'), path: '/farmer/animals', icon: ListOrdered },
          { name: t('nav_add_animal'), path: '/farmer/animals/add', icon: PlusCircle },
          { name: t('nav_report_issue'), path: '/farmer/report', icon: FileText },
          { name: t('nav_upload_image'), path: '/farmer/upload-image', icon: Camera },
          { name: t('nav_alerts'), path: '/farmer/alerts', icon: Bell }
        ];
      case 'VETERINARIAN':
        return [
          { name: t('nav_vet_dashboard'), path: '/veterinarian/dashboard', icon: LayoutDashboard },
          { name: t('nav_high_risk_cases'), path: '/veterinarian/cases', icon: AlertTriangle },
          { name: t('nav_health_history'), path: '/veterinarian/history', icon: Activity },
          { name: t('nav_potential_clusters'), path: '/veterinarian/clusters', icon: Layers }
        ];
      case 'OFFICER':
      case 'ADMIN':
        return [
          { name: t('nav_analytics_dashboard'), path: '/admin/dashboard', icon: BarChart3 },
          { name: t('nav_surveillance_map'), path: '/admin/map', icon: Map },
          { name: t('nav_cluster_mgmt'), path: '/admin/clusters', icon: Layers },
          { name: t('nav_system_alerts'), path: '/admin/alerts', icon: Bell }
        ];
      default:
        return [];
    }
  };

  const navLinks = getNavLinks();

  return (
    <>
      {/* Mobile backdrop overlay */}
      {isSidebarOpen && (
        <div 
          onClick={closeSidebar} 
          className="fixed inset-0 bg-slate-950/60 backdrop-blur-xs z-40 md:hidden transition-opacity"
          aria-hidden="true"
        />
      )}

      {/* Sidebar Navigation Panel */}
      <div 
        className={`bg-emerald-900 text-white flex flex-col justify-between p-6 shrink-0 shadow-xl transition-all duration-300 z-50 ${
          isSidebarOpen 
            ? 'fixed inset-y-0 left-0 w-72 h-full flex translate-x-0' 
            : 'fixed inset-y-0 left-0 w-72 h-full -translate-x-full md:translate-x-0 md:static md:w-64 lg:w-72 md:h-screen md:flex'
        }`}
      >
        <div>
          {/* Branding */}
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-amber-500/20 border border-amber-400/30 flex items-center justify-center text-amber-400 shrink-0">
                <Activity size={24} />
              </div>
              <div>
                <h1 className="text-base font-bold tracking-tight leading-snug">
                  {t('app_name')}
                </h1>
                <span className="text-[10px] text-emerald-300/80 uppercase tracking-widest font-semibold block">
                  AI Health Intelligence
                </span>
              </div>
            </div>
            
            {/* Close button for mobile drawer */}
            <button
              onClick={closeSidebar}
              className="p-1 text-emerald-300 hover:text-white md:hidden cursor-pointer"
              aria-label="Close sidebar"
            >
              <X size={20} />
            </button>
          </div>

          {/* User Badge */}
          <div className="bg-white/10 border border-white/10 rounded-xl p-3 mb-6">
            <p className="text-[10px] text-emerald-200/80 uppercase tracking-wider font-semibold">
              {t('logged_in_as')}
            </p>
            <p className="text-sm font-bold text-white truncate mt-0.5">
              {user.fullname || user.username}
            </p>
            <span className="inline-block text-[11px] font-medium text-emerald-300 mt-0.5">
              {t('role')}: {role}
            </span>
          </div>

          {/* Navigation Links */}
          <nav className="flex flex-col gap-1.5">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const isActive = location.pathname === link.path || (link.path !== '/' && location.pathname.startsWith(link.path + '/'));
              return (
                <Link 
                  key={link.path} 
                  to={link.path}
                  onClick={closeSidebar}
                  className={`flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all duration-150 cursor-pointer ${
                    isActive 
                      ? 'bg-emerald-800/90 text-white shadow-xs font-semibold border-l-4 border-amber-400 pl-3' 
                      : 'text-emerald-100/80 hover:bg-white/10 hover:text-white'
                  }`}
                >
                  <Icon size={18} className={isActive ? 'text-amber-400' : 'text-emerald-300/70'} />
                  <span>{link.name}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Footer controls: Sync status, Language, Logout */}
        <div className="flex flex-col gap-4 mt-8 pt-4 border-t border-emerald-800/80">
          {/* Offline Sync Status */}
          <div className="bg-black/20 rounded-xl p-3 text-xs border border-white/5">
            <div className="flex items-center justify-between">
              <span className="text-emerald-200/70">{t('device_mode')}:</span>
              <div className="flex items-center gap-1.5">
                {isOnline ? (
                  <>
                    <Wifi size={13} className="text-emerald-400" />
                    <span className="text-emerald-400 font-semibold">{t('online')}</span>
                  </>
                ) : (
                  <>
                    <WifiOff size={13} className="text-rose-400" />
                    <span className="text-rose-400 font-semibold">{t('offline')}</span>
                  </>
                )}
              </div>
            </div>
            {pendingCount > 0 && (
              <div className="flex items-center justify-between mt-2 pt-2 border-t border-white/10 text-amber-300">
                <span>{pendingCount} {t('records_queued')}</span>
                {isOnline && (
                  <button 
                    onClick={syncPendingRecords}
                    className="text-white hover:text-amber-300 transition-colors cursor-pointer"
                    title="Sync now"
                  >
                    <RefreshCw size={12} className={syncStatus === 'SYNCING' ? 'animate-spin' : ''} />
                  </button>
                )}
              </div>
            )}
          </div>

          {/* Language Switcher */}
          <div className="flex items-center justify-center gap-2 text-xs text-white/80">
            <Globe size={14} className="text-emerald-300" />
            <button 
              onClick={() => setLanguage('en')}
              className={`cursor-pointer transition-colors ${language === 'en' ? 'text-amber-400 font-bold' : 'hover:text-white'}`}
            >
              English
            </button>
            <span className="text-white/30">|</span>
            <button 
              onClick={() => setLanguage('mr')}
              className={`cursor-pointer transition-colors ${language === 'mr' ? 'text-amber-400 font-bold' : 'hover:text-white'}`}
            >
              मराठी
            </button>
          </div>

          {/* Logout */}
          <button 
            onClick={() => {
              closeSidebar();
              logout();
            }}
            className="flex items-center justify-center gap-2 w-full py-2.5 bg-red-600/20 hover:bg-red-600/30 text-rose-200 hover:text-white rounded-xl text-xs font-semibold transition-all border border-red-500/20 cursor-pointer"
          >
            <LogOut size={15} />
            <span>{t('sign_out')}</span>
          </button>
        </div>
      </div>
    </>
  );
};

export default Sidebar;
