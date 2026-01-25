import React, { useState, useRef, useEffect } from 'react';
import { Loader2, ArrowLeftRight, Paintbrush } from 'lucide-react';

interface DesignComparisonProps {
    originalImage: string;
    redesignedImage: string;
    styleName: string;
    isGenerating?: boolean;
}

export function DesignComparison({ originalImage, redesignedImage, styleName, isGenerating }: DesignComparisonProps) {
    const [sliderPosition, setSliderPosition] = useState(50);
    const [isDragging, setIsDragging] = useState(false);
    const containerRef = useRef<HTMLDivElement>(null);

    const handleMove = (event: React.MouseEvent | React.TouchEvent) => {
        if (!isDragging || !containerRef.current) return;

        const { left, width } = containerRef.current.getBoundingClientRect();
        const pageX = 'touches' in event ? event.touches[0].pageX : event.pageX;
        const position = ((pageX - left) / width) * 100;

        setSliderPosition(Math.min(Math.max(position, 0), 100));
    };

    useEffect(() => {
        const handleUp = () => setIsDragging(false);
        window.addEventListener('mouseup', handleUp);
        window.addEventListener('touchend', handleUp);
        return () => {
            window.removeEventListener('mouseup', handleUp);
            window.removeEventListener('touchend', handleUp);
        };
    }, []);

    return (
        <div className="bg-white rounded-xl border border-slate-100 shadow-soft overflow-hidden">
            <div className="p-4 border-b border-slate-100 flex justify-between items-center bg-white z-10 relative">
                <div className="flex items-center gap-2">
                    <div className="bg-brand-100 p-2 rounded-lg">
                        <Paintbrush className="w-4 h-4 text-brand-600" />
                    </div>
                    <div>
                        <h3 className="font-bold text-slate-900 text-sm">AI Interior Redesign</h3>
                        <p className="text-xs text-slate-500">Style Applied: <span className="font-medium text-brand-600">{styleName}</span></p>
                    </div>
                </div>

                {isGenerating && (
                    <div className="flex items-center gap-2 text-xs font-medium text-brand-600 bg-brand-50 px-3 py-1 rounded-full">
                        <Loader2 className="w-3 h-3 animate-spin" />
                        Generative AI Processing...
                    </div>
                )}
            </div>

            <div
                ref={containerRef}
                className="relative aspect-video select-none cursor-ew-resize group"
                onMouseDown={() => setIsDragging(true)}
                onTouchStart={() => setIsDragging(true)}
                onMouseMove={handleMove}
                onTouchMove={handleMove}
            >
                {/* Original Image (Background) */}
                <img
                    src={originalImage}
                    alt="Original Room"
                    className="absolute inset-0 w-full h-full object-cover pointer-events-none"
                />

                <div className="absolute top-4 left-4 bg-black/50 backdrop-blur-md text-white px-3 py-1 rounded-full text-xs font-bold pointer-events-none">
                    Original
                </div>

                {/* Redesigned Image (Foreground / Clipped) */}
                <div
                    className="absolute inset-0 overflow-hidden pointer-events-none"
                    style={{ width: `${sliderPosition}%` }}
                >
                    <img
                        src={redesignedImage}
                        alt="AI Redesign"
                        className="absolute inset-0 w-full h-full object-cover"
                        style={{ width: '100vw', maxWidth: 'none' }} // Trick to keep image fixed while container shrinks
                    // Actually, cleaner way:
                    />
                    {/* We need the inner image to NOT shrink. 
                 The parent div width changes, masking the content. 
                 So inner image needs to be full width of the containerRef, not the parent div. 
                 Let's use a standard implementation pattern.
             */}
                </div>

                {/* Correction for the clipped image logic above */}
                <div
                    className="absolute inset-0 overflow-hidden pointer-events-none border-r-2 border-white/50"
                    style={{ clipPath: `inset(0 ${100 - sliderPosition}% 0 0)` }}
                >
                    <img
                        src={redesignedImage}
                        alt="AI Redesign"
                        className="absolute inset-0 w-full h-full object-cover"
                    />
                    <div className="absolute top-4 left-4 bg-brand-600/90 backdrop-blur-md text-white px-3 py-1 rounded-full text-xs font-bold">
                        AI Redesign
                    </div>
                </div>

                {/* Slider Handle */}
                <div
                    className="absolute top-0 bottom-0 w-1 bg-white cursor-ew-resize hover:shadow-glow transition-shadow"
                    style={{ left: `${sliderPosition}%` }}
                >
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-8 h-8 bg-white rounded-full shadow-lg flex items-center justify-center text-brand-600 group-hover:scale-110 transition-transform">
                        <ArrowLeftRight className="w-4 h-4" />
                    </div>
                </div>
            </div>
        </div>
    );
}
