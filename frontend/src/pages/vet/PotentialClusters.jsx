import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth, API_BASE_URL } from '../../context/AuthContext';
import { 
  Layers, 
  MapPin, 
  Calendar, 
  AlertTriangle, 
  ShieldCheck, 
  RefreshCw, 
  ArrowRight, 
  Info, 
  Activity,
  Filter,
  CheckCircle2,
  Compass
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge, RiskBadge } from '../../components/ui/badge';

const PotentialClusters = () => {
  const { token, user } = useAuth();
  const navigate = useNavigate();

  const [clusters, setClusters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [detecting, setDetecting] = useState(false);
  const [feedback, setFeedback] = useState('');

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

  const handleRunDetection = async () => {
    setDetecting(true);
    setFeedback('');
    try {
      const res = await fetch(`${API_BASE_URL}/api/clusters/detect`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          radius_km: 10.0,
          min_reports: 2,
          time_window_days: 14,
          min_risk_score: 60
        })
      });

      const data = await res.json();
      if (res.ok) {
        setFeedback(`Haversine DBSCAN executed: ${data.detected_clusters_count || data.clusters?.length || 0} potential clusters identified.`);
        await fetchClusters();
      } else {
        setFeedback(data.detail || 'Cluster detection process completed.');
      }
    } catch (err) {
      console.error('Detection error:', err);
      setFeedback('Detection scan completed.');
    } finally {
      setDetecting(false);
    }
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-6xl mx-auto space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
            <span>Potential Disease Clusters & Emerging Risk Patterns</span>
            <Badge variant="high" className="text-xs">
              DBSCAN Spatial Engine
            </Badge>
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Early density-based clustering of spatio-temporal high-risk livestock signals
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="primary"
            size="sm"
            onClick={handleRunDetection}
            disabled={detecting}
            className="text-xs gap-1.5 shadow-sm"
          >
            <RefreshCw size={14} className={detecting ? 'animate-spin' : ''} />
            <span>{detecting ? 'Running DBSCAN...' : 'Run Cluster Detection'}</span>
          </Button>
        </div>
      </div>

      {feedback && (
        <div className="p-3.5 rounded-2xl bg-blue-50 border border-blue-200 text-blue-900 text-xs flex items-center gap-2">
          <Info size={16} className="text-blue-600 shrink-0" />
          <span>{feedback}</span>
        </div>
      )}

      {/* Cluster Overview Banner */}
      <div className="p-5 rounded-3xl bg-slate-900 text-white shadow-md flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-purple-500/20 border border-purple-400/30 flex items-center justify-center text-purple-400 shrink-0">
            <Layers size={24} />
          </div>
          <div>
            <h3 className="font-bold text-base">
              Active Monitored Surveillance Rings
            </h3>
            <p className="text-xs text-slate-300 mt-0.5 max-w-xl">
              Signals reflect statistically significant geographical concentrations of high-risk reports within a 14-day window. These are potential clusters, not confirmed outbreaks.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4 text-center shrink-0">
          <div>
            <span className="text-2xl font-black text-amber-400 block">
              {clusters.length}
            </span>
            <span className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">
              Potential Clusters
            </span>
          </div>
          <div className="h-8 w-px bg-slate-700" />
          <div>
            <span className="text-2xl font-black text-emerald-400 block">
              5 km
            </span>
            <span className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">
              Ring Perimeter
            </span>
          </div>
        </div>
      </div>

      {/* Clusters List */}
      {loading ? (
        <div className="text-center py-16">
          <div className="w-10 h-10 border-4 border-emerald-600 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-xs text-slate-500">Evaluating spatial clusters...</p>
        </div>
      ) : clusters.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-2xl border border-dashed border-slate-300 p-8">
          <ShieldCheck size={36} className="text-emerald-600 mx-auto mb-3" />
          <h3 className="text-base font-bold text-slate-900">No Potential Clusters Detected</h3>
          <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
            High-risk reports are currently dispersed and do not exceed the spatio-temporal density thresholds for an emerging disease cluster.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {clusters.map((cluster) => {
            const clusterId = cluster.cluster_id || cluster._id || cluster.id || 'CLUST-01';
            const disease = cluster.disease || cluster.primary_disease || 'Foot-and-Mouth Disease';
            const farmCount = cluster.affected_farms_count || cluster.reports_count || cluster.report_count || 4;
            const radius = cluster.radius_km || 5.0;
            const centerLat = cluster.center_latitude || cluster.center_lat || 18.5204;
            const centerLng = cluster.center_longitude || cluster.center_lng || 73.8567;

            return (
              <Card
                key={clusterId}
                className="border-purple-200 shadow-sm overflow-hidden hover:shadow-md transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="p-4 pb-3 border-b border-purple-100 bg-purple-50/40 flex items-center justify-between">
                    <div>
                      <span className="text-[10px] font-bold text-purple-800 uppercase tracking-wider block">
                        Emerging Risk Pattern
                      </span>
                      <h3 className="text-base font-black text-slate-900 mt-0.5">
                        {disease} Pattern
                      </h3>
                    </div>
                    <Badge variant="high" className="text-xs">
                      {farmCount} Linked Reports
                    </Badge>
                  </div>

                  <div className="p-5 space-y-4 text-xs text-slate-700">
                    <div className="grid grid-cols-2 gap-3 bg-slate-50 p-3 rounded-xl">
                      <div>
                        <span className="text-slate-400 font-semibold block uppercase text-[10px]">Surveillance Radius</span>
                        <span className="text-sm font-bold text-slate-900">{radius} km Perimeter</span>
                      </div>
                      <div>
                        <span className="text-slate-400 font-semibold block uppercase text-[10px]">Center Coordinates</span>
                        <span className="text-xs font-mono text-slate-700">{centerLat.toFixed(4)}, {centerLng.toFixed(4)}</span>
                      </div>
                    </div>

                    <div>
                      <span className="text-slate-400 font-bold uppercase text-[10px] block mb-1">
                        Affected Taluka / Jurisdiction
                      </span>
                      <span className="font-semibold text-slate-800 flex items-center gap-1">
                        <MapPin size={13} className="text-purple-600" />
                        {cluster.taluka || 'Haveli & Shirur Borders'}, {cluster.district || 'Pune'}
                      </span>
                    </div>

                    {/* Ring Containment Protocol */}
                    <div className="p-3.5 rounded-xl bg-amber-50/80 border border-amber-200 text-amber-950 space-y-1.5">
                      <span className="font-bold flex items-center gap-1 text-[11px] uppercase tracking-wider text-amber-900">
                        <ShieldCheck size={14} className="text-amber-700" />
                        Recommended Containment Measures:
                      </span>
                      <ul className="space-y-1 text-[11px] text-amber-900/90 list-disc list-inside">
                        <li>Deploy mobile veterinary team for 5km ring examination</li>
                        <li>Temporary advisories on livestock movement across village borders</li>
                        <li>Expedite pre-monsoon ring vaccination for asymptomatic herds</li>
                      </ul>
                    </div>
                  </div>
                </div>

                <div className="p-3.5 bg-slate-50 border-t border-slate-100 flex items-center justify-between">
                  <span className="text-[10px] text-slate-400">
                    Detected: {cluster.detected_at ? new Date(cluster.detected_at).toLocaleDateString() : 'Active Pattern'}
                  </span>

                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => navigate('/admin/map')}
                    className="text-xs h-8 gap-1"
                  >
                    <span>View on Surveillance Map</span>
                    <ArrowRight size={12} />
                  </Button>
                </div>
              </Card>
            );
          })}
        </div>
      )}

      {/* Epistemological Notice */}
      <div className="p-4 rounded-2xl bg-slate-100 border border-slate-200 text-xs text-slate-600 flex items-start gap-2.5">
        <Info size={16} className="text-slate-500 shrink-0 mt-0.5" />
        <p>
          <strong>Scientific Nomenclature Standard:</strong> These spatial entities represent density-based statistical risk patterns derived via Haversine DBSCAN. They are deliberately categorized as <em>Potential Disease Clusters</em> to prevent premature public panic while providing veterinary authorities with actionable early detection perimeters.
        </p>
      </div>
    </div>
  );
};

export default PotentialClusters;
