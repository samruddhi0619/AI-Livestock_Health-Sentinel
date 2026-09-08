import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { animalsApi } from '../../api/client';
import { 
  PlusCircle, 
  ArrowLeft, 
  MapPin, 
  ShieldCheck, 
  CheckCircle2, 
  AlertCircle, 
  QrCode, 
  Camera, 
  Sparkles,
  Info,
  Compass
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input, Select, Textarea } from '../../components/ui/input';
import { Badge } from '../../components/ui/badge';

const AddAnimal = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [species, setSpecies] = useState('Cattle');
  const [tagId, setTagId] = useState('');
  const [breed, setBreed] = useState('Gir');
  const [age, setAge] = useState('3.5');
  const [gender, setGender] = useState('Female');
  const [healthHistory, setHealthHistory] = useState('Fully vaccinated; routine deworming completed.');
  
  // Location states
  const [village, setVillage] = useState(user?.village || 'Wadgaon');
  const [taluka, setTaluka] = useState(user?.taluka || 'Haveli');
  const [district, setDistrict] = useState(user?.district || 'Pune');
  const [latitude, setLatitude] = useState(18.5204);
  const [longitude, setLongitude] = useState(73.8567);
  const [gpsDetecting, setGpsDetecting] = useState(false);
  const [gpsSuccess, setGpsSuccess] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [createdAnimal, setCreatedAnimal] = useState(null);

  // Common breeds by species
  const breedOptions = {
    Cattle: ['Gir', 'Sahiwal', 'Red Sindhi', 'Khillari', 'Deoni', 'Holstein Friesian Cross', 'Jersey Cross', 'Indigenous / Non-Descript'],
    Buffalo: ['Murrah', 'Pandharpuri', 'Jaffarabadi', 'Surti', 'Nagpuri', 'Mehsana', 'Indigenous Buffalo'],
    Sheep: ['Deccani', 'Nellore', 'Madras Red', 'Marwari', 'Crossbred Sheep'],
    Goat: ['Osmanabadi', 'Sirohi', 'Beetal', 'Barbari', 'Jamnapari', 'Local Black Bengal']
  };

  const handleSpeciesChange = (newSpecies) => {
    setSpecies(newSpecies);
    setBreed(breedOptions[newSpecies][0]);
  };

  const handleAutoTag = () => {
    const prefix = species === 'Buffalo' ? 'BUF' : species === 'Sheep' ? 'SHP' : species === 'Goat' ? 'GOT' : 'CTL';
    const rand = Math.floor(1000 + Math.random() * 9000);
    setTagId(`MH-PUN-${prefix}-${rand}`);
  };

  const handleDetectGps = () => {
    if (!navigator.geolocation) {
      setError('Geolocation is not supported by your browser.');
      return;
    }
    setGpsDetecting(true);
    setError('');
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLatitude(parseFloat(position.coords.latitude.toFixed(6)));
        setLongitude(parseFloat(position.coords.longitude.toFixed(6)));
        setGpsDetecting(false);
        setGpsSuccess(true);
      },
      (err) => {
        setGpsDetecting(false);
        console.warn('GPS detection failed, using farm centroid:', err.message);
        setLatitude(18.5204);
        setLongitude(73.8567);
      },
      { timeout: 10000, enableHighAccuracy: true }
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Client-side Validation
    const ageNum = parseFloat(age);
    if (isNaN(ageNum) || ageNum <= 0 || ageNum > 30) {
      setError('Please provide a valid animal age in years (0.1 - 30.0).');
      return;
    }
    if (!village.trim() || !taluka.trim() || !district.trim()) {
      setError('Please complete all farm location fields.');
      return;
    }

    setLoading(true);

    const payload = {
      species,
      animal_id: tagId.trim() || undefined,
      breed,
      age: ageNum,
      gender,
      health_history: healthHistory,
      village: village.trim(),
      taluka: taluka.trim(),
      district: district.trim(),
      latitude: parseFloat(latitude),
      longitude: parseFloat(longitude)
    };

    try {
      const data = await animalsApi.registerAnimal(payload);
      setCreatedAnimal(data);
    } catch (err) {
      setError(err.message || 'An error occurred during registration.');
    } finally {
      setLoading(false);
    }
  };

  // Success view with digital passport link & QR code preview
  if (createdAnimal) {
    const animal = createdAnimal.animal || {};
    const animalId = createdAnimal.animal_id || animal.animal_id;
    const qrBase64 = createdAnimal.qr_code_base64;

    return (
      <div className="p-4 sm:p-6 lg:p-8 max-w-2xl mx-auto space-y-6">
        <Card className="border-emerald-200 bg-emerald-50/40 shadow-lg text-center p-6 sm:p-8">
          <div className="w-16 h-16 rounded-3xl bg-emerald-700 text-white flex items-center justify-center mx-auto mb-4 shadow-md shadow-emerald-700/30">
            <CheckCircle2 size={36} />
          </div>

          <h2 className="text-2xl font-black text-slate-900 tracking-tight">
            Livestock Registered Successfully!
          </h2>
          <p className="text-sm text-slate-600 mt-1">
            Official Ear-Tag ID and tamper-proof Digital Health Passport generated.
          </p>

          <div className="my-6 p-5 rounded-2xl bg-white border border-emerald-100 shadow-xs max-w-md mx-auto space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <span className="text-xs text-slate-500 font-bold uppercase">Official Ear-Tag ID</span>
              <span className="text-base font-black text-emerald-900">{animalId}</span>
            </div>

            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <span className="text-xs text-slate-500 font-bold uppercase">Species & Breed</span>
              <span className="text-sm font-bold text-slate-800">{species} • {breed}</span>
            </div>

            {/* QR Code asset render */}
            {qrBase64 && (
              <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 inline-block">
                <img
                  src={qrBase64}
                  alt={`QR Passport for ${animalId}`}
                  className="w-36 h-36 mx-auto rounded-lg"
                />
                <span className="text-[10px] text-slate-500 block mt-1">
                  Scannable by field veterinarians
                </span>
              </div>
            )}
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
            <Button
              variant="primary"
              size="md"
              onClick={() => navigate(`/farmer/passport/${animalId}`)}
              className="w-full sm:w-auto"
            >
              <QrCode size={16} />
              <span>Open Digital Health Passport</span>
            </Button>
            <Button
              variant="outline"
              size="md"
              onClick={() => {
                setCreatedAnimal(null);
                setTagId('');
              }}
              className="w-full sm:w-auto"
            >
              <PlusCircle size={16} />
              <span>Register Another Animal</span>
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-3xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => navigate(-1)}
          className="p-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-600 transition-colors cursor-pointer"
        >
          <ArrowLeft size={18} />
        </button>
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">
            Register New Livestock
          </h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Create an official national ear-tag profile and instant Digital Health Passport
          </p>
        </div>
      </div>

      <Card className="border-slate-200 shadow-md">
        <form onSubmit={handleSubmit}>
          <CardHeader className="border-b border-slate-100 pb-4">
            <CardTitle className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Sparkles size={18} className="text-amber-500" />
              <span>Animal Identity & Demographics</span>
            </CardTitle>
            <CardDescription>
              Specify the biological attributes of the animal
            </CardDescription>
          </CardHeader>

          <CardContent className="p-6 space-y-6">
            {error && (
              <div className="p-3.5 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm flex items-center gap-2.5">
                <AlertCircle size={18} className="shrink-0 text-red-600" />
                <span>{error}</span>
              </div>
            )}

            {/* Species Selector */}
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Livestock Species *
              </label>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {[
                  { label: 'Cattle / Cow', value: 'Cattle', emoji: '🐄' },
                  { label: 'Buffalo', value: 'Buffalo', emoji: '🐃' },
                  { label: 'Sheep', value: 'Sheep', emoji: '🐑' },
                  { label: 'Goat', value: 'Goat', emoji: '🐐' }
                ].map((item) => (
                  <button
                    type="button"
                    key={item.value}
                    onClick={() => handleSpeciesChange(item.value)}
                    className={`p-3.5 rounded-2xl border text-center transition-all cursor-pointer flex flex-col items-center justify-center ${
                      species === item.value
                        ? 'border-emerald-600 bg-emerald-50 text-emerald-950 ring-2 ring-emerald-600/20 font-bold shadow-xs'
                        : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50'
                    }`}
                  >
                    <span className="text-2xl mb-1">{item.emoji}</span>
                    <span className="text-xs font-semibold">{item.label}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Ear Tag & Auto Generation */}
            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="block text-xs font-semibold text-slate-700">
                  National Ear-Tag Identifier
                </label>
                <button
                  type="button"
                  onClick={handleAutoTag}
                  className="text-xs font-semibold text-emerald-700 hover:text-emerald-800 hover:underline flex items-center gap-1 cursor-pointer"
                >
                  <Sparkles size={12} />
                  <span>Auto-Generate Tag</span>
                </button>
              </div>
              <Input
                placeholder="Leave blank for automatic tag (e.g. MH-PUN-CTL-4912)"
                value={tagId}
                onChange={(e) => setTagId(e.target.value)}
              />
              <p className="text-[11px] text-slate-500 mt-1">
                If the animal already has a physical ear-tag issued by the Animal Husbandry Department, enter it here.
              </p>
            </div>

            {/* Breed, Age, Gender */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Breed *
                </label>
                <Select
                  value={breed}
                  onChange={(e) => setBreed(e.target.value)}
                >
                  {breedOptions[species]?.map((b) => (
                    <option key={b} value={b}>{b}</option>
                  ))}
                </Select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Age (in Years) *
                </label>
                <Input
                  type="number"
                  step="0.5"
                  min="0.1"
                  max="25"
                  value={age}
                  onChange={(e) => setAge(e.target.value)}
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Gender *
                </label>
                <Select
                  value={gender}
                  onChange={(e) => setGender(e.target.value)}
                >
                  <option value="Female">Female</option>
                  <option value="Male">Male</option>
                </Select>
              </div>
            </div>

            {/* Prior Health History */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Health & Vaccination History
              </label>
              <Textarea
                placeholder="e.g. FMD vaccinated in March 2026; no prior foot lesions; healthy milk production."
                value={healthHistory}
                onChange={(e) => setHealthHistory(e.target.value)}
                rows={2}
              />
            </div>

            {/* Location & GPS */}
            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
                  <MapPin size={15} className="text-emerald-700" />
                  Farm Geolocation & Privacy Protection
                </span>
                <Badge variant="low" className="text-[10px]">
                  Fuzzed on Public Map
                </Badge>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-[11px] font-medium text-slate-600 mb-1">
                    Village
                  </label>
                  <Input
                    value={village}
                    onChange={(e) => setVillage(e.target.value)}
                    required
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-medium text-slate-600 mb-1">
                    Taluka
                  </label>
                  <Input
                    value={taluka}
                    onChange={(e) => setTaluka(e.target.value)}
                    required
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-medium text-slate-600 mb-1">
                    District
                  </label>
                  <Input
                    value={district}
                    onChange={(e) => setDistrict(e.target.value)}
                    required
                  />
                </div>
              </div>

              <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2">
                <div className="text-xs text-slate-500">
                  <span>Coordinates: </span>
                  <span className="font-mono text-slate-700">{latitude.toFixed(4)}, {longitude.toFixed(4)}</span>
                  {gpsSuccess && <span className="text-emerald-600 font-semibold ml-2">✓ Verified via GPS</span>}
                </div>

                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={handleDetectGps}
                  disabled={gpsDetecting}
                  className="text-xs bg-white text-slate-700 cursor-pointer"
                >
                  <Compass size={14} className={gpsDetecting ? 'animate-spin' : ''} />
                  <span>{gpsDetecting ? 'Detecting GPS...' : 'Detect Farm GPS'}</span>
                </Button>
              </div>
            </div>
          </CardContent>

          <CardFooter className="border-t border-slate-100 p-6 flex items-center justify-between">
            <Button
              type="button"
              variant="ghost"
              onClick={() => navigate('/farmer/animals')}
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
              <PlusCircle size={16} />
              <span>{loading ? 'Registering Animal...' : 'Register Livestock & Generate Passport'}</span>
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
};

export default AddAnimal;
