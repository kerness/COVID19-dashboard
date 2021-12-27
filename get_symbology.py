import os
import json

from arcgis.gis import GIS

# just query for item data (symbology) and save it to file 

# to run this in your environment:
#   - change GIS username and password
#   - change working_dir and specify your own path

arcgis_user = 'changeit'
arcgis_pass = 'changeit'


gis = GIS(username= arcgis_user, password= arcgis_pass)


def save_symbology(item_to_update):
    item = gis.content.get(item_to_update)
    item_data = item.get_data()

    with open('webmaplyr_reference.json', 'w') as file:
        json.dump(item_data, file, indent=4)



webmap = "8bf43e150eb0448591b2b69961a194ee" # dashboard map
save_symbology(webmap) 
