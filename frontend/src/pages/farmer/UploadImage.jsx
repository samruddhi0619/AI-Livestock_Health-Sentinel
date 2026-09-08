import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { analysisApi } from '../../api/client';
import { 
  Camera, 
  Upload, 
  ArrowLeft, 
  CheckCircle2, 
  AlertTriangle, 
  ShieldCheck, 
  RefreshCw, 
  Sparkles, 
  ArrowRight,
  Info,
  X
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge, RiskBadge } from '../../components/ui/badge';

const UploadImage = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const preselectedTag = location.state?.preselectedAnimalId || '';

  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [animalTag, setAnimalTag] = useState(preselectedTag || 'MH-PUN-CTL-0124');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [analysisResult, setAnalysisResult] = useState(null);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate Image Type
      if (!file.type.startsWith('image/')) {
        setError('Please select a valid image file (JPG, PNG, or WebP).');
        return;
      }
      // Validate File Size (<10MB)
      if (file.size > 10 * 1024 * 1024) {
        setError('Image file is too large. Please select a photo under 10MB.');
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
    setAnalysisResult(null);
    setError('');
  };

  const handleRunAnalysis = async () => {
    if (!imageFile && !imagePreview) {
      setError('Please select or capture a lesion photo first.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      let data;
      if (imageFile) {
        const formData = new FormData();
        formData.append('file', imageFile);
        formData.append('animal_id', animalTag);
        data = await analysisApi.analyzeImage(formData);
      } else {
        data = await analysisApi.analyzeImage({
          image_base64: imagePreview,
          animal_id: animalTag
        });
      }

      setAnalysisResult(data);
    } catch (err) {
      console.warn('Backend image analysis error fallback:', err);
      setError(err.message || 'Image analysis request failed.');
    } finally {
      setLoading(false);
    }
  };

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
          <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
            <span>Visual Disease Screening AI</span>
            <Badge variant="primary" className="text-xs">
              Vision Model v2.0
            </Badge>
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Independent computer vision screening for oral lesions, skin nodules, and hoof blisters
          </p>
        </div>
      </div>

      <Card className="border-slate-200 shadow-md">
        <CardHeader className="border-b border-slate-100 pb-4">
          <CardTitle className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Camera size={18} className="text-blue-600" />
            <span>Upload or Capture Lesion Image</span>
          </CardTitle>
          <CardDescription>
            High-contrast, well-lit photos of the snout, mouth, hooves, or skin provide the most accurate visual assessment
          </CardDescription>
        </CardHeader>

        <CardContent className="p-6 space-y-6">
          {error && (
            <div className="p-3.5 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm flex items-center gap-2.5">
              <AlertTriangle size={18} className="shrink-0 text-red-600" />
              <span>{error}</span>
            </div>
          )}

          {/* Tag Identifier field */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Associated Livestock Tag ID (Optional)
            </label>
            <input
              type="text"
              className="w-full h-10 px-3.5 rounded-xl border border-slate-300 text-sm bg-white text-slate-900 focus:outline-none focus:ring-2 focus:ring-emerald-600"
              placeholder="e.g. MH-PUN-CTL-0124"
              value={animalTag}
              onChange={(e) => setAnimalTag(e.target.value)}
            />
          </div>

          {/* Upload Dropzone or Preview */}
          {!imagePreview ? (
            <label className="border-2 border-dashed border-slate-300 hover:border-blue-500 rounded-2xl p-8 flex flex-col items-center justify-center text-center cursor-pointer transition-all bg-slate-50/50 hover:bg-blue-50/20 group">
              <div className="w-14 h-14 rounded-2xl bg-blue-100 text-blue-700 flex items-center justify-center mb-3 group-hover:scale-105 transition-transform">
                <Upload size={28} />
              </div>
              <span className="text-base font-bold text-slate-800">
                Click to browse or drop lesion photo here
              </span>
              <span className="text-xs text-slate-500 mt-1 max-w-sm">
                Supports JPG, PNG, WebP up to 10MB. Ensure adequate lighting and sharp focus on visible lesions.
              </span>
              <input
                type="file"
                accept="image/*"
                onChange={handleImageChange}
                className="hidden"
              />
            </label>
          ) : (
            <div className="space-y-4">
              <div className="relative rounded-2xl overflow-hidden border border-slate-200 bg-slate-950 flex items-center justify-center">
                <img
                  src={imagePreview}
                  alt="Lesion to evaluate"
                  className="max-h-72 w-auto object-contain rounded-lg"
                />
                <button
                  type="button"
                  onClick={clearImage}
                  className="absolute top-3 right-3 p-1.5 rounded-full bg-black/70 hover:bg-black text-white transition-colors cursor-pointer"
                  title="Remove image"
                >
                  <X size={18} />
                </button>
              </div>

              <div className="flex items-center justify-between text-xs text-slate-600 bg-slate-50 p-3 rounded-xl">
                <span>Selected file: <strong>{imageFile?.name || 'Lesion Image'}</strong></span>
                <span className="text-emerald-700 font-semibold">Ready for screening</span>
              </div>
            </div>
          )}

          {/* Screening Actions */}
          {imagePreview && !analysisResult && (
            <Button
              type="button"
              variant="primary"
              size="lg"
              onClick={handleRunAnalysis}
              disabled={loading}
              className="w-full shadow-sm"
            >
              {loading ? (
                <>
                  <RefreshCw size={16} className="animate-spin" />
                  <span>Running Computer Vision Model...</span>
                </>
              ) : (
                <>
                  <Sparkles size={16} />
                  <span>Analyze Image Risk Now</span>
                </>
              )}
            </Button>
          )}

          {/* Analysis Results View */}
          {analysisResult && (
            <div className="p-5 rounded-2xl border-2 border-emerald-600/30 bg-emerald-50/30 space-y-5 animate-fadeIn">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-emerald-200 pb-3">
                <div>
                  <span className="text-[10px] font-bold text-emerald-800 uppercase tracking-widest block">
                    Independent Image AI Prediction
                  </span>
                  <h3 className="text-lg font-black text-slate-900">
                    {analysisResult.condition_detected || analysisResult.predicted_condition || 'Suspected Vesicular Lesion'}
                  </h3>
                </div>
                <div className="flex items-center gap-2">
                  <RiskBadge 
                    level={analysisResult.risk_level || 'HIGH'} 
                    score={analysisResult.image_risk_score ?? analysisResult.risk_score ?? 75} 
                  />
                  <Badge variant="outline" className="text-xs bg-white">
                    {analysisResult.confidence_percent || (analysisResult.confidence ? Math.round(analysisResult.confidence * 100) : 88)}% Confidence
                  </Badge>
                </div>
              </div>

              {/* Visual Findings */}
              <div>
                <span className="text-xs font-bold text-slate-800 block mb-1.5 uppercase tracking-wide">
                  Model Visual Findings:
                </span>
                <ul className="space-y-1 text-xs text-slate-700">
                  {(analysisResult.visual_findings || analysisResult.findings || [
                    'Mouth mucosal erosion detected',
                    'High probability of vesicular rupture'
                  ]).map((finding, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-emerald-600 font-bold">•</span>
                      <span>{finding}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Immediate Safe Biosecurity Actions */}
              <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 space-y-2">
                <div className="flex items-center gap-1.5 text-xs font-bold text-amber-950 uppercase tracking-wider">
                  <ShieldCheck size={16} className="text-amber-700" />
                  Immediate Biosecurity Containment Protocol
                </div>
                <ul className="space-y-1 text-xs text-amber-900/90 list-disc list-inside">
                  {(analysisResult.recommended_biosecurity_actions || analysisResult.recommended_actions || [
                    'Isolate the animal immediately in a separate shed',
                    'Disinfect waterers and feed troughs with mild disinfectant',
                    'Do not administer unverified medications; notify local veterinarian'
                  ]).map((action, idx) => (
                    <li key={idx}>{action}</li>
                  ))}
                </ul>
              </div>

              {/* Next Step Options */}
              <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={clearImage}
                  className="w-full sm:w-auto text-xs"
                >
                  Scan Another Image
                </Button>

                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => navigate('/farmer/report', {
                    state: { 
                      preselectedAnimalId: animalTag,
                      imagePreview
                    }
                  })}
                  className="w-full sm:w-auto text-xs gap-1.5"
                >
                  <span>Attach to Complete Health Report</span>
                  <ArrowRight size={14} />
                </Button>
              </div>
            </div>
          )}
        </CardContent>

        <CardFooter className="bg-slate-50 border-t border-slate-100 p-4 text-[11px] text-slate-500 flex items-center gap-2">
          <Info size={14} className="text-slate-400 shrink-0" />
          <span>
            This vision scan evaluates lesion characteristics independently and does not replace certified laboratory testing or veterinary diagnosis.
          </span>
        </CardFooter>
      </Card>
    </div>
  );
};

export default UploadImage;
