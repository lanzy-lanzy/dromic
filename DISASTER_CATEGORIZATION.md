# Disaster Categorization Implementation

## Overview
This document describes the implementation of disaster categorizations and dynamic date handling for the disaster management system.

## Changes Made

### 1. Database Model (models.py)
- Added `category` field to the `Disaster` model
- Category choices include:
  - Typhoon
  - Earthquake
  - Flood
  - Landslide
  - Volcanic Eruption
  - Drought
  - Tsunami
  - Wildfire
  - Storm Surge
  - Other (default)

### 2. Database Migration
- Created migration file: `0005_disaster_category.py`
- Adds the new `category` field to the Disaster table with a default value of 'other'

### 3. Backend Views (views.py)
- **get_disasters()**: Updated to include `category` in the API response
- **create_disaster()**: Updated to accept and save the `category` field
- **edit_disaster()**: Updated to handle category field updates

### 4. Frontend Template (disaster_info.html)
- **Add Modal**: 
  - Added category dropdown field with all available categories
  - Positioned between name and description fields
  
- **Edit Modal**: 
  - Added category dropdown field matching the add modal
  
- **Card View**: 
  - Displays category as a blue badge below description
  - Format: `category.replace('_', ' ')` for better readability
  
- **Table View**: 
  - Added category column between name and description
  - Displays category as a blue badge for consistency

### 5. Frontend JavaScript (disaster_info.js)
- **editDisaster()**: Updated to populate the category field when opening edit modal
  
- **saveDisaster()**: 
  - Checks if a disaster with the same name and category already exists
  - If it does and no date is provided, automatically uses the existing disaster's date
  - This prevents duplicate disasters with different dates
  
- **updateDisaster()**: 
  - Similar logic to saveDisaster() for updates
  - Checks for other disasters with the same name and category
  - Auto-fills date from existing records if not provided

### 6. Admin Interface (admin.py)
- Updated `DisasterAdmin` to:
  - Display `category` in the list view
  - Allow filtering by `category` and `date_occurred`

## Dynamic Date Handling

When creating or updating a disaster:
1. System checks if a disaster with the **same name AND category** already exists
2. If one exists and the user doesn't provide a date:
   - The existing disaster's date is automatically used
   - This prevents creating duplicate disasters with different dates
3. If the user explicitly provides a different date, it will be used as provided

### Benefits:
- Prevents accidental duplicate records for the same disaster
- Ensures consistency when multiple affected areas report the same disaster
- Allows users to focus on category selection for quick disaster identification

## Usage

### Creating a Disaster:
1. Click "Add New Disaster"
2. Fill in name, select category, add description, and optionally set date
3. If a disaster with the same name+category exists, its date will be auto-used
4. Click "Save Disaster"

### Editing a Disaster:
1. Click edit icon on a disaster card/row
2. Category field will be pre-populated
3. Update any fields as needed
4. Click "Update Disaster"

### Viewing Disasters:
- **Card View**: Shows category as a blue badge
- **Table View**: Dedicated category column for easy sorting and filtering

## Database Migration Steps

To apply the changes to your database:

```bash
python manage.py migrate
```

This will create the `category` column in the Disaster table with a default value of 'other' for existing records.

## Testing

1. Create a new disaster with a name and category
2. Try creating another disaster with the same name but different category
3. Try creating a duplicate (same name + category) - the date should auto-populate from the first record
4. Edit a disaster and verify the category field is correctly loaded
5. Check both card and table views to ensure category is displayed correctly
