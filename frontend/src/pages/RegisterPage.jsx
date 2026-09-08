import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { Activity, User, Lock, Phone, MapPin, AlertCircle, CheckCircle, ShieldCheck, Stethoscope, Sparkles } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input, Select } from '../components/ui/input';
import { Badge } from '../components/ui/badge';

const RegisterPage = () => {
  const [fullname, setFullname] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('FARMER');
  const [phone, setPhone] = useState('');
  const [village, setVillage] = useState('Wadgaon');
  const [taluka, setTaluka] = useState('Haveli');
  const [district, setDistrict] = useState('Pune');
  const [vetLicense, setVetLicense] = useState('');
  
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);
  
  const { register } = useAuth();
  const { t } = useLanguage();
  const navigate = useNavigate();

  const handleRoleSelect = (newRole) => {
    setRole(newRole);
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess(false);

    // Client-side Validation
    if (!fullname.trim()) {
      setError('Please provide your full name.');
      return;
    }
    if (!username.trim() || username.trim().length < 3) {
      setError('Username must be at least 3 characters long.');
      return;
    }
    if (!password || password.length < 5) {
      setError('Password must be at least 5 characters long.');
      return;
    }
    if (role === 'FARMER') {
      if (!village.trim() || !taluka.trim() || !district.trim()) {
        setError('Please complete all location fields for your farm (Village, Taluka, District).');
        return;
      }
    }
    if (role === 'VETERINARIAN') {
      if (!vetLicense.trim()) {
        setError('Please enter your Veterinary Council License number.');
        return;
      }
    }

    setLoading(true);

    const payload = {
      username: username.trim(),
      password: password.trim(),
      fullname: fullname.trim(),
      role,
      phone: phone.trim(),
      village: role === 'FARMER' ? village.trim() : '',
      taluka: role === 'FARMER' ? taluka.trim() : '',
      district: district.trim(),
      license_number: role === 'VETERINARIAN' ? vetLicense.trim() : ''
    };

    try {
      await register(payload);
      setSuccess(true);
      setTimeout(() => {
        navigate('/login');
      }, 1500);
    } catch (err) {
      setError(err.message || 'Registration failed. Please check inputs and try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-emerald-900/10 via-amber-500/5 to-emerald-950/15 py-12 px-4 sm:px-6 lg:px-8 font-['Outfit',sans-serif]">
      <div className="w-full max-w-xl">
        {/* Logo and Brand */}
        <div className="text-center mb-6">
          <Link to="/" className="inline-flex items-center gap-2.5 mb-2 hover:opacity-90 transition-opacity">
            <div className="w-12 h-12 rounded-2xl bg-emerald-800 text-amber-400 flex items-center justify-center shadow-lg shadow-emerald-900/20">
              <Activity size={28} />
            </div>
            <div className="text-left">
              <h1 className="text-xl font-black text-emerald-950 tracking-tight leading-tight">
                AI-Livestock Health Sentinel
              </h1>
              <span className="text-[11px] font-semibold text-emerald-700 tracking-wider uppercase">
                Early Outbreak Surveillance
              </span>
            </div>
          </Link>
          <p className="text-sm text-slate-600">
            Create an account to safeguard your herd and participate in regional disease surveillance
          </p>
        </div>

        <Card className="shadow-xl border-slate-200/80 bg-white/95 backdrop-blur">
          <CardHeader className="pb-4">
            <CardTitle className="text-xl font-bold text-slate-900">
              Create New Account
            </CardTitle>
            <CardDescription>
              Select your role and provide your operational details
            </CardDescription>

            {/* Role Switcher Tabs */}
            <div className="grid grid-cols-3 gap-2 pt-3">
              <button
                type="button"
                onClick={() => handleRoleSelect('FARMER')}
                className={`flex flex-col items-center justify-center p-3 rounded-xl border text-center transition-all cursor-pointer ${
                  role === 'FARMER'
                    ? 'border-emerald-600 bg-emerald-50 text-emerald-900 ring-2 ring-emerald-600/20 font-bold shadow-xs'
                    : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50'
                }`}
              >
                <span className="text-lg mb-1">🌾</span>
                <span className="text-xs font-semibold">Farmer</span>
              </button>

              <button
                type="button"
                onClick={() => handleRoleSelect('VETERINARIAN')}
                className={`flex flex-col items-center justify-center p-3 rounded-xl border text-center transition-all cursor-pointer ${
                  role === 'VETERINARIAN'
                    ? 'border-emerald-600 bg-emerald-50 text-emerald-900 ring-2 ring-emerald-600/20 font-bold shadow-xs'
                    : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50'
                }`}
              >
                <Stethoscope size={20} className={role === 'VETERINARIAN' ? 'text-emerald-700 mb-1' : 'text-slate-400 mb-1'} />
                <span className="text-xs font-semibold">Veterinarian</span>
              </button>

              <button
                type="button"
                onClick={() => handleRoleSelect('ADMIN')}
                className={`flex flex-col items-center justify-center p-3 rounded-xl border text-center transition-all cursor-pointer ${
                  role === 'ADMIN'
                    ? 'border-emerald-600 bg-emerald-50 text-emerald-900 ring-2 ring-emerald-600/20 font-bold shadow-xs'
                    : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50'
                }`}
              >
                <ShieldCheck size={20} className={role === 'ADMIN' ? 'text-emerald-700 mb-1' : 'text-slate-400 mb-1'} />
                <span className="text-xs font-semibold">District Admin</span>
              </button>
            </div>
          </CardHeader>

          <CardContent>
            {error && (
              <div className="mb-4 p-3.5 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm flex items-center gap-2.5">
                <AlertCircle size={18} className="shrink-0 text-red-600" />
                <span>{error}</span>
              </div>
            )}

            {success && (
              <div className="mb-4 p-3.5 rounded-xl bg-green-50 border border-green-200 text-green-800 text-sm flex items-center gap-2.5">
                <CheckCircle size={18} className="shrink-0 text-green-600" />
                <span>Account created successfully! Redirecting you to login...</span>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Full Name *
                  </label>
                  <Input
                    placeholder="e.g. Ramesh Patil"
                    value={fullname}
                    onChange={(e) => setFullname(e.target.value)}
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Username *
                  </label>
                  <Input
                    placeholder="e.g. ramesh_p"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Password *
                  </label>
                  <Input
                    type="password"
                    placeholder="Choose secure password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Phone Number
                  </label>
                  <Input
                    type="tel"
                    placeholder="+91 98XXXXXXXX"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                  />
                </div>
              </div>

              {/* Role-specific sections */}
              {role === 'FARMER' && (
                <div className="p-4 rounded-xl bg-emerald-50/60 border border-emerald-100 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-emerald-900 uppercase tracking-wide flex items-center gap-1.5">
                      <MapPin size={14} className="text-emerald-700" />
                      Farm Location Details
                    </span>
                    <Badge variant="low" className="text-[10px]">Privacy Protected</Badge>
                  </div>

                  <div className="grid grid-cols-3 gap-2">
                    <div>
                      <label className="block text-[11px] font-medium text-slate-600 mb-1">
                        Village *
                      </label>
                      <Input
                        placeholder="Village"
                        value={village}
                        onChange={(e) => setVillage(e.target.value)}
                        required={role === 'FARMER'}
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] font-medium text-slate-600 mb-1">
                        Taluka *
                      </label>
                      <Input
                        placeholder="Taluka"
                        value={taluka}
                        onChange={(e) => setTaluka(e.target.value)}
                        required={role === 'FARMER'}
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] font-medium text-slate-600 mb-1">
                        District *
                      </label>
                      <Select
                        value={district}
                        onChange={(e) => setDistrict(e.target.value)}
                      >
                        <option value="Pune">Pune</option>
                        <option value="Satara">Satara</option>
                        <option value="Kolhapur">Kolhapur</option>
                        <option value="Ahmednagar">Ahmednagar</option>
                        <option value="Solapur">Solapur</option>
                        <option value="Nashik">Nashik</option>
                      </Select>
                    </div>
                  </div>
                  <p className="text-[11px] text-emerald-800/80">
                    Exact farm coordinates are never disclosed to other farmers or public maps.
                  </p>
                </div>
              )}

              {role === 'VETERINARIAN' && (
                <div className="p-4 rounded-xl bg-blue-50/60 border border-blue-100 space-y-3">
                  <span className="text-xs font-bold text-blue-900 uppercase tracking-wide flex items-center gap-1.5">
                    <Stethoscope size={14} className="text-blue-700" />
                    Veterinary Accreditation
                  </span>
                  <div>
                    <label className="block text-[11px] font-medium text-slate-600 mb-1">
                      Veterinary Council Reg. / License No. *
                    </label>
                    <Input
                      placeholder="e.g. VCI-MH-2018-9842"
                      value={vetLicense}
                      onChange={(e) => setVetLicense(e.target.value)}
                      required={role === 'VETERINARIAN'}
                    />
                  </div>
                  <div>
                    <label className="block text-[11px] font-medium text-slate-600 mb-1">
                      Assigned District
                    </label>
                    <Select
                      value={district}
                      onChange={(e) => setDistrict(e.target.value)}
                    >
                      <option value="Pune">Pune Division</option>
                      <option value="Satara">Satara Division</option>
                      <option value="Kolhapur">Kolhapur Division</option>
                      <option value="Ahmednagar">Ahmednagar Division</option>
                    </Select>
                  </div>
                </div>
              )}

              {role === 'ADMIN' && (
                <div className="p-4 rounded-xl bg-amber-50/60 border border-amber-200/60 space-y-2">
                  <span className="text-xs font-bold text-amber-900 uppercase tracking-wide flex items-center gap-1.5">
                    <ShieldCheck size={14} className="text-amber-700" />
                    District Health Authority Officer
                  </span>
                  <div>
                    <label className="block text-[11px] font-medium text-slate-600 mb-1">
                      Surveillance Jurisdiction District
                    </label>
                    <Select
                      value={district}
                      onChange={(e) => setDistrict(e.target.value)}
                    >
                      <option value="Pune">Pune District Surveillance Unit</option>
                      <option value="Satara">Satara District Surveillance Unit</option>
                      <option value="Maharashtra State">Maharashtra State Directorate</option>
                    </Select>
                  </div>
                </div>
              )}

              <Button
                type="submit"
                variant="primary"
                size="lg"
                className="w-full mt-2"
                disabled={loading}
              >
                {loading ? 'Creating Account...' : `Register as ${role.charAt(0) + role.slice(1).toLowerCase()}`}
              </Button>
            </form>
          </CardContent>

          <CardFooter className="flex justify-center border-t border-slate-100 py-4">
            <p className="text-sm text-slate-600">
              Already have an account?{' '}
              <Link to="/login" className="font-semibold text-emerald-700 hover:text-emerald-800 hover:underline">
                Sign In here
              </Link>
            </p>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
};

export default RegisterPage;
