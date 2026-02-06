import { Building2 } from 'lucide-react';
import { Link, useNavigate, useLocation } from 'react-router-dom';

export function Header() {
    const navigate = useNavigate();
    const location = useLocation();

    const handleNavigation = (id: string) => {
        // If we represent the home page with '/', check if we are there
        if (location.pathname === '/') {
            document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
        } else {
            // Navigate to home and pass the ID to scroll to
            navigate('/', { state: { scrollTo: id } });
        }
    };

    return (
        <nav className="fixed w-full top-0 z-50 bg-cream-50/80 backdrop-blur-md border-b border-brand-100 transition-all duration-300">
            <div className="container mx-auto px-6 h-20 flex items-center justify-between">
                {/* Logo - Always links to Home */}
                <Link to="/" className="flex items-center gap-3 group cursor-pointer">
                    <div className="w-10 h-10 bg-brand-800 rounded-xl flex items-center justify-center text-white shadow-soft group-hover:scale-105 transition-transform">
                        <Building2 className="w-6 h-6" />
                    </div>
                    <span className="text-xl font-serif font-bold text-brand-900 tracking-tight">Property Gemini</span>
                </Link>

                <div className="hidden md:flex items-center gap-8 absolute left-1/2 -translate-x-1/2">
                    <button
                        onClick={() => handleNavigation('features')}
                        className="text-sm font-medium text-brand-700 hover:text-brand-900 transition-colors bg-transparent border-none cursor-pointer"
                    >
                        Features
                    </button>
                    <button
                        onClick={() => handleNavigation('how-it-works')}
                        className="text-sm font-medium text-brand-700 hover:text-brand-900 transition-colors bg-transparent border-none cursor-pointer"
                    >
                        How it Works
                    </button>
                    {/* Get Started - Always links to Analysis */}
                    <Link to="/analysis" className="text-sm font-bold text-brand-800 hover:text-gold-500 transition-colors border-b-2 border-gold-400">
                        Get Started
                    </Link>
                </div>

                <div className="w-24"></div>
            </div>
        </nav>
    );
}
