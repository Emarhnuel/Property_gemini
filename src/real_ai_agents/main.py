#!/usr/bin/env python
"""
AI Real Estate Agent Flow - Find & Redesign

Orchestrates the real estate workflow with human-in-the-loop:
1. Research Phase - Find properties matching search criteria
2. Human Approval - User selects which properties to proceed with
3. Location Phase - Analyze neighborhood amenities
4. Design Phase - Generate AI-powered room redesigns
"""

import json
from typing import List, Optional
from pydantic import BaseModel, Field

from crewai.flow.flow import Flow, listen, start, and_
from crewai.flow.human_feedback import human_feedback, HumanFeedbackResult

from src.real_ai_agents.crews.research_crew.research_crew import ResearchCrew
from src.real_ai_agents.crews.location_analyzer_crew.location_analyzer_crew import LocationAnalyzerCrew
from src.real_ai_agents.crews.interior_design_crew.interior_design_crew import InteriorDesignCrew


class SearchCriteria(BaseModel):
    """User search criteria for property discovery."""
    location: str = Field(description="City, neighborhood, or area to search")
    property_type: str = Field(default="apartment", description="Type: apartment, house, condo, etc.")
    bedrooms: Optional[int] = Field(default=None, description="Number of bedrooms")
    bathrooms: Optional[int] = Field(default=None, description="Number of bathrooms")
    max_price: Optional[float] = Field(default=None, description="Maximum price/rent")
    additional_requirements: Optional[str] = Field(default=None, description="Other requirements")


class RealEstateState(BaseModel):
    """State model for the Real Estate Agent Flow."""
    search_criteria: Optional[SearchCriteria] = None
    design_style_preference: str = "modern minimalist"
    approved_property_ids: List[str] = Field(default_factory=list)
    research_results: Optional[str] = None
    filtered_research_results: Optional[str] = None
    location_results: Optional[str] = None
    design_results: Optional[str] = None
    properties_found: int = 0
    properties_approved: int = 0
    properties_analyzed: int = 0
    rooms_redesigned: int = 0


