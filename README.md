# Project proposal: EartquakeTrends
Based on the publicly available data at the USGS Earthquake Hazard Program: http://earthquake.usgs.gov/earthquakes/search/

A subset was downloaded through the Earthquake Catalog API and made available in the repository for use in the plotting scripts given here. The scripts to download the data are included in trends.py as well.

## Installation
You can download the script and data to your hard disk: 
* Clone the git repository to create a local copy, located in ~/EarthquakeTrends/ (or whichever location your prefer, replace ~/ with the parent folder you want):
    - $ cd ~/
    - $ git clone https://github.com/robinlombaert/EarthquakeTrends.git EarthquakeTrends
    
Remember to add ~/EarthquakeTrends to your system PYTHONPATH variable if you wish to import the trends module into python.

The required python modules are listed in requirements.txt.

