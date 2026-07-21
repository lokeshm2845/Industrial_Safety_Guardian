
import folium
import json
import os

# Define the coordinates for the 5 mock refinery plant zones
ZONE_POLYGONS = {
    "Zone A": [[22.4700, 70.0700], [22.4720, 70.0700], [22.4720, 70.0720], [22.4700, 70.0720]],
    "Zone B": [[22.4700, 70.0720], [22.4720, 70.0720], [22.4720, 70.0740], [22.4700, 70.0740]],
    "Zone C": [[22.4680, 70.0700], [22.4700, 70.0700], [22.4700, 70.0720], [22.4680, 70.0720]],
    "Zone D": [[22.4680, 70.0720], [22.4700, 70.0720], [22.4700, 70.0740], [22.4680, 70.0740]],
    "Zone E": [[22.4720, 70.0700], [22.4740, 70.0700], [22.4740, 70.0740], [22.4720, 70.0740]]
}

def get_risk_color(score: float) -> str:
    """
    Map risk score to corresponding color code.
    """
    if score < 0.3:
        return "#2ecc71"  # Green
    elif score < 0.5:
        return "#f1c40f"  # Yellow
    elif score < 0.8:
        return "#e67e22"  # Orange
    else:
        return "#e74c3c"  # Red

def generate_heatmap_html(zone_risks: dict, workers: list, permits: list) -> str:
    """
    Generate an interactive Folium map representing the plant safety status.
    Returns: HTML representation of the map.
    """
    # Center map on the plant coordinates
    m = folium.Map(location=[22.4710, 70.0720], zoom_start=16, control_scale=True, tiles="OpenStreetMap")

    # Add zone polygons
    for zone_name, coords in ZONE_POLYGONS.items():
        # Get evaluation details for the zone
        risk_detail = zone_risks.get(zone_name, {"risk_score": 0.0, "reasons": ["Normal Operations"]})
        risk_score = risk_detail["risk_score"]
        reasons = risk_detail["reasons"]
        
        color = get_risk_color(risk_score)
        
        # Format zone tooltip/popup text
        reasons_html = "<br>".join([f"• {r}" for r in reasons])
        popup_content = f"""
        <div style="font-family: Arial, sans-serif; min-width: 200px;">
            <h4 style="margin: 0 0 5px 0; color: #333;">{zone_name}</h4>
            <p><b>Risk Score:</b> <span style="color: {color}; font-weight: bold;">{risk_score}</span></p>
            <p><b>Status Details:</b><br>{reasons_html}</p>
        </div>
        """
        
        # Add polygon overlay for the zone
        folium.Polygon(
            locations=coords,
            color=color,
            weight=3,
            fill=True,
            fill_color=color,
            fill_opacity=0.35,
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=f"{zone_name} - Risk: {risk_score}"
        ).add_to(m)

    # Add Assembly Point Marker
    folium.Marker(
        location=[22.4750, 70.0750],
        icon=folium.Icon(color="green", icon="ok-sign"),
        tooltip="Safe Assembly Point (Muster Gate 2)",
        popup="<b>Muster Gate 2</b><br>Primary emergency assembly station with medical responders."
    ).add_to(m)

    # Plot permit boundaries (using markers or small polygon badges)
    for p in permits:
        if p["status"] != "Active":
            continue
        # Find a center coordinate for the zone
        zone_coords = ZONE_POLYGONS.get(p["zone"])
        if zone_coords:
            center_lat = sum(c[0] for c in zone_coords) / len(zone_coords)
            center_lon = sum(c[1] for c in zone_coords) / len(zone_coords)
            
            # Place permit indicators on the map
            icon_color = "red" if p["type"] == "Hot Work" else "blue"
            popup_text = f"""
            <div style="font-family: Arial, sans-serif;">
                <b>Permit:</b> {p['permit_id']}<br>
                <b>Type:</b> {p['type']}<br>
                <b>Desc:</b> {p['description']}<br>
                <b>LOTO:</b> {p['loto_status']}
            </div>
            """
            folium.Marker(
                location=[center_lat + 0.0002, center_lon],  # slightly offset from center
                icon=folium.Icon(color=icon_color, icon="info-sign"),
                popup=folium.Popup(popup_text, max_width=250),
                tooltip=f"PTW: {p['permit_id']} ({p['type']})"
            ).add_to(m)

    # Plot workers and routing
    for w in workers:
        # Determine safety status
        zone_name = w["zone"]
        zone_risk_detail = zone_risks.get(zone_name, {"risk_score": 0.0})
        risk_score = zone_risk_detail.get("risk_score", 0.0)
        
        is_critical_alert = any(zr.get("risk_score", 0.0) >= 0.8 for zr in zone_risks.values())
        
        # Color coding state
        if is_critical_alert and zone_name == "Zone A":
            # Worker evacuated to assembly point
            worker_status = "Evacuated"
            status_color = "#3498db"
            worker_color = "#2980b9"
        elif risk_score >= 0.8:
            worker_status = "In Danger Zone"
            status_color = "#e74c3c"
            worker_color = "#c0392b"
        elif risk_score >= 0.5:
            worker_status = "Elevated Risk"
            status_color = "#e67e22"
            worker_color = "#d35400"
        else:
            worker_status = "Safe"
            status_color = "#2ecc71"
            worker_color = "#27ae60"

        # Construct digital ID popup
        popup_text = f"""
        <div style="font-family: 'Outfit', 'Inter', sans-serif; padding: 10px; border-radius: 8px; background: #1e293b; color: white; border-top: 4px solid {status_color}; min-width: 180px;">
            <div style="font-size: 9px; text-transform: uppercase; color: #94a3b8; font-weight: bold; letter-spacing: 0.5px;">UWB Digital ID</div>
            <div style="font-size: 13px; font-weight: bold; margin-top: 2px; color: #ffffff;">{w['name']}</div>
            <div style="font-size: 11px; color: #94a3b8; margin-bottom: 6px;">{w['role']}</div>
            <hr style="border: 0; border-top: 1px solid #334155; margin: 4px 0;" />
            <div style="font-size: 11px; color: #cbd5e1; line-height: 1.4;">
                <b>Active Zone:</b> {zone_name}<br>
                <b>Blood Group:</b> {w.get('blood_group', 'O+')}<br>
                <b>Fitness:</b> {w.get('medical_clearance', 'FIT')}<br>
                <b>UWB Tag:</b> {w.get('uwb_tag_id', w['worker_id'])}
            </div>
            <div style="margin-top: 8px; display: inline-block; padding: 2px 6px; border-radius: 4px; font-size: 9px; font-weight: bold; background: {status_color}; color: white;">{worker_status}</div>
        </div>
        """
        
        # Plot worker circle
        folium.CircleMarker(
            location=[w["lat"], w["lon"]],
            radius=7,
            color=worker_color,
            fill=True,
            fill_color=worker_color,
            fill_opacity=0.9,
            popup=folium.Popup(popup_text, max_width=220),
            tooltip=f"{w['name']} ({w['role']}) - {worker_status}"
        ).add_to(m)

        # Draw Smart Evacuation Route if risk is high (>= 0.8) and worker is near or in the area
        if risk_score >= 0.8 or (is_critical_alert and zone_name == "Zone A"):
            # Route starting from worker coordinate, bypassing the danger zone center, to Assembly point
            start_coord = [w["lat"], w["lon"]]
            end_coord = [22.4750, 70.0750]
            
            # Simple bypass node: offset slightly to route around the hazard polygon center
            if zone_name == "Zone A":
                # Route around Zone A to the East, then North
                bypass_coord = [22.4725, 70.0735]
            elif zone_name == "Zone C":
                # Route around Zone C to the West, then North
                bypass_coord = [22.4700, 70.0690]
            else:
                bypass_coord = [22.4730, 70.0720]
                
            route_coords = [start_coord, bypass_coord, end_coord]
            
            folium.PolyLine(
                locations=route_coords,
                color="#00bcd4",
                weight=3,
                dash_array="6, 6",
                tooltip=f"Evacuation Path for {w['name']} (Muster Gate 2)",
                popup=f"<b>Dynamic Evacuation Routing</b><br>Path: Bypass {zone_name} hazard corridor -> Assembly Gate 2."
            ).add_to(m)

    # Return map as HTML string
    return m._repr_html_()

