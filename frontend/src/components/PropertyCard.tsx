import { MapPin, BedDouble, Bath, Square, Sparkles, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';

export interface Property {
    id: string;
    title: string;
    price: string;
    address: string;
    specs: {
        beds: number;
        baths: number;
        sqft: number;
    };
    image: string;
    rating: number; // 0-100
    tags: string[];
}

interface PropertyCardProps {
    property: Property;
    index: number;
    onSelect: (id: string) => void;
}

export function PropertyCard({ property, index, onSelect }: PropertyCardProps) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="card group cursor-pointer hover:border-brand-300 bg-cream-100 border-none"
            onClick={() => onSelect(property.id)}
        >
            <div className="relative aspect-[4/3] rounded-xl overflow-hidden mb-4 bg-brand-50">
                <img
                    src={property.image}
                    alt={property.title}
                    className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
                />

                <div className="absolute top-3 right-3 bg-cream-50/95 backdrop-blur-md px-3 py-1.5 rounded-full text-xs font-bold text-brand-800 shadow-sm flex items-center gap-1 border border-brand-100">
                    <Sparkles className="w-3 h-3 text-gold-500" />
                    Score: {property.rating}
                </div>
            </div>

            <div className="space-y-4 px-2">
                <div>
                    <div className="flex justify-between items-start mb-1">
                        <h3 className="font-serif font-bold text-lg text-brand-900 line-clamp-1 group-hover:text-brand-600 transition-colors">
                            {property.title}
                        </h3>
                        <span className="font-bold text-brand-700 whitespace-nowrap bg-brand-50 px-2 py-1 rounded-md text-sm">{property.price}</span>
                    </div>

                    <div className="flex items-center text-brand-500 text-sm">
                        <MapPin className="w-4 h-4 mr-1" />
                        <span className="line-clamp-1">{property.address}</span>
                    </div>
                </div>

                <div className="flex items-center justify-between py-3 border-t border-brand-100/50">
                    <div className="flex items-center gap-1 text-brand-600 text-sm font-medium">
                        <BedDouble className="w-4 h-4 text-brand-400" />
                        <span>{property.specs.beds} Beds</span>
                    </div>
                    <div className="flex items-center gap-1 text-brand-600 text-sm font-medium">
                        <Bath className="w-4 h-4 text-brand-400" />
                        <span>{property.specs.baths} Baths</span>
                    </div>
                    <div className="flex items-center gap-1 text-brand-600 text-sm font-medium">
                        <Square className="w-4 h-4 text-brand-400" />
                        <span>{property.specs.sqft} sqft</span>
                    </div>
                </div>

                <button className="w-full btn-secondary py-2.5 text-sm flex items-center justify-center gap-2 group-hover:bg-brand-900 group-hover:text-white group-hover:border-brand-900 transition-all">
                    View Analysis
                    <ArrowRight className="w-4 h-4" />
                </button>
            </div>
        </motion.div>
    );
}
