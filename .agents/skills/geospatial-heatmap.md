# Geospatial Safety Heatmap

## Description
Real-time geospatial layer over plant layout showing dynamic risk zones.

## Technical Requirements
- **Library**: Folium (Python) for HTML map generation
- **Data Sources**: Worker UWB positions, hazard zone polygons, permit areas
- **Features**:
  - Dynamic color coding (Green → Yellow → Orange → Red)
  - Worker positions as dots
  - Permit boundaries as overlays
  - Layer control for toggling views

## Implementation Steps
1. Create `src/backend/geospatial/heatmap.py`
2. Define plant zones as GeoJSON polygons
3. Update heatmap every 5 seconds with new data
4. Generate self-contained HTML file for dashboard

## Deliverables
- [ ] Interactive plant map
- [ ] Real-time worker tracking
- [ ] Dynamic risk zone coloring
- [ ] Permit boundary overlay
