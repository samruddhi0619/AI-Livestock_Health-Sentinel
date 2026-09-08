import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { casesApi } from '../../api/client';
import { 
  Stethoscope, 
  ArrowLeft, 
  ShieldCheck, 
  AlertTriangle, 
  CheckCircle2, 
  Camera, 
  Activity, 
  FileText, 
  Calendar, 
  MapPin, 
  Phone,
  RefreshCw,
  QrCode
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge, RiskBadge } from '../../components/ui/badge';
import { Input, Select, Textarea } from '../../components/ui/input';

const ReviewAssessments = () => {
  const { case_id } = useParams();
  const location = useLocation();
  const navigate = useNavigate();

  const [casesList, setCasesList] = useState([]);
  const [selectedCaseId, setSelectedCaseId] = useState(case_id || '');
  const [currentCase, setCurrentCase] = useState(location.state?.caseData || null);
  const [loading, setLoading] = useState(false);

  // Verification Form State
  const [adjudicationStatus, setAdjudicationStatus] = useState('VERIFIED');
  const [diagnosis, setDiagnosis] = useState('');
  const [managementNotes, setManagementNotes] = useState('');
  const [quarantineOrder, setQuarantineOrder] = useState(false);
  const [followUpDate, setFollowUpDate] = useState('');

  const [submitting, setSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  // Fetch list of cases using casesApi
  useEffect(() => {
    const fetchCases = async () => {
      try {
        const list = await casesApi.getCases();
        setCasesList(list || []);
        if (!selectedCaseId && list.length > 0) {
          setSelectedCaseId(list[0]._id || list[0].case_id);
          setCurrentCase(list[0]);
        }
      } catch (err) {
        console.error('Failed to load cases list:', err);
      }
    };
    fetchCases();
  }, []);

  // Load specific case details
  useEffect(() => {
    if (!selectedCaseId) return;
    const target = casesList.find(c => (c._id || c.case_id) === selectedCaseId);
    if (target) {
      setCurrentCase(target);
      setDiagnosis(target.disease || 'Foot-and-Mouth Disease (Suspected)');
    }
  }, [selectedCaseId, casesList]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedCaseId) return;

    // Client-side Validation
    if (!diagnosis.trim()) {
      setErrorMsg('Please enter an official clinical diagnosis.');
      return;
    }

    setSubmitting(true);
    setErrorMsg('');
    setSuccessMsg('');

    try {
      const payload = {
        status: adjudicationStatus,
        diagnosis: diagnosis.trim(),
        treatment: managementNotes.trim() || 'Sanitize affected pen. Isolate animal from herd for 14 days. Provide soft mash feed and fresh water.',
        follow_up: followUpDate.trim() || 'In 7 days'
      };

      await casesApi.verifyCase(selectedCaseId, payload);

      setSuccessMsg('Clinical adjudication certified and recorded in digital passport.');
      setTimeout(() => {
        navigate('/veterinarian/cases');
      }, 1500);

    } catch (err) {
      setErrorMsg(err.message || 'Error recording clinical verification.');
    } finally {
      setSubmitting(false);
    }
  };

  if (!currentCase && !loading) {
    return (
      <div className="p-8 max-w-2xl mx-auto text-center space-y-4">
        <Stethoscope size={32} className="text-slate-400 mx-auto" />
        <h2 className="text-xl font-bold text-slate-900">No Case Selected</h2>
        <p className="text-xs text-slate-500">Select a case from the high-risk triage queue to begin review.</p>
        <Button variant="primary" size="sm" onClick={() => navigate('/veterinarian/cases')}>
          Return to High-Risk Cases
        </Button>
      </div>
    );
  }

  const animalId = currentCase?.animal_id || 'MH-PUN-CTL-0124';
  const riskScore = currentCase?.risk_score ?? 78;

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/veterinarian/cases')}
            className="p-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-600 transition-colors cursor-pointer"
          >
            <ArrowLeft size={18} />
          </button>
          <div>
            <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
              <span>Clinical Adjudication Console</span>
              <RiskBadge level={currentCase?.risk_level || 'HIGH'} score={riskScore} />
            </h1>
            <p className="text-xs text-slate-500 mt-0.5">
              Review multi-modal evidence, determine infectious status, and certify management protocols
            </p>
          </div>
        </div>

        {casesList.length > 1 && (
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-500 font-semibold">Switch Case:</span>
            <Select
              value={selectedCaseId}
              onChange={(e) => setSelectedCaseId(e.target.value)}
              className="text-xs h-9 bg-white"
            >
              {casesList.map((c) => (
                <option key={c._id || c.case_id} value={c._id || c.case_id}>
                  {c.animal_id} — {c.disease || 'Suspected Case'}
                </option>
              ))}
            </Select>
          </div>
        )}
      </div>

      {successMsg && (
        <div className="p-4 rounded-2xl bg-green-50 border border-green-200 text-green-800 text-sm flex items-center gap-2.5">
          <CheckCircle2 size={20} className="text-green-600 shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {errorMsg && (
        <div className="p-4 rounded-2xl bg-red-50 border border-red-200 text-red-700 text-sm flex items-center gap-2.5">
          <AlertTriangle size={20} className="text-red-600 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Two Column Layout: Evidence & Adjudication */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left 5 Cols: AI Evidence & Animal Snapshot */}
        <div className="lg:col-span-5 space-y-5">
          <Card className="border-slate-200 shadow-sm">
            <CardHeader className="pb-3 border-b border-slate-100">
              <CardTitle className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <FileText size={16} className="text-emerald-700" />
                <span>Animal & Field Report Context</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="p-4 space-y-3 text-xs text-slate-700">
              <div className="grid grid-cols-2 gap-2 bg-slate-50 p-3 rounded-xl">
                <div>
                  <span className="text-slate-400 font-bold uppercase text-[10px] block">Animal Tag</span>
                  <span className="text-sm font-black text-slate-900">{animalId}</span>
                </div>
                <div>
                  <span className="text-slate-400 font-bold uppercase text-[10px] block">Suspected Condition</span>
                  <span className="text-sm font-bold text-slate-800">{currentCase?.disease || 'Vesicular Disease'}</span>
                </div>
              </div>

              <div className="space-y-1">
                <div className="flex justify-between text-[11px]">
                  <span className="text-slate-500">Farmer:</span>
                  <span className="font-semibold text-slate-800">{currentCase?.farmer_name || 'Ramesh Patil'}</span>
                </div>
                <div className="flex justify-between text-[11px]">
                  <span className="text-slate-500">Authorized Farm Location:</span>
                  <span className="font-semibold text-slate-800">{currentCase?.village || 'Wadgaon'}, {currentCase?.taluka || 'Haveli'}</span>
                </div>
                <div className="flex justify-between text-[11px]">
                  <span className="text-slate-500">Reported Timestamp:</span>
                  <span className="font-semibold text-slate-800">{currentCase?.date ? new Date(currentCase.date).toLocaleString() : 'Recent'}</span>
                </div>
              </div>

              {/* Reported Symptoms */}
              <div className="pt-2 border-t border-slate-100">
                <span className="text-slate-400 font-bold uppercase text-[10px] block mb-1">
                  Reported Clinical Signs
                </span>
                <p className="bg-slate-50 p-2.5 rounded-xl border border-slate-100 text-[11px] text-slate-700">
                  {Array.isArray(currentCase?.symptoms) ? currentCase.symptoms.join(', ') : (currentCase?.symptoms || 'Fever (39.6°C), heavy mouth salivation, off feed for 2 days.')}
                </p>
              </div>

              {/* Lesion Photo Preview */}
              <div className="pt-2">
                <span className="text-slate-400 font-bold uppercase text-[10px] block mb-1 flex items-center gap-1">
                  <Camera size={12} className="text-blue-600" />
                  Submitted Lesion Photo
                </span>
                <div className="rounded-xl overflow-hidden border border-slate-200 bg-slate-900 text-center p-2">
                  <img
                    src="https://images.unsplash.com/photo-1570042225831-d98fa7577f1e?w=500&auto=format&fit=crop&q=60"
                    alt="Clinical Lesion"
                    className="h-40 w-full object-cover rounded-lg mx-auto"
                  />
                  <span className="text-[10px] text-slate-400 block mt-1">
                    Oral mucosal ulceration • AI Vision Confidence 88.5%
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right 7 Cols: Official Clinical Adjudication Form */}
        <div className="lg:col-span-7 space-y-5">
          <Card className="border-slate-200 shadow-md">
            <form onSubmit={handleSubmit}>
              <CardHeader className="border-b border-slate-100 pb-4">
                <CardTitle className="text-base font-bold text-slate-900 flex items-center gap-2">
                  <Stethoscope size={18} className="text-emerald-700" />
                  <span>Veterinary Clinical Adjudication & Biosecurity Order</span>
                </CardTitle>
                <CardDescription>
                  This official clinical determination certifies the status in the digital animal health passport
                </CardDescription>
              </CardHeader>

              <CardContent className="p-6 space-y-5">
                {/* 1. Adjudication Status */}
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                    1. Clinical Determination Decision *
                  </label>
                  <div className="grid grid-cols-3 gap-2.5">
                    <button
                      type="button"
                      onClick={() => setAdjudicationStatus('VERIFIED')}
                      className={`p-3 rounded-xl border text-center text-xs font-bold transition-all cursor-pointer ${
                        adjudicationStatus === 'VERIFIED'
                          ? 'border-red-600 bg-red-50 text-red-900 ring-2 ring-red-600/20 shadow-xs'
                          : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50'
                      }`}
                    >
                      <span className="block text-sm mb-0.5">🔴</span>
                      <span>Confirmed Case</span>
                    </button>

                    <button
                      type="button"
                      onClick={() => setAdjudicationStatus('RULED_OUT')}
                      className={`p-3 rounded-xl border text-center text-xs font-bold transition-all cursor-pointer ${
                        adjudicationStatus === 'RULED_OUT'
                          ? 'border-green-600 bg-green-50 text-green-900 ring-2 ring-green-600/20 shadow-xs'
                          : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50'
                      }`}
                    >
                      <span className="block text-sm mb-0.5">🟢</span>
                      <span>Ruled Out (Benign)</span>
                    </button>

                    <button
                      type="button"
                      onClick={() => setAdjudicationStatus('INCONCLUSIVE')}
                      className={`p-3 rounded-xl border text-center text-xs font-bold transition-all cursor-pointer ${
                        adjudicationStatus === 'INCONCLUSIVE'
                          ? 'border-amber-600 bg-amber-50 text-amber-900 ring-2 ring-amber-600/20 shadow-xs'
                          : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50'
                      }`}
                    >
                      <span className="block text-sm mb-0.5">🟡</span>
                      <span>Inconclusive</span>
                    </button>
                  </div>
                </div>

                {/* 2. Official Diagnosis */}
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Official Certified Diagnosis *
                  </label>
                  <Input
                    value={diagnosis}
                    onChange={(e) => setDiagnosis(e.target.value)}
                    placeholder="e.g. Foot-and-Mouth Disease (Aphthovirus Serotype O)"
                    required
                  />
                </div>

                {/* 3. Management & Biosecurity Advisory (Strictly non-prescriptive) */}
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Biosecurity Management Instructions & Advisory Notes *
                  </label>
                  <Textarea
                    value={managementNotes}
                    onChange={(e) => setManagementNotes(e.target.value)}
                    placeholder="Specify quarantine parameters, sanitization protocols (e.g. 4% sodium carbonate wash), and supportive hydration instructions..."
                    rows={4}
                    required
                  />
                  <p className="text-[11px] text-slate-500 mt-1">
                    Strict biosecurity guideline: Provide farm management guidance without dispensing unverified pharmaceutical prescriptions remotely.
                  </p>
                </div>

                {/* 4. Quarantine Order Toggle */}
                <div className="p-3.5 rounded-xl bg-red-50/60 border border-red-200 flex items-start gap-3">
                  <input
                    type="checkbox"
                    id="quarantineToggle"
                    checked={quarantineOrder}
                    onChange={(e) => setQuarantineOrder(e.target.checked)}
                    className="mt-1 h-4 w-4 rounded text-red-600 focus:ring-red-500 border-slate-300"
                  />
                  <label htmlFor="quarantineToggle" className="text-xs text-red-950 cursor-pointer">
                    <span className="font-bold block">
                      Issue Formal 14-Day Movement Restriction / Quarantine Order
                    </span>
                    <span className="text-red-800/90 leading-relaxed block text-[11px]">
                      Restricts animal transport and prevents participation in local livestock markets to prevent regional spread.
                    </span>
                  </label>
                </div>

                {/* 5. Follow Up Date */}
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Recommended Follow-up Re-examination
                  </label>
                  <Input
                    type="text"
                    value={followUpDate}
                    onChange={(e) => setFollowUpDate(e.target.value)}
                    placeholder="e.g. In 5 days (2026-09-12) or Immediate if blisters ulcerate further"
                  />
                </div>
              </CardContent>

              <CardFooter className="border-t border-slate-100 p-6 flex items-center justify-between">
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => navigate('/veterinarian/cases')}
                >
                  Cancel
                </Button>

                <Button
                  type="submit"
                  variant="primary"
                  size="lg"
                  disabled={submitting}
                  className="shadow-sm"
                >
                  <ShieldCheck size={16} />
                  <span>{submitting ? 'Certifying Record...' : 'Certify Clinical Adjudication'}</span>
                </Button>
              </CardFooter>
            </form>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default ReviewAssessments;
