import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { Header } from './components/Header';
import { Hero } from './components/Hero';
import { HowItWorks } from './components/HowItWorks';
import { Features } from './components/Features';
import { LocationAnalysis } from './components/LocationAnalysis';
import { DesignComparison } from './components/DesignComparison';
import { ArrowLeft } from 'lucide-react';
import { AnalysisPage } from './pages/AnalysisPage';

// Types for property details (keeping for future integration)
import type { Property } from './components/PropertyCard';

function HomePage() {
  const [selectedPropertyId, setSelectedPropertyId] = useState<string | null>(null);
  const navigate = useNavigate();
  const location = useLocation();

  // Handle scroll to section if coming from another page
  useEffect(() => {
    if (location.state && location.state.scrollTo) {
      const id = location.state.scrollTo;
      setTimeout(() => {
        document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    }
  }, [location]);

  // Placeholder for future real data
  const properties: Property[] = [];
  const selectedProperty = properties.find(p => p.id === selectedPropertyId);

  return (
    <div className="min-h-screen bg-white selection:bg-brand-100 selection:text-brand-900">
      <Header />
      <main>
        {selectedProperty ? (
          <div className="pt-24 pb-20 container mx-auto px-6 animate-in fade-in slide-in-from-bottom-4">
            <button
              onClick={() => setSelectedPropertyId(null)}
              className="flex items-center gap-2 text-slate-500 hover:text-brand-600 mb-8 transition-colors font-medium"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Results
            </button>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
              {/* Left Column: Design & Images */}
              <div className="space-y-8">
                <div>
                  <h1 className="text-3xl font-bold text-slate-900 mb-2">{selectedProperty.title}</h1>
                  <p className="text-xl text-brand-600 font-medium">{selectedProperty.price}</p>
                  <p className="text-slate-500 mt-1">{selectedProperty.address}</p>
                </div>

                <DesignComparison
                  originalImage={selectedProperty.image}
                  redesignedImage="https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?auto=format&fit=crop&q=80&w=800"
                  styleName="Modern Minimalist"
                  isGenerating={false}
                />

                <div className="bg-slate-50 rounded-xl p-6 border border-slate-100">
                  <h3 className="font-bold text-slate-900 mb-4">Property Specs</h3>
                  <div className="grid grid-cols-3 gap-4">
                    <div className="text-center p-4 bg-white rounded-lg shadow-sm">
                      <span className="block text-2xl font-bold text-slate-900">{selectedProperty.specs.beds}</span>
                      <span className="text-xs text-slate-500 uppercase tracking-wider">Beds</span>
                    </div>
                    <div className="text-center p-4 bg-white rounded-lg shadow-sm">
                      <span className="block text-2xl font-bold text-slate-900">{selectedProperty.specs.baths}</span>
                      <span className="text-xs text-slate-500 uppercase tracking-wider">Baths</span>
                    </div>
                    <div className="text-center p-4 bg-white rounded-lg shadow-sm">
                      <span className="block text-2xl font-bold text-slate-900">{selectedProperty.specs.sqft}</span>
                      <span className="text-xs text-slate-500 uppercase tracking-wider">Sqft</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Right Column: Location Intelligence */}
              <div>
                <LocationAnalysis
                  score={selectedProperty.rating}
                  grade="A"
                  amenities={[
                    { category: 'markets', score: 95, distance: '0.2km', count: 4 },
                    { category: 'gyms', score: 85, distance: '0.5km', count: 2 },
                    { category: 'transit', score: 70, distance: '1.2km', count: 1 },
                    { category: 'airports', score: 60, distance: '15km', count: 1 },
                  ]}
                />
              </div>
            </div>
          </div>
        ) : (
          <>
            <Hero />
            <HowItWorks />
            <Features />

            <div className="container mx-auto px-6 py-24 text-center">
              <h2 className="text-3xl font-bold text-brand-900 mb-6">Ready to find your next investment?</h2>
              <p className="text-brand-700 max-w-2xl mx-auto mb-8">
                Our AI agents are standing by to analyze locations and redesign properties for you.
              </p>

              <button
                onClick={() => navigate('/analysis')}
                className="btn-primary inline-flex items-center gap-2 px-8 py-4 text-lg shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all duration-300"
              >
                <span>Start Analysis</span>
                <ArrowLeft className="w-5 h-5 rotate-180" />
              </button>
            </div>
          </>
        )}
      </main>

      <footer className="bg-slate-50 border-t border-slate-200 py-12">
        <div className="container mx-auto px-6 text-center text-slate-500 text-sm">
          <p>© 2026 Property Gemini AI. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/analysis" element={<AnalysisPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
