import { useState } from 'react';
import { Header } from './components/Header';
import { Hero } from './components/Hero';
import { SearchForm } from './components/SearchForm';
import { PropertyGrid } from './components/PropertyGrid';
import type { Property } from './components/PropertyCard';
import { LocationAnalysis } from './components/LocationAnalysis';
import { DesignComparison } from './components/DesignComparison';
import { ArrowLeft } from 'lucide-react';

// Mock Data
const MOCK_PROPERTIES: Property[] = [
  {
    id: '1',
    title: 'Modern Downtown Loft',
    price: '$2,450/mo',
    address: '123 Congress Ave, Austin, TX',
    specs: { beds: 2, baths: 2, sqft: 1200 },
    image: 'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&q=80&w=800',
    rating: 92,
    tags: ['Downtown', 'Gym']
  },
  {
    id: '2',
    title: 'Riverside Condo with View',
    price: '$3,100/mo',
    address: '456 Riverside Dr, Austin, TX',
    specs: { beds: 3, baths: 2.5, sqft: 1800 },
    image: 'https://images.unsplash.com/photo-1512918760532-3ed64bc8066e?auto=format&fit=crop&q=80&w=800',
    rating: 88,
    tags: ['Waterfront', 'Pool']
  },
  {
    id: '3',
    title: 'Historic Bungalow',
    price: '$2,800/mo',
    address: '789 East 6th St, Austin, TX',
    specs: { beds: 2, baths: 1, sqft: 1100 },
    image: 'https://images.unsplash.com/photo-1513584687574-9cfbe9300081?auto=format&fit=crop&q=80&w=800',
    rating: 95,
    tags: ['Historic', 'Garden']
  }
];

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [properties, setProperties] = useState<Property[]>([]);
  const [hasSearched, setHasSearched] = useState(false);
  const [selectedPropertyId, setSelectedPropertyId] = useState<string | null>(null);

  const handleSearch = (criteria: any) => {
    console.log("Searching with:", criteria);
    setIsLoading(true);
    // Simulate API call
    setTimeout(() => {
      setProperties(MOCK_PROPERTIES);
      setHasSearched(true);
      setIsLoading(false);
    }, 1500);
  };

  const handlePropertySelect = (id: string) => {
    setSelectedPropertyId(id);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

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
            <div className="container mx-auto px-6 mb-20">
              <SearchForm onSearch={handleSearch} isLoading={isLoading} />

              {hasSearched && (
                <div className="mt-24 animate-in fade-in slide-in-from-bottom-4 duration-700">
                  <div className="flex items-center justify-between mb-8">
                    <h2 className="text-2xl font-bold text-slate-900">Top AI Recommendations</h2>
                    <span className="text-sm text-slate-500">Found {properties.length} properties matching your criteria</span>
                  </div>
                  <PropertyGrid properties={properties} onSelect={handlePropertySelect} />
                </div>
              )}
            </div>
          </>
        )}
      </main>

      {/* Footer Placeholder */}
      <footer className="bg-slate-50 border-t border-slate-200 py-12 mt-20">
        <div className="container mx-auto px-6 text-center text-slate-500 text-sm">
          <p>© 2024 Property Gemini AI. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
