import os
import re
import requests
from datetime import datetime, timedelta
from html.parser import HTMLParser

SCENE_DIR = "s1_downloads_decending"  # Directory with Sentinel-1 zip files
ORBIT_DIR = "s1_downloads_decending_orbits"  # Directory to save downloaded precice orbits
BASE_URL = "https://step.esa.int/auxdata/orbits/Sentinel-1/POEORB" # ESA STEP Precise Orbits base URL

class HREFParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.files = []
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr in attrs:
                if attr[0] == 'href':
                    if attr[1].endswith('.EOF.zip'):
                        self.files.append(attr[1])

def get_files_from_url(url):
        response = requests.get(url, timeout=20)
        if response.status_code != 200: return []
        parser = HREFParser()
        parser.feed(response.text)
        return parser.files

def parse_validity_from_filename(filename):
    # Matches: S1A_..._V20231005T225942_20231007T005942.EOF.zip
    match = re.search(r'_V(\d{8}T\d{6})_(\d{8}T\d{6})', filename)
    if match:
        t_start = datetime.strptime(match.group(1), "%Y%m%dT%H%M%S")
        t_end   = datetime.strptime(match.group(2), "%Y%m%dT%H%M%S")
        return t_start, t_end
    return None, None

# --- MAIN SCRIPT ---

zip_files = [f for f in os.listdir(SCENE_DIR) if f.endswith('.zip') and f.startswith('S1')]
print(f"Found {len(zip_files)} scenes. Starting ESA STEP search...")

dir_cache = {} 

# Name pattern to extract platform and date from filename EXAMPE:  S1A_IW_GRDH_1SDV_20250915T042342_20250915T042407_045678_055A3B_1234.zip
name_pattern = re.compile(r'(S1[ABC])_.*_(\d{8}T\d{6})_')

for zip_file in zip_files:
    match = name_pattern.match(zip_file)


    platform = match.group(1) # e.g. S1A
    date_str = match.group(2) # e.g. 20250915T042342

    scene_time = datetime.strptime(date_str, "%Y%m%dT%H%M%S")


    print(f"\n Processing>> {zip_file} ({platform})")
    
    # 2. Check Current Month + Next Month
    months_to_check = [scene_time, scene_time + timedelta(days=31)]
    
    found_orbit = None
    
    for d in months_to_check:
        year = d.strftime("%Y")
        month = d.strftime("%m")
        
        # S1C has its own folder now (e.g. S1C/2025/09)
        search_path = f"{platform}/{year}/{month}"
        full_url = f"{BASE_URL}/{search_path}/"
        
        if search_path not in dir_cache:
            dir_cache[search_path] = get_files_from_url(full_url)
            
        file_list = dir_cache[search_path]
        
        for fname in file_list:
            v_start, v_end = parse_validity_from_filename(fname)
            if v_start and v_end:
                if v_start <= scene_time <= v_end:
                    found_orbit = fname
                    break 
        
        if found_orbit: break

    # 3. Download
    if found_orbit:
        orbit_url = f"{BASE_URL}/{search_path}/{found_orbit}"
        local_path = os.path.join(ORBIT_DIR, found_orbit)
        
        if os.path.exists(local_path):
            print(f">>file already exists {found_orbit}")
        else:
            print(f"Downloading orbit file <<< {found_orbit}")
            try:
                r = requests.get(orbit_url, stream=True)
                if r.status_code == 200:
                    with open(local_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print("Done Downloading")
                else:
                    print(f" >> HTTP Error {r.status_code}")
            except Exception as e:
                print(f"Download Failed: {e}")
    else:
        print(f">> No Precise Orbit found for {scene_time}")
