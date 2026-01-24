# AI Real Estate Agent - Architecture & Agent Reference

## Project Overview

The AI Real Estate Agent is an event-driven automation system that handles the complete real estate discovery, analysis, and visualization process. It orchestrates multiple AI agents through a **three-phase workflow**:

1. **Research Phase** - Property scraping and data extraction
2. **Location Phase** - Geospatial amenity analysis
3. **Design Phase** - AI-powered interior redesign visualization

The system helps users find properties, analyze neighborhoods, and visualize potential interior transformations using AI-generated images.

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| **Orchestration** | CrewAI Flows |
| **LLM Provider** | OpenRouter (DeepSeek-R1, DeepSeek-Chat) |
| **Web Scraping** | Tavily Search & Extractor |
| **Geospatial** | Google Maps Places API (v1) |
| **Image Generation** | Google Gemini 2.0 Flash (Image API) |
| **Data Validation** | Pydantic + Custom Guardrails |

---

## Crew Architecture

### 1. Research Crew (`src/real_ai_agents/crews/research_crew/`)

**Process:** Sequential  
**LLM:** DeepSeek-R1 via OpenRouter  
**Purpose:** Research phase - finds and structures property listings

#### Agents

| Agent | Role | Key Capabilities |
|-------|------|------------------|
| **Scraper** | Senior Real Estate Platform Scraper | Multi-platform discovery, Tavily integration, dynamic content handling |
| **Data Extractor** | Property Data Extraction Specialist | Pattern recognition, structured data extraction, image URL capture |
| **Validator** | Real Estate Data Quality Analyst | Quality scoring (0-100), phone/URL validation, price reasonability checks |
| **Report Agent** | Property Research Report Compiler | JSON formatting for frontend, metadata compilation |

#### Task Flow
```
scrape_listings → extract_property_data → validate_data → compile_research_report
```

#### Guardrails
- `truncate_listings_guardrail` - Enforces max 6 listings
- `validate_property_extraction` - Ensures mandatory fields (phone, URL, location, price, images, agent name)
- `HallucinationGuardrail` - Prevents fabricated data (threshold: 7.0)

#### Output
```json
{
  "metadata": { "search_criteria": "...", "total_found": 25, "total_validated": 22 },
  "properties": [{ "id": "prop_001", "display_title": "...", "price_display": "$2,500/month", ... }],
  "issues": { "properties_with_no_contact": [], "properties_flagged": [] }
}
```

---

### 2. Location Analyzer Crew (`src/real_ai_agents/crews/location_analyzer_crew/`)

**Process:** Hierarchical (parallel execution)  
**LLM:** DeepSeek-Chat via OpenRouter  
**Purpose:** Location phase - geospatial analysis for properties

#### Agents

| Agent | Role | Key Capabilities |
|-------|------|------------------|
| **Manager** | Location Analysis Operations Manager | Property assignment, parallel coordination, progress monitoring |
| **Location Analyzer (x6)** | Senior Location Intelligence Analyst | Google Maps API integration, 8-category amenity search, proximity scoring |
| **Report Agent** | Location Intelligence Report Compiler | Comparative analysis, score normalization, frontend-ready JSON |

#### Amenity Categories (6km radius, 50km for airports)
1. Markets (grocery stores, supermarkets)
2. Gyms (fitness centers)
3. Bus Parks (transit stations)
4. Railway Terminals (train/subway stations)
5. Stadiums (sports venues)
6. Malls (shopping centers)
7. Airports (extended 50km radius)
8. Seaports (coastal properties only)

#### Task Flow
```
assign_properties → [analyze_property_1..6 (parallel)] → compile_location_report
```

#### Guardrails
- `validate_location_analysis` - Ensures all 8 amenity categories present with scores
- `validate_location_report` - Validates final report structure (metadata, properties, comparison)

#### Output
```json
{
  "metadata": { "properties_analyzed": 3, "search_radius_km": 6 },
  "properties": [{ "property_id": "prop_001", "overall_score": 78, "location_grade": "B", ... }],
  "comparison": { "best_transit": "prop_003", "best_overall": "prop_001" }
}
```

---

### 3. Interior Design Crew (`src/real_ai_agents/crews/interior_design_crew/`)

**Process:** Sequential  
**LLM:** DeepSeek-Chat via OpenRouter  
**Purpose:** Design phase - AI-powered room redesign visualization

#### Agents

| Agent | Role | Key Capabilities |
|-------|------|------------------|
| **Design Coordinator** | Interior Design Coordinator | Room type identification, style analysis, condition assessment |
| **Room Redesigner** | AI Room Redesigner | Gemini image generation, style application, before/after creation |
| **Report Agent** | Design Report Compiler | JSON compilation, before/after pairing, metadata tracking |

#### Task Flow
```
analyze_room_images → generate_redesigns → compile_design_report
```

#### Guardrails
- `validate_room_analysis` - Ensures properties array with room data (property_id, rooms[])
- `validate_design_report` - Validates final report structure (metadata, properties)

#### Output
```json
{
  "metadata": { "generated_at": "...", "total_properties": 3, "total_rooms_redesigned": 8 },
  "properties": [
    {
      "property_id": "prop_001",
      "location": "...",
      "rooms": [
        {
          "room_type": "living room",
          "original_image_url": "...",
          "redesigned_image_base64": "...",
          "style_applied": "Modern Minimalist",
          "design_notes": "..."
        }
      ]
    }
  ]
}
```

