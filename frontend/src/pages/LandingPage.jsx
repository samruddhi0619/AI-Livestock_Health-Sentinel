import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Activity, 
  ShieldAlert, 
  QrCode, 
  Map, 
  CheckCircle2, 
  ArrowRight, 
  Tractor, 
  Stethoscope, 
  Shield, 
  Sparkles,
  Layers,
  HeartPulse
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Badge, RiskBadge } from '../components/ui/badge';

const LandingPage = () => {
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleDemoLogin = async (role) => {
    try {
      if (role === 'farmer') {
        await login('farmer_ramesh', 'farmer123');
        navigate('/farmer/dashboard');
      } else if (role === 'vet') {
        await login('vet_sharma', 'vet12345');
        navigate('/veterinarian/dashboard');
      } else if (role === 'admin') {
        await login('admin_patil', 'admin123');
        navigate('/admin/dashboard');
      }
    } catch (e) {
      navigate('/login');
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 font-sans">
      {/* Top Navbar */}
      <header className="h-20 bg-white/95 backdrop-blur-md border-b border-slate-200 sticky top-0 z-40 px-4 sm:px-10 flex items-center justify-between shadow-xs">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-700 text-white flex items-center justify-center shadow-md">
            <HeartPulse size={24} />
          </div>
          <div>
            <h1 className="text-lg font-black text-emerald-950 tracking-tight leading-tight">
              AI-Livestock Health Sentinel
            </h1>
            <span className="text-[11px] font-semibold text-emerald-700 tracking-wide uppercase">
              Early Warning Disease Intelligence
            </span>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <Link to="/login">
            <Button variant="outline" size="sm">Sign In</Button>
          </Link>
          <Link to="/register">
            <Button variant="primary" size="sm">Register</Button>
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative overflow-hidden py-16 sm:py-24 px-4 sm:px-10 bg-linear-to-b from-emerald-50/70 via-white to-slate-50 border-b border-slate-200/60">
        <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          <div className="lg:col-span-7 space-y-6 text-left">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-amber-100 text-amber-900 border border-amber-300/60 text-xs font-bold uppercase tracking-wider">
              <Sparkles size={14} className="text-amber-600" />
              Smart India Hackathon 2026 Innovation
            </div>
            
            <h2 className="text-3xl sm:text-5xl font-black text-slate-950 tracking-tight leading-tight">
              Predicting livestock outbreaks <span className="text-emerald-700">before</span> they spread.
            </h2>
            
            <p className="text-base sm:text-lg text-slate-600 leading-relaxed max-w-xl">
              An AI-assisted early warning sentinel fusing visual lesion diagnosis, symptom analysis, 
              and environmental vector modeling with India’s Digital Animal Health Passport.
            </p>

            {/* Quick Demo Switcher */}
            <div className="pt-2">
              <p className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">
                1-Click Instant Demo Login:
              </p>
              <div className="flex flex-wrap gap-2.5">
                <Button 
                  variant="primary" 
                  size="md"
                  onClick={() => handleDemoLogin('farmer')}
                  className="bg-emerald-800 hover:bg-emerald-900"
                >
                  <Tractor size={16} />
                  <span>Enter as Farmer</span>
                </Button>
                <Button 
                  variant="secondary" 
                  size="md"
                  onClick={() => handleDemoLogin('vet')}
                  className="bg-blue-100 text-blue-900 hover:bg-blue-200"
                >
                  <Stethoscope size={16} />
                  <span>Enter as Veterinarian</span>
                </Button>
                <Button 
                  variant="outline" 
                  size="md"
                  onClick={() => handleDemoLogin('admin')}
                  className="border-slate-300"
                >
                  <Shield size={16} />
                  <span>Enter as Admin</span>
                </Button>
              </div>
            </div>

            {/* Platform Highlights */}
            <div className="pt-4 grid grid-cols-3 gap-4 border-t border-slate-200/80 text-left">
              <div>
                <p className="text-2xl font-black text-emerald-800">4-Tier</p>
                <p className="text-xs text-slate-500 font-medium mt-0.5">Transparent Risk Engine</p>
              </div>
              <div>
                <p className="text-2xl font-black text-emerald-800">DBSCAN</p>
                <p className="text-xs text-slate-500 font-medium mt-0.5">Spatio-Temporal Clusters</p>
              </div>
              <div>
                <p className="text-2xl font-black text-emerald-800">100%</p>
                <p className="text-xs text-slate-500 font-medium mt-0.5">Privacy-Guarded GPS</p>
              </div>
            </div>
          </div>

          {/* Interactive Hero Card */}
          <div className="lg:col-span-5">
            <Card className="shadow-xl border-emerald-100/80 bg-white p-6 relative overflow-hidden">
              <div className="flex items-center justify-between pb-4 border-b border-slate-100">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                  Live Sentinel Surveillance
                </span>
                <span className="flex items-center gap-1.5 text-xs font-semibold text-emerald-700">
                  <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
                  Realtime Active
                </span>
              </div>

              {/* Sample Livestock Triage Item */}
              <div className="mt-4 p-4 bg-slate-50 rounded-xl border border-slate-200/70 space-y-3">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-bold text-sm text-slate-900">Gir Cow (TAG-0824)</h4>
                    <p className="text-xs text-slate-500">Wagholi, Haveli • Age 4y</p>
                  </div>
                  <RiskBadge level="High" score={74.5} />
                </div>
                
                <div className="space-y-1.5 text-xs text-slate-600">
                  <div className="flex justify-between">
                    <span>Visual Lesion Risk (Image AI):</span>
                    <span className="font-bold text-slate-800">82%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Symptom Congruence:</span>
                    <span className="font-bold text-slate-800">76%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Environmental Vector Hazard:</span>
                    <span className="font-bold text-slate-800">65%</span>
                  </div>
                </div>

                <div className="p-2.5 bg-amber-50 rounded-lg border border-amber-200 text-[11px] text-amber-900 flex items-start gap-2">
                  <ShieldAlert size={16} className="text-amber-700 shrink-0 mt-0.5" />
                  <span>
                    <strong>Biosecurity Alert:</strong> Isolate animal in shaded pen immediately. Clinical review triggered.
                  </span>
                </div>
              </div>

              {/* Clear Risk Indicators Guide */}
              <div className="mt-4 pt-4 border-t border-slate-100">
                <p className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">
                  Transparent Risk Spectrum:
                </p>
                <div className="grid grid-cols-4 gap-1.5 text-center text-[11px]">
                  <div className="p-1.5 bg-emerald-50 text-emerald-800 rounded-md font-semibold border border-emerald-200">
                    Low (0-30)
                  </div>
                  <div className="p-1.5 bg-amber-50 text-amber-800 rounded-md font-semibold border border-amber-200">
                    Med (31-60)
                  </div>
                  <div className="p-1.5 bg-orange-50 text-orange-800 rounded-md font-semibold border border-orange-200">
                    High (61-80)
                  </div>
                  <div className="p-1.5 bg-red-50 text-red-800 rounded-md font-semibold border border-red-200">
                    Crit (81-100)
                  </div>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </section>

      {/* Core Platform Pillars */}
      <section className="py-16 px-4 sm:px-10 max-w-6xl mx-auto w-full">
        <div className="text-center max-w-2xl mx-auto mb-12">
          <h3 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
            Designed for Farmers. Trusted by Veterinarians.
          </h3>
          <p className="text-sm sm:text-base text-slate-600 mt-2">
            A unified ecosystem bridging farm-level reporting, automated multimodal AI triage, and statutory epidemiological control.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="p-6 hover:shadow-md transition-shadow">
            <div className="w-12 h-12 rounded-xl bg-emerald-100 text-emerald-800 flex items-center justify-center mb-4">
              <QrCode size={24} />
            </div>
            <h4 className="text-lg font-bold text-slate-900 mb-2">Digital Health Passport</h4>
            <p className="text-xs text-slate-600 leading-relaxed mb-4">
              Unique ear-tag QR codes cleanly separating farmer-reported records, AI risk screening, and certified veterinarian clinical reviews.
            </p>
            <div className="text-xs font-semibold text-emerald-700 flex items-center gap-1">
              <span>Dynamic QR Ledger</span>
              <ArrowRight size={14} />
            </div>
          </Card>

          <Card className="p-6 hover:shadow-md transition-shadow">
            <div className="w-12 h-12 rounded-xl bg-blue-100 text-blue-800 flex items-center justify-center mb-4">
              <Layers size={24} />
            </div>
            <h4 className="text-lg font-bold text-slate-900 mb-2">Multi-Modal Risk AI</h4>
            <p className="text-xs text-slate-600 leading-relaxed mb-4">
              Transparent synthesis of MobileNetV3 visual lesions, symptom tree models with SHAP explanations, and geospatial vector breeding risk.
            </p>
            <div className="text-xs font-semibold text-blue-700 flex items-center gap-1">
              <span>Explainable AI Triage</span>
              <ArrowRight size={14} />
            </div>
          </Card>

          <Card className="p-6 hover:shadow-md transition-shadow">
            <div className="w-12 h-12 rounded-xl bg-amber-100 text-amber-800 flex items-center justify-center mb-4">
              <Map size={24} />
            </div>
            <h4 className="text-lg font-bold text-slate-900 mb-2">Haversine DBSCAN Surveillance</h4>
            <p className="text-xs text-slate-600 leading-relaxed mb-4">
              Early detection of emerging risk patterns without false alarm escalation, maintaining strict agricultural privacy across OpenStreetMap.
            </p>
            <div className="text-xs font-semibold text-amber-700 flex items-center gap-1">
              <span>Cluster Intelligence</span>
              <ArrowRight size={14} />
            </div>
          </Card>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto py-8 px-4 sm:px-10 bg-white border-t border-slate-200 text-center text-xs text-slate-500">
        <p className="font-semibold text-slate-700">AI-Livestock Health Sentinel • SIH 2026 Prototype</p>
        <p className="mt-1 text-[11px] text-slate-400">
          AI-assisted screening and surveillance tool. Not a substitute for official veterinary diagnosis.
        </p>
      </footer>
    </div>
  );
};

export default LandingPage;
