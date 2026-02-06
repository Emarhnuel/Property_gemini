import { Search, Map, Paintbrush, FileText, CheckCircle2 } from 'lucide-react';
import { motion } from 'framer-motion';

export function Features() {
    const features = [
        {
            icon: <Search className="w-6 h-6 text-brand-600" />,
            title: "Deep Market Scan",
            description: "Access validated listings from top platforms. Our anti-bot browsers extract real data where standard APIs fail."
        },
        {
            icon: <Map className="w-6 h-6 text-brand-600" />,
            title: "Hyper-Local Insights",
            description: "Know the neighborhood before you visit. We analyze 8 key amenities within a 6km radius of every property."
        },
        {
            icon: <Paintbrush className="w-6 h-6 text-brand-600" />,
            title: "Instant Redesigns",
            description: "Visualize potential. Toggle between 'Modern Minimalist', 'Scandi', and 'Industrial' styles instantly."
        },
        {
            icon: <FileText className="w-6 h-6 text-brand-600" />,
            title: "Investment Reports",
            description: "Export comprehensive PDFs with location grades, renovation estimates, and projected ROI."
        }
    ];

    return (
        <section id="features" className="py-24 bg-white">
            <div className="container mx-auto px-6">
                <div className="text-center mb-16">
                    <h2 className="text-3xl font-bold text-slate-900 mb-4 font-serif">Powering Smart Decisions</h2>
                    <p className="text-slate-500 max-w-2xl mx-auto">
                        From sourcing to visualization, our agent swarm gives you the competitive edge.
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                    {features.map((feature, index) => (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: index * 0.1, duration: 0.5 }}
                            className="p-6 rounded-2xl bg-slate-50 border border-slate-100 hover:shadow-lg hover:border-brand-200 transition-all duration-300 group"
                        >
                            <div className="w-12 h-12 bg-white rounded-xl shadow-sm flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                                {feature.icon}
                            </div>
                            <h3 className="text-lg font-bold text-slate-900 mb-3">{feature.title}</h3>
                            <p className="text-slate-600 text-sm leading-relaxed">
                                {feature.description}
                            </p>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}
