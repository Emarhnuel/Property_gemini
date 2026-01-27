import { ArrowRight, Sparkles, CheckCircle2 } from 'lucide-react';
import { motion } from 'framer-motion';

export function Hero() {
    return (
        <div className="relative w-full min-h-[700px] flex items-center justify-center overflow-hidden">
            {/* Background Illustration */}
            <div
                className="absolute inset-0 z-0 bg-nature-pattern bg-cover bg-bottom bg-no-repeat transform scale-105"
                style={{ backgroundPosition: 'center bottom' }}
            />

            {/* Gradient Overlay for Text Readability - Fade from Cream to Transparent */}
            <div className="absolute inset-0 z-10 bg-gradient-to-b from-cream-50/90 via-cream-50/50 to-transparent" />

            {/* Content */}
            <div className="container mx-auto px-6 relative z-20 pt-20 text-center">
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, ease: "easeOut" }}
                    className="max-w-4xl mx-auto"
                >
                    <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-brand-100 border border-brand-200 text-brand-700 text-sm font-semibold mb-8 shadow-sm">
                        <Sparkles className="w-4 h-4 text-gold-500" />
                        <span>AI-Powered Real Estate Intelligence</span>
                    </div>

                    <h1 className="text-5xl md:text-7xl font-bold text-brand-900 mb-6 tracking-tight leading-tight font-serif">
                        Raise the bar for every <br />
                        <span className="text-brand-600">property investment</span>
                    </h1>

                    <p className="text-xl text-brand-700 mb-10 max-w-2xl mx-auto leading-relaxed">
                        Stop guessing. Start knowing. Our autonomous agents analyze location data and generate redesign visualizations to reveal a property's true potential.
                    </p>

                    <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                        <button className="btn-primary flex items-center gap-2 group text-lg h-14 px-10">
                            Start Analysis
                            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                        </button>
                        <button className="btn-secondary text-lg h-14 px-10">
                            View Sample Report
                        </button>
                    </div>

                    <div className="mt-12 flex items-center justify-center gap-8 text-sm font-medium text-brand-600">
                        <div className="flex items-center gap-2">
                            <CheckCircle2 className="w-5 h-5 text-brand-500" />
                            <span>Deep Location Data</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <CheckCircle2 className="w-5 h-5 text-brand-500" />
                            <span>Generative Redesigns</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <CheckCircle2 className="w-5 h-5 text-brand-500" />
                            <span>Unified Reporting</span>
                        </div>
                    </div>
                </motion.div>
            </div>
        </div>
    );
}


