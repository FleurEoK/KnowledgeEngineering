import pandas as pd
import re
from haversine import haversine

connections = pd.read_csv('connectiondata.csv')

print(len(connections))
df = connections.drop_duplicates()
print(len(df))

special_places = {'Marienplatz, München' : 'München',
 'Hauptbahnhof, München' : 'München',
 'ZOB, Güstrow' : 'Güstrow',
 'St-Pierre-des-Corps' : 'St-Pierre-des-Corps',
 'St. Gallen(CH)' : 'St.Gallen',
 'St. Margrethen SG' : 'St.Margrethen',
 'St.Pölten Hbf' : 'St.Pölten',
 'San Sebastian' : 'San Sebastian',
 'La Coruna-San Cristobal' : 'La Coruna-San Cristobal',
 'La Rochelle Ville' : 'La Rochelle Ville',
 'Les Aubrais - Orléans' : 'Orléans',
 'Le Mans' : 'Le Mans',
 'Resort Linstow, Dobbin-Linstow' : 'Dobbin-Linstow'
 }

for i, connection in df.iterrows():
    station_name_dep = connection['departure_name']
    if station_name_dep in special_places:
        df.loc[i, 'departure_city'] = special_places[station_name_dep]
    else:
        match = re.search(r"\b(\w+)\b", station_name_dep)
        df.loc[i, 'departure_city'] = match.group(1)
    
    station_name_dest = connection['destination_name']
    if station_name_dest in special_places:
        df.loc[i, 'destination_city'] = special_places[station_name_dest]
    else:
        match = re.search(r"\b(\w+)\b", station_name_dest)
        df.loc[i, 'destination_city'] = match.group(1)

distances = []
for id, row in df.iterrows():
    lat1 = row['departure_latitude']
    lon1 = row['departure_longitude']
    lat2 = row['destination_latitude']
    lon2 = row['destination_longitude']
    dist = haversine(lat1, lon1, lat2, lon2)
    distances.append(dist)

df['distance'] = distances
df.to_csv('train_connections.csv', index=True)

