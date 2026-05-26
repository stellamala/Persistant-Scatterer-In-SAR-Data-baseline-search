import asf_search as asf
import folium
import matplotlib.pyplot as plt
from datetime import datetime
import os

# replace with your token
token='YOUR TOKEN'
DATADIR = "s1_downloads_ascending" # NAME OF DIRECTORY TO SAVE THE FILES 


session = asf.ASFSession().auth_with_token(token)
# Example reference image
# S1A_IW_SLC__1SDV_20231025T162321_20231025T162348_050924_06238D_B618
target_start = "2023-10-25T16:23:48"
target_end   = "2023-10-25T16:23:48"
# Example BBOX for search
wkt_box = "POLYGON ((25.127449 35.240572, 25.000076 35.240572, 25.000076 35.357976, 25.127449 35.357976, 25.127449 35.240572))"

results = asf.search(
    platform=asf.PLATFORM.SENTINEL1,
    processingLevel=asf.PRODUCT_TYPE.SLC,
    start=target_start, 
    end=target_end,
    intersectsWith=wkt_box,
    flightDirection='ASCENDING', #'ASCENDING' or 'DESCENDING' 
    maxResults=1
)


# CHECK IF YOUR REFERENCE IMAGE EXISTS
if len(results) > 0:
    found_scene = results[0]
    print(f"[FOUND]: {found_scene.properties['sceneName']}")
else:
    print(" [ERROR]: Scene not found. Check the date.")
    exit() 

geo_json = found_scene.geojson()
geometry = geo_json['geometry']
center_lat = found_scene.centroid().y
center_lon = found_scene.centroid().x

m = folium.Map(location=[center_lat, center_lon], zoom_start=9)

# Add footprint
folium.GeoJson(
    geometry,
    style_function=lambda x: {'color': 'blue', 'fillOpacity': 0.1}
).add_to(m)

# Add POPUP marker for area of interest (example Voutes Heraklion Greece)
folium.Marker(
    [35.294, 25.078], 
    popup="Voutes", 
    icon=folium.Icon(color="red", icon="home")
).add_to(m)


m.save("search_map.html") 
print("[INFO] : Map saved to 'search_map.html'") #INSPECT SEARCH MAP FOR FOOTPRINT 

print(f"Building stack for: {found_scene.properties['sceneName']}...")
stack = found_scene.stack()

LIMIT_PERP = 100   # Meters   < PERPENDICULAR BASELINE IN METERS
LIMIT_DAYS = 750   # Days     < TEMPORAL BASELINE IN DAYS

selected_scenes = []
baselines_perp = []
baselines_temp = []
dates = []

print(f"Filtering {len(stack)} scenes...")

for scene in stack:
    perp = scene.properties.get('perpendicularBaseline')
    temp = scene.properties.get('temporalBaseline')
    date_str = scene.properties.get('startTime')
    
    if perp is not None and temp is not None and date_str is not None:
        
        # Check filters
        if abs(perp) < LIMIT_PERP and abs(temp) < LIMIT_DAYS:
            
            try:
                clean_date = date_str.rstrip('Z').split('.')[0]
                dt_obj = datetime.strptime(clean_date, '%Y-%m-%dT%H:%M:%S')
            except ValueError:
                print(f"[Warning]: Could not parse date {date_str}. Skipping scene.")
                continue  

            dates.append(dt_obj)
            baselines_perp.append(perp)
            baselines_temp.append(temp)
            selected_scenes.append(scene)

print(f"[INFO]: Filter Complete! Kept {len(selected_scenes)} scenes.")

if len(dates) == 0:
    print("[ERROR]: No scenes matched your criteria. Try increasing LIMIT_PERP.")
    exit()

plt.figure(figsize=(10, 6))


plt.scatter(dates, baselines_perp, c='blue', alpha=0.6, label='Slave Scenes')

try:
    master_idx = baselines_temp.index(0)
    plt.scatter(dates[master_idx], baselines_perp[master_idx], c='red', s=100, label='Master Scene', edgecolors='black')
except ValueError:
    pass 

plt.axhline(0, color='gray', linestyle='--', linewidth=0.8)
plt.title(f'PSI Baseline Plot\nMaster: {found_scene.properties["sceneName"]}')
plt.xlabel('Date')
plt.ylabel('Perpendicular Baseline (m)')
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


if not os.path.exists(DATADIR):
    os.makedirs(DATADIR)

scenes_to_download = []

print(f"Checking {len(selected_scenes)} scenes against local files...")

for scene in selected_scenes:
    filename = scene.properties['fileName']
    file_path = os.path.join(DATADIR, filename)
    
    if os.path.exists(file_path):
        print(f"[INFO]:  Skipping {filename} (Already exists)")
    else:
        scenes_to_download.append(scene)

if len(scenes_to_download) > 0:
    print(f"\n[INFO]: Starting download for {len(scenes_to_download)} new scenes...")
    
    try:
        asf.download_urls(
            urls=[s.properties['url'] for s in scenes_to_download], 
            path=DATADIR, 
            session=session
        )
        print("[INFO] : All new downloads finished!")
        
    except Exception as e:
        print(f"[ERROR]: Download interrupted: {e}")

else:
    print("\n [INFO] : All files are already downloaded! Nothing to do.")