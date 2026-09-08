import React, { useState, useEffect, useMemo } from 'react';
import { MapContainer, TileLayer, CircleMarker, Circle, Popup, Tooltip, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Filter, AlertTriangle, Shield, Info, MapPin, RotateCcw, Activity } from 'lucide-react';

// Fix Leaflet's default icon paths in bundlers like Vite
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

// Component to dynamically adjust map bounds when filtered data changes
function MapRecenter({ reports, clusters, hotspots, defaultCenter }) {
  const map = useMap();
  useEffect(() => {
    const latLngs = [];
    reports.forEach(r => {
      if (r.latitude && r.longitude) latLngs.push([r.latitude, r.longitude]);
    });
    clusters.forEach(c => {
      if (c.center_latitude && c.center_longitude) latLngs.push([c.center_latitude, c.center_longitude]);
    });
    hotspots.forEach(h => {
      if (h.latitude && h.longitude) latLngs.push([h.latitude, h.longitude]);
    });

    if (latLngs.length > 0) {
      const bounds = L.latLngBounds(latLngs);
      if (bounds.isValid()) {
        map.fitBounds(bounds.pad(0.2));
      }
    } else if (defaultCenter) {
      map.setView([defaultCenter.latitude, defaultCenter.longitude], defaultCenter.zoom || 12);
    }
  }, [reports, clusters, hotspots, defaultCenter, map]);

  return null;
}