@persist
class RealEstateFlow(Flow[RealEstateState]):
    """AI Real Estate Agent Flow with human-in-the-loop property approval."""

    @start()
    def initialize_search(self, crewai_trigger_payload: dict = None):
        """Initialize the flow with search criteria."""
        print("\n" + "=" * 60)
        print("🏠 AI Real Estate Agent - Find & Redesign")
        print("=" * 60)
        
        if crewai_trigger_payload:
            self.state.search_criteria = SearchCriteria(**crewai_trigger_payload.get("search_criteria", {}))
            self.state.design_style_preference = crewai_trigger_payload.get("design_style", "modern minimalist")
        else:
            self.state.search_criteria = SearchCriteria(
                location="Lagos, Nigeria",
                property_type="apartment",
                bedrooms=2,
                max_price=500000
            )
        
        print(f"   Location: {self.state.search_criteria.location}")
        print(f"   Bedrooms: {self.state.search_criteria.bedrooms}")
        print("-" * 60)

    @listen(initialize_search)
    def run_research_phase(self):
        """Phase 1: Run Research Crew to find properties."""
        print("\n🔍 Phase 1: Property Research")
        
        criteria = self.state.search_criteria
        search_query = f"{criteria.bedrooms or ''} bedroom {criteria.property_type} in {criteria.location}"
        if criteria.max_price:
            search_query += f" under {criteria.max_price}"
        
        result = ResearchCrew().crew().kickoff(inputs={"search_query": search_query.strip()})
        self.state.research_results = result.raw
        
        try:
            data = json.loads(result.raw) if isinstance(result.raw, str) else result.raw
            if isinstance(data, dict) and "properties" in data:
                self.state.properties_found = len(data["properties"])
            elif isinstance(data, dict) and "listings" in data:
                self.state.properties_found = len(data["listings"])
        except:
            pass
        
        print(f"   ✅ Found {self.state.properties_found} properties")
        return self.state.research_results

    @listen(run_research_phase)
    @human_feedback(
        message="Review the properties and select which ones to proceed with. "
                "Respond with a JSON array of property IDs, e.g. ['prop_001', 'prop_002']",
    )
    def await_property_approval(self):
        """PAUSE: Wait for user to select properties."""
        print("\n⏸️  Awaiting Property Approval...")
        return self.state.research_results

    @listen(await_property_approval)
    def filter_approved_properties(self, result: HumanFeedbackResult):
        """Process user feedback and filter properties."""
        print("\n✅ Processing Property Selection")
        
        try:
            feedback = result.feedback
            if isinstance(feedback, str) and feedback.startswith('['):
                approved_ids = json.loads(feedback)
            else:
                approved_ids = [id.strip().strip("'\"") for id in feedback.split(',')]
            self.state.approved_property_ids = approved_ids
        except:
            self.state.approved_property_ids = []
        
        try:
            data = json.loads(self.state.research_results)
            key = "properties" if "properties" in data else "listings"
            if key in data:
                data[key] = [p for p in data[key] if p.get("id") in self.state.approved_property_ids]
                self.state.properties_approved = len(data[key])
            self.state.filtered_research_results = json.dumps(data)
        except:
            self.state.filtered_research_results = self.state.research_results
        
        print(f"   ✅ Approved {self.state.properties_approved} properties")

    @listen(filter_approved_properties)
    def run_location_phase(self):
        """Phase 3: Run Location Analyzer Crew."""
        print("\n📍 Phase 3: Location Analysis")
        
        if self.state.properties_approved == 0:
            print("   ⚠️ No properties approved, skipping...")
            return
        
        result = LocationAnalyzerCrew().crew().kickoff(
            inputs={"research_results": self.state.filtered_research_results}
        )
        self.state.location_results = result.raw
        self.state.properties_analyzed = self.state.properties_approved
        print(f"   ✅ Analyzed {self.state.properties_analyzed} locations")

    @listen(filter_approved_properties)
    def run_design_phase(self):
        """Phase 4: Run Interior Design Crew."""
        print("\n🎨 Phase 4: Interior Design")
        
        if self.state.properties_approved == 0:
            print("   ⚠️ No properties to redesign, skipping...")
            return
        
        result = InteriorDesignCrew().crew().kickoff(inputs={
            "research_results": self.state.filtered_research_results,
            "design_style": self.state.design_style_preference
        })
        self.state.design_results = result.raw
        
        try:
            data = json.loads(result.raw)
            self.state.rooms_redesigned = data.get("metadata", {}).get("total_rooms_redesigned", 0)
        except:
            pass
        
        print(f"   ✅ Redesigned {self.state.rooms_redesigned} rooms")

    @listen(and_(run_location_phase, run_design_phase))
    def compile_final_report(self):
        """Final: Compile unified report."""
        print("\n📊 Compiling Final Report")
        
        final_report = {
            "search_criteria": self.state.search_criteria.model_dump() if self.state.search_criteria else {},
            "summary": {
                "properties_found": self.state.properties_found,
                "properties_approved": self.state.properties_approved,
                "properties_analyzed": self.state.properties_analyzed,
                "rooms_redesigned": self.state.rooms_redesigned
            },
            "approved_property_ids": self.state.approved_property_ids,
            "phases": {
                "research": self.state.research_results,
                "location": self.state.location_results,
                "design": self.state.design_results
            }
        }
        
        with open("output/unified_report.json", "w") as f:
            json.dump(final_report, f, indent=2)
        
        print("   ✅ Report saved to output/unified_report.json")
        print("\n🏠 Flow Complete!")
        return final_report


def kickoff():
    """Run the Real Estate Agent flow."""
    RealEstateFlow().kickoff()


def plot():
    """Generate flow visualization."""
    RealEstateFlow().plot()


if __name__ == "__main__":
    kickoff()
