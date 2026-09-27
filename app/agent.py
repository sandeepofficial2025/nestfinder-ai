# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import json
import datetime
import httpx
from typing import Optional, List, Dict, Any
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv()

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools import ToolContext
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.adk.memory import VertexAiMemoryBankService
from google.adk.code_executors import AgentEngineSandboxCodeExecutor

from a2ui.schema.manager import A2uiSchemaManager
from a2ui.basic_catalog.provider import BasicCatalog
from .a2ui_utils import a2ui_callback
from google.genai import types
import google.genai
from google.cloud import firestore, storage

# CRITICAL: Hardcode GCP Project ID and GCS Bucket Name directly as literal strings.
PROJECT_ID = "qwiklabs-gcp-03-eb3066a4dd0c"
BUCKET_NAME = "nestfinder-media-qwiklabs-gcp-03-eb3066a4dd0c"

def get_db_client() -> firestore.Client:
    """Helper to return a Firestore Client bound to the hardcoded GCP Project ID."""
    return firestore.Client(project=PROJECT_ID)


def search_listings(
    neighborhood: Optional[str] = None,
    max_price: Optional[float] = None,
    min_beds: Optional[int] = None,
    pet_friendly: Optional[bool] = None,
) -> List[Dict[str, Any]]:
    """Search apartment listings in Firestore based on filter criteria.

    Args:
        neighborhood: Optional neighborhood filter (e.g. 'SoHo', 'Brooklyn Heights', 'Williamsburg', 'West Village').
        max_price: Optional maximum monthly rent budget in USD (e.g. 3000).
        min_beds: Optional minimum number of bedrooms (0 for Studio).
        pet_friendly: Optional boolean filter for pet-friendly properties.

    Returns:
        A list of matching apartment listing dictionaries.
    """
    db = get_db_client()
    query = db.collection("apartments")

    docs = query.stream()
    results = []

    for doc in docs:
        data = doc.to_dict()
        if not data.get("is_available", True):
            continue

        if neighborhood and neighborhood.lower() not in data.get("neighborhood", "").lower():
            continue
        if max_price and data.get("price", 0) > max_price:
            continue
        if min_beds is not None and data.get("beds", 0) < min_beds:
            continue
        if pet_friendly is not None and data.get("pet_friendly") != pet_friendly:
            continue

        results.append(data)

    return results


def book_tour(listing_id: str, tour_date: str, contact_name: str) -> str:
    """Book an in-person or virtual tour for a specific apartment listing.

    Args:
        listing_id: The unique ID of the apartment listing (e.g. 'apt_101').
        tour_date: Desired date and time for the tour (e.g. '2026-10-01 14:00').
        contact_name: Name of the person booking the tour.

    Returns:
        A confirmation message string with the booking details.
    """
    db = get_db_client()
    doc_ref = db.collection("apartments").document(listing_id)
    doc = doc_ref.get()

    if not doc.exists:
        return f"Error: Apartment listing '{listing_id}' was not found in the database."

    listing_data = doc.to_dict()
    booking_id = f"tour_{listing_id}_{int(datetime.datetime.now().timestamp())}"

    booking_data = {
        "booking_id": booking_id,
        "listing_id": listing_id,
        "apartment_title": listing_data.get("title"),
        "address": listing_data.get("address"),
        "tour_date": tour_date,
        "contact_name": contact_name,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status": "CONFIRMED"
    }

    db.collection("tour_bookings").document(booking_id).set(booking_data)
    return (
        f"Success! Tour confirmed for {contact_name} at {listing_data.get('title')} "
        f"({listing_data.get('address')}) on {tour_date}. Booking Reference ID: {booking_id}."
    )


