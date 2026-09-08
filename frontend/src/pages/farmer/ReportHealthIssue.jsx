import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { animalsApi, reportsApi } from '../../api/client';
import { 
  FileText, 
  ArrowLeft, 
  Camera, 
  Upload, 
  ShieldCheck, 
  AlertTriangle, 
  CheckCircle2, 
  MapPin, 
  Thermometer, 
  Milk, 
  Activity,
  X
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input, Select, Textarea } from '../../components/ui/input';
import { Badge } from '../../components/ui/badge';

const COMMON_SYMPTOMS = [
  { id: 'fever', label: 'High Fever / Heat', icon: '🌡️' },
  { id: 'mouth_blisters', label: 'Mouth / Tongue Blisters', icon: '👄' },
  { id: 'salivation', label: 'Excessive Salivation / Drooling', icon: '💧' },
  { id: 'lameness', label: 'Lameness / Hoof Lesions', icon: '🦶' },
  { id: 'skin_nodules', label: 'Skin Lumps / Nodules', icon: '🔴' },
  { id: 'loss_of_appetite', label: 'Appetite Loss / Off Feed', icon: '🌾' },
  { id: 'milk_drop', label: 'Sudden Milk Drop', icon: '🥛' },
  { id: 'nasal_discharge', label: 'Nasal / Eye Discharge', icon: '👃' },
  { id: 'breathing_difficulty', label: 'Rapid / Labored Breathing', icon: '🫁' },
  { id: 'weakness', label: 'Lethargy / Dullness', icon: '💤' }
];

