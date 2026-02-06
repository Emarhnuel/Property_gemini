import { ScanSearch, MapPin, Palette, ShieldCheck, Zap, Brain } from 'lucide-react';
import { motion } from 'framer-motion';

export function HowItWorks() {
    const steps = [
        {
            icon: <ScanSearch className="w-8 h-8 text-gold-400" />,
            title: "Smart Scouting",
            description: "Our autonomous Crawl4AI agents patrol leading platforms using identity-protected browsers to find authentic listings.",
            detail: "Validated against spam & scams"
        },
        {
            icon: <MapPin className="w-8 h-8 text-gold-400" />,
            title: "Location Intelligence",
            description: "We compute precise driving times to 8 essential amenities (Gyms, Markets, Transit) within a 6km radius.",
            detail: "Google Maps API Integration"
        },
        {
            icon: <Palette className="w-8 h-8 text-gold-400" />,
            title: "Visionary Redesign",
            description: "Gemini Vision agents analyze room geometry to generate photorealistic quality renovation concepts.",
            detail: "Preserves structural dimensions"
        }
    ];

    return (
        <section id="how-it-works" className="py-24 bg-brand-900 relative overflow-hidden">
            {/* Background Decorative Elements */}
            <div className="absolute top-0 right-0 w-1/3 h-full bg-gradient-to-l from-brand-800/20 to-transparent pointer-events-none" />
            <div className="absolute bottom-0 left-0 w-1/4 h-1/2 bg-gradient-to-t from-brand-800/10 to-transparent pointer-events-none" />

            <div className="container mx-auto px-6 relative z-10">
                <div className="text-center mb-16">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-gold-400/10 border border-gold-400/20 text-gold-400 text-xs font-semibold uppercase tracking-wider mb-4">
                        <Brain className="w-3 h-3" />
                        <span>Autonomous Agent Workflow</span>
                    </div>
                    <h2 className="text-3xl md:text-4xl font-bold text-white mb-4 font-serif">
                        How Property Gemini Works
                    </h2>
                    <p className="text-brand-100 max-w-2xl mx-auto text-lg">
                        A coordinated swarm of AI agents handles the heavy lifting, from verification to visualization.
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {steps.map((step, index) => (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: index * 0.2, duration: 0.5 }}
                            className="bg-brand-800/40 backdrop-blur-sm border border-brand-700/50 rounded-2xl p-8 hover:bg-brand-800/60 transition-all duration-300 group"
                        >
                            <div className="bg-brand-900/50 w-16 h-16 rounded-xl flex items-center justify-center mb-6 border border-brand-700/50 group-hover:border-gold-400/30 group-hover:scale-110 transition-all duration-300 shadow-glow">
                                {step.icon}
                            </div>

                            <h3 className="text-xl font-bold text-white mb-3 font-serif">{step.title}</h3>
                            <p className="text-brand-200 mb-6 leading-relaxed">
                                {step.description}
                            </p>

                            <div className="flex items-center gap-2 text-xs font-medium text-gold-400/80 uppercase tracking-wide">
                                <ShieldCheck className="w-3 h-3" />
                                <span>{step.detail}</span>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}
