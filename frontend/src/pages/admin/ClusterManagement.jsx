import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth, API_BASE_URL } from '../../context/AuthContext';
import { 
  Layers, 
  Settings2, 
  RefreshCw, 
  ShieldCheck, 
  AlertTriangle, 
  MapPin, 
  Calendar, 
  ArrowRight, 
  CheckCircle2, 
  Info,
  Sliders
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge, RiskBadge } from '../../components/ui/badge';
import { Input, Select } from '../../components/ui/input';

const ClusterManagement = () => {
  const { token } = useAuth();
  const navigate = useNavigate();

  // DBSCAN Configurable Parameters
  const [radiusKm, setRadiusKm] = useState('10.0');
  const [minReports, setMinReports] = useState('2');
  const [timeWindowDays, setTimeWindowDays] = useState('14');
  const [minRiskScore, setMinRiskScore] = useState('60');

  const [clusters, setClusters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [resultMsg, setResultMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const fetchClusters = async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API_BASE_URL}/api/clusters`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setClusters(data.clusters || data || []);
      }
    } catch (err) {
      console.error('Failed to load clusters:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchClusters();
  }, [token]);

  const handleRunDBSCAN = async (e) => {
    e.preventDefault();
    setRunning(true);
    setResultMsg('');
    setErrorMsg('');

    try {
      const payload = {
        radius_km: parseFloat(radiusKm) || 10.0,
        min_reports: parseInt(minReports) || 2,
        time_window_days: parseInt(timeWindowDays) || 14,
        min_risk_score: parseInt(minRiskScore) || 60
      };

      const res = await fetch(`${API_BASE_URL}/api/clusters/detect`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Cluster detection failed.');
      }

      setResultMsg(`DBSCAN Complete: ${data.detected_clusters_count || data.clusters?.length || 0} potential clusters generated and recorded.`);
      await fetchClusters();
    } catch (err) {
      setErrorMsg(err.message || 'Error running cluster detection engine.');
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
            <span>Spatial Cluster Detection Management</span>
            <Badge variant="high" className="text-xs">
              Haversine DBSCAN
            </Badge>
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Configure spatio-temporal clustering hyperparameters to detect emerging livestock disease risks
          </p>
        </div>

        <Button
          variant="outline"
          size="sm"
          onClick={() => navigate('/admin/map')}
          className="text-xs gap-1.5"
        >
          <span>Surveillance Map View</span>
          <ArrowRight size={14} />
        </Button>
      </div>

      {resultMsg && (
        <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-900 text-xs flex items-center gap-2">
          <CheckCircle2 size={16} className="text-emerald-600 shrink-0" />
          <span>{resultMsg}</span>
        </div>
      )}

      {errorMsg && (
        <div className="p-4 rounded-2xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
          <AlertTriangle size={16} className="text-red-600 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Hyperparameter Tuning Form */}
      <Card className="border-slate-200 shadow-md">
        <form onSubmit={handleRunDBSCAN}>
          <CardHeader className="border-b border-slate-100 pb-4">
            <CardTitle className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Sliders size={18} className="text-purple-700" />
              <span>DBSCAN Spatio-Temporal Hyperparameters</span>
            </CardTitle>
            <CardDescription>
              Tuning distance radius ($\epsilon$) and minimum linked reports (MinPts) adjusts surveillance sensitivity
            </CardDescription>
          </CardHeader>

          <CardContent className="p-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  Epsilon Distance Radius (km) *
                </label>
                <Input
                  type="number"
                  step="0.5"
                  min="1"
                  max="50"
                  value={radiusKm}
                  onChange={(e) => setRadiusKm(e.target.value)}
                  required
                />
                <span className="text-[10px] text-slate-400 mt-1 block">Standard containment: 5.0 - 15.0 km</span>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  Minimum Reports (MinPts) *
                </label>
                <Input
                  type="number"
                  min="2"
                  max="20"
                  value={minReports}
                  onChange={(e) => setMinReports(e.target.value)}
                  required
                />
                <span className="text-[10px] text-slate-400 mt-1 block">Default threshold: 2 reports</span>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  Time Window (Days) *
                </label>
                <Input
                  type="number"
                  min="1"
                  max="90"
                  value={timeWindowDays}
                  onChange={(e) => setTimeWindowDays(e.target.value)}
                  required
                />
                <span className="text-[10px] text-slate-400 mt-1 block">Incubation span: 14 days</span>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  Minimum Risk Score Threshold *
                </label>
                <Input
                  type="number"
                  min="30"
                  max="90"
                  value={minRiskScore}
                  onChange={(e) => setMinRiskScore(e.target.value)}
                  required
                />
                <span className="text-[10px] text-slate-400 mt-1 block">Evaluates high/critical reports (≥60)</span>
              </div>
            </div>
          </CardContent>

          <CardFooter className="border-t border-slate-100 p-4 bg-slate-50 flex items-center justify-between">
            <span className="text-xs text-slate-500">
              Only reports exceeding the risk threshold are factored into spatial clustering.
            </span>
            <Button
              type="submit"
              variant="primary"
              size="md"
              disabled={running}
              className="text-xs shadow-sm"
            >
              <RefreshCw size={14} className={running ? 'animate-spin' : ''} />
              <span>{running ? 'Executing DBSCAN...' : 'Run Cluster Detection'}</span>
            </Button>
          </CardFooter>
        </form>
      </Card>

      {/* Active Potential Clusters List */}
      <Card className="border-slate-200 shadow-sm">
        <CardHeader className="pb-3 border-b border-slate-100 flex flex-row items-center justify-between">
          <div>
            <CardTitle className="text-base font-bold text-slate-900">
              Recorded Potential Disease Clusters
            </CardTitle>
            <CardDescription>
              Persisted clusters stored in database with surveillance rings
            </CardDescription>
          </div>
          <Badge variant="primary" className="text-xs">
            {clusters.length} Active Rings
          </Badge>
        </CardHeader>

        <CardContent className="p-0">
          {clusters.length === 0 ? (
            <div className="text-center py-12 text-slate-500 text-xs">
              No potential clusters currently recorded. Click "Run Cluster Detection" above to scan for spatial risk patterns.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-200 text-slate-500 font-bold uppercase tracking-wider text-[10px] bg-slate-50">
                    <th className="py-3 px-4">Cluster ID</th>
                    <th className="py-3 px-4">Disease Pattern</th>
                    <th className="py-3 px-4">Center Coordinates</th>
                    <th className="py-3 px-4">Radius</th>
                    <th className="py-3 px-4">Affected Reports</th>
                    <th className="py-3 px-4">Detection Date</th>
                    <th className="py-3 px-4 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {clusters.map((c) => {
                    const id = c.cluster_id || c._id || c.id;
                    const lat = c.center_latitude || c.center_lat || 18.5204;
                    const lng = c.center_longitude || c.center_lng || 73.8567;

                    return (
                      <tr key={id} className="hover:bg-slate-50 transition-colors">
                        <td className="py-3.5 px-4 font-mono font-bold text-slate-900">
                          {id}
                        </td>
                        <td className="py-3.5 px-4 font-semibold text-purple-900">
                          {c.disease || c.primary_disease || 'Foot-and-Mouth Disease'}
                        </td>
                        <td className="py-3.5 px-4 font-mono text-slate-600">
                          {lat.toFixed(4)}, {lng.toFixed(4)}
                        </td>
                        <td className="py-3.5 px-4 font-medium">
                          {c.radius_km || 5.0} km
                        </td>
                        <td className="py-3.5 px-4">
                          <Badge variant="high" className="text-[10px]">
                            {c.affected_farms_count || c.reports_count || 4} Cases
                          </Badge>
                        </td>
                        <td className="py-3.5 px-4 text-slate-500">
                          {c.detected_at ? new Date(c.detected_at).toLocaleDateString() : 'Active'}
                        </td>
                        <td className="py-3.5 px-4 text-right">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => navigate('/admin/map')}
                            className="text-xs h-7 text-emerald-700 hover:bg-emerald-50"
                          >
                            <span>Map</span>
                            <ArrowRight size={12} />
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

export default ClusterManagement;
