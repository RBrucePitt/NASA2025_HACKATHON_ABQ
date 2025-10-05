import pandas as pd
import folium
from folium.plugins import TimestampedGeoJson
import json
import requests
import io # To read CSV data from an API response
from datetime import datetime, timedelta

# --- Configuration ---
OUTPUT_FILENAME = "firms_terra_fire_map.html"
# IMPORTANT: Replace "YOUR_FIRMS_MAP_KEY_HERE" with the actual key you received from NASA FIRMS.
# You can register for a free key here: https://firms.modaps.eosdis.nasa.gov/api/map_key/
MAP_KEY = "c8520428d33d58670dba043925d04758" 

# Define the Area of Interest (West, South, East, North) - Western US Example
AREA_COORDS = "-125,30,-110,45"
DAYS_TO_QUERY = 7
FIRMS_SOURCE = "MODIS_NRT" # Near Real-Time MODIS data (Terra and Aqua)

START_LOCATION = [37.7749, -122.4194] # Centered near San Francisco, USA
START_ZOOM = 5

def fetch_firms_data(area_coords: str, days: int, source: str, map_key: str) -> pd.DataFrame:
    """
    Fetches real active fire data from the NASA FIRMS API as a Pandas DataFrame.
    
    If the MAP_KEY is not set or the request fails, it returns an empty DataFrame.
    """
    if map_key == "YOUR_FIRMS_MAP_KEY_HERE" or not map_key:
        print("ERROR: MAP_KEY is not set. Cannot fetch real data.")
        return pd.DataFrame()

    base_url = "https://firms.modaps.eosdis.nasa.gov/api/area/csv"
    api_url = f"{base_url}/{map_key}/{source}/{area_coords}/{days}"
    
    print(f"Fetching data from FIRMS API for the last {days} days...")
    print(f"URL: {api_url}")

    try:
        response = requests.get(api_url, timeout=30)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        
        # Check if the response is an error message instead of CSV
        if 'Error' in response.text or 'Invalid' in response.text:
            print(f"FIRMS API returned an error: {response.text.strip()}")
            return pd.DataFrame()

        # Use io.StringIO to read the text response directly as a CSV file
        df = pd.read_csv(io.StringIO(response.text))
        
        # Standard FIRMS columns for MODIS NRT: latitude, longitude, bright_ti4, acq_date, acq_time, confidence
        df = df.rename(columns={'bright_ti4': 'brightness'})
        
        # Ensure only Terra (T) and Aqua (A) data is processed for time-lapse (optional filtering)
        # Note: MODIS_NRT returns data from both Terra (T) and Aqua (A) which is fine for the map.
        
        # Filter out rows missing essential data
        df = df.dropna(subset=['latitude', 'longitude', 'acq_date', 'acq_time', 'brightness'])
        
        if df.empty:
            print("Successfully fetched data, but dataset is empty (no fires detected in area/timeframe).")
            return df
        
        # Calculate the size and color based on brightness (using same logic as mock data)
        df['size'] = df['brightness'].apply(lambda x: 5 + (x - 300) / 30 if x > 300 else 5) # Marker size
        df['color'] = df['brightness'].apply(lambda x: 
            '#d95f0e' if x > 400 else ('#feb24c' if x > 350 else '#ffffb2')) # Color gradient
            
        # Combine date and time into a single datetime object for GeoJSON
        # acq_time is typically HHMM format (e.g., 1425 for 14:25 UTC)
        df['timestamp'] = pd.to_datetime(
            df['acq_date'] + ' ' + 
            df['acq_time'].astype(str).str.zfill(4).str.slice(0, 2) + ':' + 
            df['acq_time'].astype(str).str.zfill(4).str.slice(2, 4), 
            utc=True,
            errors='coerce' # Handle invalid time formats gracefully
        )
        
        # Drop rows where timestamp parsing failed
        df = df.dropna(subset=['timestamp'])

        print(f"Successfully retrieved {len(df)} fire detections.")
        return df

    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")
    except Exception as e:
        print(f"A general processing error occurred: {e}")
        
    return pd.DataFrame()


