import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { animalsApi } from '../../api/client';
import { 
  PlusCircle, 
  Search, 
  Filter, 
  QrCode, 
  FileText, 
  Camera, 
  Activity, 
  MapPin, 
  Calendar,
  AlertCircle,
  CheckCircle2,
  RefreshCw
} from 'lucide-react';
import { Card, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge, RiskBadge } from '../../components/ui/badge';
import { Input } from '../../components/ui/input';

const MyAnimals = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [animals, setAnimals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [speciesFilter, setSpeciesFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [refreshing, setRefreshing] = useState(false);

  const fetchAnimals = async () => {
    try {
      const data = await animalsApi.getAnimals();
      setAnimals(data.animals || data || []);
    } catch (err) {
      console.error('Error fetching animals:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchAnimals();
  }, []);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchAnimals();
  };

  // Filter animals based on search query, species, and status
  const filteredAnimals = animals.filter(animal => {
    const s = search.toLowerCase();
    const matchesSearch = 
      (animal.animal_id && animal.animal_id.toLowerCase().includes(s)) ||
      (animal.breed && animal.breed.toLowerCase().includes(s)) ||
      (animal.village && animal.village.toLowerCase().includes(s));

    const matchesSpecies = 
      speciesFilter === 'ALL' || animal.species?.toUpperCase() === speciesFilter;

    const matchesStatus = 
      statusFilter === 'ALL' ||
      (statusFilter === 'HEALTHY' && (animal.health_status === 'HEALTHY' || !animal.health_status)) ||
      (statusFilter === 'RISK' && (animal.health_status === 'CRITICAL' || animal.health_status === 'HIGH_RISK' || animal.health_status === 'SUSPECTED'));

    return matchesSearch && matchesSpecies && matchesStatus;
  });

  const getSpeciesEmoji = (species) => {
    switch (species?.toUpperCase()) {
      case 'BUFFALO': return '🐃';
      case 'SHEEP': return '🐑';
      case 'GOAT': return '🐐';
      default: return '🐄';
    }
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
            <span>My Registered Livestock</span>
            <Badge variant="primary" className="text-xs">
              {animals.length} Herd Size
            </Badge>
          </h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Manage your registered livestock, view tamper-proof digital passports, and track health histories
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            className="text-slate-600"
          >
            <RefreshCw size={15} className={refreshing ? 'animate-spin' : ''} />
            <span>Refresh</span>
          </Button>
          <Button
            variant="primary"
            size="sm"
            onClick={() => navigate('/farmer/animals/add')}
            className="shadow-sm"
          >
            <PlusCircle size={16} />
            <span>Register New Animal</span>
          </Button>
        </div>
      </div>

      {/* Filter and Search Controls */}
      <Card className="border-slate-200 shadow-xs">
        <CardContent className="p-4 space-y-3">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
              <Input
                placeholder="Search by Ear Tag ID (e.g. CTL-0124), breed, or village..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-10 text-xs"
              />
            </div>
          </div>

          <div className="flex flex-wrap items-center justify-between gap-2 pt-1">
            {/* Species filters */}
            <div className="flex flex-wrap items-center gap-1.5 text-xs">
              <span className="text-slate-500 font-semibold mr-1 flex items-center gap-1">
                <Filter size={12} /> Species:
              </span>
              {['ALL', 'CATTLE', 'BUFFALO', 'SHEEP', 'GOAT'].map((sp) => (
                <button
                  key={sp}
                  onClick={() => setSpeciesFilter(sp)}
                  className={`px-2.5 py-1 rounded-lg font-medium transition-colors cursor-pointer ${
                    speciesFilter === sp
                      ? 'bg-emerald-700 text-white font-bold'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  {sp === 'ALL' ? 'All Species' : sp.charAt(0) + sp.slice(1).toLowerCase()}
                </button>
              ))}
            </div>

            {/* Health status filter */}
            <div className="flex items-center gap-1.5 text-xs">
              <span className="text-slate-500 font-semibold mr-1">Status:</span>
              <button
                onClick={() => setStatusFilter('ALL')}
                className={`px-2.5 py-1 rounded-lg font-medium transition-colors cursor-pointer ${
                  statusFilter === 'ALL' ? 'bg-slate-800 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                All
              </button>
              <button
                onClick={() => setStatusFilter('HEALTHY')}
                className={`px-2.5 py-1 rounded-lg font-medium transition-colors cursor-pointer ${
                  statusFilter === 'HEALTHY' ? 'bg-green-700 text-white' : 'bg-green-50 text-green-700 hover:bg-green-100'
                }`}
              >
                Healthy
              </button>
              <button
                onClick={() => setStatusFilter('RISK')}
                className={`px-2.5 py-1 rounded-lg font-medium transition-colors cursor-pointer ${
                  statusFilter === 'RISK' ? 'bg-orange-600 text-white' : 'bg-orange-50 text-orange-700 hover:bg-orange-100'
                }`}
              >
                At Risk
              </button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Livestock Grid */}
      {loading ? (
        <div className="text-center py-16">
          <div className="w-10 h-10 border-4 border-emerald-600 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-sm text-slate-500">Loading your herd records...</p>
        </div>
      ) : filteredAnimals.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-2xl border border-dashed border-slate-300 p-8">
          <div className="w-14 h-14 rounded-2xl bg-emerald-50 text-emerald-700 flex items-center justify-center mx-auto mb-4 text-2xl">
            🐄
          </div>
          <h3 className="text-base font-bold text-slate-900">No animals found</h3>
          <p className="text-sm text-slate-500 mt-1 max-w-sm mx-auto">
            {search || speciesFilter !== 'ALL' || statusFilter !== 'ALL'
              ? 'No registered animals match your current filters. Try resetting the search or filter.'
              : 'You have not registered any animals yet. Register an animal to generate its digital passport.'}
          </p>
          <Button
            variant="primary"
            size="md"
            onClick={() => navigate('/farmer/animals/add')}
            className="mt-5"
          >
            <PlusCircle size={16} />
            <span>Register New Livestock</span>
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredAnimals.map((animal) => {
            const isAtRisk = animal.health_status === 'CRITICAL' || animal.health_status === 'HIGH_RISK' || animal.health_status === 'SUSPECTED';
            const tagId = animal.animal_id || animal._id;
            
            return (
              <Card 
                key={tagId} 
                className="overflow-hidden border-slate-200 hover:border-emerald-500/80 hover:shadow-md transition-all group flex flex-col justify-between"
              >
                <div>
                  {/* Card Header Top with Species & Status */}
                  <div className="p-4 pb-3 border-b border-slate-100 flex items-center justify-between bg-gradient-to-r from-slate-50 to-white">
                    <div className="flex items-center gap-2.5">
                      <span className="text-2xl">{getSpeciesEmoji(animal.species)}</span>
                      <div>
                        <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">
                          Official Tag
                        </span>
                        <span className="text-sm font-black text-slate-900">
                          {tagId}
                        </span>
                      </div>
                    </div>

                    <RiskBadge 
                      level={isAtRisk ? 'HIGH' : 'LOW'} 
                      label={animal.health_status || 'HEALTHY'} 
                    />
                  </div>

                  {/* Card Body with Key Vitals */}
                  <div className="p-4 space-y-2.5 text-xs text-slate-600">
                    <div className="grid grid-cols-2 gap-2 bg-slate-50 p-2.5 rounded-xl">
                      <div>
                        <span className="text-[10px] text-slate-400 font-semibold block uppercase">Breed</span>
                        <span className="font-bold text-slate-800">{animal.breed || 'Indigenous'}</span>
                      </div>
                      <div>
                        <span className="text-[10px] text-slate-400 font-semibold block uppercase">Age & Gender</span>
                        <span className="font-bold text-slate-800">{animal.age} yrs • {animal.gender}</span>
                      </div>
                    </div>

                    <div className="flex items-center justify-between text-[11px] pt-1">
                      <span className="text-slate-500 flex items-center gap-1">
                        <MapPin size={12} className="text-slate-400" />
                        {animal.village || user?.village || 'Wadgaon'}, {animal.taluka || user?.taluka || 'Haveli'}
                      </span>
                      <span className="text-emerald-700 font-medium flex items-center gap-1">
                        <CheckCircle2 size={12} /> Registered
                      </span>
                    </div>
                  </div>
                </div>

                {/* Card Action Footer */}
                <div className="p-3 bg-slate-50/60 border-t border-slate-100 grid grid-cols-3 gap-2">
                  <Link
                    to={`/farmer/passport/${tagId}`}
                    className="flex flex-col items-center justify-center p-2 rounded-lg bg-white border border-slate-200 text-slate-700 hover:border-emerald-600 hover:text-emerald-700 transition-colors cursor-pointer text-[11px] font-semibold"
                    title="View official digital passport"
                  >
                    <QrCode size={16} className="mb-0.5 text-emerald-700" />
                    <span>Passport</span>
                  </Link>

                  <Link
                    to={`/farmer/report`}
                    state={{ preselectedAnimalId: tagId }}
                    className="flex flex-col items-center justify-center p-2 rounded-lg bg-white border border-slate-200 text-slate-700 hover:border-amber-600 hover:text-amber-700 transition-colors cursor-pointer text-[11px] font-semibold"
                    title="Report symptoms for this animal"
                  >
                    <FileText size={16} className="mb-0.5 text-amber-600" />
                    <span>Report</span>
                  </Link>

                  <Link
                    to={`/farmer/upload-image`}
                    state={{ preselectedAnimalId: tagId }}
                    className="flex flex-col items-center justify-center p-2 rounded-lg bg-white border border-slate-200 text-slate-700 hover:border-blue-600 hover:text-blue-700 transition-colors cursor-pointer text-[11px] font-semibold"
                    title="Scan lesions or skin signs"
                  >
                    <Camera size={16} className="mb-0.5 text-blue-600" />
                    <span>AI Scan</span>
                  </Link>
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default MyAnimals;
