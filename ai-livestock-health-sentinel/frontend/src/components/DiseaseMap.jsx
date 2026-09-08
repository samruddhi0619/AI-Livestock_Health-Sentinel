import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Programmatically resolve Leaflet default marker asset paths in Vite
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

const DiseaseMap = ({ cases = [], clusters = [] }) => {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const markersLayerRef = useRef(null);

  useEffect(() => {
    // 1. Initialize map if not yet done
    if (!mapInstanceRef.current && mapContainerRef.current) {
      // Default to Maharashtra coordinates (Pune: 18.5204, 73.8567)
      const map = L.map(mapContainerRef.current).setView([18.525, 73.860], 13);
      
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
      }).addTo(map);

      mapInstanceRef.current = map;
      markersLayerRef.current = L.layerGroup().addTo(map);
    }

    // 2. Clear previous markers/overlays
    if (markersLayerRef.current) {
      markersLayerRef.current.clearLayers();
    }

    const map = mapInstanceRef.current;
    const layerGroup = markersLayerRef.current;

    if (!map || !layerGroup) return;

    // Helper for risk colors
    const getRiskColor = (level) => {
      switch (level?.toUpperCase()) {
        case 'HIGH': return 'hsl(0, 75%, 52%)';
        case 'MODERATE': return 'hsl(38, 92%, 48%)';
        default: return 'hsl(142, 65%, 38%)';
      }
    };

    // 3. Render cases
    cases.forEach((c) => {
      const lat = c.location?.latitude || c.latitude;
      const lng = c.location?.longitude || c.longitude;
      
      if (!lat || !lng) return;

      const riskColor = getRiskColor(c.risk_level);
      const isVerified = c.status === 'VERIFIED';
      
      // Draw a neat circle marker for each case
      const marker = L.circleMarker([lat, lng], {
        radius: 8,
        fillColor: riskColor,
        color: isVerified ? '#000000' : '#ffffff',
        weight: isVerified ? 2.5 : 1.5,
        opacity: 1,
        fillOpacity: 0.85
      });

      const popupContent = `
        <div style="font-family: 'Outfit', sans-serif; font-size: 0.85rem; min-width: 160px;">
          <h4 style="margin:0 0 4px 0; color: hsl(var(--primary)); font-weight:600;">
            ${c.disease}
          </h4>
          <p style="margin:2px 0;"><strong>Animal ID:</strong> ${c.animal_id}</p>
          <p style="margin:2px 0;"><strong>Status:</strong> 
            <span style="font-weight:700; color: ${c.status === 'VERIFIED' ? 'green' : 'orange'};">
              ${c.status}
            </span>
          </p>
          <p style="margin:2px 0;"><strong>Risk:</strong> 
            <span style="font-weight:700; color: ${riskColor};">${c.risk_level}</span>
          </p>
          <p style="margin:2px 0;"><strong>Location:</strong> ${c.village || 'Pune'}</p>
        </div>
      `;
      marker.bindPopup(popupContent);
      layerGroup.addLayer(marker);
    });

    // 4. Render Outbreak Clusters (Draw concentric alerts circles)
    clusters.forEach((cluster) => {
      const lat = cluster.center_location?.latitude;
      const lng = cluster.center_location?.longitude;
      const radiusMeters = (cluster.radius || 1) * 1000;

      if (!lat || !lng) return;

      // Draw the main warning zone circle
      const circle = L.circle([lat, lng], {
        radius: radiusMeters,
        color: '#ef4444',
        weight: 1.5,
        fillColor: '#ef4444',
        fillOpacity: 0.15,
        dashArray: '5, 5'
      });

      const popupContent = `
        <div style="font-family: 'Outfit', sans-serif; font-size: 0.85rem; min-width: 200px;">
          <h4 style="margin:0 0 4px 0; color:#dc2626; font-weight:700;">
            ⚠️ POSSIBLE OUTBREAK ZONE
          </h4>
          <p style="margin:2px 0;"><strong>Disease:</strong> ${cluster.disease}</p>
          <p style="margin:2px 0;"><strong>Cases Count:</strong> ${cluster.cases_count}</p>
          <p style="margin:2px 0;"><strong>Radius:</strong> ${cluster.radius} km</p>
          <p style="margin:2px 0;"><strong>Farms Affected:</strong> ${cluster.affected_farms?.join(', ')}</p>
          <p style="margin:4px 0 0 0; font-size:0.75rem; color:#6b7280; font-style:italic;">
            Status: Veterinary Verification Pending
          </p>
        </div>
      `;
      circle.bindPopup(popupContent);
      layerGroup.addLayer(circle);
    });

    // Adjust map bounds if cases exist
    if (cases.length > 0) {
      const group = new L.FeatureGroup(layerGroup.getLayers());
      if (group.getBounds().isValid()) {
        map.fitBounds(group.getBounds().pad(0.1));
      }
    }

  }, [cases, clusters]);

  // Clean up Leaflet instance on unmount
  useEffect(() => {
    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  return (
    <div style={{ position: 'relative' }}>
      <div ref={mapContainerRef} id="map" style={{ height: '400px', width: '100%', borderRadius: '12px' }} />
      
      {/* Map Legend Overlay */}
      <div style={{
        position: 'absolute',
        bottom: '15px',
        right: '15px',
        backgroundColor: 'rgba(255,255,255,0.95)',
        padding: '0.75rem 1rem',
        borderRadius: '8px',
        fontSize: '0.8rem',
        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
        zIndex: 1000,
        fontFamily: "'Outfit', sans-serif",
        border: '1px solid #e2e8f0',
        display: 'flex',
        flexDirection: 'column',
        gap: '4px'
      }}>
        <div style={{ fontWeight: 600, marginBottom: '4px', borderBottom: '1px solid #edf2f7', paddingBottom: '2px' }}>
          Map Legend
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: 'hsl(0, 75%, 52%)', display: 'inline-block' }} />
          <span>High Risk Case</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: 'hsl(38, 92%, 48%)', display: 'inline-block' }} />
          <span>Moderate Risk Case</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: 'hsl(142, 65%, 38%)', display: 'inline-block' }} />
          <span>Low Risk Case</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '2px' }}>
          <span style={{ width: '12px', height: '12px', borderRadius: '50%', border: '2px solid #000000', display: 'inline-block' }} />
          <span>Verified Diagnosis</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ width: '20px', height: '10px', border: '1px dashed #ef4444', backgroundColor: 'rgba(239, 68, 68, 0.15)', display: 'inline-block' }} />
          <span>Outbreak cluster Zone</span>
        </div>
      </div>
    </div>
  );
};

export default DiseaseMap;