const SurveillanceMap = ({
  initialData = null,
  userRole = 'FARMER',
  token = null,
  height = '520px'
}) => {
  // Filters state
  const [diseaseFilter, setDiseaseFilter] = useState('All');
  const [dateRangeFilter, setDateRangeFilter] = useState('30');
  const [riskLevelFilter, setRiskLevelFilter] = useState('All');
  const [regionFilter, setRegionFilter] = useState('All');
  
  // Data state
  const [mapData, setMapData] = useState(initialData || {
    reports: [],
    clusters: [],
    hotspots: [],
    regional_indicators: [],
    filter_options: {
      diseases: ['Lumpy Skin Disease', 'Foot-and-Mouth Disease', 'Anthrax', 'Brucellosis'],
      risk_levels: ['Low', 'Medium', 'High', 'Critical'],
      regions: ['Haveli', 'Baramati', 'Pune', 'Shirur'],
      date_ranges: ['7', '14', '30', 'all']
    },
    is_farmer_view: userRole === 'FARMER',
    map_center: { latitude: 18.5204, longitude: 73.8567, zoom: 12 }
  });
  
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('map'); // 'map' or 'regions'

  // Fetch updated map data from backend API
  const fetchSurveillanceData = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (diseaseFilter !== 'All') params.append('disease', diseaseFilter);
      if (riskLevelFilter !== 'All') params.append('risk_level', riskLevelFilter);
      if (regionFilter !== 'All') params.append('region', regionFilter);
      if (dateRangeFilter !== 'all') params.append('days', dateRangeFilter);

      const headers = { 'Content-Type': 'application/json' };
      const authToken = token || localStorage.getItem('token');
      if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
      }

      const response = await fetch(`/api/reports/surveillance-map?${params.toString()}`, { headers });
      if (response.ok) {
        const json = await response.json();
        setMapData(json);
      }
    } catch (err) {
      console.warn('Failed to fetch surveillance map data, maintaining cached state:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSurveillanceData();
  }, [diseaseFilter, dateRangeFilter, riskLevelFilter, regionFilter]);

  const handleResetFilters = () => {
    setDiseaseFilter('All');
    setDateRangeFilter('30');
    setRiskLevelFilter('All');
    setRegionFilter('All');
  };

  // Color mappings
  const getRiskColor = (level) => {
    switch (level?.toLowerCase()) {
      case 'critical': return '#dc2626'; // Dark Red
      case 'high': return '#f97316';     // Orange
      case 'medium':
      case 'moderate': return '#eab308'; // Amber
      case 'low': return '#16a34a';      // Emerald Green
      default: return '#3b82f6';
    }
  };

  const isFarmerView = mapData.is_farmer_view ?? (userRole === 'FARMER');

  return (
    <div style={{
      fontFamily: "'Outfit', system-ui, -apple-system, sans-serif",
      backgroundColor: '#ffffff',
      borderRadius: '16px',
      boxShadow: '0 4px 20px -2px rgba(0, 0, 0, 0.06)',
      border: '1px solid #e2e8f0',
      overflow: 'hidden'
    }}>
      {/* 1. Header & Dynamic Controls Bar */}
      <div style={{
        padding: '1.25rem 1.5rem',
        borderBottom: '1px solid #f1f5f9',
        backgroundColor: '#f8fafc'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '1rem' }}>
          <div>
            <h3 style={{ margin: 0, fontSize: '1.2rem', fontWeight: 700, color: '#0f172a', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Activity size={20} color="#0284c7" />
              Livestock Disease Surveillance Map
            </h3>
            <p style={{ margin: '4px 0 0 0', fontSize: '0.85rem', color: '#64748b' }}>
              {isFarmerView 
                ? 'Regional early warning network prioritizing community risk indicators & cluster zones.'
                : 'Veterinary clinical surveillance view with authorized triage tracking & containment mapping.'}
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{
              fontSize: '0.75rem',
              fontWeight: 600,
              padding: '4px 10px',
              borderRadius: '9999px',
              backgroundColor: isFarmerView ? '#dbeafe' : '#fef3c7',
              color: isFarmerView ? '#1e40af' : '#92400e'
            }}>
              {isFarmerView ? '🌾 Farmer View: Regional Focus' : '🩺 Clinician/Admin View'}
            </span>
            {loading && <span style={{ fontSize: '0.8rem', color: '#0284c7' }}>Updating...</span>}
          </div>
        </div>

        {/* Filters Row */}
        <div style={{
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          gap: '12px',
          paddingTop: '8px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', fontWeight: 600, color: '#475569' }}>
            <Filter size={16} /> Filters:
          </div>

          {/* Disease Filter */}
          <select
            value={diseaseFilter}
            onChange={(e) => setDiseaseFilter(e.target.value)}
            style={{
              padding: '6px 12px',
              borderRadius: '8px',
              border: '1px solid #cbd5e1',
              backgroundColor: '#ffffff',
              fontSize: '0.85rem',
              color: '#334155',
              cursor: 'pointer'
            }}
          >
            <option value="All">All Diseases</option>
            {mapData.filter_options?.diseases?.map((d) => (
              <option key={d} value={d}>{d}</option>
            ))}
          </select>

          {/* Date Range Filter */}
          <select
            value={dateRangeFilter}
            onChange={(e) => setDateRangeFilter(e.target.value)}
            style={{
              padding: '6px 12px',
              borderRadius: '8px',
              border: '1px solid #cbd5e1',
              backgroundColor: '#ffffff',
              fontSize: '0.85rem',
              color: '#334155',
              cursor: 'pointer'
            }}
          >
            <option value="7">Last 7 Days</option>
            <option value="14">Last 14 Days</option>
            <option value="30">Last 30 Days</option>
            <option value="all">All Time</option>
          </select>

          {/* Risk Level Filter */}
          <select
            value={riskLevelFilter}
            onChange={(e) => setRiskLevelFilter(e.target.value)}
            style={{
              padding: '6px 12px',
              borderRadius: '8px',
              border: '1px solid #cbd5e1',
              backgroundColor: '#ffffff',
              fontSize: '0.85rem',
              color: '#334155',
              cursor: 'pointer'
            }}
          >
            <option value="All">All Risk Tiers</option>
            <option value="Critical">Critical (81-100)</option>
            <option value="High">High (61-80)</option>
            <option value="Medium">Medium (31-60)</option>
            <option value="Low">Low (0-30)</option>
          </select>

          {/* Region Filter */}
          <select
            value={regionFilter}
            onChange={(e) => setRegionFilter(e.target.value)}
            style={{
              padding: '6px 12px',
              borderRadius: '8px',
              border: '1px solid #cbd5e1',
              backgroundColor: '#ffffff',
              fontSize: '0.85rem',
              color: '#334155',
              cursor: 'pointer'
            }}
          >
            <option value="All">All Regions / Talukas</option>
            {mapData.filter_options?.regions?.map((r) => (
              <option key={r} value={r}>{r}</option>
            ))}
          </select>

          {/* Reset Filters Button */}
          <button
            onClick={handleResetFilters}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              padding: '6px 12px',
              borderRadius: '8px',
              border: '1px solid #e2e8f0',
              backgroundColor: '#ffffff',
              color: '#64748b',
              fontSize: '0.8rem',
              cursor: 'pointer',
              fontWeight: 500
            }}
          >
            <RotateCcw size={14} /> Reset
          </button>
        </div>
      </div>

      {/* 2. Farmer Privacy Notice Banner */}
      {isFarmerView && (
        <div style={{
          backgroundColor: '#eff6ff',
          padding: '0.65rem 1.25rem',
          borderBottom: '1px solid #dbeafe',
          fontSize: '0.8rem',
          color: '#1e40af',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <Shield size={16} color="#2563eb" />
          <span>
            <strong>Agricultural Privacy Active:</strong> Exact farm homestead coordinates are concealed.
            The map highlights regional alert zones, cluster perimeters, and your own registered cattle.
          </span>
        </div>
      )}

      {/* 3. Regional Risk Indicators Bar */}
      {mapData.regional_indicators?.length > 0 && (
        <div style={{
          padding: '0.75rem 1.5rem',
          backgroundColor: '#ffffff',
          borderBottom: '1px solid #f1f5f9',
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          gap: '12px'
        }}>
          <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#475569', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            Regional Risk:
          </span>
          {mapData.regional_indicators.map((reg, idx) => (
            <div
              key={idx}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '4px 10px',
                borderRadius: '8px',
                backgroundColor: reg.risk_level === 'High' || reg.risk_level === 'Critical' ? '#fef2f2' : '#f0fdf4',
                border: `1px solid ${reg.risk_level === 'High' || reg.risk_level === 'Critical' ? '#fecaca' : '#bbf7d0'}`,
                fontSize: '0.8rem'
              }}
            >
              <span style={{ fontWeight: 600, color: '#0f172a' }}>{reg.region_name}:</span>
              <span style={{
                fontWeight: 700,
                color: getRiskColor(reg.risk_level),
                textTransform: 'uppercase',
                fontSize: '0.75rem'
              }}>
                {reg.risk_level} ({reg.average_risk_score}/100)
              </span>
              <span style={{ color: '#64748b', fontSize: '0.75rem' }}>
                • {reg.predominant_disease} ({reg.total_cases} reports)
              </span>
              {reg.active_clusters > 0 && (
                <span style={{
                  backgroundColor: '#dc2626',
                  color: '#ffffff',
                  fontSize: '0.65rem',
                  fontWeight: 700,
                  padding: '1px 5px',
                  borderRadius: '4px'
                }}>
                  {reg.active_clusters} CLUSTER
                </span>
              )}
            </div>
          ))}
        </div>
      )}

      {/* 4. The Leaflet Map Container */}
      <div style={{ position: 'relative', height: height, width: '100%' }}>
        <MapContainer
          center={[mapData.map_center.latitude, mapData.map_center.longitude]}
          zoom={mapData.map_center.zoom}
          style={{ height: '100%', width: '100%' }}
          scrollWheelZoom={true}
        >
          {/* OpenStreetMap Base Tile Layer */}
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          <MapRecenter
            reports={mapData.reports || []}
            clusters={mapData.clusters || []}
            hotspots={mapData.hotspots || []}
            defaultCenter={mapData.map_center}
          />

          {/* Layer A: Disease Outbreak Clusters (DBSCAN) */}
          {mapData.clusters?.map((cluster, idx) => (
            <Circle
              key={`cluster-${idx}`}
              center={[cluster.center_latitude, cluster.center_longitude]}
              radius={cluster.radius_km * 1000}
              pathOptions={{
                color: '#dc2626',
                fillColor: '#ef4444',
                fillOpacity: 0.18,
                weight: 2,
                dashArray: '6, 6'
              }}
            >
              <Popup>
                <div style={{ fontFamily: 'sans-serif', fontSize: '0.85rem', minWidth: '220px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#dc2626', fontWeight: 700, marginBottom: '6px' }}>
                    <AlertTriangle size={18} />
                    <span>EPIDEMIC OUTBREAK CLUSTER</span>
                  </div>
                  <div style={{ fontSize: '0.9rem', fontWeight: 600, color: '#0f172a' }}>
                    {cluster.disease}
                  </div>
                  <div style={{ margin: '4px 0', color: '#334155' }}>
                    <strong>Cluster Code:</strong> {cluster.cluster_code}
                  </div>
                  <div style={{ margin: '4px 0', color: '#334155' }}>
                    <strong>Cases in Zone:</strong> {cluster.cases_count} cases
                  </div>
                  <div style={{ margin: '4px 0', color: '#334155' }}>
                    <strong>Containment Radius:</strong> {cluster.radius_km} km
                  </div>
                  <div style={{ margin: '4px 0', color: '#334155' }}>
                    <strong>Location:</strong> {cluster.taluka}, {cluster.district}
                  </div>
                  <div style={{
                    marginTop: '8px',
                    padding: '6px',
                    backgroundColor: '#fef2f2',
                    borderRadius: '6px',
                    fontSize: '0.75rem',
                    color: '#991b1b',
                    fontWeight: 500
                  }}>
                    ⚠️ Biosecurity protocol active. Movement restriction advised.
                  </div>
                </div>
              </Popup>
            </Circle>
          ))}

          {/* Layer B: Potential Hotspots (Bioclimatic + Density) */}
          {mapData.hotspots?.map((hotspot, idx) => (
            <Circle
              key={`hotspot-${idx}`}
              center={[hotspot.latitude, hotspot.longitude]}
              radius={hotspot.radius_meters || 2500}
              pathOptions={{
                color: '#f97316',
                fillColor: '#fb923c',
                fillOpacity: 0.12,
                weight: 1.5
              }}
            >
              <Tooltip direction="top" opacity={0.9}>
                <span>🔥 {hotspot.name} ({hotspot.dominant_disease})</span>
              </Tooltip>
              <Popup>
                <div style={{ fontFamily: 'sans-serif', fontSize: '0.85rem' }}>
                  <h4 style={{ margin: '0 0 6px 0', color: '#c2410c' }}>{hotspot.name}</h4>
                  <p style={{ margin: '3px 0' }}><strong>Dominant Disease:</strong> {hotspot.dominant_disease}</p>
                  <p style={{ margin: '3px 0' }}><strong>Reported Cases:</strong> {hotspot.case_count}</p>
                  <p style={{ margin: '3px 0' }}><strong>Environmental Risk:</strong> {hotspot.environmental_risk_score}/100</p>
                  <p style={{ margin: '3px 0' }}><strong>Risk Tier:</strong> <span style={{ color: getRiskColor(hotspot.risk_level), fontWeight: 700 }}>{hotspot.risk_level}</span></p>
                </div>
              </Popup>
            </Circle>
          ))}

          {/* Layer C: Individual Reports (Where Authorized) */}
          {mapData.reports?.map((report, idx) => {
            const riskColor = getRiskColor(report.risk_level);
            const isAuthorizedExact = report.location_access_level === 'authorized_exact';
            
            return (
              <CircleMarker
                key={`report-${idx}`}
                center={[report.latitude, report.longitude]}
                radius={isAuthorizedExact ? 8 : 7}
                pathOptions={{
                  color: report.is_surveillance_triggered ? '#991b1b' : '#ffffff',
                  fillColor: riskColor,
                  fillOpacity: 0.85,
                  weight: report.is_surveillance_triggered ? 2.5 : 1.5
                }}
              >
                <Popup>
                  <div style={{ fontFamily: 'sans-serif', fontSize: '0.85rem', minWidth: '190px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                      <span style={{ fontWeight: 700, fontSize: '0.9rem', color: '#0f172a' }}>
                        {report.animal_tag}
                      </span>
                      <span style={{
                        backgroundColor: riskColor,
                        color: '#ffffff',
                        fontSize: '0.7rem',
                        fontWeight: 700,
                        padding: '2px 6px',
                        borderRadius: '4px'
                      }}>
                        {report.risk_level}
                      </span>
                    </div>

                    <div style={{ margin: '4px 0', color: '#334155' }}>
                      <strong>Suspected Condition:</strong> {report.disease}
                    </div>
                    <div style={{ margin: '4px 0', color: '#334155' }}>
                      <strong>Multi-Modal Risk:</strong> {report.risk_score}/100
                    </div>
                    <div style={{ margin: '4px 0', color: '#334155' }}>
                      <strong>Location:</strong> {report.village}, {report.taluka}
                    </div>
                    <div style={{ margin: '4px 0', color: '#64748b', fontSize: '0.75rem' }}>
                      <strong>Coordinate Precision:</strong> {isAuthorizedExact ? 'Authorized Farm GPS' : 'Approximate Area (~1.1km)'}
                    </div>
                    {report.is_surveillance_triggered && (
                      <div style={{
                        marginTop: '6px',
                        padding: '4px 6px',
                        backgroundColor: '#fef2f2',
                        color: '#991b1b',
                        borderRadius: '4px',
                        fontSize: '0.75rem',
                        fontWeight: 600
                      }}>
                        🚨 Official Surveillance Case Active
                      </div>
                    )}
                    <div style={{ marginTop: '8px', fontSize: '0.7rem', color: '#94a3b8', fontStyle: 'italic', borderTop: '1px solid #e2e8f0', paddingTop: '4px' }}>
                      Not a veterinary diagnosis. Early warning screening only.
                    </div>
                  </div>
                </Popup>
              </CircleMarker>
            );
          })}
        </MapContainer>

        {/* 5. Map Legend Overlay */}
        <div style={{
          position: 'absolute',
          bottom: '15px',
          right: '15px',
          backgroundColor: 'rgba(255, 255, 255, 0.96)',
          backdropFilter: 'blur(4px)',
          padding: '0.75rem 1rem',
          borderRadius: '10px',
          fontSize: '0.78rem',
          boxShadow: '0 4px 16px rgba(0,0,0,0.15)',
          zIndex: 1000,
          border: '1px solid #e2e8f0',
          display: 'flex',
          flexDirection: 'column',
          gap: '5px',
          maxWidth: '240px'
        }}>
          <div style={{ fontWeight: 700, color: '#0f172a', borderBottom: '1px solid #e2e8f0', paddingBottom: '3px' }}>
            Surveillance Legend
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#dc2626', display: 'inline-block' }} />
            <span>Critical Risk (81-100)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#f97316', display: 'inline-block' }} />
            <span>High Risk (61-80)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#eab308', display: 'inline-block' }} />
            <span>Medium Risk (31-60)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#16a34a', display: 'inline-block' }} />
            <span>Low Risk (0-30)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '3px' }}>
            <span style={{ width: '22px', height: '10px', border: '1.5px dashed #dc2626', backgroundColor: 'rgba(239, 68, 68, 0.2)', display: 'inline-block' }} />
            <span>DBSCAN Outbreak Zone</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ width: '22px', height: '10px', border: '1px solid #f97316', backgroundColor: 'rgba(251, 146, 60, 0.15)', display: 'inline-block' }} />
            <span>Potential Hotspot</span>
          </div>
          <div style={{ fontSize: '0.7rem', color: '#64748b', marginTop: '2px', borderTop: '1px solid #f1f5f9', paddingTop: '3px' }}>
            {isFarmerView ? '• Farm locations masked to ~1.1km' : '• Verified triage access enabled'}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SurveillanceMap;
