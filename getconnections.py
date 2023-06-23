import pandas as pd
import requests
from tqdm import tqdm
import time

def check_connection(departure=8400621, destination=8400206): #Utrecht - Eindhoven as standard values to check if it actually works
    #Get journey between the destinations
    r = requests.get('https://v6.db.transport.rest/journeys?from=' + str(departure) + '&to=' + str(destination))
    if r.status_code == 200:
        res = r.json()
        return res
    #Retry if timeout
    if r.status_code == 429:
        time.sleep(0.5)
        return check_connection(departure, destination)
    return None

#################################################### END HELPER FUNCTIONS #########################################################################################################################################################

stations_df = pd.read_csv('routes_filtered_with_DBids.csv')

#Prepare final dataframe
columns = ['departure_id', 'departure_city', 'departure_name', 'departure_latitude', 'departure_longitude', 'destination_id',  'destination_city', 'destination_name',  'destination_latitude', 'destination_longitude']
df = pd.DataFrame(columns=columns)

#Create progress bar
total_iterations = len(stations_df)
progress_bar = tqdm(total=total_iterations, desc="Progress", unit="Route")

for index, row in stations_df.iterrows():
    dep = row['dep_DBid']
    dest=row['dest_DBid']
    #dep_city = row['source_city']
    #dest_city = row['dest_city']
    if pd.notnull(dep) and pd.notnull(dest):       ###### Check if we have a DBid to use for querying
        
        res = check_connection(int(dep), int(dest))
        if res is not None:
                for leg in res['journeys'][0]['legs']:   ######## There might be multiple transers, add the connection between each separate station in the route to get direct connections
                    data= {
                        'departure_id' : leg['origin']['id'],
                        'departure_name' : leg['origin']['name'],
                        'departure_longitude' : leg['origin']['location']['longitude'],
                        'departure_latitude' : leg['origin']['location']['latitude'],
                        'destination_id' : leg['destination']['id'],
                        'destination_name' : leg['destination']['name'],
                        'destination_longitude' : leg['destination']['location']['longitude'],
                        'destination_latitude' : leg['destination']['location']['latitude']
                    }
                    df = df.append(data, ignore_index=True)
    progress_bar.update(1)

progress_bar.close()



df.to_csv('connectiondata.csv', index=False) #Store all data
