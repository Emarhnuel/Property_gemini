# AI Real Estate Agent (Find & Redesign)

An intelligent agent system that finds properties matchings your criteria, analyzes the neighborhood, and uses AI to generate interior design makeovers for every room - helping you visualize the potential of your future home.

## 🚀 Features

- **Deep Discovery**: Scrapes and structures property listings from across the web
- **Location Intelligence**: Analyzes neighborhood amenities (markets, gyms, airports) using Google Maps
- **AI Interior Design**: Uses Gemini AI (Nano Banana technology) to redesign rooms based on your preferred style (e.g., "Modern Minimalist", "Cozy Scandinavian")
- **Unified Reporting**: Generates a comprehensive report with property data, location scores, and before/after design visualizations

## 🛠️ Architecture

Built with [CrewAI](https://crewai.com) and Google Gemini API.

### Crews
1. **ResearchCrew**: Finds properties and extracts high-quality images
2. **LocationAnalyzerCrew**: Scores neighborhoods based on amenity proximity
3. **InteriorDesignCrew**: Analyzes room photos and generates AI redesigns

### Tools
- **Tavily Search**: For finding listings
- **Google Maps Platform**: For location analysis
- **Gemini 2.5/3.0 Image API**: For interior design visualization

## 📦 Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables in `.env`:
   ```env
   OPENROUTER_API_KEY=sk-...
   GOOGLE_MAPS_API_KEY=AIza...
   GOOGLE_API_KEY=AIza...  # For Gemini Image Gen
   TAVILY_API_KEY=tvly-...
   ```

## 🏃‍♂️ Usage

Run the agent flow:
```bash
python -m real_ai_agents.main
```

Or trigger with custom inputs:
```bash
python -m real_ai_agents.main run_with_trigger '{"search_criteria": {"location": "Lagos", "property_type": "apartment", "bedrooms": 3}, "design_style": "Industrial Loft"}'
```