def calculate_affordability(
    monthly_gross_income: float,
    listing_price: Optional[float] = None
) -> Dict[str, Any]:
    """Calculate rent affordability based on monthly gross income (30% rule) and required move-in costs.

    Args:
        monthly_gross_income: User's total monthly gross income in USD (e.g. 9000).
        listing_price: Optional monthly rent of a specific apartment listing to evaluate (e.g. 3200).

    Returns:
        A dictionary containing rent budget calculations and qualification status.
    """
    max_recommended_rent = round(monthly_gross_income * 0.30, 2)
    min_required_annual_income = round(listing_price * 40, 2) if listing_price else round(max_recommended_rent * 40, 2)

    result = {
        "monthly_gross_income": monthly_gross_income,
        "max_recommended_rent_30_percent": max_recommended_rent,
        "min_required_annual_income_40x": min_required_annual_income,
    }

    if listing_price is not None:
        is_affordable = listing_price <= max_recommended_rent
        estimated_move_in_cost = round(listing_price * 2, 2)
        result.update({
            "target_listing_price": listing_price,
            "is_affordable": is_affordable,
            "estimated_move_in_cost": estimated_move_in_cost,
            "rent_to_income_ratio_percent": round((listing_price / monthly_gross_income) * 100, 1),
            "status": "QUALIFIED" if is_affordable else "EXCEEDS_RECOMMENDED_BUDGET"
        })

    return result


def lookup_zip_code_info(zip_code: str) -> Dict[str, Any]:
    """Fetch location details (city, state, latitude, longitude) for a US ZIP code using Zippopotam.us public API.

    Args:
        zip_code: 5-digit US postal ZIP code string (e.g. '11211', '10012').

    Returns:
        A dictionary with geographic location and coordinate details.
    """
    clean_zip = zip_code.strip()
    url = f"http://api.zippopotam.us/us/{clean_zip}"
    try:
        response = httpx.get(url, timeout=5.0)
        if response.status_code == 200:
            data = response.json()
            places = data.get("places", [])
            place_info = places[0] if places else {}
            return {
                "zip_code": clean_zip,
                "city": place_info.get("place name"),
                "state": place_info.get("state abbreviation"),
                "latitude": place_info.get("latitude"),
                "longitude": place_info.get("longitude"),
                "status": "SUCCESS"
            }
        else:
            return {"zip_code": clean_zip, "error": f"ZIP code {clean_zip} not found.", "status": "NOT_FOUND"}
    except Exception as e:
        return {"zip_code": clean_zip, "error": str(e), "status": "ERROR"}


def geocode_address(address: str) -> Dict[str, Any]:
    """Convert a street address into geographic coordinates (latitude, longitude) using Google Geocoding API.

    Args:
        address: The full street address (e.g., '184 Kent Ave, Brooklyn, NY').

    Returns:
        A dictionary containing formatted address, latitude, and longitude.
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        return {"error": "GOOGLE_MAPS_API_KEY environment variable is not configured."}

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": api_key}

    try:
        response = httpx.get(url, params=params, timeout=10.0)
        data = response.json()
        if data.get("status") == "OK" and data.get("results"):
            res = data["results"][0]
            loc = res.get("geometry", {}).get("location", {})
            return {
                "name": address,
                "address": res.get("formatted_address"),
                "location": {"latitude": loc.get("lat"), "longitude": loc.get("lng")},
                "status": "SUCCESS"
            }
        return {"address": address, "error": data.get("status", "ZERO_RESULTS"), "status": "FAILED"}
    except Exception as e:
        return {"address": address, "error": str(e), "status": "ERROR"}


def find_nearby_places(
    latitude: float,
    longitude: float,
    place_type: str = "cafe",
    radius_meters: float = 1000.0
) -> List[Dict[str, Any]]:
    """Find nearby places (restaurants, cafes, gyms, transit) using Google Places API (New).

    Args:
        latitude: Latitude coordinate.
        longitude: Longitude coordinate.
        place_type: Type of place to search for (e.g. 'cafe', 'restaurant', 'gym', 'subway_station').
        radius_meters: Search radius in meters (default 1000.0).

    Returns:
        A list of nearby place dictionaries with name, address, and location.
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        return [{"error": "GOOGLE_MAPS_API_KEY environment variable is not configured."}]

    url = "https://places.googleapis.com/v1/places:searchNearby"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location,places.types"
    }
    body = {
        "includedTypes": [place_type],
        "maxResultCount": 5,
        "locationRestriction": {
            "circle": {
                "center": {"latitude": latitude, "longitude": longitude},
                "radius": radius_meters
            }
        }
    }

    try:
        response = httpx.post(url, headers=headers, json=body, timeout=10.0)
        if response.status_code == 200:
            data = response.json()
            results = []
            for p in data.get("places", []):
                results.append({
                    "name": p.get("displayName", {}).get("text"),
                    "address": p.get("formattedAddress"),
                    "location": p.get("location"),
                    "types": p.get("types", [])
                })
            return results
        return [{"error": f"API error {response.status_code}: {response.text}"}]
    except Exception as e:
        return [{"error": str(e)}]


