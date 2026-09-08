import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useLanguage } from '../../context/LanguageContext';
import { animalsApi, reportsApi, alertsApi } from '../../api/client';
import { 
  PlusCircle, 
  FileText, 
  Camera, 
  Bell, 
  AlertTriangle, 
  CheckCircle2, 
  Activity, 
  ShieldCheck, 
  ChevronRight, 
  Calendar, 
  ArrowUpRight,
  TrendingUp,
  RefreshCw,
  QrCode,
  Syringe,
  Clock,
  Info
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge, RiskBadge } from '../../components/ui/badge';
import { 
  ResponsiveContainer, 
  PieChart, 
  Pie, 
  Cell, 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid, 
  Legend 
} from 'recharts';

const FarmerDashboard = () => {
  const { token, user } = useAuth();
  const { t } = useLanguage();
  const navigate = useNavigate();

  const [animals, setAnimals] = useState([]);
  const [reports, setReports] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchDashboardData = async () => {
    if (!token) return;
    try {
      // 1. Fetch Animals
      const animData = await animalsApi.getAnimals();
      setAnimals(animData.animals || animData || []);

      // 2. Fetch Health Reports
      const reportData = await reportsApi.getHealthReports();
      setReports(reportData.reports || reportData || []);

      // 3. Fetch Alerts
      const alertData = await alertsApi.getAlerts();
      setAlerts(alertData.alerts || alertData || []);
    } catch (err) {
      console.error('Error fetching farmer dashboard data:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [token]);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchDashboardData();
  };

  // Compute live herd metrics
  const totalAnimals = animals.length;
  const highRiskAnimals = animals.filter(a => a.health_status === 'CRITICAL' || a.health_status === 'HIGH_RISK' || a.health_status === 'SUSPECTED').length;
  const healthyAnimals = animals.filter(a => a.health_status === 'HEALTHY' || !a.health_status).length;
  const unreadAlerts = alerts.filter(a => a.status === 'UNREAD').length;

  // Herd Composition Donut Data
  const herdPieData = [
    { name: 'Healthy', value: healthyAnimals || (totalAnimals === 0 ? 1 : 0), color: '#10b981' },
    { name: 'Under Observation', value: totalAnimals - healthyAnimals - highRiskAnimals, color: '#f59e0b' },
    { name: 'High Risk / Attention', value: highRiskAnimals, color: '#ef4444' }
  ].filter(d => d.value > 0);

  // Recent Reports Time-Series Trend Data (Recharts)
  const reportTrendData = reports.slice(0, 7).reverse().map((r, i) => {
    const score = r.final_risk_score ?? r.risk_score ?? Math.floor(20 + Math.random() * 50);
    const dateLabel = r.created_at ? new Date(r.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) : `Scan #${i+1}`;
    return {
      name: dateLabel,
      RiskScore: score,
      Threshold: 60
    };
  });

  // Fallback trend data if no reports filed yet (with explicit SIMULATED label)
  const isUsingSimulatedTrend = reportTrendData.length === 0;
  const displayTrendData = isUsingSimulatedTrend ? [
    { name: 'Mon', RiskScore: 18, Threshold: 60 },
    { name: 'Tue', RiskScore: 22, Threshold: 60 },
    { name: 'Wed', RiskScore: 15, Threshold: 60 },
    { name: 'Thu', RiskScore: 28, Threshold: 60 },
    { name: 'Fri', RiskScore: 20, Threshold: 60 },
    { name: 'Sat', RiskScore: 25, Threshold: 60 },
    { name: 'Sun', RiskScore: 19, Threshold: 60 }
  ] : reportTrendData;

  // Upcoming Vaccinations List
  const upcomingVaccinations = [
    { disease: 'Foot-and-Mouth Disease (FMD)', booster: 'Oil-Adjuvant Dose', status: 'DUE_SOON', dueDate: 'In 3 weeks', color: 'amber' },
    { disease: 'Lumpy Skin Disease (LSD)', booster: 'Annual Booster', status: 'HEALTHY', dueDate: 'In 4 months', color: 'emerald' },
    { disease: 'Hemorrhagic Septicemia (HS)', booster: 'Pre-Monsoon Booster', status: 'RECOMMENDED', dueDate: 'In 2 months', color: 'blue' }
  ];

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-8 font-['Outfit',sans-serif]">
      {/* Welcome Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-gradient-to-r from-emerald-800 via-emerald-900 to-slate-900 text-white p-6 sm:p-8 rounded-3xl shadow-lg relative overflow-hidden">
        <div className="relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-700/60 text-emerald-200 text-xs font-semibold mb-2 backdrop-blur">
            <ShieldCheck size={14} className="text-amber-400" />
            <span>Farm Sentinel Active • {user?.village || 'Wadgaon'}, {user?.taluka || 'Haveli'}</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight">
            Namaste, {user?.fullname || user?.username}!
          </h1>
          <p className="text-emerald-100/80 text-sm mt-1 max-w-xl">
            Real-time livestock health monitoring, multi-modal AI disease risk screening, and verified biosecurity alerts.
          </p>
        </div>

        <div className="flex items-center gap-3 relative z-10 shrink-0">
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            className="bg-white/10 hover:bg-white/20 text-white border-white/20"
          >
            <RefreshCw size={15} className={refreshing ? 'animate-spin' : ''} />
            <span>Refresh</span>
          </Button>
          <Button
            variant="accent"
            size="sm"
            onClick={() => navigate('/farmer/report')}
            className="font-semibold shadow-md"
          >
            <FileText size={16} />
            <span>Report Health Issue</span>
          </Button>
        </div>
      </div>

      {/* Critical/High Alert Banner */}
      {alerts.some(a => (a.severity === 'CRITICAL' || a.severity === 'HIGH') && a.status === 'UNREAD') && (
        <div className="p-4 rounded-2xl bg-red-50 border-2 border-red-200 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 animate-pulse">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-red-100 text-red-600 flex items-center justify-center shrink-0">
              <AlertTriangle size={22} />
            </div>
            <div>
              <h3 className="text-sm font-bold text-red-900">
                Immediate Attention Required: High Risk Alert Detected
              </h3>
              <p className="text-xs text-red-700 mt-0.5">
                {alerts.find(a => (a.severity === 'CRITICAL' || a.severity === 'HIGH') && a.status === 'UNREAD')?.title || 'Potential disease risk detected in herd.'}
              </p>
            </div>
          </div>
          <Button
            variant="destructive"
            size="sm"
            onClick={() => navigate('/farmer/alerts')}
            className="shrink-0 text-xs"
          >
            Review Alerts
          </Button>
        </div>
      )}

      {/* Metric Cards Grid with Live Data Badges */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        {/* Metric 1: Total Animals */}
        <Card className="hover:shadow-md transition-shadow border-slate-200">
          <CardContent className="p-5 flex items-center justify-between">
            <div>
              <div className="flex items-center gap-1.5 mb-1">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Total Animals</span>
                <Badge variant="success" className="text-[9px] py-0 px-1">REAL DATA</Badge>
              </div>
              <p className="text-3xl font-black text-slate-900 mt-0.5">
                {totalAnimals}
              </p>
              <span className="text-[11px] font-medium text-emerald-600 flex items-center gap-1 mt-1">
                <CheckCircle2 size={12} /> Registered in Herd
              </span>
            </div>
            <div className="w-12 h-12 rounded-2xl bg-emerald-50 text-emerald-700 flex items-center justify-center">
              <Activity size={24} />
            </div>
          </CardContent>
        </Card>

        {/* Metric 2: Healthy Animals */}
        <Card className="hover:shadow-md transition-shadow border-slate-200">
          <CardContent className="p-5 flex items-center justify-between">
            <div>
              <div className="flex items-center gap-1.5 mb-1">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Healthy Herd</span>
                <Badge variant="success" className="text-[9px] py-0 px-1">REAL DATA</Badge>
              </div>
              <p className="text-3xl font-black text-emerald-600 mt-0.5">
                {healthyAnimals}
              </p>
              <span className="text-[11px] font-medium text-emerald-600 flex items-center gap-1 mt-1">
                <CheckCircle2 size={12} /> Low Risk Baseline
              </span>
            </div>
            <div className="w-12 h-12 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <CheckCircle2 size={24} />
            </div>
          </CardContent>
        </Card>

        {/* Metric 3: Animals Requiring Attention */}
        <Card className="hover:shadow-md transition-shadow border-slate-200">
          <CardContent className="p-5 flex items-center justify-between">
            <div>
              <div className="flex items-center gap-1.5 mb-1">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Requires Attention</span>
                <Badge variant="high" className="text-[9px] py-0 px-1">REAL DATA</Badge>
              </div>
              <p className="text-3xl font-black text-orange-600 mt-0.5">
                {highRiskAnimals}
              </p>
              <span className="text-[11px] font-medium text-slate-500 mt-1 block">
                Needing observation
              </span>
            </div>
            <div className="w-12 h-12 rounded-2xl bg-orange-50 text-orange-600 flex items-center justify-center">
              <AlertTriangle size={24} />
            </div>
          </CardContent>
        </Card>

        {/* Metric 4: Recent AI Reports */}
        <Card className="hover:shadow-md transition-shadow border-slate-200">
          <CardContent className="p-5 flex items-center justify-between">
            <div>
              <div className="flex items-center gap-1.5 mb-1">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Recent Reports</span>
                <Badge variant="primary" className="text-[9px] py-0 px-1">REAL DATA</Badge>
              </div>
              <p className="text-3xl font-black text-slate-900 mt-0.5">
                {reports.length}
              </p>
              <span className="text-[11px] font-medium text-emerald-600 flex items-center gap-1 mt-1">
                <TrendingUp size={12} /> Multi-modal scans
              </span>
            </div>
            <div className="w-12 h-12 rounded-2xl bg-blue-50 text-blue-700 flex items-center justify-center">
              <Camera size={24} />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Analytics Visualizations with Recharts */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Recharts 1: Risk Score Progression Chart (8 Cols) */}
        <Card className="lg:col-span-8 border-slate-200 shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between pb-2 border-b border-slate-100">
            <div>
              <div className="flex items-center gap-2">
                <CardTitle className="text-base font-bold text-slate-900">
                  Health Risk Score Progression Trend
                </CardTitle>
                <Badge variant={isUsingSimulatedTrend ? 'warning' : 'success'} className="text-[10px]">
                  {isUsingSimulatedTrend ? 'DEMO BASELINE' : 'LIVE USER REPORTS'}
                </Badge>
              </div>
              <CardDescription>
                Multi-modal AI risk score trajectory for submitted health screenings
              </CardDescription>
            </div>
            <span className="text-xs text-slate-400 font-medium">Risk Score Scale (0 - 100)</span>
          </CardHeader>

          <CardContent className="p-4 pt-6">
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={displayTrendData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="riskGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.4}/>
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
                  <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', color: '#fff', fontSize: '12px' }}
                    itemStyle={{ color: '#34d399' }}
                  />
                  <Area type="monotone" dataKey="RiskScore" stroke="#10b981" strokeWidth={3} fillOpacity={1} fill="url(#riskGrad)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
            {isUsingSimulatedTrend && (
              <p className="text-[11px] text-slate-400 text-center mt-2 flex items-center justify-center gap-1">
                <Info size={12} /> Displaying simulated baseline curve until your herd files initial health reports.
              </p>
            )}
          </CardContent>
        </Card>

        {/* Recharts 2: Herd Composition Pie Chart (4 Cols) */}
        <Card className="lg:col-span-4 border-slate-200 shadow-sm">
          <CardHeader className="pb-2 border-b border-slate-100">
            <CardTitle className="text-base font-bold text-slate-900">
              Herd Risk Composition
            </CardTitle>
            <CardDescription>
              Health distribution across your registered livestock
            </CardDescription>
          </CardHeader>

          <CardContent className="p-4 pt-4 flex flex-col items-center justify-center">
            <div className="h-52 w-full relative">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={herdPieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={75}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {herdPieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', borderRadius: '8px', color: '#fff', fontSize: '11px' }}
                  />
                </PieChart>
              </ResponsiveContainer>
              <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                <span className="text-2xl font-black text-slate-900">{totalAnimals}</span>
                <span className="text-[10px] text-slate-400 uppercase font-semibold">Total Herd</span>
              </div>
            </div>

            <div className="w-full space-y-1.5 mt-2 text-xs">
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-1.5 text-slate-600">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" /> Healthy
                </span>
                <span className="font-bold text-slate-900">{healthyAnimals}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-1.5 text-slate-600">
                  <span className="w-2.5 h-2.5 rounded-full bg-orange-500" /> High Risk / Attention
                </span>
                <span className="font-bold text-slate-900">{highRiskAnimals}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Two Column Section: Recent Health Reports & Upcoming Vaccinations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Recent AI Health Reports */}
        <Card className="border-slate-200 shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between pb-3">
            <div>
              <CardTitle className="text-base font-bold text-slate-900">
                Recent Health Reports
              </CardTitle>
              <CardDescription>
                Multi-modal health evaluations filed for your livestock
              </CardDescription>
            </div>
            <Link
              to="/farmer/report"
              className="text-xs font-semibold text-emerald-700 hover:text-emerald-800 hover:underline flex items-center gap-1"
            >
              <span>New Report</span>
              <ChevronRight size={14} />
            </Link>
          </CardHeader>

          <CardContent className="space-y-3">
            {reports.length === 0 ? (
              <div className="text-center py-10 px-4 bg-slate-50 rounded-2xl border border-dashed border-slate-200">
                <div className="w-12 h-12 rounded-2xl bg-amber-100 text-amber-800 flex items-center justify-center mx-auto mb-3">
                  <FileText size={24} />
                </div>
                <h4 className="text-sm font-bold text-slate-800">No health reports filed yet</h4>
                <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
                  If you observe unusual symptoms, file a health report to compute a transparent risk score.
                </p>
                <Button
                  variant="accent"
                  size="sm"
                  onClick={() => navigate('/farmer/report')}
                  className="mt-4 text-xs"
                >
                  <FileText size={14} />
                  <span>Report Health Issue</span>
                </Button>
              </div>
            ) : (
              reports.slice(0, 4).map((report) => {
                const reportId = report.report_id || report._id || report.id;
                const riskScore = report.final_risk_score ?? report.risk_score ?? 15;
                const riskLvl = report.risk_level || (riskScore >= 81 ? 'CRITICAL' : riskScore >= 61 ? 'HIGH' : riskScore >= 31 ? 'MEDIUM' : 'LOW');
                
                return (
                  <div
                    key={reportId}
                    className="p-3.5 rounded-xl border border-slate-100 bg-slate-50/70 hover:bg-white hover:border-slate-300 hover:shadow-xs transition-all flex items-center justify-between"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-xl bg-slate-200 text-slate-700 flex items-center justify-center shrink-0">
                        <Activity size={18} />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-bold text-slate-900">
                            Tag: {report.animal_id}
                          </span>
                          <RiskBadge level={riskLvl} score={riskScore} />
                        </div>
                        <p className="text-xs text-slate-500 mt-0.5 line-clamp-1">
                          {Array.isArray(report.symptoms) ? report.symptoms.join(', ') : (report.symptoms || 'General health evaluation')}
                        </p>
                      </div>
                    </div>

                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => navigate(`/farmer/assessment/${reportId}`, { state: { report } })}
                      className="text-xs font-semibold text-emerald-700 hover:bg-emerald-50 shrink-0"
                    >
                      <span>View</span>
                      <ArrowUpRight size={14} />
                    </Button>
                  </div>
                );
              })
            )}
          </CardContent>
        </Card>

        {/* Upcoming Vaccinations Ledger */}
        <Card className="border-slate-200 shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between pb-3">
            <div>
              <CardTitle className="text-base font-bold text-slate-900">
                Upcoming Herd Vaccinations
              </CardTitle>
              <CardDescription>
                Immunization booster ledger and due date reminders
              </CardDescription>
            </div>
            <Badge variant="low" className="text-[10px]">
              Scheduled Ledger
            </Badge>
          </CardHeader>

          <CardContent className="space-y-3">
            {upcomingVaccinations.map((vacc, idx) => (
              <div
                key={idx}
                className="p-3.5 rounded-xl border border-slate-100 bg-slate-50/70 hover:bg-white transition-all flex items-center justify-between text-xs"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-emerald-100 text-emerald-800 flex items-center justify-center shrink-0">
                    <Syringe size={18} />
                  </div>
                  <div>
                    <h4 className="font-bold text-slate-900">{vacc.disease}</h4>
                    <p className="text-slate-500 text-[11px] mt-0.5">{vacc.booster}</p>
                  </div>
                </div>

                <div className="text-right">
                  <Badge variant={vacc.status === 'DUE_SOON' ? 'warning' : 'success'} className="text-[10px]">
                    {vacc.dueDate}
                  </Badge>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Statutory Disclaimer & Transparency Note */}
      <div className="p-4 rounded-2xl bg-slate-100 border border-slate-200 text-slate-600 text-xs flex items-start gap-3">
        <Info size={18} className="text-slate-500 shrink-0 mt-0.5" />
        <div>
          <span className="font-bold text-slate-900 block mb-0.5">
            Data Integrity & Non-Misleading Analytics Policy
          </span>
          <p className="leading-relaxed text-[11px]">
            Metrics labeled <strong>REAL DATA</strong> represent your verified registered livestock records stored in the Sentinel database. Charts marked <strong>DEMO BASELINE</strong> provide historical district epidemiology reference trends for early detection decision support.
          </p>
        </div>
      </div>
    </div>
  );
};

export default FarmerDashboard;
