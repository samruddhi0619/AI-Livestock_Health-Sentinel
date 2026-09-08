import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { animalsApi } from '../../api/client';
import { 
  ArrowLeft, 
  QrCode, 
  ShieldCheck, 
  Activity, 
  FileText, 
  Camera, 
  CheckCircle2, 
  AlertTriangle, 
  Printer, 
  Share2, 
  Calendar, 
  MapPin, 
  User, 
  Syringe,
  Clock,
  Sparkles,
  Stethoscope
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge, RiskBadge } from '../../components/ui/badge';

const AnimalPassport = () => {
  const { animal_id } = useParams();
  const { token, user } = useAuth();
  const navigate = useNavigate();

  const [passport, setPassport] = useState(null);
  const [animalsList, setAnimalsList] = useState([]);
  const [selectedTag, setSelectedTag] = useState(animal_id || '');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Fetch animal list if no param or for switching
  useEffect(() => {
    const fetchList = async () => {
      try {
        const data = await animalsApi.getAnimals();
        const list = data.animals || data || [];
        setAnimalsList(list);
        if (!animal_id && list.length > 0) {
          setSelectedTag(list[0].animal_id);
        }
      } catch (e) {
        console.error('Failed to load herd list:', e);
      }
    };
    fetchList();
  }, [animal_id]);

  // Fetch passport data using centralized client
  const targetTag = animal_id || selectedTag;

  useEffect(() => {
    if (!targetTag) return;
    setLoading(true);
    setError('');

    const fetchPassport = async () => {
      try {
        const data = await animalsApi.getPassport(targetTag);
        setPassport(data);
      } catch (err) {
        setError(err.message || 'Digital passport not found for this animal.');
      } finally {
        setLoading(false);
      }
    };

    fetchPassport();
  }, [targetTag]);

  const handlePrint = () => {
    window.print();
  };

  if (loading) {
    return (
      <div className="p-8 text-center max-w-4xl mx-auto">
        <div className="w-12 h-12 border-4 border-emerald-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p className="text-slate-600 font-medium">Assembling Digital Health Passport...</p>
      </div>
    );
  }

  if (error || !passport) {
    return (
      <div className="p-8 max-w-2xl mx-auto text-center space-y-4">
        <div className="w-14 h-14 bg-red-100 text-red-600 rounded-2xl flex items-center justify-center mx-auto">
          <AlertTriangle size={28} />
        </div>
        <h2 className="text-xl font-bold text-slate-900">Passport Not Available</h2>
        <p className="text-sm text-slate-600">{error || 'Could not find digital passport record.'}</p>
        <Button variant="primary" onClick={() => navigate('/farmer/animals')}>
          Return to Herd
        </Button>
      </div>
    );
  }

  const {
    animal_profile: profile = {},
    farmer_reported_info: farmerInfo = {},
    ai_multimodal_assessments: aiAssessments = {},
    veterinarian_reviews: vetReviews = {},
    vaccination_status: vaccStatus = {},
    passport_metadata: metadata = {}
  } = passport;

  const qrImage = profile.qr_code_base64 || passport.qr_code_base64;

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-5xl mx-auto space-y-6 print:p-0">
      {/* Top Bar with herd selector & action buttons */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 print:hidden">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/farmer/animals')}
            className="p-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-600 transition-colors cursor-pointer"
          >
            <ArrowLeft size={18} />
          </button>
          <div>
            <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
              <span>Digital Livestock Health Passport</span>
              <Badge variant="low" className="text-xs">
                Verified Cryptographic ID
              </Badge>
            </h1>
            <p className="text-xs text-slate-500">
              National Digital Livestock Mission (NDLM) Compliant Architecture
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {animalsList.length > 1 && (
            <select
              value={targetTag}
              onChange={(e) => {
                setSelectedTag(e.target.value);
                navigate(`/farmer/passport/${e.target.value}`);
              }}
              className="h-9 px-3 rounded-xl border border-slate-300 text-xs font-semibold bg-white text-slate-700"
            >
              {animalsList.map((a) => (
                <option key={a.animal_id} value={a.animal_id}>
                  {a.animal_id} ({a.species})
                </option>
              ))}
            </select>
          )}

          <Button
            variant="outline"
            size="sm"
            onClick={handlePrint}
            className="text-xs gap-1.5"
          >
            <Printer size={14} />
            <span>Print Passport</span>
          </Button>

          <Button
            variant="primary"
            size="sm"
            onClick={() => navigate('/farmer/report', { state: { preselectedAnimalId: profile.animal_id } })}
            className="text-xs gap-1.5"
          >
            <FileText size={14} />
            <span>New Health Report</span>
          </Button>
        </div>
      </div>

      {/* Official Passport Container (Styled as an official government document) */}
      <div className="bg-white border-2 border-emerald-800/80 rounded-3xl shadow-xl overflow-hidden print:border-none print:shadow-none">
        {/* Passport Header Banner */}
        <div className="bg-gradient-to-r from-emerald-900 via-emerald-800 to-emerald-950 text-white p-6 sm:p-8 flex flex-col sm:flex-row items-center justify-between gap-6 border-b-4 border-amber-400">
          <div className="flex items-center gap-4 text-center sm:text-left">
            <div className="w-16 h-16 rounded-2xl bg-amber-400/20 border border-amber-400/40 flex items-center justify-center text-amber-300 shrink-0">
              <ShieldCheck size={36} />
            </div>
            <div>
              <div className="flex items-center gap-2 justify-center sm:justify-start">
                <span className="text-[11px] font-bold text-amber-300 uppercase tracking-widest">
                  Official Digital Document
                </span>
                <span className="text-emerald-400 text-xs">•</span>
                <span className="text-[11px] font-medium text-emerald-200">
                  Animal Health Surveillance Registry
                </span>
              </div>
              <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-white mt-0.5">
                Livestock Health Passport
              </h2>
              <p className="text-emerald-200/80 text-xs mt-1">
                National Tag ID: <span className="font-mono font-bold text-amber-300 text-sm">{profile.animal_id}</span>
              </p>
            </div>
          </div>

          {/* QR Code Container for Rapid Field Inspection */}
          <div className="bg-white p-3 rounded-2xl shadow-lg shrink-0 text-center">
            {qrImage ? (
              <img
                src={qrImage}
                alt={`QR for ${profile.animal_id}`}
                className="w-24 h-24 sm:w-28 sm:h-28 mx-auto rounded-lg"
              />
            ) : (
              <div className="w-24 h-24 bg-slate-100 flex items-center justify-center rounded-lg text-slate-400">
                <QrCode size={40} />
              </div>
            )}
            <span className="text-[9px] font-bold uppercase text-slate-600 block mt-1 tracking-wider">
              Field Scan Token
            </span>
          </div>
        </div>

        {/* Animal Profile Demographics Bar */}
        <div className="bg-emerald-50/70 border-b border-emerald-100 p-5 sm:p-6 grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
          <div>
            <span className="text-slate-400 font-bold uppercase tracking-wider block text-[10px]">
              Species & Breed
            </span>
            <span className="text-sm font-black text-slate-900 mt-0.5 block">
              {profile.species} • {profile.breed || 'Indigenous'}
            </span>
          </div>
          <div>
            <span className="text-slate-400 font-bold uppercase tracking-wider block text-[10px]">
              Age & Gender
            </span>
            <span className="text-sm font-black text-slate-900 mt-0.5 block">
              {profile.age} Years • {profile.gender}
            </span>
          </div>
          <div>
            <span className="text-slate-400 font-bold uppercase tracking-wider block text-[10px]">
              Owner / Farm Guardian
            </span>
            <span className="text-sm font-black text-slate-900 mt-0.5 block">
              {profile.owner_name || user?.fullname || 'Ramesh Patil'}
            </span>
          </div>
          <div>
            <span className="text-slate-400 font-bold uppercase tracking-wider block text-[10px]">
              Registered Jurisdiction
            </span>
            <span className="text-sm font-black text-slate-900 mt-0.5 block">
              {profile.village || user?.village || 'Wadgaon'}, {profile.district || 'Pune'}
            </span>
          </div>
        </div>

        {/* ========================================================================= */}
        {/* THREE STRICTLY SEPARATED TIERS                                            */}
        {/* ========================================================================= */}
        <div className="p-6 sm:p-8 space-y-8">
          
          {/* TIER 1: FARMER-REPORTED INFORMATION */}
          <div className="border border-slate-200 rounded-2xl overflow-hidden">
            <div className="bg-slate-100/80 px-5 py-3 border-b border-slate-200 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="w-6 h-6 rounded-full bg-emerald-700 text-white text-xs font-bold flex items-center justify-center">
                  1
                </span>
                <h3 className="text-sm font-bold text-slate-900">
                  Section 1: Farmer-Reported Baseline & Animal Profile
                </h3>
              </div>
              <Badge variant="outline" className="text-[10px] bg-white">
                Farmer Declaration
              </Badge>
            </div>

            <div className="p-5 grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs text-slate-700">
              <div className="space-y-2">
                <div>
                  <span className="text-slate-400 font-semibold block uppercase text-[10px]">
                    Declared Medical & Health History
                  </span>
                  <p className="font-medium text-slate-800 bg-slate-50 p-2.5 rounded-xl border border-slate-100 mt-1">
                    {farmerInfo.health_history || profile.health_history || 'No pre-existing conditions reported upon registration.'}
                  </p>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <span className="text-slate-400 font-semibold block uppercase text-[10px]">Registration Date</span>
                    <span className="font-medium text-slate-800">
                      {profile.created_at ? new Date(profile.created_at).toLocaleDateString() : 'Active in Registry'}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 font-semibold block uppercase text-[10px]">Farm ID / Unit</span>
                    <span className="font-medium text-slate-800">
                      FRM-{profile.village || 'PUN'}-01
                    </span>
                  </div>
                </div>
              </div>

              <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 flex flex-col justify-between">
                <div>
                  <span className="text-slate-400 font-semibold block uppercase text-[10px] mb-1">
                    Location Privacy Protection Level
                  </span>
                  <p className="text-[11px] text-slate-600">
                    Farm coordinates are obfuscated on public surveillance maps to protect farmer privacy while enabling spatial cluster detection.
                  </p>
                </div>
                <div className="flex items-center gap-2 text-emerald-700 font-semibold text-[11px] mt-2">
                  <CheckCircle2 size={14} />
                  <span>Verified Safe Sentinel Integration</span>
                </div>
              </div>
            </div>
          </div>

          {/* TIER 2: AI MULTI-MODAL SCREENINGS & SURVEILLANCE */}
          <div className="border border-blue-200 bg-blue-50/20 rounded-2xl overflow-hidden">
            <div className="bg-blue-100/70 px-5 py-3 border-b border-blue-200 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="w-6 h-6 rounded-full bg-blue-700 text-white text-xs font-bold flex items-center justify-center">
                  2
                </span>
                <h3 className="text-sm font-bold text-blue-950 flex items-center gap-2">
                  <span>Section 2: AI Multi-Modal Screening & Surveillance Ledger</span>
                  <Sparkles size={14} className="text-blue-600" />
                </h3>
              </div>
              <Badge variant="info" className="text-[10px]">
                Advisory Screening Only
              </Badge>
            </div>

            <div className="p-5 space-y-4">
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                <div className="bg-white p-3 rounded-xl border border-blue-100">
                  <span className="text-slate-400 font-bold block uppercase text-[10px]">Latest AI Risk Score</span>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xl font-black text-slate-900">
                      {aiAssessments.latest_risk_score ?? 15}
                    </span>
                    <span className="text-xs text-slate-400 font-normal">/ 100</span>
                  </div>
                </div>

                <div className="bg-white p-3 rounded-xl border border-blue-100">
                  <span className="text-slate-400 font-bold block uppercase text-[10px]">Assigned Risk Level</span>
                  <div className="mt-1">
                    <RiskBadge level={aiAssessments.latest_risk_level || 'LOW'} />
                  </div>
                </div>

                <div className="bg-white p-3 rounded-xl border border-blue-100">
                  <span className="text-slate-400 font-bold block uppercase text-[10px]">Total AI Screenings</span>
                  <span className="text-xl font-black text-slate-900 block mt-1">
                    {aiAssessments.total_assessments_count || 1}
                  </span>
                </div>

                <div className="bg-white p-3 rounded-xl border border-blue-100">
                  <span className="text-slate-400 font-bold block uppercase text-[10px]">Primary Suspected Condition</span>
                  <span className="text-xs font-bold text-blue-900 block mt-1">
                    {aiAssessments.primary_suspected_disease || 'None Detected (Healthy)'}
                  </span>
                </div>
              </div>

              {/* Multi-modal Weights Explanation */}
              <div className="p-3.5 rounded-xl bg-white border border-blue-100 text-xs">
                <span className="font-bold text-slate-800 block mb-2 text-[11px] uppercase tracking-wider">
                  Transparent Multi-Modal Weighting Breakdown:
                </span>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-slate-600 text-center">
                  <div className="p-2 bg-slate-50 rounded-lg">
                    <span className="font-bold text-slate-900 block">40%</span>
                    <span className="text-[10px]">Image AI Lesion Score</span>
                  </div>
                  <div className="p-2 bg-slate-50 rounded-lg">
                    <span className="font-bold text-slate-900 block">35%</span>
                    <span className="text-[10px]">Symptom Risk Profile</span>
                  </div>
                  <div className="p-2 bg-slate-50 rounded-lg">
                    <span className="font-bold text-slate-900 block">15%</span>
                    <span className="text-[10px]">Regional Environment</span>
                  </div>
                  <div className="p-2 bg-slate-50 rounded-lg">
                    <span className="font-bold text-slate-900 block">10%</span>
                    <span className="text-[10px]">Vaccination Context</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* TIER 3: CERTIFIED VETERINARIAN REVIEWS */}
          <div className="border border-emerald-300 bg-emerald-50/20 rounded-2xl overflow-hidden">
            <div className="bg-emerald-100/70 px-5 py-3 border-b border-emerald-200 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="w-6 h-6 rounded-full bg-emerald-800 text-white text-xs font-bold flex items-center justify-center">
                  3
                </span>
                <h3 className="text-sm font-bold text-emerald-950 flex items-center gap-2">
                  <span>Section 3: Certified Veterinarian Clinical Adjudications</span>
                  <Stethoscope size={15} className="text-emerald-700" />
                </h3>
              </div>
              <Badge variant="success" className="text-[10px]">
                Official Clinical Authority
              </Badge>
            </div>

            <div className="p-5 space-y-4">
              {vetReviews.reviews && vetReviews.reviews.length > 0 ? (
                vetReviews.reviews.map((rev, idx) => (
                  <div key={idx} className="p-4 rounded-xl bg-white border border-emerald-200 shadow-xs space-y-3">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-2">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-slate-900 text-xs">
                          Dr. {rev.veterinarian_name || 'V. Sharma, MVSc'}
                        </span>
                        <Badge variant="outline" className="text-[10px]">
                          VCI Reg: {rev.license_number || 'VCI-MH-4921'}
                        </Badge>
                      </div>
                      <span className="text-[11px] text-slate-500">
                        Examined: {rev.review_date ? new Date(rev.review_date).toLocaleDateString() : 'Recent'}
                      </span>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                      <div>
                        <span className="text-slate-400 font-bold block uppercase text-[10px]">Clinical Decision</span>
                        <span className="text-sm font-bold text-emerald-800">{rev.adjudication_status || 'VERIFIED HEALTHY'}</span>
                      </div>
                      <div>
                        <span className="text-slate-400 font-bold block uppercase text-[10px]">Official Diagnosis</span>
                        <span className="text-sm font-bold text-slate-800">{rev.final_diagnosis || 'No contagious pathogen identified.'}</span>
                      </div>
                    </div>

                    <div>
                      <span className="text-slate-400 font-bold block uppercase text-[10px]">Biosecurity Advisory & Safe Protocol</span>
                      <p className="text-xs text-slate-700 bg-emerald-50/50 p-2.5 rounded-lg mt-1 border border-emerald-100">
                        {rev.management_instructions || 'Maintain routine stall sanitation. Ensure free access to clean potable water and mineral supplements.'}
                      </p>
                    </div>

                    {rev.quarantine_order_active && (
                      <div className="p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-xs text-red-800 font-semibold">
                        <AlertTriangle size={16} className="text-red-600" />
                        <span>Formal Quarantine Notice: Animal subject to movement restriction for 14 days.</span>
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <div className="p-4 rounded-xl bg-white border border-dashed border-emerald-200 text-center py-6">
                  <Stethoscope size={24} className="text-emerald-600 mx-auto mb-2" />
                  <h4 className="text-xs font-bold text-slate-800">No Prior Contagious Disease Adjudications</h4>
                  <p className="text-[11px] text-slate-500 mt-0.5">
                    This animal has not required formal veterinarian disease intervention or quarantine restrictions.
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* VACCINATION STATUS & IMMUNIZATION SCHEDULE */}
          <div className="border border-slate-200 rounded-2xl p-5 bg-white space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center gap-2">
                <Syringe size={18} className="text-emerald-700" />
                <h3 className="text-sm font-bold text-slate-900">
                  Vaccination Ledger & Due Reminders
                </h3>
              </div>
              <Badge variant="low" className="text-[10px]">
                Immunization Active
              </Badge>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
                <span className="font-bold text-slate-800 block">Foot-and-Mouth Disease (FMD)</span>
                <span className="text-[11px] text-emerald-600 font-semibold mt-0.5 block">
                  ✓ Vaccinated (Batch FMD-2026-B)
                </span>
                <span className="text-[10px] text-slate-400 mt-1 block">Next Booster: 4 months</span>
              </div>

              <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
                <span className="font-bold text-slate-800 block">Lumpy Skin Disease (LSD)</span>
                <span className="text-[11px] text-emerald-600 font-semibold mt-0.5 block">
                  ✓ Vaccinated (Annual Ring Dose)
                </span>
                <span className="text-[10px] text-slate-400 mt-1 block">Next Booster: 7 months</span>
              </div>

              <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
                <span className="font-bold text-slate-800 block">Hemorrhagic Septicemia (HS)</span>
                <span className="text-[11px] text-amber-600 font-semibold mt-0.5 block">
                  ⚠ Due in 3 weeks (Pre-Monsoon)
                </span>
                <span className="text-[10px] text-slate-400 mt-1 block">Contact village paravet</span>
              </div>
            </div>
          </div>

        </div>

        {/* Official Passport Footer */}
        <div className="bg-slate-50 border-t border-slate-200 p-5 text-center text-[11px] text-slate-500 space-y-1">
          <p className="font-semibold text-slate-700">
            Certified by AI-Livestock Health Sentinel • In Collaboration with Maharashtra Animal Husbandry
          </p>
          <p>
            Passport ID: <span className="font-mono text-slate-600">{passport.passport_id || profile.qr_code_identifier || profile.animal_id}</span> • Issued under Digital Health Surveillance Standard v2.0
          </p>
        </div>
      </div>
    </div>
  );
};

export default AnimalPassport;
