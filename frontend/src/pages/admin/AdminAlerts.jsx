import React, { useState, useEffect } from 'react';
import { useAuth, API_BASE_URL } from '../../context/AuthContext';
import { 
  Bell, 
  AlertTriangle, 
  Layers, 
  ShieldCheck, 
  Check, 
  Trash2, 
  RefreshCw, 
  Sparkles, 
  CheckCheck,
  MapPin,
  Clock
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge, RiskBadge } from '../../components/ui/badge';

const AdminAlerts = () => {
  const { token } = useAuth();
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterSeverity, setFilterSeverity] = useState('ALL');
  const [seeding, setSeeding] = useState(false);

  const fetchAlerts = async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API_BASE_URL}/api/alerts`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setAlerts(data.alerts || data || []);
      }
    } catch (err) {
      console.error('Failed to load admin alerts:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [token]);

  const handleMarkAsRead = async (alertId) => {
    try {
      await fetch(`${API_BASE_URL}/api/alerts/${alertId}/read`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });
      setAlerts(alerts.map(a => a.alert_id === alertId || a._id === alertId ? { ...a, status: 'READ' } : a));
    } catch (err) {
      console.error('Failed to mark alert as read:', err);
    }
  };

  const handleDismiss = async (alertId) => {
    try {
      await fetch(`${API_BASE_URL}/api/alerts/${alertId}/dismiss`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });
      setAlerts(alerts.filter(a => a.alert_id !== alertId && a._id !== alertId));
    } catch (err) {
      console.error('Failed to dismiss alert:', err);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await fetch(`${API_BASE_URL}/api/alerts/read-all`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });
      setAlerts(alerts.map(a => ({ ...a, status: 'READ' })));
    } catch (err) {
      console.error('Failed to mark all read:', err);
    }
  };

  const handleSeedSamples = async () => {
    setSeeding(true);
    try {
      await fetch(`${API_BASE_URL}/api/alerts/seed-samples`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });
      await fetchAlerts();
    } catch (err) {
      console.error('Failed to seed alerts:', err);
    } finally {
      setSeeding(false);
    }
  };

  const filteredAlerts = alerts.filter(a => {
    if (filterSeverity === 'ALL') return true;
    return a.severity === filterSeverity;
  });

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
            <span>District Disease Surveillance Alerts</span>
            <Badge variant="high" className="text-xs">
              {alerts.filter(a => a.status === 'UNREAD').length} Unread
            </Badge>
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Real-time notifications for emerging spatial clusters, critical case spikes, and containment protocols
          </p>
        </div>

        <div className="flex items-center gap-2">
          {alerts.length > 0 && (
            <Button
              variant="outline"
              size="sm"
              onClick={handleMarkAllRead}
              className="text-xs gap-1.5"
            >
              <CheckCheck size={14} />
              <span>Mark All Read</span>
            </Button>
          )}

          <Button
            variant="accent"
            size="sm"
            onClick={handleSeedSamples}
            disabled={seeding}
            className="text-xs gap-1.5"
          >
            <Sparkles size={14} className={seeding ? 'animate-spin' : ''} />
            <span>Generate Sample Alerts</span>
          </Button>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex flex-wrap items-center gap-2 border-b border-slate-200 pb-3 text-xs">
        <button
          onClick={() => setFilterSeverity('ALL')}
          className={`px-3 py-1.5 rounded-xl font-medium transition-colors cursor-pointer ${
            filterSeverity === 'ALL'
              ? 'bg-emerald-800 text-white font-bold'
              : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
          }`}
        >
          All System Alerts ({alerts.length})
        </button>

        <button
          onClick={() => setFilterSeverity('CRITICAL')}
          className={`px-3 py-1.5 rounded-xl font-medium transition-colors cursor-pointer ${
            filterSeverity === 'CRITICAL'
              ? 'bg-red-600 text-white font-bold'
              : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
          }`}
        >
          Critical Severity
        </button>

        <button
          onClick={() => setFilterSeverity('HIGH')}
          className={`px-3 py-1.5 rounded-xl font-medium transition-colors cursor-pointer ${
            filterSeverity === 'HIGH'
              ? 'bg-orange-600 text-white font-bold'
              : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
          }`}
        >
          High Severity
        </button>

        <button
          onClick={() => setFilterSeverity('MEDIUM')}
          className={`px-3 py-1.5 rounded-xl font-medium transition-colors cursor-pointer ${
            filterSeverity === 'MEDIUM'
              ? 'bg-amber-600 text-white font-bold'
              : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
          }`}
        >
          Medium Severity
        </button>
      </div>

      {/* Alerts Feed */}
      {loading ? (
        <div className="text-center py-16">
          <div className="w-10 h-10 border-4 border-emerald-600 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-xs text-slate-500">Checking district alert logs...</p>
        </div>
      ) : filteredAlerts.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-2xl border border-dashed border-slate-300 p-8">
          <ShieldCheck size={36} className="text-emerald-600 mx-auto mb-3" />
          <h3 className="text-base font-bold text-slate-900">No Active Surveillance Alerts</h3>
          <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
            No critical disease clusters or surveillance warnings match the selected filter.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredAlerts.map((alert) => {
            const id = alert.alert_id || alert._id;
            const isUnread = alert.status === 'UNREAD';

            return (
              <Card
                key={id}
                className={`overflow-hidden transition-all ${
                  isUnread
                    ? 'border-l-4 border-l-red-600 bg-white shadow-xs'
                    : 'border-slate-200 bg-slate-50/50 opacity-90'
                }`}
              >
                <CardContent className="p-5 flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                  <div className="flex items-start gap-3.5">
                    <div className="w-10 h-10 rounded-xl bg-slate-100 flex items-center justify-center shrink-0 mt-0.5">
                      {alert.severity === 'CRITICAL' ? (
                        <AlertTriangle size={20} className="text-red-600" />
                      ) : alert.alert_type?.includes('CLUSTER') ? (
                        <Layers size={20} className="text-purple-600" />
                      ) : (
                        <Bell size={20} className="text-amber-600" />
                      )}
                    </div>

                    <div className="space-y-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="text-sm font-bold text-slate-900">
                          {alert.title}
                        </span>
                        <RiskBadge level={alert.severity || 'HIGH'} />
                        {isUnread && (
                          <span className="w-2 h-2 rounded-full bg-red-600 inline-block" />
                        )}
                      </div>

                      <p className="text-xs text-slate-700 leading-relaxed">
                        {alert.message}
                      </p>

                      {/* Recommended Administrative Action */}
                      {alert.recommended_action && (
                        <div className="p-2.5 rounded-lg bg-amber-50/80 border border-amber-200 text-[11px] text-amber-950 mt-2 flex items-start gap-1.5">
                          <ShieldCheck size={14} className="text-amber-700 shrink-0 mt-0.5" />
                          <div>
                            <span className="font-bold block">Surveillance Advisory:</span>
                            <span>{alert.recommended_action}</span>
                          </div>
                        </div>
                      )}

                      <div className="flex items-center gap-3 text-[10px] text-slate-400 pt-1">
                        <span>{alert.created_at ? new Date(alert.created_at).toLocaleString() : 'Recent'}</span>
                        {alert.related_cluster_id && (
                          <span>• Cluster: <strong className="text-slate-600">{alert.related_cluster_id}</strong></span>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 shrink-0 self-end sm:self-start">
                    {isUnread && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleMarkAsRead(id)}
                        className="text-xs h-8 text-emerald-700 hover:bg-emerald-50"
                        title="Mark Read"
                      >
                        <Check size={14} />
                        <span>Read</span>
                      </Button>
                    )}

                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDismiss(id)}
                      className="text-xs h-8 text-slate-400 hover:text-red-600 hover:bg-red-50"
                      title="Dismiss"
                    >
                      <Trash2 size={14} />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default AdminAlerts;
