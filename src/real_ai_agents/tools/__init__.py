"""
Custom Tools for AI Real Estate Agent.

This module exports all custom tools used by the crews:
- Google Maps tools for location analysis (Location Analyzer Crew)
- Gemini Image tools for interior design (Interior Design Crew)
- Browser Use tools for web extraction (Research Crew)
"""

from real_ai_agents.tools.google_maps_tools import (
    google_places_geocode_tool,
    google_places_nearby_tool,
)

from real_ai_agents.tools.gemini_image_tools import (
    redesign_room_image,
    generate_room_description,
    suggest_design_styles,
)

from real_ai_agents.tools.browser_use_tool import (
    browser_extract_tool,
    browser_navigate_tool,
    BrowserExtractTool,
)

__all__ = [
    # Google Maps Tools
    "google_places_geocode_tool",
    "google_places_nearby_tool",
    # Gemini Image Tools
    "redesign_room_image",
    "generate_room_description",
    "suggest_design_styles",
    # Browser Use Tools
    "browser_extract_tool",
    "browser_navigate_tool",
    "BrowserExtractTool",
]
