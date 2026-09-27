# 💬 NestFinder AI — Prompts & Responses Documentation

This document contains a reference guide of example prompts, user interaction scenarios, expected agent responses, and tool calls supported by **NestFinder AI**.

---

## 📋 Table of Contents
1. [Apartment Search & Database Queries](#1-apartment-search--database-queries)
2. [AI Visual Image Generation](#2-ai-visual-image-generation)
3. [Virtual Video Tour Generation](#3-virtual-video-tour-generation)
4. [Rent Affordability Analysis](#4-rent-affordability-analysis)
5. [Google Maps & Neighborhood Discovery](#5-google-maps--neighborhood-discovery)
6. [Property Tour Booking](#6-property-tour-booking)

---

## 1. Apartment Search & Database Queries

### Prompt
> `"Search 2BR apartment listings in SoHo under $4000"`

### Tool Called
* `search_listings(neighborhood="SoHo", max_price=4000, min_beds=2)`

### Agent Response & UI Output
```
I found 1 available listing in SoHo matching your criteria:

• Modern Sunlit Loft
  - Address: 120 Spring St, SoHo, New York, NY
  - Price: $3,800/month
  - Bedrooms / Bathrooms: 2 Beds / 2 Baths
  - Pet Policy: Pets Allowed
  - Amenities: Exposed brick, hard-wood floors, high ceilings, in-unit washer/dryer
```

---

## 2. AI Visual Image Generation

### Prompt
> `"Generate a visual rendering of a modern sunlit living room in SoHo with exposed brick"`

### Tool Called
* `generate_apartment_image(prompt="a modern sunlit living room in SoHo with exposed brick, large windows, minimalist furniture")`

### Agent Response & UI Output
```
I have generated a high-definition visual rendering for your living room concept in SoHo!

[Image Rendered Inline via A2UI Card & Stored in Cloud Storage]
Public Media URL: https://storage.googleapis.com/nestfinder-media-qwiklabs-gcp-03-eb3066a4dd0c/soho_living_room.png
```

---

## 3. Virtual Video Tour Generation

### Prompt
> `"Generate a virtual apartment tour video for a luxury 2BR loft in SoHo"`

### Tool Called
* `generate_apartment_tour_video(apartment_name="Luxury 2BR Loft in SoHo", style="modern luxury with hardwood floors and city views")`

### Agent Response & UI Output
```
Here is your virtual apartment tour video created with Google's Omni model (gemini-omni-flash-preview):

[Video Player Rendered via A2UI Video Component]
Public Video URL: https://storage.googleapis.com/nestfinder-media-qwiklabs-gcp-03-eb3066a4dd0c/tour_luxury_2br_loft.mp4
```

---

## 4. Rent Affordability Analysis

### Prompt
> `"I make an annual salary of $120,000. What is my recommended maximum monthly rent budget?"`

### Tool Called
* `calculate_affordability(annual_income=120000)`

### Agent Response & UI Output
```
Based on the standard 30% gross income rule for housing affordability:

• Monthly Gross Income: $10,000
• Recommended Max Rent (30%): $3,000 / month
• Conservative Housing Range: $2,500 – $3,000 / month

I can help you search for available listings within the $2,500 – $3,000 range in your preferred neighborhood!
```

---

## 5. Google Maps & Neighborhood Discovery

### Prompt
> `"Find nearby transit stations, cafes, and parks for 120 Spring St, SoHo, NY"`

### Tools Called
1. `geocode_address(address="120 Spring St, SoHo, New York, NY")`
2. `find_nearby_places(latitude=40.7252, longitude=-74.0001, place_type="transit_station,cafe,park")`

### Agent Response & UI Output
```
Here are nearby points of interest around 120 Spring St, SoHo:

• Transit & Subways:
  - Spring St Station (C, E train) — 0.1 miles
  - Prince St Station (N, R, W train) — 0.2 miles

• Cafes & Coffee Shops:
  - Felix Roasting Co. — 0.1 miles
  - Balthazar Bakery — 0.2 miles

• Parks & Outdoor Spaces:
  - Vesuvio Playground & Park — 0.2 miles
```

---

## 6. Property Tour Booking

### Prompt
> `"Schedule a virtual tour for Modern Sunlit Loft in SoHo on Saturday at 2 PM"`

### Tool Called
* `book_tour(listing_id="soho_120_spring", date="2026-10-03", time="14:00", tour_type="virtual")`

### Agent Response & UI Output
```
Your virtual tour request has been confirmed!

• Property: Modern Sunlit Loft (120 Spring St, SoHo)
• Tour Type: Virtual Walk-through
• Date & Time: Saturday, October 3, 2026 at 2:00 PM EST
• Confirmation Code: TOUR-SOHO-8842

A calendar invite with the video link has been prepared for you.
```
