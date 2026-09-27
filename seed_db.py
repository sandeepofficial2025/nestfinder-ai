# Seed script for NestFinder AI Firestore database
import sys
from google.cloud import firestore

# CRITICAL: Hardcode GCP Project ID directly as a string.
# On Agent Engine / Reasoning Engine, GOOGLE_CLOUD_PROJECT returns the project NUMBER,
# which breaks Firestore database resolution.
PROJECT_ID = "qwiklabs-gcp-03-eb3066a4dd0c"

def seed_database():
    print(f"Connecting to Firestore for project: {PROJECT_ID}...")
    db = firestore.Client(project=PROJECT_ID)
    
    sample_apartments = [
        {
            "id": "apt_101",
            "title": "Modern SoHo Loft",
            "neighborhood": "SoHo",
            "price": 3200,
            "beds": 1,
            "baths": 1.0,
            "sqft": 750,
            "pet_friendly": True,
            "address": "120 Spring St, New York, NY",
            "amenities": ["In-unit Laundry", "Balcony", "Gym", "Doorman"],
            "is_available": True
        },
        {
            "id": "apt_102",
            "title": "Brooklyn Heights Studio",
            "neighborhood": "Brooklyn Heights",
            "price": 2450,
            "beds": 0,
            "baths": 1.0,
            "sqft": 500,
            "pet_friendly": True,
            "address": "45 Pierrepont St, Brooklyn, NY",
            "amenities": ["Hardwood Floors", "Dishwasher", "Roof Deck"],
            "is_available": True
        },
        {
            "id": "apt_103",
            "title": "West Village Classic 2BR",
            "neighborhood": "West Village",
            "price": 4800,
            "beds": 2,
            "baths": 2.0,
            "sqft": 1100,
            "pet_friendly": False,
            "address": "88 Perry St, New York, NY",
            "amenities": ["Fireplace", "In-unit Laundry", "Private Garden"],
            "is_available": True
        },
        {
            "id": "apt_104",
            "title": "Williamsburg Luxury 1BR",
            "neighborhood": "Williamsburg",
            "price": 2950,
            "beds": 1,
            "baths": 1.0,
            "sqft": 800,
            "pet_friendly": True,
            "address": "184 Kent Ave, Brooklyn, NY",
            "amenities": ["Gym", "Pool", "Roof Deck", "In-unit Laundry"],
            "is_available": True
        }
    ]

    collection_ref = db.collection("apartments")
    for item in sample_apartments:
        doc_ref = collection_ref.document(item["id"])
        doc_ref.set(item)
        print(f"Seeded document: {item['id']} ({item['title']})")

    print(f"\nSuccessfully seeded {len(sample_apartments)} apartments into Firestore collection 'apartments'!")

if __name__ == "__main__":
    seed_database()
