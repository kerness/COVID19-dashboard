import os
import datetime as dt
import pandas as pd
import shutil
import requests
import csv
import logging
import json

from arcgis.gis import GIS
from arcgis.features import FeatureLayerCollection

# to run this in your environment:
#   - change GIS username and password
#   - change working_dir and specify your own path

arcgis_user = 'changeit'
arcgis_pass = 'changeit'
#working_dir = os.path.join('/home/mbak/Studia/semestr5/geoportale/projekty/proj2')
working_dir = os.path.join('/home/ubuntu/csv_updater')

# get the timestamp
now = str(dt.datetime.now().strftime("%d%m%Y_%H%M%S"))

# prepare directories
downloaded = os.path.join(working_dir, 'downloaded')
to_upload = os.path.join(working_dir, 'to_upload')
logs = os.path.join(working_dir, 'logs')
if not os.path.exists(downloaded):
    os.makedirs(downloaded)
if not os.path.exists(to_upload):
    os.makedirs(to_upload)
if not os.path.exists(logs):
    os.makedirs(logs)

# logging
logging.basicConfig(filename=os.path.join(working_dir, 'logs/csv_updater' + now + '.log'), filemode='w', format='%(name)s - %(levelname)s - %(message)s')
logging.root.setLevel(logging.NOTSET)



# login to arcgis
gis = GIS(username= arcgis_user, password= arcgis_pass)
logging.info(f'Logged to AGOL as: {arcgis_user}')


# download new data
url = 'https://www.arcgis.com/sharing/rest/content/items/153a138859bb4c418156642b5b74925b/data'
covid_data = requests.get(url)
logging.info(f'Recent Poland covid data downloaded.')

covid_working_dir = os.path.join(working_dir, "downloaded/covid_data_" + now + '.csv')
open(covid_working_dir, 'wb').write(covid_data.content)


# add "nazwa" column with voivodeships names without special chars

# convert to pandas dataframe
covid_df = pd.read_csv(covid_working_dir, sep=';', encoding='iso-8859-15')

# create dataframe with correct names
woj = [ ["caly_kraj"], ["dolnoslaskie"], ["kujawsko-pomorskie"],
            ["lubelskie"], ["lubuskie"], ["lodzkie"], ["malopolskie"],
            ["mazowieckie"], ["opolskie"], ["podkarpackie"], ["podlaskie"],
            ["pomorskie"], ["slaskie"], ["swietokrzyskie"], ["warminsko-mazurskie"],
            ["wielkopolskie"], ["zachodniopomorskie"]
        ]
nazwa = pd.DataFrame(woj, columns=['nazwa'] )

# merge correct names with downloaded data
covid_df_merged = pd.concat([covid_df, nazwa], axis=1)
covid_df_merged['nazwa_pl'] = ''
# delete "caly_kraj"
covid_df_merged = covid_df_merged.drop(0)
# save to csv file
covid_merged = os.path.join(working_dir, 'to_upload/covid_data_upload_' + now + '.csv')
covid_df_merged.to_csv(covid_merged, sep=';')

# make variable name more meaningful
current_data = covid_merged

###############################################################################
# UPDATE THE DATA
item_to_update = "ce8d3898df3c4eadb2f830d61073f6c5"

covid = gis.content.get(item_to_update)
covid_flayer = FeatureLayerCollection.fromitem(covid)
res = covid_flayer.manager.overwrite(current_data)
covid.update(item_properties={"title":"COVID_DATA", "description":"Data update timestamp: " + now})

if res.get('success') == True:
    logging.info('Layer updated successfully')
else:
    logging.error('Error updating the layer.')



###############################################################################
#  UPDATE THE SYMBOLOGY OF THE COVID DATA IN THE WEBMAP

logging.info('Trying to update the symbology')

# get the item data
webmap_id = "8bf43e150eb0448591b2b69961a194ee" # mapka z dashobardu
webmap = gis.content.get(webmap_id)
webmap_data = webmap.get_data()

# chcek for the symbology JSON
symbology_json = os.path.join(working_dir, 'webmaplyr.json')
if not os.path.exists(symbology_json):
    logging.error('Symbology file: ' + symbology_json + ' not found.')
else:
    logging.info('Symbology file: ' + symbology_json + ' found.')


# Open JSON file containing correct symbology (this file was saved before - it is just item_data variable contents)
with open(symbology_json) as json_data:
    lyr_data = json.load(json_data)

# Set the item_properties to include the update
webmap_properties = {"text": json.dumps(lyr_data)}

# update item properties
webmap.update(item_properties=webmap_properties)

new_webmap_data = webmap.get_data()

if new_webmap_data == lyr_data:
    logging.info('Symbology update completed successfully!')
else:
    logging.error('Something unexpected happened :/')


########################################################3

###############################################################################
# CREATE THE DATA - this part was only used to create the initial dataset

#upload data to agol - create new layer with location as address
# def create_inital_data():
#     item_prop = {'title':'COVID_Data_' + str(now)}
#     csv_item = gis.content.add(item_properties=item_prop, data=covid_merged)
#     print(now)

#     #publish as feature layer
#     publish_params = {"locationType":"address", "name":"MB", "addressTemplate": "{Address}", "addressFields": {"Address": "nazwa"}}
#     covid_item = csv_item.publish(publish_parameters=publish_params)
#     covid_item.update(item_properties={"title":"PL_COVID_DATA", "description":"Data update timestamp: " + now})
#     #update the layer
#     covid_flayer = FeatureLayerCollection.fromitem(covid_item)
#     covid_flayer.manager.overwrite(covid_update)
