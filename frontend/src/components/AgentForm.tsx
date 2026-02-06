import { useState } from 'react';
import { Search, Loader2 } from 'lucide-react';
import type { SearchCriteria } from '../api/crewai';

interface AgentFormProps {
    onSubmit: (data: SearchCriteria) => void;
    isLoading: boolean;
}

export function AgentForm({ onSubmit, isLoading }: AgentFormProps) {
    const [formData, setFormData] = useState<SearchCriteria>({
        location: '',
        property_type: 'apartment',
        bedrooms: 2,
        bathrooms: 2,
        max_price: undefined,
        rent_frequency: 'yearly',
        additional_requirements: ''
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onSubmit(formData);
    };

    return (
        <div className="bg-white rounded-2xl shadow-xl p-8 border border-slate-100 max-w-2xl mx-auto">
            <div className="text-center mb-8">
                <h2 className="text-2xl font-bold text-slate-900 font-serif">Tell us what you're looking for</h2>
                <p className="text-slate-500">Our agents will scour the web to find your perfect match.</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
                {/* Location */}
                <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">Location / Area</label>
                    <div className="relative">
                        <Search className="absolute left-3 top-3 w-5 h-5 text-slate-400" />
                        <input
                            type="text"
                            required
                            placeholder="e.g. Austin Downtown, zip 78701"
                            className="w-full pl-10 pr-4 py-3 rounded-xl border border-slate-200 focus:border-brand-500 focus:ring-2 focus:ring-brand-200 outline-none transition-all"
                            value={formData.location}
                            onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                        />
                    </div>
                </div>

                {/* Type & Frequency Row */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-2">Property Type</label>
                        <select
                            className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-brand-500 focus:ring-2 focus:ring-brand-200 outline-none bg-white"
                            value={formData.property_type}
                            onChange={(e) => setFormData({ ...formData, property_type: e.target.value })}
                        >
                            <option value="apartment">Apartment</option>
                            <option value="house">House</option>
                            <option value="condo">Condo</option>
                            <option value="townhouse">Townhouse</option>
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-2">Rent Frequency</label>
                        <select
                            className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-brand-500 focus:ring-2 focus:ring-brand-200 outline-none bg-white"
                            value={formData.rent_frequency as string}
                            onChange={(e) => setFormData({ ...formData, rent_frequency: e.target.value as 'monthly' | 'yearly' })}
                        >
                            <option value="monthly">Monthly</option>
                            <option value="yearly">Yearly</option>
                        </select>
                    </div>
                </div>

                {/* Beds, Baths, Price Row */}
                <div className="grid grid-cols-3 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-2">Bedrooms</label>
                        <input
                            type="number"
                            min="0"
                            className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-brand-500 focus:ring-2 focus:ring-brand-200 outline-none"
                            value={formData.bedrooms || ''}
                            onChange={(e) => setFormData({ ...formData, bedrooms: parseInt(e.target.value) || 0 })}
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-2">Bathrooms</label>
                        <input
                            type="number"
                            min="0"
                            className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-brand-500 focus:ring-2 focus:ring-brand-200 outline-none"
                            value={formData.bathrooms || ''}
                            onChange={(e) => setFormData({ ...formData, bathrooms: parseInt(e.target.value) || 0 })}
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-2">Max Price</label>
                        <input
                            type="number"
                            placeholder="No Limit"
                            className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-brand-500 focus:ring-2 focus:ring-brand-200 outline-none"
                            value={formData.max_price || ''}
                            onChange={(e) => setFormData({ ...formData, max_price: parseInt(e.target.value) || undefined })}
                        />
                    </div>
                </div>

                {/* Additional Req */}
                <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">Additional Requirements</label>
                    <textarea
                        placeholder="e.g. Must have a balcony, pet friendly, near a park..."
                        className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-brand-500 focus:ring-2 focus:ring-brand-200 outline-none h-24 resize-none"
                        value={formData.additional_requirements}
                        onChange={(e) => setFormData({ ...formData, additional_requirements: e.target.value })}
                    />
                </div>

                <button
                    type="submit"
                    disabled={isLoading}
                    className="w-full btn-primary py-4 text-lg font-bold shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all duration-300 flex items-center justify-center gap-2 "
                >
                    {isLoading ? (
                        <>
                            <Loader2 className="w-5 h-5 animate-spin" />
                            Initializing Agents...
                        </>
                    ) : (
                        'Deploy Agents'
                    )}
                </button>
            </form>
        </div>
    );
}
