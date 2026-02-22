#!/usr/bin/env python
"""
AI Real Estate Agent Flow - Find & Redesign
AMP-Optimized Input Version
"""

import json
import asyncio
from typing import List, Optional
from pydantic import BaseModel, Field

from crewai.flow.flow import Flow, listen, start
from crewai.flow.persistence import persist
from crewai.flow.human_feedback import human_feedback, HumanFeedbackResult

from real_ai_agents.crews.research_crew.research_crew import ResearchCrew
from real_ai_agents.crews.location_analyzer_crew.location_analyzer_crew import LocationAnalyzerCrew
from real_ai_agents.crews.interior_design_crew.interior_design_crew import InteriorDesignCrew


# =========================
# INPUT MODELS
# =========================

class SearchCriteria(BaseModel):
    location: str
    property_type: str = "apartment"
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    max_price: Optional[float] = None
    rent_frequency: str = "monthly"
    additional_requirements: Optional[str] = None


# =========================
# FLOW STATE (INTERNAL)
# =========================

class RealEstateState(BaseModel):
    search_criteria: Optional[SearchCriteria] = None
    design_style_preference: str = "modern minimalist"

    approved_property_ids: List[str] = []
    excluded_sites: List[str] = []

    retry_count: int = 0
    user_feedback: Optional[str] = None

    research_results: Optional[str] = None
    filtered_research_results: Optional[str] = None
    location_results: Optional[str] = None
    design_results: Optional[str] = None

    properties_found: int = 0
    properties_approved: int = 0
    properties_analyzed: int = 0
    rooms_redesigned: int = 0


# =========================
# FLOW
# =========================

@persist
class RealEstateFlow(Flow[SearchCriteria]):

    # ✅ AMP will now only ask for these two inputs
    @start()
    def initialize_search(
        self,
        search_criteria: SearchCriteria,
        design_style: str = "modern minimalist",
    ):
        """Initialize search from AMP input."""

        print("\n🏠 AI Real Estate Agent - Find & Redesign")
        print("=" * 50)

        self.state.search_criteria = search_criteria
        self.state.design_style_preference = design_style

        print(f"Location: {search_criteria.location}")
        print(f"Bedrooms: {search_criteria.bedrooms}")

    # -------------------------
    # PHASE 1 — RESEARCH
    # -------------------------

    @listen(initialize_search)
    def run_research_phase(self):

        criteria = self.state.search_criteria

        search_query = f"{criteria.bedrooms or ''} bedroom {criteria.property_type} in {criteria.location}"
        if criteria.max_price:
            search_query += f" under {criteria.max_price}"
        search_query += f" ({criteria.rent_frequency} rent)"

        result = ResearchCrew().crew().kickoff(inputs={
            "search_criteria": search_query.strip(),
            "excluded_sites": self.state.excluded_sites
        })

        self.state.research_results = result.raw

        try:
            data = json.loads(result.raw)
            key = "properties" if "properties" in data else "listings"
            if key in data:
                self.state.properties_found = len(data[key])
        except:
            pass

        print(f"Found {self.state.properties_found} properties")
        return self.state.research_results

    # -------------------------
    # HUMAN APPROVAL
    # -------------------------

    @listen(run_research_phase)
    @human_feedback(
        message="Select property IDs to proceed (e.g. ['prop_001']). Or type 'retry'.",
        emit=["approved", "retry"],
        llm="gemini/gemini-3-flash-preview",
        default_outcome="approved",
    )
    def await_property_approval(self):
        return self.state.research_results

    @listen("approved")
    def filter_approved_properties(self, result: HumanFeedbackResult):

        try:
            approved_ids = json.loads(result.feedback)
            self.state.approved_property_ids = approved_ids
        except:
            self.state.approved_property_ids = []

        try:
            data = json.loads(self.state.research_results)
            key = "properties" if "properties" in data else "listings"
            if key in data:
                data[key] = [
                    p for p in data[key]
                    if p.get("id") in self.state.approved_property_ids
                ]
                self.state.properties_approved = len(data[key])

            self.state.filtered_research_results = json.dumps(data)
        except:
            self.state.filtered_research_results = self.state.research_results

    @listen("retry")
    def handle_retry_search(self, result: HumanFeedbackResult):
        self.state.retry_count += 1
        self.state.user_feedback = result.feedback
        return self.run_research_phase()

    # -------------------------
    # PHASE 2 — PARALLEL
    # -------------------------

    @listen(filter_approved_properties)
    async def run_parallel_action_phase(self):

        if self.state.properties_approved == 0:
            return

        inputs = {
            "research_results": self.state.filtered_research_results,
            "design_style": self.state.design_style_preference
        }

        location_task = asyncio.create_task(
            LocationAnalyzerCrew().crew().kickoff_async(inputs=inputs)
        )

        design_task = asyncio.create_task(
            InteriorDesignCrew().crew().kickoff_async(inputs=inputs)
        )

        location_result, design_result = await asyncio.gather(
            location_task,
            design_task
        )

        self.state.location_results = location_result.raw
        self.state.design_results = design_result.raw

        self.state.properties_analyzed = self.state.properties_approved

        try:
            design_data = json.loads(design_result.raw)
            self.state.rooms_redesigned = design_data.get(
                "metadata", {}
            ).get("total_rooms_redesigned", 0)
        except:
            pass

    # -------------------------
    # FINAL REPORT
    # -------------------------

    @listen(run_parallel_action_phase)
    def compile_final_report(self):

        final_report = {
            "search_criteria": self.state.search_criteria.model_dump(),
            "summary": {
                "properties_found": self.state.properties_found,
                "properties_approved": self.state.properties_approved,
                "properties_analyzed": self.state.properties_analyzed,
                "rooms_redesigned": self.state.rooms_redesigned,
            },
            "approved_property_ids": self.state.approved_property_ids,
            "phases": {
                "research": self.state.research_results,
                "location": self.state.location_results,
                "design": self.state.design_results,
            },
        }

        with open("output/unified_report.json", "w") as f:
            json.dump(final_report, f, indent=2)

        print("Flow Complete")
        return final_report


