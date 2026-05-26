#  Persistent Scatterer InSAR Data: Baseline Search

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Sentinel-1](https://img.shields.io/badge/Data-Sentinel--1-lightgrey.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)

A lightweight tutorial and automation toolset designed for faster searching and downloading of **Sentinel-1 Baseline Data** and **Precise Orbit Ephemerides (POEORB)** using the Alaska Satellite Facility (ASF) API.

##  Overview

When processing Persistent Scatterer Interferometric Synthetic Aperture Radar (PS-InSAR) data, acquiring the correct baseline imagery and precise orbit files is a critical first step. This mini-project serves as a streamlined guide and toolkit to automate the retrieval of both ascending and descending `.zip` data and their corresponding `.EOF` orbit files.

##  Project Structure

To keep the downloaded data organized for immediate processing, the project enforces the following directory structure:

```text
Project/
├──  ascending_zips/          # Sentinel-1 SLC data (.zip) - Ascending pass
├──  ascending_orbits/        # Precise orbit files (.EOF) - Ascending pass
├──  descending_zips/         # Sentinel-1 SLC data (.zip) - Descending pass
├──  descending_orbits/       # Precise orbit files (.EOF) - Descending pass
├──  Baseline_download_data.py  # Script to search and download baseline SAR data
├──  Download_orbit_files.py    # Script to fetch corresponding precise orbits
└──  search_map.html            # Interactive map interface for data search/visualization
```


##  How to run 

```text
pip install -r requirements.txt
```

