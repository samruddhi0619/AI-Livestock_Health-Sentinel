import React from 'react';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Map, ArrowLeft, ShieldCheck, Info, Layers, Filter } from 'lucide-react';
import SurveillanceMap from '../../components/SurveillanceMap';
import { Card, CardContent } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Button } from '../../components/ui/button';

const SurveillanceMapPage = () => {
  const { token, user } = useAuth();
  const navigate = useNavigate();
  const userRole = (user?.role || 'ADMIN').toUpperCase();

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate(-1)}
            className="p-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-600 transition-colors cursor-pointer"
          >
            <ArrowLeft size={18} />
          </button>
          <div>
            <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
              <span>Geospatial Disease Surveillance Map</span>
              <Badge variant="primary" className="text-xs">
                React Leaflet + OpenStreetMap
              </Badge>
            </h1>
            <p className="text-xs text-slate-500 mt-0.5">
              Epidemiological tracking of high-risk cases, density hotspots, and DBSCAN potential clusters
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Badge variant="outline" className="text-xs bg-white text-slate-700 py-1.5 px-3">
            Role: <strong>{userRole}</strong> (Detailed Access Authorized)
          </Badge>
        </div>
      </div>

      {/* Main Map Card */}
      <Card className="border-slate-200 shadow-md overflow-hidden">
        <CardContent className="p-4 sm:p-6">
          <SurveillanceMap
            userRole={userRole}
            token={token}
            height="620px"
          />
        </CardContent>
      </Card>

      {/* Privacy Preservation and Containment Guidelines */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
        <div className="p-4 rounded-2xl bg-emerald-50/80 border border-emerald-200 text-emerald-950 space-y-1.5">
          <span className="font-bold flex items-center gap-1.5 text-sm text-emerald-900">
            <ShieldCheck size={16} className="text-emerald-700" />
            Location Privacy Preservation Standard
          </span>
          <p className="text-emerald-900/90 leading-relaxed text-[11px]">
            To protect smallholder farmers, farm coordinates are obfuscated on external maps using centroid aggregation. For authorized veterinarians and administrators, high-risk case coordinates are accessible solely for disease prevention and containment enforcement.
          </p>
        </div>

        <div className="p-4 rounded-2xl bg-purple-50/80 border border-purple-200 text-purple-950 space-y-1.5">
          <span className="font-bold flex items-center gap-1.5 text-sm text-purple-900">
            <Layers size={16} className="text-purple-700" />
            DBSCAN Spatial Cluster Guidance
          </span>
          <p className="text-purple-900/90 leading-relaxed text-[11px]">
            Circles with a red/purple radius designate <em>Potential Disease Clusters</em> detected when multiple high-risk reports converge within a 5.0 km radius in 14 days. These signify proactive surveillance perimeters rather than confirmed outbreaks.
          </p>
        </div>
      </div>
    </div>
  );
};

export default SurveillanceMapPage;