---

## Tools Reference

### Google Maps Tools (`src/real_ai_agents/tools/google_maps_tools.py`)

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `google_places_geocode_tool` | Address → Coordinates | `address`, `country` (optional ISO alpha-2) |
| `google_places_nearby_tool` | Find nearby POIs | `latitude`, `longitude`, `category`, `radius_meters`, `limit` |

**Supported Categories:** restaurant, cafe, park, school, hospital, gym, shopping_mall, transit_station, airport, supermarket, train_station, bus_station, stadium, etc.

**Features:**
- Uses Google Places API v1 (New)
- Haversine distance calculation
- Automatic coordinate validation

---

### Gemini Image Tools (`src/real_ai_agents/tools/gemini_image_tools.py`)

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `redesign_room_image` | Transform room photos with AI | `image_url`, `style_prompt`, `property_id`, `room_type` |
| `generate_room_description` | Analyze room images | `image_url`, `property_id` |
| `suggest_design_styles` | Get style recommendations | `room_type`, `user_preferences` |

**Supported Room Types & Styles:**

| Room Type | Available Styles |
|-----------|------------------|
| Living Room | Modern Minimalist, Cozy Scandinavian, Industrial Loft, Bohemian Eclectic |
| Bedroom | Serene Sanctuary, Luxurious Hotel, Japandi Zen |
| Kitchen | Modern Chef's Kitchen, Farmhouse Charm, Sleek Contemporary |
| Bathroom | Spa Retreat, Modern Luxury |

**Features:**
- Uses Gemini 2.0 Flash (`gemini-2.0-flash-exp`)
- Image-to-image transformation
- Base64 encoded output
- Automatic MIME type detection

---

## Environment Variables

```env
# LLM
OPENROUTER_API_KEY=your_key

# Google Maps
GOOGLE_MAPS_API_KEY=your_key

# Google Gemini (Image Generation)
GOOGLE_API_KEY=your_key
GEMINI_IMAGE_MODEL=gemini-2.0-flash-exp  # Optional, defaults to this
```

---

## Data Flow Summary

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER INPUT                                     │
│                    (Search Criteria + Design Style)                      │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      1. RESEARCH CREW                                    │
│  Scraper → Extractor → Validator → Report                               │
│  Output: research_results.json (max 6 properties)                        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                  2. LOCATION ANALYZER CREW                               │
│  Manager assigns → 6 Analyzers (parallel) → Report                       │
│  Output: location_intelligence.json                                      │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                  3. INTERIOR DESIGN CREW                                 │
│  Coordinator → Redesigner → Report                                       │
│  Output: design_results.json (before/after images)                       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    UNIFIED REPORT                                        │
│  Output: unified_report.json (all phases combined)                       │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Flow Controller (`src/real_ai_agents/main.py`)

The `RealEstateFlow` class orchestrates all three crews using CrewAI Flows with `@listen` decorators:

```python
@start()
def initialize_search()      # Set up search criteria and design preferences

@listen(initialize_search)
def run_research_phase()     # Execute Research Crew

@listen(run_research_phase)
def run_location_phase()     # Execute Location Analyzer Crew

@listen(run_location_phase)
def run_design_phase()       # Execute Interior Design Crew

@listen(run_design_phase)
def compile_final_report()   # Merge all outputs into unified_report.json
```

### State Model

```python
class RealEstateState(BaseModel):
    search_criteria: SearchCriteria       # Location, type, bedrooms, price
    design_style_preference: str          # e.g., "modern minimalist"
    research_results: str                 # JSON from Research Crew
    location_results: str                 # JSON from Location Crew
    design_results: str                   # JSON from Design Crew
    properties_found: int
    properties_analyzed: int
    rooms_redesigned: int
```

---

## Key Design Decisions

1. **Max 6 Properties** - Controlled by guardrails to limit API costs and ensure quality
2. **Hierarchical + Parallel** - Location analysis runs 6 agents in parallel for speed
3. **Sequential Design** - Room analysis → redesign → report ensures proper data flow
4. **Gemini Image Generation** - Uses Gemini 2.0 Flash for photorealistic room transformations
5. **JSON Guardrails** - All crews validate output structure before proceeding

---

## Output Files

| File | Generated By | Purpose |
|------|--------------|---------|
| `output/research_results.json` | Research Crew | Property listings with images and contact info |
| `output/location_intelligence.json` | Location Analyzer Crew | Amenity scores and comparisons |
| `output/design_results.json` | Interior Design Crew | Before/after room images |
| `output/unified_report.json` | Flow Controller | Combined report from all phases |

---

## Running the System

```bash
# Default run (Lagos, Nigeria demo)
python -m src.real_ai_agents.main

# With custom trigger payload
python -c "from src.real_ai_agents.main import run_with_trigger; run_with_trigger()" \
  '{"search_criteria": {"location": "Austin, TX", "bedrooms": 2}, "design_style": "modern minimalist"}'

# Generate flow visualization
python -c "from src.real_ai_agents.main import plot; plot()"
```
