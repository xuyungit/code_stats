# Files Changed Column Fix

## Issue
The "FILES CHANGED" column in the Daily Statistics Table showed "N/A" for all entries despite the data being present in the database.

## Root Cause
There was a naming mismatch between the backend API and frontend:
- **Backend API**: Returns `files_changed` field in the response
- **Frontend**: Expected `total_files_changed` field in the TypeScript interface and template

## Investigation Steps
1. **Database Schema**: Confirmed `files_changed` column exists in `daily_author_stats` table
2. **Database Data**: Verified data exists for repository 6 with proper values
3. **API Implementation**: Confirmed backend returns `files_changed` in the response models
4. **Frontend Code**: Found the mismatch in TypeScript interface and Vue template

## Solution
Updated the frontend to use `files_changed` instead of `total_files_changed`:

1. **TypeScript Interface** (`RepositoryStatsView.vue`):
   ```typescript
   // Changed from:
   total_files_changed: number
   // To:
   files_changed: number
   ```

2. **Vue Template** (`RepositoryStatsView.vue`):
   ```vue
   <!-- Changed from: -->
   {{ stat.total_files_changed?.toLocaleString() || 'N/A' }}
   <!-- To: -->
   {{ stat.files_changed?.toLocaleString() || 'N/A' }}
   ```

3. **Tooltip** (Chart.js callback):
   ```javascript
   // Changed from:
   `Files Changed: ${stat.total_files_changed || 'N/A'}`
   // To:
   `Files Changed: ${stat.files_changed || 'N/A'}`
   ```

## Result
The "FILES CHANGED" column now correctly displays the data from the database instead of showing "N/A".

## Affected Files
- `/Users/xuyun/AI/code_stats/frontend/src/views/RepositoryStatsView.vue`

## Note
This fix maintains consistency with the backend API naming convention. The field is named `files_changed` throughout the backend (database schema, models, and API responses), so the frontend should match this naming.