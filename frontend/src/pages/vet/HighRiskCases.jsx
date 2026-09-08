import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth, API_BASE_URL } from '../../context/AuthContext';
import { 
  AlertTriangle, 
  Search, 
  Filter, 
  MapPin, 
  Calendar, 
  ChevronRight, 
  Activity, 
  Stethoscope, 
  RefreshCw,
  Phone,
  Camera,
  ArrowUpRight
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge, RiskBadge } from '../../components/ui/badge';
import { Input } from '../../components/ui/input';

const HighRiskCases = () => {
  const { token, user } = useAuth();
  const navigate = useNavigate();

  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [search, setSearch] = useState('');
  const [severityFilter, setSeverityFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');

  const fetchCases = async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API_BASE_URL}/api/cases`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setCases(data || []);
      }
    } catch (err) {
      console.error('Failed to load high risk cases:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchCases();
  }, [token]);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchCases();
  };

  const filteredCases = cases.filter((c) => {
    const s = search.toLowerCase();
    const matchesSearch =
      (c.animal_id && c.animal_id.toLowerCase().includes(s)) ||
      (c.disease && c.disease.toLowerCase().includes(s)) ||
      (c.village && c.village.toLowerCase().includes(s)) ||
      (c.farmer_name && c.farmer_name.toLowerCase().includes(s));

    const matchesSeverity =
      severityFilter === 'ALL' ||
      (severityFilter === 'CRITICAL' && (c.risk_level === 'CRITICAL' || (c.risk_score && c.risk_score >= 81))) ||
      (severityFilter === 'HIGH' && (c.risk_level === 'HIGH' || (c.risk_score && c.risk_score >= 61 && c.risk_score < 81)));

    const matchesStatus =
      statusFilter === 'ALL' || c.status === statusFilter;

    return matchesSearch && matchesSeverity && matchesStatus;
  });

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
            <span>High-Risk Livestock Triage Queue</span>
            <Badge variant="high" className="text-xs">
              {filteredCases.length} Cases
            </Badge>
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Suspected infectious disease reports prioritized by multi-modal AI risk score
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            className="text-xs gap-1.5"
          >
            <RefreshCw size={14} className={refreshing ? 'animate-spin' : ''} />
            <span>Refresh Queue</span>
          </Button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <Card className="border-slate-200 shadow-xs">
        <CardContent className="p-4 space-y-3">
          <div className="relative">
            <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <Input
              placeholder="Search by Animal Tag, Suspected Disease, Farmer Name, or Village..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-10 text-xs"
            />
          </div>

          <div className="flex flex-wrap items-center justify-between gap-2 pt-1">
            {/* Urgency filters */}
            <div className="flex items-center gap-1.5 text-xs">
              <span className="text-slate-500 font-semibold mr-1 flex items-center gap-1">
                <Filter size={12} /> Severity:
              </span>
              <button
                onClick={() => setSeverityFilter('ALL')}
                className={`px-2.5 py-1 rounded-lg font-medium transition-colors cursor-pointer ${
                  severityFilter === 'ALL' ? 'bg-slate-800 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                All Urgencies
              </button>
              <button
                onClick={() => setSeverityFilter('CRITICAL')}
                className={`px-2.5 py-1 rounded-lg font-medium transition-colors cursor-pointer ${
                  severityFilter === 'CRITICAL' ? 'bg-red-600 text-white font-bold' : 'bg-red-50 text-red-700 hover:bg-red-100'
                }`}
              >
                Critical Risk (81+)
              </button>
              <button
                onClick={() => setSeverityFilter('HIGH')}
                className={`px-2.5 py-1 rounded-lg font-medium transition-colors cursor-pointer ${
                  severityFilter === 'HIGH' ? 'bg-orange-600 text-white font-bold' : 'bg-orange-50 text-orange-700 hover:bg-orange-100'
                }`}
              >
                High Risk (61-80)
              </button>
            </div>

            {/* Status filters */}
            <div className="flex items-center gap-1.5 text-xs">
              <span className="text-slate-500 font-semibold mr-1">Status:</span>
              <button
                onClick={() => setStatusFilter('ALL')}
                className={`px-2.5 py-1 rounded-lg font-medium transition-colors cursor-pointer ${
                  statusFilter === 'ALL' ? 'bg-emerald-800 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                All
              </button>
              <button
                onClick={() => setStatusFilter('SUSPECTED')}
                className={`px-2.5 py-1 rounded-lg font-medium transition-colors cursor-pointer ${
                  statusFilter === 'SUSPECTED' ? 'bg-amber-600 text-white' : 'bg-amber-50 text-amber-700 hover:bg-amber-100'
                }`}
              >
                Pending Review
              </button>
              <button
                onClick={() => setStatusFilter('VERIFIED')}
                className={`px-2.5 py-1 rounded-lg font-medium transition-colors cursor-pointer ${
                  statusFilter === 'VERIFIED' ? 'bg-green-700 text-white' : 'bg-green-50 text-green-700 hover:bg-green-100'
                }`}
              >
                Adjudicated
              </button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Triage Grid */}
      {loading ? (
        <div className="text-center py-16">
          <div className="w-10 h-10 border-4 border-emerald-600 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-xs text-slate-500">Loading cases queue...</p>
        </div>
      ) : filteredCases.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-2xl border border-dashed border-slate-300 p-8">
          <Stethoscope size={32} className="text-emerald-600 mx-auto mb-3" />
          <h3 className="text-base font-bold text-slate-900">No matching cases found</h3>
          <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
            All livestock health reports in your jurisdiction have either been triaged or do not exceed the risk filter.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredCases.map((c) => {
            const caseId = c._id || c.case_id || c.id;
            const score = c.risk_score ?? 75;
            const isCritical = c.risk_level === 'CRITICAL' || score >= 81;

            return (
              <Card
                key={caseId}
                className="overflow-hidden border-slate-200 hover:border-amber-500/80 hover:shadow-md transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="p-4 pb-3 border-b border-slate-100 bg-gradient-to-r from-slate-50 to-white flex items-center justify-between">
                    <div>
                      <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">
                        Animal Tag
                      </span>
                      <span className="text-sm font-black text-slate-900">
                        {c.animal_id}
                      </span>
                    </div>

                    <RiskBadge level={c.risk_level || (isCritical ? 'CRITICAL' : 'HIGH')} score={score} />
                  </div>

                  <div className="p-4 space-y-3 text-xs text-slate-700">
                    <div>
                      <span className="text-[10px] text-slate-400 font-semibold block uppercase">
                        Suspected Condition
                      </span>
                      <span className="text-sm font-bold text-slate-900">
                        {c.disease || 'Suspected Foot-and-Mouth Disease'}
                      </span>
                    </div>

                    <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100 space-y-1">
                      <div className="flex items-center justify-between text-[11px]">
                        <span className="text-slate-500">Owner:</span>
                        <span className="font-semibold text-slate-800">{c.farmer_name || 'Local Farmer'}</span>
                      </div>
                      <div className="flex items-center justify-between text-[11px]">
                        <span className="text-slate-500">Location:</span>
                        <span className="font-semibold text-slate-800">{c.village || 'Wadgaon'}, {c.taluka || 'Haveli'}</span>
                      </div>
                      <div className="flex items-center justify-between text-[11px]">
                        <span className="text-slate-500">Status:</span>
                        <Badge variant={c.status === 'VERIFIED' ? 'success' : 'warning'} className="text-[10px] py-0">
                          {c.status || 'SUSPECTED'}
                        </Badge>
                      </div>
                    </div>

                    {c.symptoms && (
                      <div>
                        <span className="text-[10px] text-slate-400 font-semibold block uppercase mb-1">
                          Reported Symptoms
                        </span>
                        <p className="text-[11px] text-slate-600 line-clamp-2">
                          {Array.isArray(c.symptoms) ? c.symptoms.join(', ') : c.symptoms}
                        </p>
                      </div>
                    )}
                  </div>
                </div>

                <div className="p-3 bg-slate-50 border-t border-slate-100 flex items-center justify-between gap-2">
                  <span className="text-[10px] text-slate-400">
                    {c.date ? new Date(c.date).toLocaleDateString() : 'Recent'}
                  </span>

                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => navigate(`/veterinarian/review/${caseId}`, { state: { caseData: c } })}
                    className="text-xs h-8 gap-1"
                  >
                    <Stethoscope size={13} />
                    <span>Review Case</span>
                  </Button>
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default HighRiskCases;
