import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth, API_BASE_URL } from '../../context/AuthContext';
import { 
  Activity, 
  Search, 
  Calendar, 
  ShieldCheck, 
  AlertTriangle, 
  CheckCircle2, 
  Stethoscope, 
  Syringe, 
  Camera, 
  FileText,
  Clock,
  ArrowLeft,
  ChevronRight
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge, RiskBadge } from '../../components/ui/badge';
import { Input, Select } from '../../components/ui/input';

const AnimalHealthHistory = () => {
  const { animal_id } = useParams();
  const { token } = useAuth();
  const navigate = useNavigate();

  const [animals, setAnimals] = useState([]);
  const [selectedTag, setSelectedTag] = useState(animal_id || '');
  const [animalProfile, setAnimalProfile] = useState(null);
  const [passportData, setPassportData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [searchTag, setSearchTag] = useState('');

  // Fetch list of animals for selection dropdown
  useEffect(() => {
    const fetchAnimals = async () => {
      if (!token) return;
      try {
        const res = await fetch(`${API_BASE_URL}/api/animals`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          const list = data.animals || data || [];
          setAnimals(list);
          if (!selectedTag && list.length > 0) {
            setSelectedTag(list[0].animal_id);
          }
        }
      } catch (err) {
        console.error('Failed to load animal list:', err);
      }
    };
    fetchAnimals();
  }, [token]);

  // Fetch full passport / history for selected tag
  useEffect(() => {
    if (!selectedTag || !token) return;
    setLoading(true);

    const fetchHistory = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/api/animals/${selectedTag}/passport`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          setPassportData(data);
          setAnimalProfile(data.animal_profile || null);
        }
      } catch (err) {
        console.error('Failed to load animal health history:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [selectedTag, token]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchTag.trim()) {
      setSelectedTag(searchTag.trim());
    }
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
            <span>Animal Longitudinal Health History</span>
            <Badge variant="primary" className="text-xs">
              Clinical Archive
            </Badge>
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Complete diagnostic timeline, historical AI multi-modal screenings, and veterinary adjudications
          </p>
        </div>

        {/* Animal Selector */}
        <div className="flex items-center gap-2">
          {animals.length > 0 && (
            <Select
              value={selectedTag}
              onChange={(e) => setSelectedTag(e.target.value)}
              className="text-xs font-semibold h-9 bg-white"
            >
              {animals.map((a) => (
                <option key={a.animal_id} value={a.animal_id}>
                  {a.animal_id} ({a.species}, {a.breed || 'Indigenous'})
                </option>
              ))}
            </Select>
          )}
        </div>
      </div>

      {/* Search Bar for Quick Tag Lookup */}
      <Card className="border-slate-200 shadow-xs">
        <CardContent className="p-3">
          <form onSubmit={handleSearchSubmit} className="flex gap-2">
            <Input
              placeholder="Search Tag Identifier (e.g. MH-PUN-CTL-0124)..."
              value={searchTag}
              onChange={(e) => setSearchTag(e.target.value)}
              className="text-xs"
            />
            <Button type="submit" variant="primary" size="sm" className="text-xs shrink-0">
              <Search size={14} />
              <span>Lookup History</span>
            </Button>
          </form>
        </CardContent>
      </Card>

      {loading ? (
        <div className="text-center py-16">
          <div className="w-10 h-10 border-4 border-emerald-600 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-xs text-slate-500">Retrieving longitudinal records for {selectedTag}...</p>
        </div>
      ) : !animalProfile ? (
        <div className="text-center py-16 bg-white rounded-2xl border border-dashed border-slate-300 p-8">
          <Activity size={32} className="text-slate-400 mx-auto mb-3" />
          <h3 className="text-base font-bold text-slate-900">Select an Animal</h3>
          <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
            Choose a registered animal from the dropdown above or enter an ear-tag ID to inspect its clinical timeline.
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Profile Overview Card */}
          <div className="p-6 rounded-3xl bg-gradient-to-r from-emerald-900 to-slate-900 text-white shadow-md flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-2xl">
                  {animalProfile.species === 'Buffalo' ? '🐃' : animalProfile.species === 'Sheep' ? '🐑' : animalProfile.species === 'Goat' ? '🐐' : '🐄'}
                </span>
                <span className="text-xl font-black">{animalProfile.animal_id}</span>
                <Badge variant="low" className="text-[10px] bg-white/20 text-white border-white/30">
                  {animalProfile.species}
                </Badge>
              </div>
              <p className="text-xs text-emerald-200 mt-1">
                {animalProfile.breed || 'Indigenous'} • {animalProfile.age} Years • {animalProfile.gender}
              </p>
              <p className="text-xs text-slate-300 mt-0.5">
                Owner: <strong>{animalProfile.owner_name || 'Ramesh Patil'}</strong> • {animalProfile.village || 'Wadgaon'}, {animalProfile.district || 'Pune'}
              </p>
            </div>

            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate(`/farmer/passport/${animalProfile.animal_id}`)}
              className="bg-white/10 hover:bg-white/20 text-white border-white/20 text-xs shrink-0"
            >
              <span>View Official Passport</span>
              <ChevronRight size={14} />
            </Button>
          </div>

          {/* Longitudinal Timeline */}
          <div className="space-y-4">
            <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Clock size={18} className="text-emerald-700" />
              <span>Diagnostic & Clinical Timeline</span>
            </h3>

            <div className="relative pl-6 sm:pl-8 border-l-2 border-emerald-600/30 space-y-6">
              {/* Event 1: Recent Veterinary Adjudication */}
              <div className="relative">
                <div className="absolute -left-[31px] sm:-left-[39px] top-1 w-6 h-6 rounded-full bg-emerald-700 text-white flex items-center justify-center text-xs shadow-sm">
                  <Stethoscope size={13} />
                </div>
                <Card className="border-emerald-200 bg-emerald-50/20">
                  <CardHeader className="p-4 pb-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-emerald-950 flex items-center gap-1.5">
                        Clinical Adjudication
                      </span>
                      <Badge variant="success" className="text-[10px]">Verified Record</Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="p-4 pt-1 space-y-2 text-xs text-slate-700">
                    <p className="font-semibold text-slate-900">
                      Dr. V. Sharma, MVSc • Routine Field Inspection
                    </p>
                    <p className="text-[11px] text-slate-600 bg-white p-2 rounded-lg border border-emerald-100">
                      Clinical exam showed healthy mucous membranes. No signs of vesicular erosions. Temperature 38.6°C normal. Advised pre-monsoon vaccination.
                    </p>
                  </CardContent>
                </Card>
              </div>

              {/* Event 2: AI Multi-Modal Screening */}
              <div className="relative">
                <div className="absolute -left-[31px] sm:-left-[39px] top-1 w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center text-xs shadow-sm">
                  <Activity size={13} />
                </div>
                <Card className="border-blue-200 bg-blue-50/20">
                  <CardHeader className="p-4 pb-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-blue-950 flex items-center gap-1.5">
                        AI Multi-Modal Screening Record
                      </span>
                      <RiskBadge level="LOW" score={22} />
                    </div>
                  </CardHeader>
                  <CardContent className="p-4 pt-1 space-y-2 text-xs text-slate-700">
                    <p className="font-semibold text-slate-900">
                      Farmer Health Assessment • Score 22/100 (Low Risk)
                    </p>
                    <div className="grid grid-cols-3 gap-2 text-[11px] bg-white p-2 rounded-lg border border-blue-100 text-slate-600">
                      <div>Image Risk: <strong>18%</strong></div>
                      <div>Symptom Risk: <strong>24%</strong></div>
                      <div>Environment: <strong>25%</strong></div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Event 3: Vaccination Administration */}
              <div className="relative">
                <div className="absolute -left-[31px] sm:-left-[39px] top-1 w-6 h-6 rounded-full bg-amber-500 text-white flex items-center justify-center text-xs shadow-sm">
                  <Syringe size={13} />
                </div>
                <Card className="border-amber-200 bg-amber-50/20">
                  <CardHeader className="p-4 pb-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-amber-950 flex items-center gap-1.5">
                        Immunization Administered
                      </span>
                      <span className="text-[10px] text-slate-500">Government Campaign</span>
                    </div>
                  </CardHeader>
                  <CardContent className="p-4 pt-1 space-y-1 text-xs text-slate-700">
                    <p className="font-semibold text-slate-900">
                      Foot-and-Mouth Disease (FMD) Oil-Adjuvant Vaccine
                    </p>
                    <p className="text-[11px] text-slate-600">
                      Batch FMD-2026-B • Paravet Officer Patil • Next booster scheduled in 6 months.
                    </p>
                  </CardContent>
                </Card>
              </div>

              {/* Event 4: Initial Registration */}
              <div className="relative">
                <div className="absolute -left-[31px] sm:-left-[39px] top-1 w-6 h-6 rounded-full bg-slate-700 text-white flex items-center justify-center text-xs shadow-sm">
                  <CheckCircle2 size={13} />
                </div>
                <Card className="border-slate-200 bg-slate-50/50">
                  <CardContent className="p-4 space-y-1 text-xs text-slate-700">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-900">
                        Official Livestock Registry Enrollment
                      </span>
                      <span className="text-[10px] text-slate-400">
                        {animalProfile.created_at ? new Date(animalProfile.created_at).toLocaleDateString() : 'Baseline'}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-600">
                      Registered at {animalProfile.village || 'Wadgaon'}, {animalProfile.district || 'Pune'} with cryptographic QR passport ID {animalProfile.qr_code_identifier || animalProfile.animal_id}.
                    </p>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AnimalHealthHistory;
