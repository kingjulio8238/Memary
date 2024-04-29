import os
import googlemaps
import json
from langchain.chat_models import ChatOpenAI
from langchain.tools import StructuredTool
from langchain.agents import initialize_agent, AgentType
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Union, List, Tuple, Any 
from dotenv import load_dotenv

load_dotenv()

google_maps_key = os.getenv("google_maps_key")
gmaps = googlemaps.Client(key=google_maps_key)

def retrieve_location(): 
  "Returns latitude and longitude of current location"
  latitude = 37.423304896346345
  longitude = -122.16023584591919
   
  return latitude, longitude

def reverse_geocode(latitude: float, longitude: float): 
  "Converts latitude and longitude into a readable address"
  result = gmaps.reverse_geocode((latitude, longitude))
  if result:
        address = result[0].get('formatted_address', 'No address found')
  else:
    address = 'No address found'
  
  return address

def find_places(query: None, location = None, radius = None, language = None, min_price = None, max_price = None, open_now = False, place_type = None, region = None): 
  params = {
        'query': query,
        'location': location,
        'radius': radius,
        'language': language,
        'min_price': min_price,
        'max_price': max_price,
        'open_now': open_now,
        'type': place_type,
        'region': region
    } 
  
  params = {k: v for k, v in params.items() if v is not None}
  response = gmaps.places(**params)
  
  results = response['results'][:5] # limit to top 5 results 
  
  simplified_results = []
  for place in results: 
    place_info = {
      'place_id': place.get('place_id'), 
      'name': place.get('name'), 
      'location': (place['geometry']['location']['lat'], place['geometry']['location']['lng']), 
      'formatted_address': place.get('formatted_address'), 
      'rating': place.get('rating')
    }
    simplified_results.append(place_info)
    
  return simplified_results

class FindPlacesArgs(BaseModel): 
  query: Optional[str] = Field(None, description = "Text string to search for, e.g., 'restaurant'")
  location: Optional[Union[tuple, list, str]] = Field(None, description = "Latitude and longitude as a tuple or string")
  radius: Optional[int] = Field(None, description = "Search radius in meters")
  language: Optional[str] = Field(None, description = "The language in which to return results")
  min_price: Optional[int] = Field(None, description = "Minimum price level of places to include, from 0 (most affordable) to 4 (most expensive)")
  max_price: Optional[int] = Field(None, description = "Maximum price level of places to include, from 0 (most affordable) to 4 (most expensive)")
  open_now: Optional[bool] = Field(False, description = "Return only those places that are open for business at the time the query is sent")
  place_type: Optional[str] = Field(None, description = "Type of place to restrict results to")
  region: Optional[str] = Field(None, description = "Region code to bias results towards")
  
find_places_tool = StructuredTool(
  func = find_places, 
  name = "Find Places", 
  description = "Finds places based on location and other optional parameters. For each place, returns place ID, name, coordinates as a tuple, formatted address, and rating.", 
  args_schema = FindPlacesArgs
)

def get_directions(origin, destination, mode="walking", waypoints=None, alternatives=False, avoid=None, language=None, units=None, region=None, departure_time=None, arrival_time=None, optimize_waypoints=False, transit_mode=None, transit_routing_preference=None, traffic_model=None): 
  params = {
        'origin': origin,
        'destination': destination,
        'mode': mode,
        'waypoints': waypoints,
        'alternatives': alternatives,
        'avoid': avoid,
        'language': language,
        'units': units,
        'region': region,
        'departure_time': departure_time,
        'arrival_time': arrival_time,
        'optimize_waypoints': optimize_waypoints,
        'transit_mode': transit_mode,
        'transit_routing_preference': transit_routing_preference,
        'traffic_model': traffic_model
    }
    
  # Remove None values
  params = {k: v for k, v in params.items() if v is not None}
    
  # Make the API call
  response = gmaps.directions(**params)
    
  return response  

class DirectionsArgs(BaseModel):
    origin: Union[str, Tuple[float, float]] = Field(..., description="The starting address or latitude/longitude value.")
    destination: Union[str, Tuple[float, float]] = Field(..., description="The ending address or latitude/longitude value.")
    mode: Optional[str] = Field("walking", description="Mode of transport (driving, walking, bicycling, or transit).")
    waypoints: Optional[Union[List[Union[str, Tuple[float, float]]], str]] = Field(None, description="Array of waypoints to alter the route. To route through a location without stopping, prefix it with 'via:', e.g., ['via:San Francisco', 'via:Mountain View'].")
    alternatives: bool = Field(False, description="If True, more than one route may be returned in the response.")
    avoid: Optional[Union[str, List[str]]] = Field(None, description="Features to avoid (tolls, highways, ferries, etc.).")
    language: Optional[str] = Field(None, description="Language for the results.")
    units: Optional[str] = Field(None, description="Unit system for the results (metric or imperial).")
    region: Optional[str] = Field(None, description="Region code, specified as a ccTLD two-character value.")
    departure_time: Optional[Union[int, datetime]] = Field(None, description="Desired time of departure as a timestamp or datetime.")
    arrival_time: Optional[Union[int, datetime]] = Field(None, description="Desired time of arrival as a timestamp or datetime.")
    optimize_waypoints: bool = Field(False, description="Whether to optimize the order of waypoints.")
    transit_mode: Optional[Union[str, List[str]]] = Field(None, description="Preferred modes of transit (bus, subway, train, etc.).")
    transit_routing_preference: Optional[str] = Field(None, description="Preferences for transit routing (less_walking or fewer_transfers).")
    traffic_model: Optional[str] = Field(None, description="Predictive travel time model (best_guess, optimistic, pessimistic).")

def main(): 
  tools = []
  tools.append(StructuredTool.from_function(retrieve_location))
  tools.append(StructuredTool.from_function(reverse_geocode))
  tools.append(find_places_tool)
  
  # TODO: 
  # Missing: place (implement?)
  # Missing: find_place (implement?)
  # Missing: directions 
  # Missing: distance_matrix
  # Missing: vision 
  # Missing: audio
  
  # llm = ChatOpenAI(model="gpt-4")
  # agent_chain = initialize_agent(tools, llm, agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
  # agent_chain.invoke(
  #   {
  #     "input": "Is there a cafe near me?"
  #   }
  # )
  
  latitude = 37.423304896346345
  longitude = -122.16023584591919
  
  response = get_directions(origin=(latitude, longitude), destination="Coupa Cafe Green Library Stanford")
  # print(response[0]['legs'][0]) # 'legs' because walking was specified?
  # print(response[0]['legs'][0].keys()) # keys = distance, duration, end_address, end_location, start_address, start_location, steps, traffic_speed_entry, via_waypoint
  # print(response[0]['legs'][0]['steps'][0].keys()) # keys = distance, duration, end_location, html_instructions, polyline, start_location, travel_mode
  
  # TODO: 
  # places()
    # Only certain 'type' can be accepted. Prompt agent. 
    # Only certain 'regions' can be accepted. 
  
  
   
if __name__ == "__main__": 
  main()
  # Important GMaps documentation: https://googlemaps.github.io/google-maps-services-python/docs/index.html#googlemaps.Client.places

  
 
  

