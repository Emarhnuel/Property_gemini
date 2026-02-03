"""
Browser Use Cloud Tool for CrewAI.

This tool wraps the Browser Use Cloud SDK to provide real browser automation
capabilities to CrewAI agents. It bypasses the MCP integration issues by
using the Browser Use Python SDK directly.
"""

import os
import asyncio
import json
from typing import Type, Optional, Any
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


# Browser Use SDK imports
try:
    from browser_use import Browser, Agent as BrowserAgent
    from langchain_openai import ChatOpenAI
    BROWSER_USE_AVAILABLE = True
except ImportError:
    BROWSER_USE_AVAILABLE = False


BROWSER_USE_API_KEY = os.getenv("BROWSER_USE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class BrowserExtractInput(BaseModel):
    """Input schema for BrowserExtractTool."""
    url: str = Field(
        ...,
        description="The URL of the property listing page to extract data from."
    )
    extraction_task: str = Field(
        default="Extract all property listing details including price, address, bedrooms, bathrooms, description, images, and contact information.",
        description="Specific extraction instructions for the browser agent."
    )


class BrowserExtractTool(BaseTool):
    """
    A CrewAI tool that uses Browser Use Cloud to extract data from web pages.
    
    This tool spins up a cloud browser, navigates to the specified URL,
    and extracts structured data using an AI agent.
    """
    
    name: str = "browser_extract"
    description: str = """
    Extract structured data from a web page using a real cloud browser.
    Use this tool to scrape property listings that require JavaScript rendering.
    
    The tool will:
    1. Open the URL in a cloud browser
    2. Wait for JavaScript to fully render
    3. Extract all visible content including images
    4. Return structured JSON data
    
    Input:
    - url: The full URL of the page to extract from
    - extraction_task: Optional specific instructions for what to extract
    
    Returns JSON with extracted property data.
    """
    args_schema: Type[BaseModel] = BrowserExtractInput
    
    # Cloud browser configuration
    cloud_timeout: int = 15  # minutes (max for free tier)
    cloud_proxy_country: Optional[str] = "us"  # Bypass geo-restrictions
    
    def _run(self, url: str, extraction_task: str = None) -> str:
        """Synchronous wrapper for the async browser extraction."""
        if not BROWSER_USE_AVAILABLE:
            return json.dumps({
                "error": "browser-use package not installed. Run: pip install browser-use"
            })
        
        if not BROWSER_USE_API_KEY:
            return json.dumps({
                "error": "BROWSER_USE_API_KEY environment variable not set"
            })
        
        if not OPENAI_API_KEY:
            return json.dumps({
                "error": "OPENAI_API_KEY environment variable not set (required for browser agent)"
            })
        
        # Default extraction task for real estate
        if not extraction_task:
            extraction_task = """
            Extract ALL property listing details from this page:
            
            REQUIRED FIELDS:
            - listing_url: The current page URL
            - platform: The website name (e.g., Zillow, Realtor.com)
            - address: Full property address
            - price: Listed price with currency
            - price_frequency: Rental frequency if applicable (monthly, weekly, etc.)
            - bedrooms: Number of bedrooms
            - bathrooms: Number of bathrooms
            - description: Full property description (verbatim text)
            - images: List of ALL image URLs on the page
            - facts_and_features: Dict of property facts (sqft, year built, etc.)
            - contact: Agent/property manager contact info
            
            IMPORTANT:
            - Extract ONLY what is visible on the rendered page
            - Include ALL image URLs you can find
            - Return data as valid JSON
            - If a field is not found, use null
            """
        
        # Run the async extraction in a new event loop
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self._async_extract(url, extraction_task)
            )
            return result
        except Exception as e:
            return json.dumps({
                "error": f"Browser extraction failed: {str(e)}",
                "url": url
            })
        finally:
            loop.close()
    
    async def _async_extract(self, url: str, extraction_task: str) -> str:
        """Async browser extraction using Browser Use Cloud."""
        
        browser = None
        try:
            # Initialize cloud browser
            browser = Browser(
                use_cloud=True,
                cloud_proxy_country_code=self.cloud_proxy_country,
                cloud_timeout=self.cloud_timeout,
            )
            
            # Initialize LLM for the browser agent
            llm = ChatOpenAI(
                model="gpt-4o-mini",  # Cost-effective for extraction
                temperature=0,
            )
            
            # Create the browser agent with extraction task
            full_task = f"""
            Navigate to: {url}
            
            Then perform this extraction task:
            {extraction_task}
            
            After extracting, return ONLY valid JSON with the extracted data.
            Do not include any markdown formatting or explanations.
            """
            
            agent = BrowserAgent(
                task=full_task,
                llm=llm,
                browser=browser,
            )
            
            # Run the browser agent
            result = await agent.run()
            
            # Extract the final result
            if hasattr(result, 'final_result') and result.final_result:
                return result.final_result
            elif hasattr(result, 'extracted_content') and result.extracted_content:
                return result.extracted_content
            else:
                return json.dumps({
                    "raw_result": str(result),
                    "url": url
                })
                
        except Exception as e:
            return json.dumps({
                "error": f"Async extraction error: {str(e)}",
                "url": url
            })
        finally:
            # Cleanup browser
            if browser:
                try:
                    await browser.close()
                except:
                    pass


class BrowserNavigateTool(BaseTool):
    """
    A simpler tool that just navigates and retrieves page content.
    Useful for quick content extraction without complex instructions.
    """
    
    name: str = "browser_navigate"
    description: str = """
    Navigate to a URL and retrieve the full page content using a cloud browser.
    Use this for simple page content retrieval where JavaScript rendering is needed.
    
    Returns the page HTML content and any extracted text.
    """
    args_schema: Type[BaseModel] = BrowserExtractInput
    
    def _run(self, url: str, extraction_task: str = None) -> str:
        """Navigate and extract basic content."""
        if not BROWSER_USE_AVAILABLE:
            return json.dumps({
                "error": "browser-use package not installed"
            })
        
        # Use the same extraction logic but with simpler task
        simple_task = extraction_task or f"""
        Go to {url} and extract:
        1. The page title
        2. All visible text content
        3. All image URLs
        4. Any property/listing details visible
        
        Return as JSON.
        """
        
        extractor = BrowserExtractTool()
        return extractor._run(url, simple_task)


# Instantiate tools for easy import
browser_extract_tool = BrowserExtractTool()
browser_navigate_tool = BrowserNavigateTool()
