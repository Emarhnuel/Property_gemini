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
# FLOW STATE
# =========================

class RealEstateState(BaseModel):
    # --- User Inputs (Visible in AMP UI) ---
    location: str = "Ojodu, Lagos"
    property_type: str = "apartment"
    bedrooms: int = 2
    max_price: float = 3000000.0
    rent_frequency: str = "yearly"
    design_style_preference: str = "modern minimalist"

    # --- Internal State (Hidden from AMP UI) ---
    approved_property_ids: List[str] = Field(default=[], exclude=True)
    excluded_sites: List[str] = Field(default=[], exclude=True)

    retry_count: int = Field(default=0, exclude=True)
    user_feedback: Optional[str] = Field(default=None, exclude=True)

    research_results: Optional[str] = Field(default=None, exclude=True)
    location_results: Optional[str] = Field(default=None, exclude=True)
    design_results: Optional[str] = Field(default=None, exclude=True)

    properties_found: int = Field(default=0, exclude=True)
    properties_approved: int = Field(default=0, exclude=True)
    properties_analyzed: int = Field(default=0, exclude=True)
    rooms_redesigned: int = Field(default=0, exclude=True)


# =========================
# FLOW
# =========================

@persist()
class RealEstateFlow(Flow[RealEstateState]):

    @start()
    def initialize_search(self):
        """Initialize search from state (populated by kickoff inputs)."""

        print("\n🏠 AI Real Estate Agent - Find & Redesign")
        print("=" * 50)

        print(f"Location: {self.state.location}")
        print(f"Bedrooms: {self.state.bedrooms}")

    # -------------------------
    # PHASE 1 — RESEARCH
    # -------------------------

    @listen(initialize_search)
    def run_research_phase(self):

        search_query = f"{self.state.bedrooms or ''} bedroom {self.state.property_type} in {self.state.location}"
        if self.state.max_price:
            search_query += f" under {self.state.max_price}"
        search_query += f" ({self.state.rent_frequency} rent)"

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
            "search_criteria": {
                "location": self.state.location,
                "property_type": self.state.property_type,
                "bedrooms": self.state.bedrooms,
                "max_price": self.state.max_price,
                "rent_frequency": self.state.rent_frequency,
            },
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


def kickoff():
    """Run the flow."""
    RealEstateFlow().kickoff(inputs={
        "location": "Ojodu, Lagos",
        "property_type": "apartment, Flat",
        "bedrooms": 2,
        "max_price": 3000000.0,
        "rent_frequency": "yearly/annually",
        "design_style_preference": "modern minimalist",
    })


if __name__ == "__main__":
    kickoff()
