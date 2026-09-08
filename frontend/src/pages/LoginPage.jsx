import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { HeartPulse, Lock, User, AlertCircle, ArrowRight, Tractor, Stethoscope, Shield } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/card';

const LoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
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
    <div className="min-h-screen flex items-center justify-center p-4 bg-linear-to-br from-emerald-50 via-slate-50 to-amber-50/40">
      <div className="w-full max-w-md">
        {/* Branding header */}
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-2.5 mb-2">
            <div className="w-10 h-10 rounded-xl bg-emerald-700 text-white flex items-center justify-center shadow-md">
              <HeartPulse size={22} />
            </div>
            <span className="text-xl font-black text-slate-900 tracking-tight">
              Livestock Sentinel
            </span>
          </Link>
          <p className="text-xs text-slate-500 font-medium">
            Sign in to access your livestock health & surveillance portal
          </p>
        </div>

        <Card className="shadow-xl border-slate-200/80 bg-white">
          <CardHeader className="pb-4">
            <CardTitle>Welcome Back</CardTitle>
            <CardDescription>Enter your credentials to continue</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-xs text-red-700 flex items-start gap-2">
                <AlertCircle size={16} className="shrink-0 mt-0.5" />
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleLogin} className="space-y-3.5">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Username
                </label>
                <div className="relative">
                  <User size={16} className="absolute left-3.5 top-3.5 text-slate-400" />
                  <Input 
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="Enter your username"
                    className="pl-10"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Password
                </label>
                <div className="relative">
                  <Lock size={16} className="absolute left-3.5 top-3.5 text-slate-400" />
                  <Input 
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="pl-10"
                    required
                  />
                </div>
              </div>

              <Button 
                type="submit" 
                variant="primary" 
                className="w-full mt-2" 
                disabled={loading}
              >
                {loading ? 'Signing In...' : 'Sign In to Portal'}
                <ArrowRight size={16} />
              </Button>
            </form>

            {/* Instant Demo Presets */}
            <div className="pt-4 border-t border-slate-100">
              <p className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2 text-center">
                1-Click Quick Demo Login:
              </p>
              <div className="grid grid-cols-3 gap-2">
                <button
                  type="button"
                  onClick={() => handleQuickPreset('farmer')}
                  className="flex flex-col items-center p-2.5 rounded-xl border border-emerald-200 bg-emerald-50/60 hover:bg-emerald-100/80 transition-colors text-emerald-900 cursor-pointer text-center"
                >
                  <Tractor size={18} className="mb-1 text-emerald-700" />
                  <span className="text-[11px] font-bold">Farmer</span>
                </button>
                <button
                  type="button"
                  onClick={() => handleQuickPreset('vet')}
                  className="flex flex-col items-center p-2.5 rounded-xl border border-blue-200 bg-blue-50/60 hover:bg-blue-100/80 transition-colors text-blue-900 cursor-pointer text-center"
                >
                  <Stethoscope size={18} className="mb-1 text-blue-700" />
                  <span className="text-[11px] font-bold">Veterinarian</span>
                </button>
                <button
                  type="button"
                  onClick={() => handleQuickPreset('admin')}
                  className="flex flex-col items-center p-2.5 rounded-xl border border-amber-200 bg-amber-50/60 hover:bg-amber-100/80 transition-colors text-amber-900 cursor-pointer text-center"
                >
                  <Shield size={18} className="mb-1 text-amber-700" />
                  <span className="text-[11px] font-bold">Admin</span>
                </button>
              </div>
            </div>

            <div className="text-center pt-2">
              <p className="text-xs text-slate-500">
                New to Sentinel?{' '}
                <Link to="/register" className="text-emerald-700 font-bold hover:underline">
                  Create an account
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
