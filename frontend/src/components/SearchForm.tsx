import React, { useState } from 'react';
import { Search, Home, DollarSign, MapPin } from 'lucide-react';
import { motion } from 'framer-motion';

interface SearchCriteria {
    location: string;
    property_type: string;
    max_price: number | '';
    bedrooms: number | '';
}

interface SearchFormProps {
    onSearch: (criteria: SearchCriteria) => void;
    isLoading: boolean;
}

export function SearchForm({ onSearch, isLoading }: SearchFormProps) {
    const [criteria, setCriteria] = useState<SearchCriteria>({
        location: '',
        property_type: 'apartment',
        max_price: '',
        bedrooms: ''
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onSearch(criteria);
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-2xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-brand-100 p-8 max-w-4xl mx-auto -mt-24 relative z-20 backdrop-blur-sm bg-white/95"
        >
            <form onSubmit={handleSubmit}>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <div className="md:col-span-1 space-y-2">
                        <label className="text-xs font-bold uppercase text-brand-400 tracking-wider">Location</label>
                        <div className="relative">
                            <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-brand-300" />
                            <input
                                type="text"
                                placeholder="City or Area"
                                className="w-full pl-10 pr-4 py-3 bg-brand-50/50 border border-brand-100 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500 focus:bg-white transition-all text-brand-900 placeholder:text-brand-300 font-medium"
                                value={criteria.location}
                                onChange={(e) => setCriteria({ ...criteria, location: e.target.value })}
                                required
                            />
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label className="text-xs font-bold uppercase text-brand-400 tracking-wider">Type</label>
                        <div className="relative">
                            <Home className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-brand-300" />
                            <select
                                className="w-full pl-10 pr-4 py-3 bg-brand-50/50 border border-brand-100 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500 focus:bg-white transition-all text-brand-900 appearance-none font-medium"
                                value={criteria.property_type}
                                onChange={(e) => setCriteria({ ...criteria, property_type: e.target.value })}
                            >
                                <option value="apartment">Apartment</option>
                                <option value="house">House</option>
                                <option value="condo">Condo</option>
                                <option value="villa">Villa</option>
                            </select>
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label className="text-xs font-bold uppercase text-brand-400 tracking-wider">Budget</label>
                        <div className="relative">
                            <DollarSign className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-brand-300" />
                            <input
                                type="number"
                                placeholder="Max Price"
                                className="w-full pl-10 pr-4 py-3 bg-brand-50/50 border border-brand-100 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500 focus:bg-white transition-all text-brand-900 placeholder:text-brand-300 font-medium"
                                value={criteria.max_price}
                                onChange={(e) => setCriteria({ ...criteria, max_price: Number(e.target.value) || '' })}
                            />
                        </div>
                    </div>

                    <div className="flex items-end">
                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full btn-primary h-[50px] flex items-center justify-center gap-2"
                        >
                            {isLoading ? (
                                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                            ) : (
                                <>
                                    <Search className="w-5 h-5" />
                                    <span>Search</span>
                                </>
                            )}
                        </button>
                    </div>
                </div>
            </form>
        </motion.div>
    );
}
