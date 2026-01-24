#!/usr/bin/env python
"""
AI Real Estate Agent Flow - Find & Redesign

This flow orchestrates the three crews through the real estate workflow:
1. Research Phase - Find properties matching search criteria
2. Location Phase - Analyze neighborhood amenities
3. Design Phase - Generate AI-powered room redesigns

The flow uses CrewAI Flows with @listen decorators to chain crew outputs.
"""

import json
from typing import List, Optional
from pydantic import BaseModel, Field

from crewai.flow import Flow, listen, start

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
    # Input
    search_criteria: Optional[SearchCriteria] = None
    design_style_preference: Optional[str] = Field(default="modern minimalist", description="Preferred interior style")
    
    # Phase outputs
    research_results: Optional[str] = None
    location_results: Optional[str] = None
    design_results: Optional[str] = None
    
    # Metadata
    properties_found: int = 0
    properties_analyzed: int = 0
    rooms_redesigned: int = 0


class RealEstateFlow(Flow[RealEstateState]):
    """
    AI Real Estate Agent Flow
    
    Orchestrates the Find & Redesign workflow:
    1. Research → Find properties matching criteria
    2. Location → Analyze neighborhood amenities  
    3. Design → Generate AI-powered room redesigns
    """

    @start()
    def initialize_search(self, crewai_trigger_payload: dict = None):
        """Initialize the flow with search criteria."""
        print("\n" + "=" * 60)
        print("🏠 AI Real Estate Agent - Find & Redesign")
        print("=" * 60)
        
        if crewai_trigger_payload:
            # Use trigger payload for search criteria
            self.state.search_criteria = SearchCriteria(**crewai_trigger_payload.get("search_criteria", {}))
            self.state.design_style_preference = crewai_trigger_payload.get("design_style", "modern minimalist")
            print(f"📋 Received search criteria from trigger")
        else:
            # Default demo criteria
            self.state.search_criteria = SearchCriteria(
                location="Lagos, Nigeria",
                property_type="apartment",
                bedrooms=2,
                max_price=500000
            )
            print(f"📋 Using default search criteria")
        
        print(f"   Location: {self.state.search_criteria.location}")
        print(f"   Type: {self.state.search_criteria.property_type}")
        print(f"   Bedrooms: {self.state.search_criteria.bedrooms}")
        print(f"   Style Preference: {self.state.design_style_preference}")
        print("-" * 60)

    @listen(initialize_search)
    def run_research_phase(self):
        """Phase 1: Run Research Crew to find properties."""
        print("\n🔍 Phase 1: Property Research")
        print("-" * 40)
        
        criteria = self.state.search_criteria
        search_query = f"{criteria.bedrooms or ''} bedroom {criteria.property_type} in {criteria.location}"
        if criteria.max_price:
            search_query += f" under {criteria.max_price}"
        if criteria.additional_requirements:
            search_query += f" {criteria.additional_requirements}"
        
        print(f"   Search: {search_query}")
        
        result = (
            ResearchCrew()
            .crew()
            .kickoff(inputs={"search_query": search_query.strip()})
        )
        
        self.state.research_results = result.raw
        
        # Count properties found
        try:
            data = json.loads(result.raw) if isinstance(result.raw, str) else result.raw
            if isinstance(data, dict) and "listings" in data:
                self.state.properties_found = len(data["listings"])
            elif isinstance(data, list):
                self.state.properties_found = len(data)
        except:
            self.state.properties_found = 0
        
        print(f"   ✅ Found {self.state.properties_found} properties")

    @listen(run_research_phase)
    def run_location_phase(self):
        """Phase 2: Run Location Analyzer Crew for neighborhood analysis."""
        print("\n📍 Phase 2: Location Analysis")
        print("-" * 40)
        
        if self.state.properties_found == 0:
            print("   ⚠️ No properties to analyze, skipping...")
            return
        
        result = (
            LocationAnalyzerCrew()
            .crew()
            .kickoff(inputs={"research_results": self.state.research_results})
        )
        
        self.state.location_results = result.raw
        
        # Count properties analyzed
        try:
            data = json.loads(result.raw) if isinstance(result.raw, str) else result.raw
            if isinstance(data, dict) and "properties" in data:
                self.state.properties_analyzed = len(data["properties"])
        except:
            self.state.properties_analyzed = self.state.properties_found
        
        print(f"   ✅ Analyzed {self.state.properties_analyzed} property locations")

    @listen(run_location_phase)
    def run_design_phase(self):
        """Phase 3: Run Interior Design Crew for room redesigns."""
        print("\n🎨 Phase 3: Interior Design")
        print("-" * 40)
        
        if self.state.properties_found == 0:
            print("   ⚠️ No properties to redesign, skipping...")
            return
        
        print(f"   Style: {self.state.design_style_preference}")
        
        result = (
            InteriorDesignCrew()
            .crew()
            .kickoff(inputs={
                "research_results": self.state.research_results,
                "design_style": self.state.design_style_preference
            })
        )
        
        self.state.design_results = result.raw
        
        # Count rooms redesigned
        try:
            data = json.loads(result.raw) if isinstance(result.raw, str) else result.raw
            if isinstance(data, dict) and "metadata" in data:
                self.state.rooms_redesigned = data["metadata"].get("total_rooms_redesigned", 0)
        except:
            pass
        
        print(f"   ✅ Redesigned {self.state.rooms_redesigned} rooms")

    @listen(run_design_phase)
    def compile_final_report(self):
        """Final step: Compile and save the unified report."""
        print("\n📊 Compiling Final Report")
        print("-" * 40)
        
        final_report = {
            "search_criteria": self.state.search_criteria.model_dump() if self.state.search_criteria else {},
            "design_style_preference": self.state.design_style_preference,
            "summary": {
                "properties_found": self.state.properties_found,
                "properties_analyzed": self.state.properties_analyzed,
                "rooms_redesigned": self.state.rooms_redesigned
            },
            "phases": {
                "research": self.state.research_results,
                "location": self.state.location_results,
                "design": self.state.design_results
            }
        }
        
        # Save to output file
        with open("output/unified_report.json", "w") as f:
            json.dump(final_report, f, indent=2)
        
        print("   ✅ Report saved to output/unified_report.json")
        print("\n" + "=" * 60)
        print("🏠 Real Estate Agent Flow Complete!")
        print(f"   📦 Properties Found: {self.state.properties_found}")
        print(f"   📍 Locations Analyzed: {self.state.properties_analyzed}")
        print(f"   🎨 Rooms Redesigned: {self.state.rooms_redesigned}")
        print("=" * 60 + "\n")


def kickoff():
    """Run the Real Estate Agent flow."""
    flow = RealEstateFlow()
    flow.kickoff()


def plot():
    """Generate a visualization of the flow."""
    flow = RealEstateFlow()
    flow.plot()


def run_with_trigger():
    """
    Run the flow with trigger payload.
    
    Example payload:
    {
        "search_criteria": {
            "location": "Lagos, Nigeria",
            "property_type": "apartment",
            "bedrooms": 3,
            "max_price": 1000000
        },
        "design_style": "modern minimalist with gray walls and indoor plants"
    }
    """
    import sys
    
    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided. Please provide JSON payload as argument.")
    
    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument")
    
    flow = RealEstateFlow()
    
    try:
        result = flow.kickoff({"crewai_trigger_payload": trigger_payload})
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the flow with trigger: {e}")


if __name__ == "__main__":
    kickoff()
