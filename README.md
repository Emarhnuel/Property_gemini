# AI Real Estate Agent (Find & Redesign)

An intelligent agent system that finds properties matchings your criteria, analyzes the neighborhood, and uses AI to generate interior design makeovers for every room - helping you visualize the potential of your future home.

## 🚀 Features

- **Deep Discovery**: Scrapes and structures property listings from across the web using Amazon Nova AI models
- **Location Intelligence**: Analyzes neighborhood amenities (markets, gyms, airports) using Google Maps
- **AI Interior Design**: Uses Gemini AI to redesign rooms based on your preferred style (e.g., "Modern Minimalist", "Cozy Scandinavian")
- **Unified Reporting**: Generates a comprehensive report with property data, location scores, and before/after design visualizations

## 🛠️ Architecture

Built with [CrewAI](https://crewai.com), Amazon Bedrock, and Google Gemini API.

### Crews
1. **ResearchCrew**: Finds properties and extracts high-quality images using Amazon Nova Lite v1:0
2. **LocationAnalyzerCrew**: Scores neighborhoods based on amenity proximity using Amazon Nova 2 Lite/Pro
3. **InteriorDesignCrew**: Analyzes room photos and generates AI redesigns using Amazon Nova 2 Lite/Pro

### Tools
- **Tavily Search**: For finding listings
- **Crawl4AI**: For extracting data from real estate sites
- **Google Maps Platform**: For location analysis
- **Gemini 2.0 Flash Image API**: For interior design visualization
- **Amazon Bedrock**: For LLM inference with Nova models

## 📦 Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -e .
   ```
3. Set up environment variables in `.env`:
   ```env
   # Amazon Bedrock (for Nova models)
   AWS_ACCESS_KEY_ID=your_key
   AWS_SECRET_ACCESS_KEY=your_secret
   AWS_DEFAULT_REGION=us-east-1
   
   # Google APIs
   GOOGLE_MAPS_API_KEY=AIza...
   GOOGLE_API_KEY=AIza...  # For Gemini Image Gen
   
   # Other services
   TAVILY_API_KEY=tvly...
   ```

## 🏃‍♂️ Usage

Run the agent flow:
```bash
python -m src.real_ai_agents.main
```

The system will:
1. Search for properties in Lagos, Nigeria (default demo)
2. Extract property data using Amazon Nova models
3. Analyze location amenities using Google Maps
4. Generate AI-powered room redesigns using Gemini

## 🔄 Recent Updates

**Model Migration**: The system has been migrated from OpenRouter/Moonshot models to Amazon Bedrock Nova models:
- Research Crew: Amazon Nova Lite v1:0
- Location Analyzer Crew: Amazon Nova 2 Lite/Pro  
- Interior Design Crew: Amazon Nova 2 Lite/Pro

This migration provides better performance, lower latency, and improved cost efficiency for real estate data processing.