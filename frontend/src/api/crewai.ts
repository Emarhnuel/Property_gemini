import axios from 'axios';

// Environment variables should be set in .env.local
const API_BASE_URL = import.meta.env.VITE_CREW_API_BASE_URL || 'http://localhost:8000'; // Default for local dev
const API_KEY = import.meta.env.VITE_CREW_API_KEY;

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Authorization': `Bearer ${API_KEY}`,
        'Content-Type': 'application/json',
    },
});

export interface SearchCriteria {
    location: string;
    property_type: string;
    bedrooms?: number;
    bathrooms?: number;
    max_price?: number;
    rent_frequency: 'monthly' | 'yearly';
    additional_requirements?: string;
}

export interface FlowStatus {
    execution_id: string;
    status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'WAITING_INPUT';
    result?: any;
    current_step?: string;
    last_feedback_request?: string; // Message from the agent
}

export const crewAiApi = {
    // Start the flow
    startFlow: async (criteria: SearchCriteria) => {
        // Mapping frontend criteria to the payload expected by main.py's initialize_search
        const payload = {
            inputs: {
                search_criteria: criteria,
                design_style: "modern minimalist" // Default, can be expanded later
            }
        };
        const response = await api.post('/kickoff', payload);
        return response.data; // Expected: { kick_off_id: "..." }
    },

    // Get Flow Status
    getFlowStatus: async (kickoffId: string): Promise<FlowStatus> => {
        const response = await api.get(`/status/${kickoffId}`);
        return response.data;
    },

    // Submit Human Feedback
    submitFeedback: async (kickoffId: string, feedback: any) => {
        // Feedback format depends on what @human_feedback expects.
        // In main.py: emit=["approved", "retry"]
        // If approved, it expects JSON array of IDs.
        const response = await api.post(`/feedback/${kickoffId}`, { feedback });
        return response.data;
    }
};
