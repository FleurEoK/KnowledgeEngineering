import pandas as pd
from tqdm import tqdm
import requests
import time
from haversine import haversine

############################################### HELPER FUNCTIONS ######################################################################################################################



#Send API request to Deutsche Bahn 
def send_request(city, latitude, longitude, country=None,):
    #try with country and city so that Germany is not preferred
    if country is not None:
        r = requests.get('https://v6.db.transport.rest/locations?query=' + str(city) + ' ' + str(country) + '&fuzzy=true&results=10&stops=true&addresses=true&poi=true&linesOfStops=false&language=en')
    #try only city
    else:
        r = requests.get('https://v6.db.transport.rest/locations?query=' + str(city) + '&fuzzy=true&results=10&stops=true&addresses=true&poi=true&linesOfStops=false&language=en')
    
    #retry if timeout
    if r.status_code == 429:
        time.sleep(0.5)
        return send_request(city, latitude, longitude, country)
    
    if r.status_code == 200:
        res = r.json()
        station_id = res[0]['id']
       
        #retry if country + city did not give good results
        if station_id is None and country is not None:
            return send_request(city, latitude, longitude)
        #if a station id has been found, check if it is close to the requested city (API has a tendency to match things in different countries)
        if station_id is not None :
            #First try to see if the first response is correct, try-except because not all JSONs are formatted exatcly the same
            try:
                res_longitude = res[0]['location']['longitude']
                res_latitude = res[0]['location']['latitude']
            except:
                res_longitude = res[0]['longitude']
                res_latitude = res[0]['latitude']
            dist=haversine(latitude, longitude, res_latitude, res_longitude)
            if dist < 100.0:
                return station_id
            #If it was not, because there was a very similar city in Germany (DB prefers German adresses) try the second
            try:
                res_longitude = res[1]['location']['longitude']
                res_latitude = res[1]['location']['latitude']
            except:
                res_longitude = res[1]['longitude']
                res_latitude = res[1]['latitude']
            dist=haversine(latitude, longitude, res_latitude, res_longitude)
            if dist < 100.0:
                return station_id
            
    return None

######################################### END OF THE HELPER FUNCTIONS ##############################################################################################################

# Read data
routes_df = pd.read_csv('data/routes_filtered.csv')

#Reformat longitude and latitude to actual coördinates, since domain is EU, all values have 2 values before the comma
for coord in ['source_longitude', 'source_latitude', 'dest_longitude', 'dest_latitude']:
    routes_df[coord] = routes_df[coord].str.replace('.', '')
    routes_df[coord] = routes_df[coord].str[:2] + '.' + routes_df[coord].str[2:]
    routes_df[coord] = routes_df[coord].astype(float)

#Set up progress bar
total_iterations = len(routes_df)
progress_bar = tqdm(total=total_iterations, desc="Progress", unit="station")


DBid_dict = {} #Dictionary to collect all the ID's for each unique city in the dataset

#Find the Deutsche Bahn id's
for index, row in routes_df.iterrows():

    #Collect all data required for querying
    city_dep = row['source_city']
    country_dep=row['source_country_code']
    long_dep=row['source_longitude']
    lat_dep=row['source_latitude']
    city_dest=row['dest_city']
    country_dest=row['dest_country_code']
    long_dest=row['dest_longitude']
    lat_dest=row['dest_latitude']

    #Add departure and destination city to dictionary
    if city_dep not in DBid_dict:
        station_id_dep = send_request(city_dep, lat_dep, long_dep, country_dep)
        DBid_dict[city_dep] = station_id_dep
    if city_dest not in DBid_dict:
        station_id_dest = send_request(city_dest, lat_dest, long_dest, country_dest)
        DBid_dict[city_dest] = station_id_dest

    progress_bar.update(1)

progress_bar.close()

#Add the DBid for each city to the dataframe
for index, row in routes_df.iterrows():
    if row["source_city"] in DBid_dict:
        routes_df.at[index, "dep_DBid"] = DBid_dict[row["source_city"]]
    if row["dest_city"] in DBid_dict:
        routes_df.at[index, "dest_DBid"] = DBid_dict[row["dest_city"]]


#Save the new dataframe
routes_df.to_csv('routes_filtered_with_DBids.csv', index=True)

