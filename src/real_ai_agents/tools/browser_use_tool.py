"""
Browser Use Cloud Tool for CrewAI.

This tool wraps the Browser Use Cloud SDK to provide real browser automation
capabilities to CrewAI agents. It bypasses the MCP integration issues by
using the Browser Use Python SDK directly.

Uses Google Gemini for the browser agent.
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

# Browser Use SDK imports
try:
    from browser_use import Browser, Agent as BrowserAgent, ChatGoogle
    BROWSER_USE_AVAILABLE = True
    logger.info("✅ browser-use package loaded successfully")
except ImportError as e:
    BROWSER_USE_AVAILABLE = False
    logger.error(f"❌ browser-use import failed: {e}")


BROWSER_USE_API_KEY = os.getenv("BROWSER_USE_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


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
    and extracts structured data using a Google Gemini AI agent.
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
        logger.info(f"🌐 BrowserExtractTool called with URL: {url}")
        
        if not BROWSER_USE_AVAILABLE:
            error = "browser-use package not installed. Run: pip install browser-use"
            logger.error(f"❌ {error}")
            return json.dumps({"error": error})
        
        if not BROWSER_USE_API_KEY:
            error = "BROWSER_USE_API_KEY environment variable not set"
            logger.error(f"❌ {error}")
            return json.dumps({"error": error})
        
        if not GOOGLE_API_KEY:
            error = "GOOGLE_API_KEY environment variable not set (required for Gemini browser agent)"
            logger.error(f"❌ {error}")
            return json.dumps({"error": error})
        
        logger.info("✅ All API keys verified")
        
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
            logger.info("🔄 Starting async extraction...")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self._async_extract(url, extraction_task)
            )
            logger.info(f"✅ Extraction completed. Result length: {len(result)} chars")
            return result
        except Exception as e:
            error_msg = f"Browser extraction failed: {str(e)}"
            logger.error(f"❌ {error_msg}", exc_info=True)
            return json.dumps({
                "error": error_msg,
                "url": url,
                "exception_type": type(e).__name__
            })
        finally:
            try:
                loop.close()
            except:
                pass
    
    async def _async_extract(self, url: str, extraction_task: str) -> str:
        """Async browser extraction using Browser Use Cloud with Gemini."""
        
        browser = None
        try:
            logger.info("🚀 Initializing cloud browser...")
            
            # Initialize cloud browser
            browser = Browser(
                use_cloud=True,
                cloud_proxy_country_code=self.cloud_proxy_country,
                cloud_timeout=self.cloud_timeout,
            )
            logger.info("✅ Cloud browser initialized")
            
            # Initialize Google Gemini LLM for the browser agent
            logger.info("🤖 Initializing Gemini LLM...")
            llm = ChatGoogle(model='gemini-2.5-flash-preview-04-17')
            logger.info("✅ Gemini LLM initialized")
            
            # Create the browser agent with extraction task
            full_task = f"""
            Navigate to: {url}
            
            Then perform this extraction task:
            {extraction_task}
            
            After extracting, return ONLY valid JSON with the extracted data.
            Do not include any markdown formatting or explanations.
            """
            
            logger.info("🤖 Creating browser agent...")
            agent = BrowserAgent(
                task=full_task,
                llm=llm,
                browser=browser,
            )
            logger.info("✅ Browser agent created")
            
            # Run the browser agent
            logger.info("▶️ Running browser agent...")
            result = await agent.run()
            logger.info(f"✅ Agent run completed. Result type: {type(result)}")
            
            # Log result attributes for debugging
            logger.info(f"📋 Result attributes: {dir(result)}")
            
            # Extract the final result
            if hasattr(result, 'final_result') and result.final_result:
                logger.info("📄 Found final_result attribute")
                return result.final_result
            elif hasattr(result, 'extracted_content') and result.extracted_content:
                logger.info("📄 Found extracted_content attribute")
                return result.extracted_content
            elif hasattr(result, 'model_output') and result.model_output:
                logger.info("📄 Found model_output attribute")
                return str(result.model_output)
            else:
                logger.warning(f"⚠️ No standard result attribute found. Raw result: {result}")
                return json.dumps({
                    "raw_result": str(result),
                    "url": url,
                    "result_type": str(type(result))
                })
                
        except Exception as e:
            error_msg = f"Async extraction error: {str(e)}"
            logger.error(f"❌ {error_msg}", exc_info=True)
            return json.dumps({
                "error": error_msg,
                "url": url,
                "exception_type": type(e).__name__
            })
        finally:
            # Cleanup browser
            if browser:
                try:
                    logger.info("🧹 Closing browser...")
                    await browser.close()
                    logger.info("✅ Browser closed")
                except Exception as e:
                    logger.warning(f"⚠️ Browser close error: {e}")


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
