import os
import requests
from math import radians, sin, cos, sqrt, atan2
from typing import Dict, List, Any
from crewai.tools import tool


# Google Places API configuration
GOOGLE_PLACES_BASE_URL = "https://places.googleapis.com/v1"


@tool("Google Places Geocode Tool")
def google_places_geocode_tool(address: str, country: str = None) -> Dict[str, Any]:
    """Convert address to coordinates using Google Places Text Search API.
    
    Args:
        address: Property address to geocode (can be address, landmark, or place name)
        country: Optional ISO 3166 alpha-2 country code (e.g., 'NG' for Nigeria, 'US' for USA)
    
    Returns:
        Dictionary with success status, latitude, longitude, formatted_address, name, and place_id
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_MAPS_API_KEY environment variable is not set")
    
    try:
        url = f"{GOOGLE_PLACES_BASE_URL}/places:searchText"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.location"
        }
        
        body = {"textQuery": address}
        if country:
            body["regionCode"] = country.upper()
        
        response = requests.post(url, headers=headers, json=body, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("places") or len(data["places"]) == 0:
            return {
                "success": False,
                "error": "Address not found"
            }
        
        place = data["places"][0]
        location = place.get("location", {})
        
        # Validate that location contains valid coordinates
        try:
            lat = location.get("latitude")
            lon = location.get("longitude")
            
            if lat is None or lon is None:
                return {
                    "success": False,
                    "error": "Location coordinates not available for this address",
                    "formatted_address": place.get("formattedAddress", address),
                    "name": place.get("displayName", {}).get("text", ""),
                    "place_id": place.get("id", "")
                }
            
            # Ensure coordinates are valid floats
            latitude = float(lat)
            longitude = float(lon)
            
            return {
                "success": True,
                "latitude": latitude,
                "longitude": longitude,
                "formatted_address": place.get("formattedAddress", address),
                "name": place.get("displayName", {}).get("text", ""),
                "place_id": place.get("id", "")
            }
        except (ValueError, TypeError) as e:
            return {
                "success": False,
                "error": f"Invalid coordinate format: {str(e)}",
                "formatted_address": place.get("formattedAddress", address),
                "name": place.get("displayName", {}).get("text", ""),
                "place_id": place.get("id", "")
            }
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return {"success": False, "error": "Address not found"}
        raise Exception(f"Google Places geocoding API error: {str(e)}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Google Places geocoding request failed: {str(e)}")


@tool("Google Places Nearby Search Tool")
def google_places_nearby_tool(
    latitude: float,
    longitude: float,
    category: str,
    radius_meters: int = 5000,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """Find nearby points of interest using Google Places Nearby Search API.
    
    Args:
        latitude: Property latitude
        longitude: Property longitude
        category: POI category (e.g., "restaurant", "cafe", "park", "school", 
                  "hospital", "gym", "shopping_mall", "transit_station")
        radius_meters: Search radius in meters (default 5000m = 5km, max 50000m)
        limit: Maximum number of results (max 20)
    
    Returns:
        List of nearby places with name, category, distance, coordinates, address, rating
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_MAPS_API_KEY environment variable is not set")
    
    try:
        url = f"{GOOGLE_PLACES_BASE_URL}/places:searchNearby"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.location,places.rating,places.userRatingCount"
        }
        
        body = {
            "includedTypes": [category],
            "maxResultCount": min(limit, 20),
            "locationRestriction": {
                "circle": {
                    "center": {
                        "latitude": latitude,
                        "longitude": longitude
                    },
                    "radius": min(float(radius_meters), 5000.0)
                }
            }
        }
        
        response = requests.post(url, headers=headers, json=body, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        pois = []
        for place in data.get("places", []):
            place_location = place.get("location", {})
            place_lat = place_location.get("latitude")
            place_lon = place_location.get("longitude")
            
            if place_lat is None or place_lon is None:
                continue
            
            distance = calculate_distance(
                latitude, longitude,
                place_lat, place_lon
            )
            
            pois.append({
                "name": place.get("displayName", {}).get("text", "Unknown"),
                "category": category,
                "distance_meters": round(distance, 2),
                "latitude": place_lat,
                "longitude": place_lon,
                "address": place.get("formattedAddress", ""),
                "rating": place.get("rating"),
                "user_ratings_total": place.get("userRatingCount", 0),
                "place_id": place.get("id", "")
            })
        
        return pois
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return []
        raise Exception(f"Google Places nearby search API error: {str(e)}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Google Places nearby search request failed: {str(e)}")


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates using Haversine formula.
    
    Args:
        lat1: Latitude of first point
        lon1: Longitude of first point
        lat2: Latitude of second point
        lon2: Longitude of second point
    
    Returns:
        Distance in meters
    """
    # Earth radius in meters
    R = 6371000
    
    # Convert to radians
    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)
    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)
    
    # Haversine formula
    a = sin(delta_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    
    return distance
