import { Building2 } from 'lucide-react';

export function Header() {
    return (
        <nav className="fixed w-full top-0 z-50 bg-cream-50/80 backdrop-blur-md border-b border-brand-100 transition-all duration-300">
            <div className="container mx-auto px-6 h-20 flex items-center justify-between">
                <div className="flex items-center gap-3 group cursor-pointer">
                    <div className="w-10 h-10 bg-brand-800 rounded-xl flex items-center justify-center text-white shadow-soft group-hover:scale-105 transition-transform">
                        <Building2 className="w-6 h-6" />
                    </div>
                    <span className="text-xl font-serif font-bold text-brand-900 tracking-tight">Property Gemini</span>
                </div>

                <div className="hidden md:flex items-center gap-8">
                    <a href="#" className="text-sm font-medium text-brand-700 hover:text-brand-900 transition-colors">Features</a>
                    <a href="#" className="text-sm font-medium text-brand-700 hover:text-brand-900 transition-colors">How it Works</a>
                    <a href="#" className="text-sm font-medium text-brand-700 hover:text-brand-900 transition-colors">Pricing</a>
                </div>

                <div className="flex items-center gap-4">
                    <button className="text-sm font-medium text-brand-700 hover:text-brand-900 transition-colors">Sign In</button>
                    <button className="bg-brand-800 text-white px-5 py-2.5 rounded-full text-sm font-medium hover:bg-brand-900 transition-colors shadow-soft hover:shadow-lg">
                        Get Started
                    </button>
                </div>
            </div>
        </nav>
    );
}