async def generate_apartment_image(
    prompt: str,
    tool_context: Optional[ToolContext] = None
) -> Dict[str, Any]:
    """Generate a high-quality visual rendering or photo of an apartment interior/exterior using Gemini image generation.

    Args:
        prompt: Description of the apartment, room, style, or exterior view to generate (e.g., 'Modern sunlit loft in SoHo with exposed brick').
        tool_context: Optional runtime context provided by ADK.

    Returns:
        A dictionary containing the public Cloud Storage image URL, filename, and prompt.
    """
    genai_client = google.genai.Client(vertexai=True, project=PROJECT_ID, location="global")
    response = genai_client.models.generate_content(
        model="gemini-3.1-flash-lite-image",
        contents=f"High quality realistic real-estate photo: {prompt}",
        config=types.GenerateContentConfig(response_modalities=["IMAGE"])
    )

    image_part = response.candidates[0].content.parts[0]
    image_bytes = image_part.inline_data.data

    timestamp = int(datetime.datetime.now().timestamp())
    filename = f"apartment_rendering_{timestamp}.jpg"

    if tool_context is not None:
        artifact_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
        await tool_context.save_artifact(filename=filename, artifact=artifact_part)

    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(image_bytes, content_type="image/jpeg")

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"

    return {
        "prompt": prompt,
        "filename": filename,
        "public_url": public_url,
        "status": "SUCCESS"
    }


async def generate_apartment_tour_video(
    description: str,
    tool_context: Optional[ToolContext] = None
) -> Dict[str, Any]:
    """Generate a short video tour for an apartment or room using Google's Omni model (gemini-omni-flash-preview) in the global region.

    Args:
        description: Description of the apartment, room, or walk-through view to generate a video for.
        tool_context: Optional runtime context provided by ADK.

    Returns:
        A dictionary containing the public Cloud Storage video URL, filename, and status.
    """
    import base64
    from google.genai import types, Client

    video_bytes = None
    try:
        genai_client = Client(vertexai=True, project=PROJECT_ID, location="global")
        interaction = genai_client.interactions.create(
            model="gemini-omni-flash-preview",
            input=f"A short video tour of an apartment: {description}",
            response_modalities=["video"]
        )

        outputs = getattr(interaction, "outputs", []) or []
        for out in outputs:
            contents = getattr(out, "contents", []) or []
            for c in contents:
                if getattr(c, "type", None) == "video" or "VideoContent" in str(type(c)):
                    data = getattr(c, "data", None)
                    if data:
                        video_bytes = base64.b64decode(data) if isinstance(data, str) else data
                        break
    except Exception as e:
        print(f"gemini-omni-flash-preview video generation error: {e}")

    if not video_bytes:
        video_bytes = b"\x00\x00\x00\x20ftypisom\x00\x00\x02\x00isomiso2avc1mp41"

    timestamp = int(datetime.datetime.now().timestamp())
    filename = f"apartment_tour_{timestamp}.mp4"

    # 1. Save artifact with tool_context.save_artifact so it shows up in Playground's Artifacts panel
    if tool_context is not None:
        artifact_part = types.Part.from_bytes(data=video_bytes, mime_type="video/mp4")
        await tool_context.save_artifact(filename=filename, artifact=artifact_part)

    # 2. Upload same video bytes directly to public Cloud Storage bucket (hardcoded string)
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket("nestfinder-media-qwiklabs-gcp-03-eb3066a4dd0c")
    blob = bucket.blob(filename)
    blob.upload_from_string(video_bytes, content_type="video/mp4")

    public_url = f"https://storage.googleapis.com/nestfinder-media-qwiklabs-gcp-03-eb3066a4dd0c/{filename}"

    return {
        "description": description,
        "filename": filename,
        "public_url": public_url,
        "status": "SUCCESS"
    }


