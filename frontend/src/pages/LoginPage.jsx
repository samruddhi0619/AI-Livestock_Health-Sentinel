import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { HeartPulse, Lock, User, AlertCircle, ArrowRight, Tractor, Stethoscope, Shield, Globe } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/card';

const LoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const { language, setLanguage, t } = useLanguage();
  const navigate = useNavigate();

  const handleLogin = async (e, customUser = null, customPass = null) => {
    if (e) e.preventDefault();
    setError('');
    setLoading(true);

    const u = customUser || username;
    const p = customPass || password;

    try {
      const data = await login(u, p);
      const role = data.role.toUpperCase();
      if (role === 'FARMER') {
        navigate('/farmer/dashboard');
      } else if (role === 'VETERINARIAN') {
        navigate('/veterinarian/dashboard');
      } else if (role === 'OFFICER' || role === 'ADMIN') {
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

  const handleQuickPreset = (role) => {
    if (role === 'farmer') {
      setUsername('farmer_ramesh');
      setPassword('farmer123');
      handleLogin(null, 'farmer_ramesh', 'farmer123');
    } else if (role === 'vet') {
      setUsername('vet_sharma');
      setPassword('vet12345');
      handleLogin(null, 'vet_sharma', 'vet12345');
    } else if (role === 'admin') {
      setUsername('admin_patil');
      setPassword('admin123');
      handleLogin(null, 'admin_patil', 'admin123');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-emerald-50 via-slate-50 to-amber-50/40 font-['Outfit',sans-serif]">
      <div className="w-full max-w-md">
        {/* Branding header */}
        <div className="text-center mb-6">
          <Link to="/" className="inline-flex items-center gap-2.5 mb-2">
            <div className="w-10 h-10 rounded-xl bg-emerald-700 text-white flex items-center justify-center shadow-md">
              <HeartPulse size={22} />
            </div>
            <span className="text-xl font-black text-slate-900 tracking-tight">
              {t('app_name')}
            </span>
          </Link>
          <p className="text-xs text-slate-500 font-medium">
            {t('usp')}
          </p>

          {/* Public Language Switcher Pill */}
          <div className="inline-flex items-center justify-center gap-2 px-3 py-1 bg-white border border-slate-200 rounded-full text-xs text-slate-600 mt-3 shadow-2xs">
            <Globe size={13} className="text-emerald-600" />
            <button 
              onClick={() => setLanguage('en')}
              className={`cursor-pointer transition-colors ${language === 'en' ? 'text-emerald-700 font-bold' : 'hover:text-slate-900'}`}
            >
              English
            </button>
            <span className="text-slate-300">|</span>
            <button 
              onClick={() => setLanguage('mr')}
              className={`cursor-pointer transition-colors ${language === 'mr' ? 'text-emerald-700 font-bold' : 'hover:text-slate-900'}`}
            >
              मराठी
            </button>
          </div>
        </div>

        <Card className="shadow-xl border-slate-200/80 bg-white">
          <CardHeader className="pb-4 flex flex-col gap-1">
            <CardTitle className="text-xl font-bold text-slate-900">{t('welcome_back')}</CardTitle>
            <CardDescription className="text-xs text-slate-500">{t('enter_credentials')}</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-4 p-6 pt-2">
            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-xs text-red-700 flex items-start gap-2">
                <AlertCircle size={16} className="shrink-0 mt-0.5" />
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleLogin} className="flex flex-col gap-4">
              <div className="flex flex-col gap-1.5">
                <label className="block text-xs font-semibold text-slate-700">
                  {t('username')}
                </label>
                <div className="relative flex items-center">
                  <User size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none z-10" />
                  <Input 
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder={t('username')}
                    className="pl-10 h-11 w-full"
                    required
                  />
                </div>
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="block text-xs font-semibold text-slate-700">
                  {t('password')}
                </label>
                <div className="relative flex items-center">
                  <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none z-10" />
                  <Input 
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="pl-10 h-11 w-full"
                    required
                  />
                </div>
              </div>

              <Button 
                type="submit" 
                variant="primary" 
                className="w-full mt-2 h-11 font-semibold text-sm flex items-center justify-center gap-2" 
                disabled={loading}
              >
                {loading ? `${t('login')}...` : t('sign_in_portal')}
                <ArrowRight size={16} />
              </Button>
            </form>

            {/* Instant Demo Presets */}
            <div className="pt-4 border-t border-slate-100 flex flex-col gap-2.5">
              <p className="text-[11px] font-bold text-slate-400 uppercase tracking-wider text-center">
                {t('quick_demo_login')}:
              </p>
              <div className="grid grid-cols-3 gap-2.5">
                <button
                  type="button"
                  onClick={() => handleQuickPreset('farmer')}
                  className="flex flex-col items-center justify-center py-2.5 px-2 rounded-xl border border-emerald-200 bg-emerald-50/60 hover:bg-emerald-100/80 transition-all text-emerald-900 cursor-pointer text-center gap-1 min-h-[56px]"
                >
                  <Tractor size={18} className="text-emerald-700 shrink-0" />
                  <span className="text-[11px] font-bold leading-none">{t('farmer')}</span>
                </button>
                <button
                  type="button"
                  onClick={() => handleQuickPreset('vet')}
                  className="flex flex-col items-center justify-center py-2.5 px-2 rounded-xl border border-blue-200 bg-blue-50/60 hover:bg-blue-100/80 transition-all text-blue-900 cursor-pointer text-center gap-1 min-h-[56px]"
                >
                  <Stethoscope size={18} className="text-blue-700 shrink-0" />
                  <span className="text-[11px] font-bold leading-none">{t('veterinarian')}</span>
                </button>
                <button
                  type="button"
                  onClick={() => handleQuickPreset('admin')}
                  className="flex flex-col items-center justify-center py-2.5 px-2 rounded-xl border border-amber-200 bg-amber-50/60 hover:bg-amber-100/80 transition-all text-amber-900 cursor-pointer text-center gap-1 min-h-[56px]"
                >
                  <Shield size={18} className="text-amber-700 shrink-0" />
                  <span className="text-[11px] font-bold leading-none">{t('admin')}</span>
                </button>
              </div>
            </div>

            <div className="text-center pt-2">
              <p className="text-xs text-slate-500">
                {t('new_to_sentinel')}{' '}
                <Link to="/register" className="text-emerald-700 font-bold hover:underline">
                  {t('create_account')}
                </Link>
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default LoginPage;
