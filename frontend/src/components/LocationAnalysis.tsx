import { motion } from 'framer-motion';
import { MapPin, ShoppingCart, Plane, Train, Dumbbell } from 'lucide-react';

interface LocationAnalysisProps {
    score: number;
    grade: 'A' | 'B' | 'C' | 'D';
    amenities: {
        category: string;
        score: number; // 0-100
        distance: string;
        count: number;
    }[];
}

const getIcon = (category: string) => {
    switch (category.toLowerCase()) {
        case 'markets': return <ShoppingCart className="w-4 h-4" />;
        case 'airports': return <Plane className="w-4 h-4" />;
        case 'transit': return <Train className="w-4 h-4" />;
        case 'gyms': return <Dumbbell className="w-4 h-4" />;
        default: return <MapPin className="w-4 h-4" />;
    }
};

export function LocationAnalysis({ score, grade, amenities }: LocationAnalysisProps) {
    return (
        <div className="bg-white rounded-xl border border-slate-100 shadow-soft p-6">
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h3 className="text-lg font-bold text-slate-900">Location Intelligence</h3>
                    <p className="text-sm text-slate-500">AI-analyzed proximity scores</p>
                </div>

                <div className="flex items-center gap-4">
                    <div className="text-right">
                        <div className="text-3xl font-bold text-brand-600">{score}</div>
                        <div className="text-xs font-bold text-brand-400 uppercase tracking-wider">Overall</div>
                    </div>
                    <div className="w-12 h-12 bg-slate-900 rounded-lg flex items-center justify-center text-white text-xl font-bold shadow-lg">
                        {grade}
                    </div>
                </div>
            </div>

            <div className="space-y-6">
                {amenities.map((item, index) => (
                    <div key={item.category}>
                        <div className="flex justify-between items-center mb-2 text-sm">
                            <div className="flex items-center gap-2 text-slate-700 font-medium capitalize">
                                {getIcon(item.category)}
                                {item.category.replace('_', ' ')}
                            </div>
                            <div className="text-slate-500">
                                <span className="font-bold text-slate-900">{item.distance}</span> • {item.count} nearby
                            </div>
                        </div>
                        <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                            <motion.div
                                initial={{ width: 0 }}
                                whileInView={{ width: `${item.score}%` }}
                                transition={{ duration: 1, delay: index * 0.1 }}
                                className={`h-full rounded-full ${item.score > 80 ? 'bg-green-500' :
                                    item.score > 50 ? 'bg-brand-500' : 'bg-orange-400'
                                    }`}
                            />
                        </div>
                    </div>
                ))}
            </div>

            <div className="mt-8 pt-6 border-t border-slate-100">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">AI Summary</h4>
                <p className="text-sm text-slate-600 leading-relaxed">
                    This property has <strong className="text-slate-900">excellent walkability</strong> with
                    grocery stores and transit within 5 minutes. The commute to the airport is optimal (20 mins).
                    However, entertainment options are <span className="text-orange-500 font-medium">limited within 2km</span>.
                </p>
            </div>
        </div>
    );
}
