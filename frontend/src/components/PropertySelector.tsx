import { useState } from 'react';
import { ExternalLink, Check, X } from 'lucide-react';

interface ScrapedProperty {
    id: string; // or address acting as ID
    url: string;
    price: string;
    address: string;
    bedrooms: number;
    bathrooms: number;
    description: string;
    images: string[];
}

interface PropertySelectorProps {
    properties: ScrapedProperty[];
    onApprove: (selectedIds: string[]) => void;
    onRetry: (feedback: string) => void;
}

export function PropertySelector({ properties, onApprove, onRetry }: PropertySelectorProps) {
    const [selectedIds, setSelectedIds] = useState<string[]>([]);
    const [feedback, setFeedback] = useState('');
    const [isRetrying, setIsRetrying] = useState(false);

    const toggleSelection = (id: string) => {
        if (selectedIds.includes(id)) {
            setSelectedIds(selectedIds.filter(sid => sid !== id));
        } else {
            setSelectedIds([...selectedIds, id]);
        }
    };

    return (
        <div className="max-w-5xl mx-auto">
            <div className="text-center mb-10">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-100 text-brand-800 text-sm font-semibold mb-4">
                    <span className="relative flex h-3 w-3">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-3 w-3 bg-brand-500"></span>
                    </span>
                    Action Required
                </div>
                <h2 className="text-3xl font-bold text-slate-900 font-serif mb-2">Agent Report: {properties.length} Properties Found</h2>
                <p className="text-slate-500">Select the properties you want to analyze deeper (Location & Design agents).</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
                {properties.map((prop) => (
                    <div
                        key={prop.id}
                        onClick={() => toggleSelection(prop.id)}
                        className={`
                            relative rounded-xl border-2 overflow-hidden cursor-pointer transition-all duration-200 hover:shadow-md
                            ${selectedIds.includes(prop.id)
                                ? 'border-brand-500 bg-brand-50/50'
                                : 'border-slate-100 bg-white hover:border-brand-200'}
                        `}
                    >
                        {/* Checkbox Indicator */}
                        <div className={`absolute top-4 right-4 z-10 w-8 h-8 rounded-full flex items-center justify-center transition-all ${selectedIds.includes(prop.id) ? 'bg-brand-500 text-white' : 'bg-white/80 text-slate-300'
                            }`}>
                            <Check className="w-5 h-5" />
                        </div>

                        {/* Image Preview */}
                        <div className="h-48 bg-slate-200 relative">
                            {prop.images && prop.images.length > 0 ? (
                                <img src={prop.images[0]} alt={prop.address} className="w-full h-full object-cover" />
                            ) : (
                                <div className="w-full h-full flex items-center justify-center text-slate-400">No Image</div>
                            )}
                            <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-4">
                                <p className="text-white font-bold">{prop.price}</p>
                            </div>
                        </div>

                        {/* Details */}
                        <div className="p-4">
                            <h3 className="font-bold text-slate-900 line-clamp-1 mb-1">{prop.address}</h3>
                            <div className="flex gap-4 text-sm text-slate-500 mb-3">
                                <span>{prop.bedrooms} Bed</span>
                                <span>{prop.bathrooms} Bath</span>
                            </div>
                            <a
                                href={prop.url}
                                target="_blank"
                                rel="noreferrer"
                                onClick={(e) => e.stopPropagation()}
                                className="text-xs text-brand-600 hover:underline flex items-center gap-1"
                            >
                                View Original Listing <ExternalLink className="w-3 h-3" />
                            </a>
                        </div>
                    </div>
                ))}
            </div>

            {/* Actions Footer */}
            <div className="sticky bottom-6 bg-white/90 backdrop-blur-lg border border-slate-200 p-4 rounded-2xl shadow-2xl flex flex-col md:flex-row items-center justify-between gap-6">

                {/* Retry Option */}
                <div className="flex-1 w-full md:w-auto">
                    {!isRetrying ? (
                        <button
                            onClick={() => setIsRetrying(true)}
                            className="text-slate-500 hover:text-slate-800 text-sm font-medium underline decoration-dotted"
                        >
                            None of these look good? Search again.
                        </button>
                    ) : (
                        <div className="flex gap-2">
                            <input
                                type="text"
                                placeholder="E.g. Search in 78704 instead..."
                                className="flex-1 px-3 py-2 rounded-lg border border-slate-300 text-sm focus:outline-brand-500"
                                value={feedback}
                                onChange={(e) => setFeedback(e.target.value)}
                            />
                            <button
                                onClick={() => onRetry(feedback)}
                                className="bg-slate-800 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-slate-900"
                            >
                                Retry
                            </button>
                            <button onClick={() => setIsRetrying(false)} className="p-2 hover:bg-slate-100 rounded-lg">
                                <X className="w-4 h-4 text-slate-500" />
                            </button>
                        </div>
                    )}
                </div>

                {/* Approve Button */}
                <div className="flex items-center gap-4">
                    <span className="text-sm font-medium text-slate-600">
                        {selectedIds.length} selected
                    </span>
                    <button
                        disabled={selectedIds.length === 0}
                        onClick={() => onApprove(selectedIds)}
                        className="btn-primary px-8 py-3 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        Approve & Analyze
                    </button>
                </div>
            </div>
        </div>
    );
}