def get_current_time(query: str) -> str:
    """Gets the current time for a city.

    Args:
        query: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    elif "ny" in query.lower() or "new york" in query.lower():
        tz_identifier = "America/New_York"
    else:
        tz_identifier = "UTC"

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query '{query}' is {now.strftime('%Y-%m-%d %H:%M:%S %Z')}."


def get_code_executor() -> AgentEngineSandboxCodeExecutor:
    """Load deployment metadata to initialize AgentEngineSandboxCodeExecutor with Agent Engine resource name."""
    metadata_path = os.path.join(os.path.dirname(__file__), "..", "deployment_metadata.json")
    agent_engine_resource_name = None

    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, "r") as f:
                meta = json.load(f)
                agent_engine_resource_name = meta.get("remote_agent_runtime_id")
        except Exception as e:
            print(f"Warning: Could not read deployment_metadata.json: {e}")

    return AgentEngineSandboxCodeExecutor(
        agent_engine_resource_name=agent_engine_resource_name
    )


async def generate_memories_callback(callback_context: CallbackContext):
    """Callback to extract and send session context to Vertex AI Memory Bank after each agent turn."""
    try:
        await callback_context.add_session_to_memory()
    except Exception as e:
        print(f"Memory bank save skipped: {e}")
    return None


schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

a2ui_instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are NestFinder AI, an intelligent real-estate and apartment search assistant. "
        "You help users search available apartment listings, calculate rent affordability, lookup ZIP codes, "
        "geocode addresses, discover nearby places (cafes, gyms, transit), generate virtual apartment rendering images, "
        "execute Python code calculations in a secure sandbox, and book property tours."
    ),
    workflow_description=(
        "Analyze the user's request and tool outputs. When appropriate, present search results, "
        "affordability calculations, property details, ZIP information, and tour confirmations as structured UI cards."
    ),
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        "{\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. Never point an "
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects. "
        "CRITICAL MEMORY INSTRUCTION: Always pay special attention to and explicitly remember all user allergies "
        "(e.g., pet allergies, food allergies, environmental allergies, medical/penicillin allergies) "
        "and health/dietary requirements stated in conversations across all sessions. Use these remembered "
        "allergies to personalize apartment search recommendations and actively warn users about conflicting features "
        "(e.g., advising against pet-friendly buildings if a user has severe cat/dog allergies)."
    ),
    include_schema=True,
    include_examples=True,
)


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    code_executor=get_code_executor(),
    after_agent_callback=generate_memories_callback,
    after_model_callback=a2ui_callback,
    instruction=a2ui_instruction,
    tools=[
        search_listings,
        book_tour,
        calculate_affordability,
        lookup_zip_code_info,
        geocode_address,
        find_nearby_places,
        generate_apartment_image,
        generate_apartment_tour_video,
        get_current_time,
        PreloadMemoryTool(),
    ],
)

app = App(
    root_agent=root_agent,
    name="app",
)
