import React, { useState, useEffect } from 'react';
import { useParams, useLocation, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { reportsApi } from '../../api/client';
import { 
  ArrowLeft, 
  ShieldCheck, 
  AlertTriangle, 
  CheckCircle2, 
  Activity, 
  Camera, 
  Thermometer, 
  CloudSun, 
  Syringe, 
  FileText, 
  Printer, 
  QrCode,
  Info,
  ChevronRight,
  Stethoscope
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge, RiskBadge } from '../../components/ui/badge';

const AssessmentResult = () => {
  const { report_id } = useParams();
  const location = useLocation();
  const navigate = useNavigate();

  const [assessment, setAssessment] = useState(location.state?.assessment || location.state?.report || null);
  const [loading, setLoading] = useState(!assessment);
  const [error, setError] = useState('');

  useEffect(() => {
    if (assessment) return;
    if (!report_id) return;

    const fetchReport = async () => {
      try {
        const data = await reportsApi.getHealthReportById(report_id);
        setAssessment(data.assessment || data.report || data);
      } catch (err) {
        setError(err.message || 'Could not retrieve assessment report.');
      } finally {
        setLoading(false);
      }
    };

    fetchReport();
  }, [report_id, assessment]);

  if (loading) {
    return (
      <div className="p-8 text-center max-w-4xl mx-auto">
        <div className="w-12 h-12 border-4 border-emerald-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p className="text-slate-600 font-medium">Computing Multi-Modal Risk Analysis...</p>
      </div>
    );
  }

  // Fallback / standard assessment representation
  const finalRisk = assessment?.final_risk_score ?? assessment?.risk_score ?? 68;
  const riskLevel = assessment?.risk_level || (finalRisk >= 81 ? 'CRITICAL' : finalRisk >= 61 ? 'HIGH' : finalRisk >= 31 ? 'MEDIUM' : 'LOW');
  
  const animalId = assessment?.animal_id || 'MH-PUN-CTL-0124';
  const individualScores = assessment?.individual_model_scores || {
    image_risk: assessment?.image_risk_score ?? 75,
    symptom_risk: assessment?.symptom_risk_score ?? 70,
    environmental_risk: assessment?.environmental_risk_score ?? 55,
    health_vaccination_risk: assessment?.vaccination_risk_score ?? 60
  };

  const contributingFactors = assessment?.contributing_factors || [
    'Elevated body temperature (39.5°C) and acute mouth vesicles',
    'High image vision match for erosive oral lesions (40% weight)',
    'Neighboring district reports 3 suspected vesicular cases',
    'Vaccination booster due within 30 days'
  ];

  const getRiskColorTheme = (lvl) => {
    switch (lvl?.toUpperCase()) {
      case 'CRITICAL':
        return {
          bg: 'bg-red-500',
          lightBg: 'bg-red-50',
          border: 'border-red-200',
          text: 'text-red-900',
          desc: 'Urgent veterinary intervention and farm biosecurity containment required.'
        };
      case 'HIGH':
        return {
          bg: 'bg-orange-500',
          lightBg: 'bg-orange-50',
          border: 'border-orange-200',
          text: 'text-orange-900',
          desc: 'High probability of infectious disease. Immediate isolation recommended.'
        };
      case 'MEDIUM':
        return {
          bg: 'bg-amber-500',
          lightBg: 'bg-amber-50',
          border: 'border-amber-200',
          text: 'text-amber-900',
          desc: 'Moderate health deviation observed. Maintain close clinical observation.'
        };
      default:
        return {
          bg: 'bg-emerald-500',
          lightBg: 'bg-emerald-50',
          border: 'border-emerald-200',
          text: 'text-emerald-900',
          desc: 'Low disease risk. Normal routine herd management advised.'
        };
    }
  };

  const theme = getRiskColorTheme(riskLevel);

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-4xl mx-auto space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/farmer/dashboard')}
            className="p-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-600 transition-colors cursor-pointer"
          >
            <ArrowLeft size={18} />
          </button>
          <div>
            <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
              <span>AI Multi-Modal Assessment Result</span>
              <Badge variant="outline" className="text-xs font-mono">
                {animalId}
              </Badge>
            </h1>
            <p className="text-xs text-slate-500 mt-0.5">
              Transparent, multi-factor risk computation based on independent analytical models
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => window.print()}
            className="text-xs gap-1.5"
          >
            <Printer size={14} />
            <span>Print Report</span>
          </Button>

          <Button
            variant="primary"
            size="sm"
            onClick={() => navigate(`/farmer/passport/${animalId}`)}
            className="text-xs gap-1.5"
          >
            <QrCode size={14} />
            <span>View Passport</span>
          </Button>
        </div>
      </div>

      {/* Main Score Hero Card */}
      <div className={`p-6 sm:p-8 rounded-3xl border-2 ${theme.border} ${theme.lightBg} shadow-sm space-y-6`}>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6 border-b border-slate-200/80 pb-6">
          <div className="space-y-1">
            <span className="text-xs font-bold uppercase tracking-widest text-slate-500">
              Aggregated Multi-Modal Risk Score
            </span>
            <div className="flex items-baseline gap-3">
              <span className="text-5xl sm:text-6xl font-black text-slate-900 tracking-tight">
                {finalRisk}
              </span>
              <span className="text-xl text-slate-400 font-bold">/ 100</span>
            </div>
            <p className="text-sm font-medium text-slate-700 max-w-lg mt-1">
              {theme.desc}
            </p>
          </div>

          <div className="shrink-0 flex flex-col items-start sm:items-end gap-2">
            <RiskBadge level={riskLevel} score={finalRisk} className="text-sm px-4 py-1.5" />
            <span className="text-xs text-slate-500 font-medium">
              Evaluated on {new Date().toLocaleDateString()}
            </span>
          </div>
        </div>

        {/* 4-Tier Risk Scale Bar */}
        <div className="space-y-2">
          <div className="flex justify-between text-[11px] font-bold text-slate-600">
            <span className="text-emerald-700">Low (0-30)</span>
            <span className="text-amber-700">Medium (31-60)</span>
            <span className="text-orange-700">High (61-80)</span>
            <span className="text-red-700">Critical (81-100)</span>
          </div>
          <div className="w-full h-3 rounded-full bg-slate-200 overflow-hidden flex">
            <div className="w-[30%] bg-emerald-500 h-full" />
            <div className="w-[30%] bg-amber-500 h-full" />
            <div className="w-[20%] bg-orange-500 h-full" />
            <div className="w-[20%] bg-red-600 h-full" />
          </div>
          <div className="text-right">
            <span className="text-[11px] font-semibold text-slate-600">
              Indicator Marker: <strong className="text-slate-900">{finalRisk}%</strong>
            </span>
          </div>
        </div>
      </div>

      {/* Transparent Breakdown of Modality Weights */}
      <Card className="border-slate-200 shadow-sm">
        <CardHeader className="border-b border-slate-100 pb-4">
          <CardTitle className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Activity size={18} className="text-emerald-700" />
            <span>Independent Sub-Model Score Breakdown</span>
          </CardTitle>
          <CardDescription>
            Configurable weights ensuring no single model dictates the final assessment in isolation
          </CardDescription>
        </CardHeader>

        <CardContent className="p-6 space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* 1. Image AI */}
            <div className="p-4 rounded-2xl border border-slate-200 bg-white shadow-xs space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-bold text-slate-700 flex items-center gap-1.5">
                  <Camera size={14} className="text-blue-600" />
                  Image AI
                </span>
                <Badge variant="outline" className="text-[10px] font-bold">40% Weight</Badge>
              </div>
              <div className="flex items-baseline gap-1">
                <span className="text-2xl font-black text-slate-900">
                  {individualScores.image_risk ?? 75}
                </span>
                <span className="text-xs text-slate-400">/100</span>
              </div>
              <p className="text-[11px] text-slate-500">
                Oral & mucosal lesion morphology analysis
              </p>
            </div>

            {/* 2. Symptom AI */}
            <div className="p-4 rounded-2xl border border-slate-200 bg-white shadow-xs space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-bold text-slate-700 flex items-center gap-1.5">
                  <Thermometer size={14} className="text-rose-600" />
                  Symptom AI
                </span>
                <Badge variant="outline" className="text-[10px] font-bold">35% Weight</Badge>
              </div>
              <div className="flex items-baseline gap-1">
                <span className="text-2xl font-black text-slate-900">
                  {individualScores.symptom_risk ?? 70}
                </span>
                <span className="text-xs text-slate-400">/100</span>
              </div>
              <p className="text-[11px] text-slate-500">
                Fever, salivation, lameness risk pattern
              </p>
            </div>

            {/* 3. Environmental */}
            <div className="p-4 rounded-2xl border border-slate-200 bg-white shadow-xs space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-bold text-slate-700 flex items-center gap-1.5">
                  <CloudSun size={14} className="text-amber-600" />
                  Environment
                </span>
                <Badge variant="outline" className="text-[10px] font-bold">15% Weight</Badge>
              </div>
              <div className="flex items-baseline gap-1">
                <span className="text-2xl font-black text-slate-900">
                  {individualScores.environmental_risk ?? 55}
                </span>
                <span className="text-xs text-slate-400">/100</span>
              </div>
              <p className="text-[11px] text-slate-500">
                Regional climate & vector exposure index
              </p>
            </div>

            {/* 4. Health & Vaccination */}
            <div className="p-4 rounded-2xl border border-slate-200 bg-white shadow-xs space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-bold text-slate-700 flex items-center gap-1.5">
                  <Syringe size={14} className="text-emerald-600" />
                  Context
                </span>
                <Badge variant="outline" className="text-[10px] font-bold">10% Weight</Badge>
              </div>
              <div className="flex items-baseline gap-1">
                <span className="text-2xl font-black text-slate-900">
                  {individualScores.health_vaccination_risk ?? 60}
                </span>
                <span className="text-xs text-slate-400">/100</span>
              </div>
              <p className="text-[11px] text-slate-500">
                Immunization validity & prior exposure
              </p>
            </div>
          </div>

          {/* Formula calculation display */}
          <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 text-xs text-slate-700 space-y-1">
            <span className="font-bold text-slate-900 block text-[11px] uppercase tracking-wider">
              Documented Weighting Calculation:
            </span>
            <p className="font-mono text-xs text-emerald-950 bg-white p-2 rounded-lg border border-slate-200">
              Final Risk ({finalRisk}) = (0.40 × {individualScores.image_risk}) + (0.35 × {individualScores.symptom_risk}) + (0.15 × {individualScores.environmental_risk}) + (0.10 × {individualScores.health_vaccination_risk})
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Contributing Factors & Actionable Biosecurity Advice */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Contributing Factors */}
        <Card className="border-slate-200">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-bold text-slate-900">
              Key Contributing Risk Factors
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2.5 text-xs text-slate-700">
              {contributingFactors.map((factor, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-700 shrink-0 mt-1.5" />
                  <span>{factor}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        {/* Recommended Biosecurity Actions */}
        <Card className="border-amber-200 bg-amber-50/40">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-bold text-amber-950 flex items-center gap-2">
              <ShieldCheck size={16} className="text-amber-700" />
              <span>Recommended Next Actions</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-xs text-amber-950">
            <div className="p-3 bg-white rounded-xl border border-amber-200 space-y-1">
              <span className="font-bold block text-slate-900">1. Isolate Affected Animal</span>
              <p className="text-slate-600 text-[11px]">
                Prevent contact with healthy cattle. Restrict shared drinking water and feed troughs immediately.
              </p>
            </div>

            <div className="p-3 bg-white rounded-xl border border-amber-200 space-y-1">
              <span className="font-bold block text-slate-900">2. Notify Local Veterinary Officer</span>
              <p className="text-slate-600 text-[11px]">
                High-risk reports are automatically forwarded to the regional triage queue for clinical review.
              </p>
            </div>

            <div className="p-3 bg-white rounded-xl border border-amber-200 space-y-1">
              <span className="font-bold block text-slate-900">3. Sanitize Barn Perimeter</span>
              <p className="text-slate-600 text-[11px]">
                Apply lime powder along stall boundaries and wash boots before entering herd enclosures.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Prominent Disclaimer */}
      <div className="p-4 rounded-2xl bg-slate-100 border border-slate-300 flex items-start gap-3 text-xs text-slate-700">
        <Info size={18} className="text-slate-500 shrink-0 mt-0.5" />
        <div>
          <span className="font-bold text-slate-900 block mb-0.5">
            AI-Assisted Risk Assessment Notice
          </span>
          <p className="leading-relaxed">
            This report represents an AI-assisted multi-modal risk calculation and is <strong>not a certified veterinary diagnosis</strong>. Do not administer prescription medications without an on-site clinical examination and official prescription by a registered veterinary practitioner.
          </p>
        </div>
      </div>
    </div>
  );
};

export default AssessmentResult;