def create_geojson_feature(df):
    """
    Converts the Pandas DataFrame into a GeoJSON structure suitable for 
    Folium's TimestampedGeoJson plugin.
    """
    features = []
    
    for _, row in df.iterrows():
        # Generate Detail URL 
        DETAIL_BURN_URL = "https://worldview.earthdata.nasa.gov/?v=-110.466006321163,32.312894812006256,-106.55172797386264,34.17319637029353&as=2012-05-09-T00%3A00%3A00Z&ae=2012-06-25-T00%3A00%3A00Z&l=Reference_Labels_15m,Reference_Features_15m,MODIS_Terra_L3_Land_Water_Mask(disabled=1),MODIS_Terra_NDVI_8Day(hidden,max=0.6201),MODIS_Combined_Thermal_Anomalies_All(palette=red),MODIS_Combined_L3_IGBP_Land_Cover_Type_Annual(opacity=0.5,disabled=16-17-12),MODIS_Terra_CorrectedReflectance_TrueColor&lg=true&av=1.5&ab=on&t=2012-05-09-T16%3A00%3A00Z"
        DETAIL_VEG_URL = "https://worldview.earthdata.nasa.gov/?v=-110.43888934801736,31.758194077444163,-107.07533711225106,34.19409996247332&ics=true&ici=3&icd=2&as=2012-05-09-T00%3A00%3A00Z&ae=2012-12-09-T00%3A00%3A00Z&l=Reference_Labels_15m,Reference_Features_15m,MODIS_Combined_Thermal_Anomalies_All(palette=red),MODIS_Combined_L3_IGBP_Land_Cover_Type_Annual(opacity=0.5,disabled=16-17-12),MODIS_Terra_CorrectedReflectance_TrueColor(opacity=0.9)&lg=true&av=1.5&ab=on"
        # Each feature represents a single fire detection event
        feature = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                # Folium/GeoJSON uses [Longitude, Latitude] order
                # 'coordinates': [row['longitude'], row['latitude']], 
                'coordinates': [-108.3451, 33.2828],
            },
            # 'times' is the critical property for the time slider
            'properties': {
                # Time must be an ISO 8601 string or epoch milliseconds
                'times': [row['timestamp'].isoformat()], 
                
                # Style properties
                'icon': 'circle',
                'iconstyle': {
                    'fillColor': row['color'],
                    'fillOpacity': 0.8,
                    'stroke': 'false',
                    'radius': row['size'],
                    'shadowRadius': 0,
                    'shadowOpacity': 0
                },
                
                # Popup data for when the user clicks a marker
                'popup': (
                    f"<b>Fire Detection ({row['satellite']})</b><br>"
                    f"Time: {row['timestamp'].strftime('%Y-%m-%d %H:%M UTC')}<br>"
                    f"Brightness: {row['brightness']:.1f} K<br>"
                    f"Confidence: {row['confidence']}<br>"
                    f"<a href='" + DETAIL_BURN_URL + "'>Fire</a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
                    f"<a href='" + DETAIL_VEG_URL + "'>Vegetation Recovery</a><br>"
                )
            }
        }
        features.append(feature)
        
    # The GeoJSON structure must be a FeatureCollection
    geojson_data = {
        'type': 'FeatureCollection',
        'features': features
    }
    
    return json.dumps(geojson_data)

def create_fire_map():
    """
    Main function to generate data, create the map, and save the HTML file.
    """
    
    # 1. Fetch Real Data
    fire_df = fetch_firms_data(
        area_coords=AREA_COORDS, 
        days=DAYS_TO_QUERY, 
        source=FIRMS_SOURCE, 
        map_key=MAP_KEY
    )
    
    if fire_df.empty:
        print("Error: No fire data available to map. Please check your MAP_KEY, AREA_COORDS, and network connection.")
        # If real data fetching fails, we can optionally fall back to mock data
        # but for this update, we will simply stop and inform the user.
        return

    # 2. Convert to GeoJSON format
    geojson_data = create_geojson_feature(fire_df)

    # 3. Create the Folium Map
    m = folium.Map(
        location=START_LOCATION, 
        zoom_start=START_ZOOM, 
        tiles="Esri.WorldImagery" # Changed to satellite view for daytime surface context
    )

    # 4. Add the TimestampedGeoJson Layer for Playback
    TimestampedGeoJson(
        geojson_data,
        period='PT1H', # Time step duration: 1 hour (PT1H)
        duration='PT12H', # How long each point remains visible: 12 hours
        add_last_point=True,
        auto_play=False, # Start paused
        loop=False,
        transition_time=500, # Transition speed in milliseconds
        # The slider will be labelled with the time from the 'times' property
        date_options='YYYY-MM-DD HH:mm:ss'
    ).add_to(m)
    
    # 5. Add a Legend (simple HTML/CSS)
    # Legend style updated for visibility over satellite imagery
    legend_html = """
         <div style="position: fixed; 
                     bottom: 50px; left: 50px; width: 180px; height: 120px; 
                     border:2px solid #555; z-index:9999; font-size:13px;
                     background-color: rgba(0, 0, 0, 0.7); color: white; opacity: 0.95; 
                     padding: 10px; border-radius: 8px;">
           &nbsp; <b>MODIS Fire Brightness</b> <br>
           &nbsp; <i style="background:#d95f0e; border-radius: 50%; display: inline-block; width: 10px; height: 10px;"></i> > 400 K (High) <br>
           &nbsp; <i style="background:#feb24c; border-radius: 50%; display: inline-block; width: 10px; height: 10px;"></i> 350-400 K (Medium) <br>
           &nbsp; <i style="background:#ffffb2; border-radius: 50%; display: inline-block; width: 10px; height: 10px;"></i> 300-350 K (Low)
        </div>
        """
    m.get_root().html.add_child(folium.Element(legend_html))


    # 6. Save the map to HTML
    m.save(OUTPUT_FILENAME)
    
    print(f"\n--- SUCCESS ---")
    print(f"Interactive map saved to: {OUTPUT_FILENAME}")
    print(f"Note: This map now uses real data from the NASA FIRMS API (MODIS NRT).")

if __name__ == "__main__":
    create_fire_map()
