import { ArrowRight, Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';

export function Hero() {
    return (
        <div className="relative w-full min-h-[700px] flex items-center justify-center overflow-hidden">
            {/* Background Illustration */}
            <div
                className="absolute inset-0 z-0 bg-nature-pattern bg-cover bg-bottom bg-no-repeat transform scale-105"
                style={{ backgroundPosition: 'center bottom' }}
            />

            {/* Dark Gradient Overlay for Text Readability - Fade from Dark Green to Transparent */}
            <div className="absolute inset-0 z-10 bg-brand-900/60" />

            {/* Content */}
            <div className="container mx-auto px-6 relative z-20 pt-32 text-center">
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, ease: "easeOut" }}
                    className="max-w-4xl mx-auto"
                >
                    <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 backdrop-blur-md border border-white/20 text-white text-sm font-semibold mb-8 shadow-sm">
                        <Sparkles className="w-4 h-4 text-gold-400" />
                        <span>AI-Powered Real Estate Intelligence</span>
                    </div>

                    <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 tracking-tight leading-tight font-serif drop-shadow-sm">
                        Raise the bar for every <br />
                        <span className="text-gold-400">property investment</span>
                    </h1>

                    <p className="text-xl text-brand-50 mb-10 max-w-2xl mx-auto leading-relaxed drop-shadow-sm">
                        Stop guessing. Start knowing. Our autonomous agents analyze location data and generate redesign visualizations to reveal a property's true potential.
                    </p>



                    <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                        <Link to="/analysis" className="btn-primary flex items-center gap-2 group text-lg h-14 px-10 border border-transparent hover:scale-105 transform transition-all duration-200 shadow-glow">
                            Start Analysis
                            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                        </Link>
                    </div>
                </motion.div>

                {/* Logo Marquee - Moved outside max-w-4xl container to span full width */}
                <div className="mt-20 mb-12 w-screen relative left-[50%] -translate-x-[50%] overflow-hidden mask-linear-fade">
                    <p className="text-white/60 text-xs font-medium uppercase tracking-widest mb-6">Trusted by top agents at</p>
                    <div className="flex w-fit animate-marquee items-center gap-16 pl-[100%]">
                        {/* First Set */}
                        <span className="text-2xl font-bold text-white font-serif whitespace-nowrap">Zillow</span>
                        <span className="text-2xl font-bold text-white font-serif whitespace-nowrap">REMAX</span>
                        <span className="text-2xl font-bold text-white font-serif whitespace-nowrap">Compass</span>
                        <span className="text-2xl font-bold text-white font-serif whitespace-nowrap">Century 21</span>
                        <span className="text-2xl font-bold text-white font-serif whitespace-nowrap">Coldwell Banker</span>
                        <span className="text-2xl font-bold text-white font-serif whitespace-nowrap">Keller Williams</span>
                        <span className="text-2xl font-bold text-white font-serif whitespace-nowrap">Redfin</span>

                        {/* Duplicate Set for smooth loop */}
                        <span className="text-2xl font-bold text-white font-serif whitespace-nowrap">Zillow</span>
                        <span className="text-2xl font-bold text-white font-serif whitespace-nowrap">REMAX</span>
                        <span className="text-2xl font-bold text-white font-serif whitespace-nowrap">Compass</span>
                        <span className="text-2xl font-bold text-white font-serif whitespace-nowrap">Century 21</span>
                        <span className="text-2xl font-bold text-white font-serif whitespace-nowrap">Coldwell Banker</span>
                        <span className="text-2xl font-bold text-white font-serif whitespace-nowrap">Keller Williams</span>
                        <span className="text-2xl font-bold text-white font-serif whitespace-nowrap">Redfin</span>
                    </div>
                </div>
            </div>
        </div>
    );
}


