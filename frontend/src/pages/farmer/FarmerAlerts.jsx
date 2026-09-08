import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { alertsApi } from '../../api/client';
import { 
  Bell, 
  AlertTriangle, 
  ShieldCheck, 
  Syringe, 
  MapPin, 
  Check, 
  Trash2, 
  RefreshCw, 
  Sparkles,
  Info,
  CheckCheck
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge, RiskBadge } from '../../components/ui/badge';

const FarmerAlerts = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterType, setFilterType] = useState('ALL');
  const [seeding, setSeeding] = useState(false);

  const fetchAlerts = async () => {
    try {
      const data = await alertsApi.getAlerts();
      setAlerts(data.alerts || data || []);
    } catch (err) {
      console.error('Error fetching farmer alerts:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, []);

  const handleMarkAsRead = async (alertId) => {
    try {
      await alertsApi.markRead(alertId);
      setAlerts(alerts.map(a => a.alert_id === alertId || a._id === alertId ? { ...a, status: 'READ' } : a));
    } catch (err) {
      console.error('Failed to mark alert as read:', err);
    }
  };

  const handleDismiss = async (alertId) => {
    try {
      await alertsApi.dismissAlert(alertId);
      setAlerts(alerts.filter(a => a.alert_id !== alertId && a._id !== alertId));
    } catch (err) {
      console.error('Failed to dismiss alert:', err);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await alertsApi.markAllRead();
      setAlerts(alerts.map(a => ({ ...a, status: 'READ' })));
    } catch (err) {
      console.error('Failed to mark all as read:', err);
    }
  };

  const handleSeedSamples = async () => {
    setSeeding(true);
    try {
      await alertsApi.seedSamples();
      await fetchAlerts();
    } catch (err) {
      console.error('Failed to seed sample alerts:', err);
    } finally {
      setSeeding(false);
    }
  };

  const filteredAlerts = alerts.filter(a => {
    if (filterType === 'ALL') return true;
    return a.alert_type === filterType;
  });

  const getAlertIcon = (type) => {
    switch (type) {
      case 'HIGH_RISK_ANIMAL':
        return <AlertTriangle size={18} className="text-orange-600" />;
      case 'VACCINATION_DUE':
        return <Syringe size={18} className="text-blue-600" />;
      case 'REGIONAL_DISEASE_RISK':
        return <MapPin size={18} className="text-rose-600" />;
      default:
        return <Bell size={18} className="text-emerald-700" />;
    }
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
            <span>Farmer Alerts & Early Warnings</span>
            <Badge variant="primary" className="text-xs">
              {alerts.filter(a => a.status === 'UNREAD').length} Unread
            </Badge>
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Role-tailored livestock health notices, booster alerts, and regional surveillance updates
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
            <span>Seed Sample Alerts</span>
          </Button>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex flex-wrap items-center gap-2 border-b border-slate-200 pb-3 text-xs">
        <button
          onClick={() => setFilterType('ALL')}
          className={`px-3 py-1.5 rounded-xl font-medium transition-colors cursor-pointer ${
            filterType === 'ALL'
              ? 'bg-emerald-800 text-white font-bold'
              : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
          }`}
        >
          All Alerts ({alerts.length})
        </button>

        <button
          onClick={() => setFilterType('HIGH_RISK_ANIMAL')}
          className={`px-3 py-1.5 rounded-xl font-medium transition-colors cursor-pointer ${
            filterType === 'HIGH_RISK_ANIMAL'
              ? 'bg-orange-600 text-white font-bold'
              : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
          }`}
        >
          High-Risk Animals
        </button>

        <button
          onClick={() => setFilterType('VACCINATION_DUE')}
          className={`px-3 py-1.5 rounded-xl font-medium transition-colors cursor-pointer ${
            filterType === 'VACCINATION_DUE'
              ? 'bg-blue-600 text-white font-bold'
              : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
          }`}
        >
          Vaccination Due
        </button>

        <button
          onClick={() => setFilterType('REGIONAL_DISEASE_RISK')}
          className={`px-3 py-1.5 rounded-xl font-medium transition-colors cursor-pointer ${
            filterType === 'REGIONAL_DISEASE_RISK'
              ? 'bg-rose-600 text-white font-bold'
              : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
          }`}
        >
          Regional Risk
        </button>
      </div>

      {/* Alerts Feed */}
      {loading ? (
        <div className="text-center py-16">
          <div className="w-10 h-10 border-4 border-emerald-600 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-xs text-slate-500">Checking alert feed...</p>
        </div>
      ) : filteredAlerts.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-2xl border border-dashed border-slate-300 p-8">
          <div className="w-14 h-14 rounded-2xl bg-emerald-50 text-emerald-700 flex items-center justify-center mx-auto mb-3">
            <CheckCircle2 size={28} />
          </div>
          <h3 className="text-base font-bold text-slate-900">All Clear! No Active Alerts</h3>
          <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
            Your registered herd has no critical warnings or overdue vaccination actions right now.
          </p>
          <Button
            variant="outline"
            size="sm"
            onClick={handleSeedSamples}
            className="mt-4 text-xs gap-1.5"
          >
            <Sparkles size={14} />
            <span>Generate Demo Alerts</span>
          </Button>
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
                    ? 'border-l-4 border-l-emerald-600 bg-white shadow-xs'
                    : 'border-slate-200 bg-slate-50/50 opacity-90'
                }`}
              >
                <CardContent className="p-4 sm:p-5 flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                  <div className="flex items-start gap-3.5">
                    <div className="w-10 h-10 rounded-xl bg-slate-100 flex items-center justify-center shrink-0 mt-0.5">
                      {getAlertIcon(alert.alert_type)}
                    </div>

                    <div className="space-y-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="text-sm font-bold text-slate-900">
                          {alert.title}
                        </span>
                        <RiskBadge level={alert.severity || 'LOW'} />
                        {isUnread && (
                          <span className="w-2 h-2 rounded-full bg-emerald-600 inline-block" />
                        )}
                      </div>

                      <p className="text-xs text-slate-700 leading-relaxed">
                        {alert.message}
                      </p>

                      {/* Recommended Next Action */}
                      {alert.recommended_action && (
                        <div className="p-2.5 rounded-lg bg-emerald-50/70 border border-emerald-100 text-[11px] text-emerald-950 mt-2 flex items-start gap-1.5">
                          <ShieldCheck size={14} className="text-emerald-700 shrink-0 mt-0.5" />
                          <div>
                            <span className="font-bold block">Recommended Action:</span>
                            <span>{alert.recommended_action}</span>
                          </div>
                        </div>
                      )}

                      <div className="flex items-center gap-3 text-[10px] text-slate-400 pt-1">
                        <span>{alert.created_at ? new Date(alert.created_at).toLocaleString() : 'Recent'}</span>
                        {alert.related_animal_id && (
                          <span>• Animal: <strong className="text-slate-600">{alert.related_animal_id}</strong></span>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2 shrink-0 self-end sm:self-start">
                    {isUnread && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleMarkAsRead(id)}
                        className="text-xs h-8 text-emerald-700 hover:bg-emerald-50"
                        title="Mark as Read"
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
                      title="Dismiss Alert"
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

export default FarmerAlerts;