const ReportHealthIssue = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const preselectedTag = location.state?.preselectedAnimalId || '';

  const [animals, setAnimals] = useState([]);
  const [selectedAnimalId, setSelectedAnimalId] = useState(preselectedTag);
  const [selectedSymptoms, setSelectedSymptoms] = useState([]);
  const [temp, setTemp] = useState('39.0');
  const [appetite, setAppetite] = useState('Reduced');
  const [milkDropPercent, setMilkDropPercent] = useState('30');
  const [notes, setNotes] = useState('');
  const [shareLocation, setShareLocation] = useState(true);

  // Image upload
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(location.state?.imagePreview || null);

  const [loading, setLoading] = useState(false);
  const [fetchingHerd, setFetchingHerd] = useState(true);
  const [error, setError] = useState('');

  // Fetch herd using centralized API client
  useEffect(() => {
    const fetchHerd = async () => {
      setFetchingHerd(true);
      try {
        const data = await animalsApi.getAnimals();
        const list = data.animals || data || [];
        setAnimals(list);
        if (!selectedAnimalId && list.length > 0) {
          setSelectedAnimalId(list[0].animal_id);
        }
      } catch (err) {
        console.error('Failed to fetch animals for report form:', err);
      } finally {
        setFetchingHerd(false);
      }
    };
    fetchHerd();
  }, []);

  const toggleSymptom = (label) => {
    if (selectedSymptoms.includes(label)) {
      setSelectedSymptoms(selectedSymptoms.filter(s => s !== label));
    } else {
      setSelectedSymptoms([...selectedSymptoms, label]);
    }
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (!file.type.startsWith('image/')) {
        setError('Please select a valid image file (JPG, PNG, WebP).');
        return;
      }
      if (file.size > 10 * 1024 * 1024) {
        setError('Image file is too large. Max allowed size is 10MB.');
        return;
      }
      setError('');
      setImageFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const clearImage = () => {
    setImageFile(null);
    setImagePreview(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Client-side Validation
    if (!selectedAnimalId) {
      setError('Please select or specify an animal tag ID.');
      return;
    }
    if (selectedSymptoms.length === 0 && !notes.trim()) {
      setError('Please select at least one observed symptom or enter observations in the field notes.');
      return;
    }
    const tempNum = parseFloat(temp);
    if (isNaN(tempNum) || tempNum < 34.0 || tempNum > 44.0) {
      setError('Body temperature must be a valid value between 34.0°C and 44.0°C.');
      return;
    }

    setLoading(true);

    try {
      // Find selected animal details
      const currentAnimal = animals.find(a => a.animal_id === selectedAnimalId) || {};

      const payload = {
        animal_id: selectedAnimalId,
        symptoms: selectedSymptoms,
        temperature: tempNum,
        appetite_level: appetite,
        milk_yield_drop: parseFloat(milkDropPercent) || 0,
        observations: notes.trim(),
        image_data: imagePreview || null,
        share_location: shareLocation,
        village: currentAnimal.village || user?.village || 'Wadgaon',
        taluka: currentAnimal.taluka || user?.taluka || 'Haveli',
        district: currentAnimal.district || user?.district || 'Pune',
        latitude: currentAnimal.latitude || 18.5204,
        longitude: currentAnimal.longitude || 73.8567
      };

      const data = await reportsApi.submitHealthReport(payload);
      const reportId = data.report_id || data._id || data.id || 'new-report';
      
      // Navigate to transparent Assessment Result page with response data
      navigate(`/farmer/assessment/${reportId}`, { 
        state: { report: data.report || data, assessment: data.assessment || data }
      });

    } catch (err) {
      setError(err.message || 'Submission error. Please verify backend connection.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-3xl mx-auto space-y-6">
      {/* Top Header */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => navigate(-1)}
          className="p-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-600 transition-colors cursor-pointer"
        >
          <ArrowLeft size={18} />
        </button>
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">
            Report Animal Health Issue
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            AI-assisted multi-modal risk scoring • Independent diagnostic evaluation
          </p>
        </div>
      </div>

      <Card className="border-slate-200 shadow-md">
        <form onSubmit={handleSubmit}>
          <CardHeader className="border-b border-slate-100 pb-4">
            <CardTitle className="text-base font-bold text-slate-900">
              Health Observation Details
            </CardTitle>
            <CardDescription>
              Select the affected animal, indicate observed symptoms, and attach lesion photos
            </CardDescription>
          </CardHeader>

          <CardContent className="p-6 space-y-6">
            {error && (
              <div className="p-3.5 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm flex items-center gap-2.5">
                <AlertTriangle size={18} className="shrink-0 text-red-600" />
                <span>{error}</span>
              </div>
            )}

            {/* 1. Animal Selection */}
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                1. Select Affected Livestock *
              </label>
              {fetchingHerd ? (
                <div className="text-xs text-slate-500 py-2 flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-emerald-600 border-t-transparent rounded-full animate-spin" />
                  Loading your herd records...
                </div>
              ) : animals.length > 0 ? (
                <Select
                  value={selectedAnimalId}
                  onChange={(e) => setSelectedAnimalId(e.target.value)}
                >
                  {animals.map((a) => (
                    <option key={a.animal_id} value={a.animal_id}>
                      {a.animal_id} — {a.species} ({a.breed || 'Indigenous'}, {a.age} yrs)
                    </option>
                  ))}
                </Select>
              ) : (
                <Input
                  placeholder="Enter Ear-Tag ID (e.g. MH-PUN-CTL-0124)"
                  value={selectedAnimalId}
                  onChange={(e) => setSelectedAnimalId(e.target.value)}
                  required
                />
              )}
            </div>

            {/* 2. Symptom Selection Chips */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
                  2. Select Observed Symptoms (Tap to toggle)
                </label>
                <span className="text-[11px] text-slate-500 font-medium">
                  {selectedSymptoms.length} selected
                </span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
                {COMMON_SYMPTOMS.map((sym) => {
                  const isSelected = selectedSymptoms.includes(sym.label);
                  return (
                    <button
                      type="button"
                      key={sym.id}
                      onClick={() => toggleSymptom(sym.label)}
                      className={`p-3 rounded-xl border text-left text-xs transition-all cursor-pointer flex items-center gap-2.5 ${
                        isSelected
                          ? 'border-emerald-600 bg-emerald-50 text-emerald-950 font-bold ring-2 ring-emerald-600/20 shadow-xs'
                          : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50'
                      }`}
                    >
                      <span className="text-base shrink-0">{sym.icon}</span>
                      <span className="leading-snug">{sym.label}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* 3. Vitals & Clinical Measurements */}
            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-4">
              <label className="block text-xs font-bold text-slate-900 uppercase tracking-wider">
                3. Temperature & Production Vitals
              </label>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label className="block text-[11px] font-semibold text-slate-600 mb-1 flex items-center gap-1">
                    <Thermometer size={13} className="text-rose-600" />
                    Body Temp (°C)
                  </label>
                  <Input
                    type="number"
                    step="0.1"
                    min="35.0"
                    max="43.0"
                    value={temp}
                    onChange={(e) => setTemp(e.target.value)}
                    placeholder="38.5"
                  />
                  <span className="text-[10px] text-slate-400 mt-0.5 block">Normal: 38.0 - 39.0°C</span>
                </div>

                <div>
                  <label className="block text-[11px] font-semibold text-slate-600 mb-1 flex items-center gap-1">
                    <Activity size={13} className="text-amber-600" />
                    Feed Appetite
                  </label>
                  <Select
                    value={appetite}
                    onChange={(e) => setAppetite(e.target.value)}
                  >
                    <option value="Normal">Normal Feeding</option>
                    <option value="Reduced">Reduced / Picky</option>
                    <option value="None">Completely Off Feed (Anorexia)</option>
                  </Select>
                </div>

                <div>
                  <label className="block text-[11px] font-semibold text-slate-600 mb-1 flex items-center gap-1">
                    <Milk size={13} className="text-blue-600" />
                    Milk Yield Drop (%)
                  </label>
                  <Input
                    type="number"
                    min="0"
                    max="100"
                    value={milkDropPercent}
                    onChange={(e) => setMilkDropPercent(e.target.value)}
                    placeholder="0"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-600 mb-1">
                  Additional Observations / Field Notes
                </label>
                <Textarea
                  placeholder="Describe when symptoms started, behavior changes, or whether neighboring animals show similar signs..."
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  rows={2}
                />
              </div>
            </div>

            {/* 4. Lesion Photo Upload */}
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                4. Attach Photo for AI Lesion Screening (Optional but Recommended)
              </label>

              {imagePreview ? (
                <div className="relative rounded-2xl border border-slate-200 overflow-hidden bg-slate-900 text-white max-w-sm">
                  <img
                    src={imagePreview}
                    alt="Uploaded lesion preview"
                    className="w-full h-48 object-cover"
                  />
                  <button
                    type="button"
                    onClick={clearImage}
                    className="absolute top-2 right-2 p-1.5 rounded-full bg-black/60 hover:bg-black text-white transition-colors cursor-pointer"
                  >
                    <X size={16} />
                  </button>
                  <div className="p-2.5 bg-black/70 text-xs flex items-center justify-between">
                    <span>{imageFile?.name || 'Lesion Image'}</span>
                    <Badge variant="low" className="text-[10px]">Ready for AI</Badge>
                  </div>
                </div>
              ) : (
                <label className="border-2 border-dashed border-slate-300 hover:border-emerald-600 rounded-2xl p-6 flex flex-col items-center justify-center text-center cursor-pointer transition-colors bg-white hover:bg-slate-50 block">
                  <div className="w-12 h-12 rounded-2xl bg-emerald-50 text-emerald-700 flex items-center justify-center mb-2">
                    <Camera size={24} />
                  </div>
                  <span className="text-sm font-bold text-slate-800">
                    Upload or Capture Lesion Photo
                  </span>
                  <span className="text-xs text-slate-500 mt-1">
                    PNG, JPG, or JPEG (Max 10MB) • Clear photo of mouth, skin nodules, or hooves
                  </span>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleImageChange}
                    className="hidden"
                  />
                </label>
              )}
            </div>

            {/* 5. Privacy & Location Notice */}
            <div className="p-4 rounded-2xl bg-emerald-50/70 border border-emerald-200 flex items-start gap-3">
              <input
                type="checkbox"
                id="shareLocation"
                checked={shareLocation}
                onChange={(e) => setShareLocation(e.target.checked)}
                className="mt-1 h-4 w-4 rounded text-emerald-600 focus:ring-emerald-500 border-slate-300"
              />
              <label htmlFor="shareLocation" className="text-xs text-emerald-950 cursor-pointer">
                <span className="font-bold block mb-0.5">
                  Share approximate regional location for disease surveillance
                </span>
                <span className="text-emerald-800/90 leading-relaxed block">
                  Your exact farm coordinates are never displayed to other users or public maps. Only generalized village/taluka center points are utilized by disease surveillance officers to detect potential emerging clusters.
                </span>
              </label>
            </div>

          </CardContent>

          <CardFooter className="border-t border-slate-100 p-6 flex items-center justify-between">
            <Button
              type="button"
              variant="ghost"
              onClick={() => navigate('/farmer/dashboard')}
            >
              Cancel
            </Button>

            <Button
              type="submit"
              variant="primary"
              size="lg"
              disabled={loading}
              className="shadow-sm"
            >
              <FileText size={16} />
              <span>{loading ? 'Evaluating Multi-Modal Risk...' : 'Submit Report & Run AI Evaluation'}</span>
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
};

export default ReportHealthIssue;
