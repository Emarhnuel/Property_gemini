#!/usr/bin/env python
"""
AI Real Estate Agent - API Flow (AMP-safe)

This flow is fully automated and API-triggerable.
NO human-in-the-loop.
Designed to expose an API URL in CrewAI AMP.
"""

import json
from typing import Optional, List
from pydantic import BaseModel, Field

from crewai.flow.flow import Flow, start, listen
from crewai.flow.persistence import persist

from real_ai_agents.crews.research_crew.research_crew import ResearchCrew
from real_ai_agents.crews.location_analyzer_crew.location_analyzer_crew import LocationAnalyzerCrew
from real_ai_agents.crews.interior_design_crew.interior_design_crew import InteriorDesignCrew


# =======================
# INPUT MODELS (API SAFE)
# =======================

class SearchCriteria(BaseModel):
    location: str
    property_type: str = "apartment"
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    max_price: Optional[float] = None
    rent_frequency: str = "monthly"
    additional_requirements: Optional[str] = None


class ApiInput(BaseModel):
    search_criteria: SearchCriteria
    design_style: str = "modern minimalist"


# =======================
# STATE
# =======================

class RealEstateApiState(BaseModel):
    search_criteria: Optional[SearchCriteria] = None
    design_style: str = "modern minimalist"

    research_results: Optional[str] = None
    location_results: Optional[str] = None
    design_results: Optional[str] = None

    properties_found: int = 0
    properties_analyzed: int = 0
    rooms_redesigned: int = 0


# =======================
# FLOW (API ENABLED)
# =======================

@persist()
class RealEstateApiFlow(Flow[RealEstateApiState]):
    """
    Fully automated API Flow.
    This is what AMP exposes as an HTTP endpoint.
    """

    @start()
    def initialize(self, crewai_trigger_payload: dict):
        """
        Entry point for API calls.
        """
        payload = ApiInput(**crewai_trigger_payload)

        self.state.search_criteria = payload.search_criteria
        self.state.design_style = payload.design_style

        return payload.model_dump()

    @listen(initialize)
    def run_research(self):
        criteria = self.state.search_criteria

        search_query = (
            f"{criteria.bedrooms or ''} bedroom "
            f"{criteria.property_type} in {criteria.location}"
        )

        if criteria.max_price:
            search_query += f" under {criteria.max_price}"

        search_query += f" ({criteria.rent_frequency} rent)"

        result = ResearchCrew().crew().kickoff(
            inputs={"search_criteria": search_query.strip()}
        )

        self.state.research_results = result.raw

        try:
            data = json.loads(result.raw)
            if "properties" in data:
                self.state.properties_found = len(data["properties"])
            elif "listings" in data:
                self.state.properties_found = len(data["listings"])
        except Exception:
            pass

        return self.state.research_results

    @listen(run_research)
    def run_location_and_design(self):
        """
        Fully automated downstream analysis.
        """
        inputs = {
            "research_results": self.state.research_results,
            "design_style": self.state.design_style,
        }

        location_result = LocationAnalyzerCrew().crew().kickoff(inputs=inputs)
        design_result = InteriorDesignCrew().crew().kickoff(inputs=inputs)

        self.state.location_results = location_result.raw
        self.state.design_results = design_result.raw

        self.state.properties_analyzed = self.state.properties_found

        try:
            design_data = json.loads(design_result.raw)
            self.state.rooms_redesigned = (
                design_data.get("metadata", {}).get("total_rooms_redesigned", 0)
            )
        except Exception:
            pass

    @listen(run_location_and_design)
    def finalize(self):
        """
        Final API response.
        """
        return {
            "search_criteria": self.state.search_criteria.model_dump(),
            "summary": {
                "properties_found": self.state.properties_found,
                "properties_analyzed": self.state.properties_analyzed,
                "rooms_redesigned": self.state.rooms_redesigned,
            },
            "results": {
                "research": self.state.research_results,
                "location": self.state.location_results,
                "design": self.state.design_results,
            },
        }


# =======================
# LOCAL RUN (OPTIONAL)
# =======================

def kickoff():
    RealEstateApiFlow().kickoff(
        inputs={
            "search_criteria": {
                "location": "Ojodu, Lagos, Nigeria",
                "property_type": "apartment",
                "bedrooms": 2,
                "max_price": 3000000,
                "rent_frequency": "yearly",
            },
            "design_style": "modern minimalist",
        }
    )


if __name__ == "__main__":
    kickoff()
