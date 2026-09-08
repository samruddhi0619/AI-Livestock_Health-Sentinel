import React from 'react';
import SurveillanceMap from './SurveillanceMap';

/**
 * DiseaseMap wrapper providing backward compatibility while delegating
 * to the enhanced React Leaflet & OpenStreetMap SurveillanceMap.
 */
const DiseaseMap = ({ cases = [], clusters = [], userRole = 'VETERINARIAN', height = '450px' }) => {
  // Format cases to match SurveillanceMap report structure
  const formattedReports = cases.map((c, idx) => ({
    report_id: c._id || c.id || `case-${idx}`,
    animal_tag: c.animal_id || `ANM-${idx}`,
    disease: c.disease || 'Suspected Condition',
    risk_level: c.risk_level || 'Moderate',
    risk_score: c.risk_score || (c.risk_level === 'HIGH' ? 75.0 : 45.0),
    latitude: c.location?.latitude || c.latitude || 18.5204,
    longitude: c.location?.longitude || c.longitude || 73.8567,
    approximate_latitude: roundCoord(c.location?.latitude || c.latitude || 18.5204),
    approximate_longitude: roundCoord(c.location?.longitude || c.longitude || 73.8567),
    village: c.village || 'Wadgaon',
    taluka: c.taluka || 'Haveli',
    district: c.district || 'Pune',
    status: c.status || 'SUSPECTED',
    is_surveillance_triggered: c.risk_level === 'HIGH' || c.status === 'VERIFIED',
    location_access_level: c.is_exact_authorized ? 'authorized_exact' : 'approximate_public'
  }));

  // Format clusters
  const formattedClusters = clusters.map((cl, idx) => ({
    cluster_code: cl.cluster_code || `CLUSTER-${idx + 1}`,
    disease: cl.disease || 'Lumpy Skin Disease',
    center_latitude: cl.center_location?.latitude || cl.center_latitude || 18.525,
    center_longitude: cl.center_location?.longitude || cl.center_longitude || 73.860,
    radius_km: cl.radius || cl.radius_km || 1.25,
    cases_count: cl.cases_count || cl.case_count || 3,
    severity: cl.severity || 'WARNING',
    taluka: cl.taluka || 'Haveli',
    district: cl.district || 'Pune'
  }));

  const initialData = {
    reports: formattedReports,
    clusters: formattedClusters,
    hotspots: [
      {
        hotspot_id: 'hotspot-haveli',
        name: 'Haveli Transmission Hotspot',
        latitude: 18.5204,
        longitude: 73.8567,
        radius_meters: 2500,
        intensity: 0.85,
        case_count: formattedReports.length || 3,
        dominant_disease: formattedReports[0]?.disease || 'Lumpy Skin Disease',
        environmental_risk_score: 68.0,
        risk_level: 'High'
      }
    ],
    regional_indicators: [
      {
        region_name: 'Haveli',
        district: 'Pune',
        total_cases: formattedReports.length || 3,
        average_risk_score: 68.5,
        risk_level: 'High',
        predominant_disease: 'Lumpy Skin Disease',
        active_clusters: formattedClusters.length || 1,
        quarantine_active: true
      }
    ],
    filter_options: {
      diseases: ['Lumpy Skin Disease', 'Foot-and-Mouth Disease', 'Anthrax', 'Brucellosis'],
      risk_levels: ['Low', 'Medium', 'High', 'Critical'],
      regions: ['Haveli', 'Baramati', 'Pune', 'Shirur'],
      date_ranges: ['7', '14', '30', 'all']
    },
    map_center: { latitude: 18.5204, longitude: 73.8567, zoom: 12 },
    is_farmer_view: userRole === 'FARMER'
  };

  return (
    <SurveillanceMap
      initialData={initialData}
      userRole={userRole}
      height={height}
    />
  );
};

function roundCoord(val) {
  const num = parseFloat(val);
  return isNaN(num) ? 18.52 : Math.round(num * 100) / 100;
}

export default DiseaseMap;
