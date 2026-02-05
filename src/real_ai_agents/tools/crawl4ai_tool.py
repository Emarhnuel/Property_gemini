"""
Crawl4AI Tool for CrewAI.

This tool uses Crawl4AI to extract property listing data from websites
using a real local browser with anti-detection features.
"""

import os
import asyncio
import json
import logging
from typing import Type, Optional
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crawl4AI imports
try:
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
    from crawl4ai.extraction_strategy import LLMExtractionStrategy, JsonCssExtractionStrategy
    from crawl4ai.async_configs import CacheMode, LLMConfig
    from crawl4ai.content_filter_strategy import PruningContentFilter
    CRAWL4AI_AVAILABLE = True
    logger.info("✅ crawl4ai package loaded successfully")
except ImportError as e:
    CRAWL4AI_AVAILABLE = False
    logger.error(f"❌ crawl4ai import failed: {e}")


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


class CrawlExtractInput(BaseModel):
    """Input schema for CrawlExtractTool."""
    url: str = Field(
        ...,
        description="The URL of the property listing page to extract data from."
    )
    extraction_task: str = Field(
        default="Extract all property listing details including price, address, bedrooms, bathrooms, description, images, and contact information.",
        description="Specific extraction instructions for what data to extract."
    )


class ListingSchema(BaseModel):
    address: str = Field(..., description="Full address of the property")
    price: str = Field(..., description="Rental price (e.g., '$3,500/mo')")
    bedrooms: str = Field(..., description="Number of bedrooms")
    bathrooms: str = Field(..., description="Number of bathrooms")
    description: str = Field(..., description="Full description text")
    facts_and_features: list[str] = Field(..., description="List of amenities and features")
    contact_info: str = Field(..., description="Contact name or phone number")


class CrawlExtractTool(BaseTool):
    """
    Optimized Crawl4AI tool for real estate listings.
    Features:
    - Identity-Based Crawling (reuses chrome profile) to bypass anti-bot
    - Structured Extraction (Pydantic schema) to prevent timeouts
    - Fit Markdown (reduces noise)
    """
    name: str = "crawl_extract"
    description: str = "Extracts structured real estate data using browser automation."
    args_schema: Type[BaseModel] = CrawlExtractInput

    def _run(self, url: str, extraction_task: str = None) -> str:
        return asyncio.run(self._async_extract(url, extraction_task))

    async def _async_extract(self, url: str, extraction_task: str) -> str:
        if not CRAWL4AI_AVAILABLE:
            return json.dumps({"error": "crawl4ai not installed"})

        # 1. Identity-Based Config (Anti-Bot Fix)
        # Points to a persistent user profile to reuse cookies/sessions
        user_data_dir = os.path.join(os.getcwd(), ".browser_profile")
        os.makedirs(user_data_dir, exist_ok=True)

        browser_config = BrowserConfig(
            headless=True,  # Changed to True for production run, can be False for debugging
            use_managed_browser=True,
            user_data_dir=user_data_dir, # PERSISTENT PROFILE
            verbose=True
        )

        # 2. Optimized Extraction Strategy (Timeout Fix)
        # Use LLM with strict schema and focused content to avoid 600s timeout
        llm_config = LLMConfig(
            provider="gemini/gemini-3-flash-preview", # Faster model
            api_token=GOOGLE_API_KEY
        )

        llm_strategy = LLMExtractionStrategy(
            llm_config=llm_config,
            schema=ListingSchema.model_json_schema(), # Strict Schema
            extraction_type="schema", # Structured output
            instruction=f"""
            Extract rental listing details matching the schema. 
            Focus on accuracy. 
            If exact value is missing, return 'N/A'.
            {extraction_task or ''}
            """,
            input_format="fit_markdown", # Reduces tokens by ~90%
            chunk_token_threshold=4000,
            apply_chunking=True
        )

        crawl_config = CrawlerRunConfig(
            extraction_strategy=llm_strategy,
            # content_filter argument removed as it is not supported in this version of CrawlerRunConfig
            cache_mode=CacheMode.BYPASS,
            wait_for_images=True,
            scan_full_page=True,
            scroll_delay=0.5,
            delay_before_return_html=3.0,
            magic=True,
        )

        try:
            async with AsyncWebCrawler(config=browser_config) as crawler:
                logger.info(f"🕷️ Crawling {url} with persistent profile...")
                result = await crawler.arun(url=url, config=crawl_config)

                if not result.success:
                    return json.dumps({"error": f"Crawl failed: {result.error_message}", "url": url})
                
                # 3. Combine LLM Data + Media (Images don't need LLM)
                data = json.loads(result.extracted_content) if result.extracted_content else {}
                
                # If specific schema extraction succeeded, it might be a list
                if isinstance(data, list) and len(data) > 0:
                    data = data[0]
                
                # Add images from browser media capture (free, no tokens)
                images = [img.get("src") for img in result.media.get("images", []) if img.get("src")]
                data["images"] = images[:15] # Top 15 images
                
                return json.dumps(data, indent=2)

        except Exception as e:
            logger.error(f"❌ Extraction error: {str(e)}")
            return json.dumps({"error": str(e), "url": url})


class CrawlSimpleTool(BaseTool):
    """
    A simpler tool that just returns raw markdown without LLM extraction.
    Use this if the main tool fails or if you just need raw text.
    """
    name: str = "crawl_simple"
    description: str = "Get raw markdown content from a URL without LLM processing."
    args_schema: Type[BaseModel] = CrawlExtractInput

    def _run(self, url: str, extraction_task: str = None) -> str:
        return asyncio.run(self._async_simple_crawl(url))
        
    async def _async_simple_crawl(self, url: str) -> str:
        try:
            browser_config = BrowserConfig(headless=True, verbose=False)
            crawl_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)
            
            async with AsyncWebCrawler(config=browser_config) as crawler:
                result = await crawler.arun(url=url, config=crawl_config)
                if result.success:
                    return result.markdown[:10000] # Return first 10k chars
                return f"Error: {result.error_message}"
        except Exception as e:
            return f"Error: {str(e)}"


# Instantiate tools for easy import
crawl_extract_tool = CrawlExtractTool()
crawl_simple_tool = CrawlSimpleTool()
