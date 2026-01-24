"""AI Real Estate Agent Crews.

This package contains the main crews for the real estate workflow:

1. ResearchCrew - Sequential process for property discovery and data extraction
2. LocationAnalyzerCrew - Hierarchical process for geospatial amenity analysis  
3. InteriorDesignCrew - Sequential process for room redesign visualization

Each crew outputs JSON files that are consumed by the next phase via Flow @listen decorators.
"""

from src.real_ai_agents.crews.research_crew.research_crew import ResearchCrew
from src.real_ai_agents.crews.location_analyzer_crew.location_analyzer_crew import LocationAnalyzerCrew
from src.real_ai_agents.crews.interior_design_crew.interior_design_crew import InteriorDesignCrew

__all__ = [
    "ResearchCrew",
    "LocationAnalyzerCrew",
    "InteriorDesignCrew",
]

