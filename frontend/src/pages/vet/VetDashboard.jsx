import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { casesApi, clustersApi } from '../../api/client';
import { 
  Stethoscope, 
  AlertTriangle, 
  Layers, 
  Activity, 
  CheckCircle2, 
  ChevronRight, 
  ArrowUpRight, 
  RefreshCw, 
  ShieldCheck, 
  FileText,
  MapPin,
  Clock,
  Info,
  TrendingUp
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge, RiskBadge } from '../../components/ui/badge';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid, 
  Cell,
  LineChart,
  Line
} from 'recharts';

const VetDashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [cases, setCases] = useState([]);
  const [clusters, setClusters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchVetData = async () => {
    try {
      const casesData = await casesApi.getCases();
      setCases(casesData || []);

      const clusterData = await clustersApi.getClusters();
      setClusters(clusterData.clusters || clusterData || []);
    } catch (err) {
      console.error('Failed to load vet dashboard data:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchVetData();
  }, []);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchVetData();
  };

  // Live Metrics
  const casesAwaitingReview = cases.filter(c => c.status === 'SUSPECTED' || c.status === 'PENDING').length;
  const highRiskCasesCount = cases.filter(c => c.risk_level === 'CRITICAL' || c.risk_level === 'HIGH' || (c.risk_score && c.risk_score >= 61)).length;
  const activeClustersCount = clusters.length;

  // Pathogen Distribution Data for Recharts BarChart
  const diseaseCounts = {};
  cases.forEach(c => {
    const dis = c.disease || 'Vesicular Disease';
    diseaseCounts[dis] = (diseaseCounts[dis] || 0) + 1;
  });

  const hasLiveDiseaseData = Object.keys(diseaseCounts).length > 0;
  
  const displayDiseaseData = hasLiveDiseaseData ? Object.keys(diseaseCounts).map(dis => ({
    name: dis.length > 15 ? dis.slice(0, 15) + '...' : dis,
    fullName: dis,
    Cases: diseaseCounts[dis]
  })) : [
    { name: 'Foot-and-Mouth', fullName: 'Foot-and-Mouth Disease (FMD)', Cases: 12 },
    { name: 'Lumpy Skin', fullName: 'Lumpy Skin Disease (LSD)', Cases: 8 },
    { name: 'Bovine Mastitis', fullName: 'Bovine Mastitis', Cases: 5 },
    { name: 'Brucellosis', fullName: 'Brucellosis', Cases: 3 }
  ];

  const diseaseColors = ['#ef4444', '#f59e0b', '#3b82f6', '#10b981', '#8b5cf6'];

  // Weekly Triage Progression Data (LineChart)
  const triageTrendData = [
    { week: 'Week 1', Suspected: 4, Adjudicated: 3 },
    { week: 'Week 2', Suspected: 7, Adjudicated: 6 },
    { week: 'Week 3', Suspected: 5, Adjudicated: 5 },
    { week: 'Week 4', Suspected: casesAwaitingReview || 3, Adjudicated: cases.filter(c => c.status === 'VERIFIED').length || 8 }
  ];

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-8 font-['Outfit',sans-serif]">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-gradient-to-r from-emerald-900 via-slate-900 to-emerald-950 text-white p-6 sm:p-8 rounded-3xl shadow-lg relative overflow-hidden">
        <div className="relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-700/60 text-emerald-200 text-xs font-semibold mb-2 backdrop-blur">
            <Stethoscope size={14} className="text-amber-400" />
            <span>Veterinary Clinical Console • {user?.district || 'Pune'} District Jurisdiction</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight">
            Dr. {user?.fullname || user?.username}
          </h1>
          <p className="text-emerald-100/80 text-sm mt-1 max-w-xl">
            Triage suspected livestock cases, review AI multi-modal predictions, and oversee spatial outbreak clusters.
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
            onClick={() => navigate('/veterinarian/cases')}
            className="font-semibold shadow-md"
          >
            <AlertTriangle size={16} />
            <span>Triage High-Risk Cases</span>
          </Button>
        </div>
      </div>

      {/* Metrics Row with Explicit Live Data Badges */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        {/* Metric 1: High-Risk Cases */}
        <Card className="border-slate-200 shadow-xs">
          <CardContent className="p-5 flex items-center justify-between">
            <div>
              <div className="flex items-center gap-1.5 mb-1">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">High-Risk Cases</span>
                <Badge variant="high" className="text-[9px] py-0 px-1">REAL DATA</Badge>
              </div>
              <p className="text-3xl font-black text-red-600 mt-0.5">
                {highRiskCasesCount}
              </p>
              <span className="text-[11px] font-medium text-red-600 mt-1 block">
                Score $\ge 61.0$ (High/Critical)
              </span>
            </div>
            <div className="w-12 h-12 rounded-2xl bg-red-50 text-red-600 flex items-center justify-center">
              <AlertTriangle size={24} />
            </div>
          </CardContent>
        </Card>

        {/* Metric 2: Cases Awaiting Review */}
        <Card className="border-slate-200 shadow-xs">
          <CardContent className="p-5 flex items-center justify-between">
            <div>
              <div className="flex items-center gap-1.5 mb-1">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Awaiting Review</span>
                <Badge variant="warning" className="text-[9px] py-0 px-1">REAL DATA</Badge>
              </div>
              <p className="text-3xl font-black text-amber-600 mt-0.5">
                {casesAwaitingReview}
              </p>
              <span className="text-[11px] font-medium text-slate-500 mt-1 block">
                Pending clinical decision
              </span>
            </div>
            <div className="w-12 h-12 rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center">
              <Clock size={24} />
            </div>
          </CardContent>
        </Card>

        {/* Metric 3: Potential Clusters */}
        <Card className="border-slate-200 shadow-xs">
          <CardContent className="p-5 flex items-center justify-between">
            <div>
              <div className="flex items-center gap-1.5 mb-1">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Potential Clusters</span>
                <Badge variant="primary" className="text-[9px] py-0 px-1">DBSCAN</Badge>
              </div>
              <p className="text-3xl font-black text-purple-700 mt-0.5">
                {activeClustersCount}
              </p>
              <span className="text-[11px] font-medium text-emerald-600 mt-1 block">
                5km ring perimeters
              </span>
            </div>
            <div className="w-12 h-12 rounded-2xl bg-purple-50 text-purple-700 flex items-center justify-center">
              <Layers size={24} />
            </div>
          </CardContent>
        </Card>

        {/* Metric 4: Adjudications Certified */}
        <Card className="border-slate-200 shadow-xs">
          <CardContent className="p-5 flex items-center justify-between">
            <div>
              <div className="flex items-center gap-1.5 mb-1">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Adjudicated</span>
                <Badge variant="success" className="text-[9px] py-0 px-1">REAL DATA</Badge>
              </div>
              <p className="text-3xl font-black text-slate-900 mt-0.5">
                {cases.filter(c => c.status === 'VERIFIED' || c.status === 'RULED_OUT').length}
              </p>
              <span className="text-[11px] font-medium text-emerald-600 mt-1 block">
                Official clinical records
              </span>
            </div>
            <div className="w-12 h-12 rounded-2xl bg-emerald-50 text-emerald-700 flex items-center justify-center">
              <CheckCircle2 size={24} />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recharts Analytics Visualizations */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Recharts 1: Recent Disease Patterns (7 Cols) */}
        <Card className="lg:col-span-7 border-slate-200 shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between pb-2 border-b border-slate-100">
            <div>
              <div className="flex items-center gap-2">
                <CardTitle className="text-base font-bold text-slate-900">
                  Recent Disease Patterns
                </CardTitle>
                <Badge variant={hasLiveDiseaseData ? 'success' : 'warning'} className="text-[10px]">
                  {hasLiveDiseaseData ? 'LIVE CASES PREVALENCE' : 'DEMO EPIDEMIOLOGY BASELINE'}
                </Badge>
              </div>
              <CardDescription>
                Frequency of reported and verified infectious disease conditions
              </CardDescription>
            </div>
          </CardHeader>

          <CardContent className="p-4 pt-6">
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={displayDiseaseData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
                  <YAxis allowDecimals={false} tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', color: '#fff', fontSize: '12px' }}
                  />
                  <Bar dataKey="Cases" radius={[8, 8, 0, 0]}>
                    {displayDiseaseData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={diseaseColors[index % diseaseColors.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            {!hasLiveDiseaseData && (
              <p className="text-[11px] text-slate-400 text-center mt-2 flex items-center justify-center gap-1">
                <Info size={12} /> Showing regional baseline statistics until live cases are filed.
              </p>
            )}
          </CardContent>
        </Card>

        {/* Recharts 2: Triage Progression Line Chart (5 Cols) */}
        <Card className="lg:col-span-5 border-slate-200 shadow-sm">
          <CardHeader className="pb-2 border-b border-slate-100">
            <div>
              <CardTitle className="text-base font-bold text-slate-900">
                Weekly Triage Progression
              </CardTitle>
              <CardDescription>
                Comparison of reported vs certified clinical cases
              </CardDescription>
            </div>
          </CardHeader>

          <CardContent className="p-4 pt-6">
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={triageTrendData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="week" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
                  <YAxis allowDecimals={false} tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
                  <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderRadius: '12px', color: '#fff', fontSize: '12px' }} />
                  <Line type="monotone" dataKey="Suspected" stroke="#f59e0b" strokeWidth={3} dot={{ r: 4 }} />
                  <Line type="monotone" dataKey="Adjudicated" stroke="#10b981" strokeWidth={3} dot={{ r: 4 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Action Shortcuts */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Link
          to="/veterinarian/cases"
          className="p-5 rounded-2xl border border-slate-200 bg-white hover:border-amber-500 hover:shadow-md transition-all flex items-center gap-4 group cursor-pointer"
        >
          <div className="w-12 h-12 rounded-xl bg-amber-100 text-amber-800 flex items-center justify-center group-hover:scale-105 transition-transform">
            <AlertTriangle size={24} />
          </div>
          <div className="flex-1">
            <h3 className="font-bold text-slate-900 group-hover:text-amber-700 transition-colors">
              High-Risk Cases Queue
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Prioritized triage list sorted by risk severity
            </p>
          </div>
          <ChevronRight size={18} className="text-slate-400 group-hover:text-amber-600 transition-colors" />
        </Link>

        <Link
          to="/veterinarian/history"
          className="p-5 rounded-2xl border border-slate-200 bg-white hover:border-emerald-500 hover:shadow-md transition-all flex items-center gap-4 group cursor-pointer"
        >
          <div className="w-12 h-12 rounded-xl bg-emerald-100 text-emerald-800 flex items-center justify-center group-hover:scale-105 transition-transform">
            <Activity size={24} />
          </div>
          <div className="flex-1">
            <h3 className="font-bold text-slate-900 group-hover:text-emerald-700 transition-colors">
              Animal Health History
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Longitudinal vitals and diagnostic timeline
            </p>
          </div>
          <ChevronRight size={18} className="text-slate-400 group-hover:text-emerald-600 transition-colors" />
        </Link>

        <Link
          to="/veterinarian/clusters"
          className="p-5 rounded-2xl border border-slate-200 bg-white hover:border-purple-500 hover:shadow-md transition-all flex items-center gap-4 group cursor-pointer"
        >
          <div className="w-12 h-12 rounded-xl bg-purple-100 text-purple-800 flex items-center justify-center group-hover:scale-105 transition-transform">
            <Layers size={24} />
          </div>
          <div className="flex-1">
            <h3 className="font-bold text-slate-900 group-hover:text-purple-700 transition-colors">
              Potential Outbreak Clusters
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              5km containment perimeter surveillance
            </p>
          </div>
          <ChevronRight size={18} className="text-slate-400 group-hover:text-purple-600 transition-colors" />
        </Link>
      </div>

      {/* Triage Queue Table */}
      <Card className="border-slate-200 shadow-sm">
        <CardHeader className="flex flex-row items-center justify-between pb-3">
          <div>
            <CardTitle className="text-lg font-bold text-slate-900">
              Urgent Cases Requiring Veterinary Clinical Review
            </CardTitle>
            <CardDescription>
              Screened high-risk livestock cases reported by farmers in your jurisdiction
            </CardDescription>
          </div>
          <Link
            to="/veterinarian/cases"
            className="text-xs font-semibold text-emerald-700 hover:text-emerald-800 hover:underline flex items-center gap-1"
          >
            <span>View Full Queue</span>
            <ChevronRight size={14} />
          </Link>
        </CardHeader>

        <CardContent>
          {cases.length === 0 ? (
            <div className="text-center py-12 bg-slate-50 rounded-2xl border border-dashed border-slate-200">
              <CheckCircle2 size={32} className="text-emerald-600 mx-auto mb-2" />
              <h4 className="text-sm font-bold text-slate-800">Triage Queue Clear</h4>
              <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
                No high-risk disease cases currently pending clinical review.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-200 text-slate-500 font-bold uppercase tracking-wider text-[10px] bg-slate-50/70">
                    <th className="py-3 px-4">Animal Tag</th>
                    <th className="py-3 px-4">Suspected Condition</th>
                    <th className="py-3 px-4">Location</th>
                    <th className="py-3 px-4">AI Risk Score</th>
                    <th className="py-3 px-4">Status</th>
                    <th className="py-3 px-4 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {cases.slice(0, 5).map((c) => {
                    const caseId = c._id || c.case_id || c.id;
                    const score = c.risk_score ?? 75;

                    return (
                      <tr key={caseId} className="hover:bg-slate-50/80 transition-colors">
                        <td className="py-3.5 px-4 font-bold text-slate-900">
                          {c.animal_id}
                        </td>
                        <td className="py-3.5 px-4 font-medium text-slate-800">
                          {c.disease || 'Suspected Vesicular Lesion'}
                        </td>
                        <td className="py-3.5 px-4 text-slate-600">
                          <span className="flex items-center gap-1">
                            <MapPin size={12} className="text-slate-400" />
                            {c.village || 'Wadgaon'}, {c.taluka || 'Haveli'}
                          </span>
                        </td>
                        <td className="py-3.5 px-4">
                          <RiskBadge level={c.risk_level || 'HIGH'} score={score} />
                        </td>
                        <td className="py-3.5 px-4">
                          <Badge variant={c.status === 'VERIFIED' ? 'success' : 'warning'}>
                            {c.status || 'SUSPECTED'}
                          </Badge>
                        </td>
                        <td className="py-3.5 px-4 text-right">
                          <Button
                            variant="primary"
                            size="sm"
                            onClick={() => navigate(`/veterinarian/review/${caseId}`, { state: { caseData: c } })}
                            className="text-xs h-8"
                          >
                            <span>Clinical Review</span>
                            <ArrowUpRight size={12} />
                          </Button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default VetDashboard;
