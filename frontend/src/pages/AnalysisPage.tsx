import { useState, useEffect } from 'react';
import { Header } from '../components/Header';
import { AgentForm } from '../components/AgentForm';
import { PropertySelector } from '../components/PropertySelector';
// import { LocationAnalysis } from '../components/LocationAnalysis'; 
// import { DesignComparison } from '../components/DesignComparison'; 
import { crewAiApi } from '../api/crewai';
import type { SearchCriteria } from '../api/crewai';
import { Brain, ScanSearch, CheckCircle2, AlertCircle } from 'lucide-react';

type PageState = 'IDLE' | 'STARTING' | 'RESEARCHING' | 'WAITING_USER_INPUT' | 'ANALYZING' | 'COMPLETED' | 'ERROR';

export function AnalysisPage() {
    const [pageState, setPageState] = useState<PageState>('IDLE');
    const [kickoffId, setKickoffId] = useState<string | null>(null);
    const [researchResults, setResearchResults] = useState<any[]>([]); // Properties found
    const [finalResults, setFinalResults] = useState<any>(null); // Location & Design results
    const [errorMessage, setErrorMessage] = useState('');

    // --- Actions ---

    const handleStart = async (criteria: SearchCriteria) => {
        try {
            setPageState('STARTING');
            const result = await crewAiApi.startFlow(criteria);
            if (result.kickoff_id) {
                setKickoffId(result.kickoff_id);
                setPageState('RESEARCHING');
            } else {
                throw new Error("Failed to get kickoff ID");
            }
        } catch (err: any) {
            setPageState('ERROR');
            setErrorMessage(err.message || "Failed to start agents");
        }
    };

    const handleApproval = async (selectedIds: string[]) => {
        if (!kickoffId) return;
        try {
            // Format for backend: JSON array string
            // Assuming main.py expects JSON string of IDs
            await crewAiApi.submitFeedback(kickoffId, JSON.stringify(selectedIds));
            setPageState('ANALYZING'); // Flow resumes for Location/Design phases
        } catch (err: any) {
            setErrorMessage(err.message || "Failed to submit feedback");
        }
    };

    const handleRetry = async (feedback: string) => {
        if (!kickoffId) return;
        try {
            // Sending 'retry' logic if backend supports it via same endpoint
            // Note: The @human_feedback decorator usually handles routing based on "emit" values
            // For now, simpler implementation: just send feedback, backend routing handles "retry" vs "approved" based on content analysis
            // Or if we specifically need to trigger "retry" emit, we might need to adjust message content
            await crewAiApi.submitFeedback(kickoffId, `retry: ${feedback}`);
            setPageState('RESEARCHING'); // Back to research state
        } catch (err: any) {
            setErrorMessage(err.message || "Failed to retry");
        }
    };


    // --- Polling Effect ---
    useEffect(() => {
        let intervalId: ReturnType<typeof setInterval>;

        const checkStatus = async () => {
            if (!kickoffId || (pageState !== 'RESEARCHING' && pageState !== 'ANALYZING')) return;

            try {
                const statusData = await crewAiApi.getFlowStatus(kickoffId);

                // 1. Check if waiting for feedback (Research Complete)
                if (statusData.status === 'WAITING_INPUT') {
                    // Fetch the intermediate results (Research Output)
                    // The backend status/result object should ideally contain the last step's output
                    // For now, assuming result field holds the interim data or we need a specific way to get it.
                    // If flow state persists, we can access flow.state.research_results via a getter if exposed.

                    // Fallback: If result is present in status payload
                    if (statusData.result) {
                        // Parse properties from result string/json
                        try {
                            const parsed = typeof statusData.result === 'string' ? JSON.parse(statusData.result) : statusData.result;
                            const properties = parsed.properties || parsed.listings || [];
                            setResearchResults(properties);
                        } catch (e) {
                            console.error("Failed to parse research results", e);
                        }
                    }
                    setPageState('WAITING_USER_INPUT');
                }

                // 2. Check for completion (Analysis Complete)
                if (statusData.status === 'COMPLETED') {
                    setFinalResults(statusData.result);
                    setPageState('COMPLETED');
                }

                // 3. Check for failure
                if (statusData.status === 'FAILED') {
                    setPageState('ERROR');
                    setErrorMessage("Workflow execution failed.");
                }

            } catch (err) {
                console.error("Polling error", err);
                // Don't stop polling immediately on one error, maybe network blip
            }
        };

        if (kickoffId && (pageState === 'RESEARCHING' || pageState === 'ANALYZING')) {
            intervalId = setInterval(checkStatus, 3000); // Poll every 3s
        }

        return () => clearInterval(intervalId);
    }, [kickoffId, pageState]);


    // --- Render Helpers ---

    return (
        <div className="min-h-screen bg-slate-50 selection:bg-brand-100 selection:text-brand-900">
            <Header />

            <main className="container mx-auto px-6 pt-32 pb-20">

                {/* IDLE: Show Form */}
                {pageState === 'IDLE' && (
                    <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                        <AgentForm onSubmit={handleStart} isLoading={false} />
                    </div>
                )}

                {/* STARTING / RESEARCHING: Show Loading */}
                {(pageState === 'STARTING' || pageState === 'RESEARCHING') && (
                    <div className="max-w-xl mx-auto text-center animate-in fade-in duration-500">
                        <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center mx-auto mb-8 shadow-xl relative">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand-400 opacity-20"></span>
                            <ScanSearch className="w-10 h-10 text-brand-600 animate-pulse" />
                        </div>
                        <h2 className="text-2xl font-bold text-slate-900 mb-4">Agents are researching...</h2>
                        <p className="text-slate-500">
                            Our Crawl4AI swarm is scanning listing sites. This usually takes 1-2 minutes.
                            We are verifying data against anti-bot protections.
                        </p>
                    </div>
                )}

                {/* WAITING_USER_INPUT: Show Selector */}
                {pageState === 'WAITING_USER_INPUT' && (
                    <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                        <PropertySelector
                            properties={researchResults}
                            onApprove={handleApproval}
                            onRetry={handleRetry}
                        />
                    </div>
                )}

                {/* ANALYZING: Show Loading 2 */}
                {pageState === 'ANALYZING' && (
                    <div className="max-w-xl mx-auto text-center animate-in fade-in duration-500">
                        <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center mx-auto mb-8 shadow-xl relative">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-gold-400 opacity-20"></span>
                            <Brain className="w-10 h-10 text-gold-500 animate-pulse" />
                        </div>
                        <h2 className="text-2xl font-bold text-slate-900 mb-4">Deep Analysis in Progress</h2>
                        <p className="text-slate-500">
                            Location Agents are calculating amenity distances.<br />
                            Design Agents are generating renovation concepts.
                        </p>
                    </div>
                )}

                {/* COMPLETED: Show Results */}
                {pageState === 'COMPLETED' && (
                    <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                        <div className="text-center mb-12">
                            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-green-100 text-green-700 font-bold mb-4">
                                <CheckCircle2 className="w-5 h-5" />
                                Analysis Complete
                            </div>
                            <h2 className="text-3xl font-bold text-slate-900 font-serif">Your Intelligence Report</h2>
                        </div>

                        {/* 
                          Ideally we render the full unified report here via property cards 
                          with tabs for 'Location' and 'Design'.
                          For MVP, dumping raw result or simple structure.
                        */}
                        <div className="prose max-w-none bg-white p-8 rounded-2xl shadow-sm border border-slate-100">
                            <pre className="text-xs bg-slate-900 text-slate-50 p-6 rounded-xl overflow-x-auto">
                                {JSON.stringify(finalResults, null, 2)}
                            </pre>
                            <div className="mt-8 text-center">
                                <button
                                    onClick={() => setPageState('IDLE')}
                                    className="btn-primary"
                                >
                                    Start New Search
                                </button>
                            </div>
                        </div>
                    </div>
                )}


                {/* ERROR STATE */}
                {pageState === 'ERROR' && (
                    <div className="max-w-md mx-auto text-center animate-in fade-in duration-500">
                        <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-6" />
                        <h2 className="text-xl font-bold text-slate-900 mb-2">Something went wrong</h2>
                        <p className="text-slate-500 mb-8">{errorMessage}</p>
                        <button
                            onClick={() => setPageState('IDLE')}
                            className="bg-slate-900 text-white px-6 py-3 rounded-xl font-bold hover:scale-105 transition-transform"
                        >
                            Try Again
                        </button>
                    </div>
                )}

            </main>
        </div>
    );
}
