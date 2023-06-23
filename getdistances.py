from haversine import haversine
import pandas as pd

flight_routes = pd.read_csv('../data/flight_connections_emissions.csv')
train_routes = pd.read_csv('../data/train_connections_emissions.csv')
cities = pd.read_csv('../data/cities_europe.csv')
cities = cities.drop_duplicates()

def add_dist(dataset, dataset_name):
    distances = []
    for index, route in dataset.iterrows():
        dest_value = route['dest_city']
        dep_value = route['source_city']

        dest_info = cities.loc[cities['city'] == dest_value]
        dep_info = cities.loc[cities['city'] == dep_value]
        
        if dest_info.empty or dep_info.empty:
            distances.append('NA')
            continue
        lat1 = dep_info['latitude']
        lon1 = dep_info['longitude']
        lat2 = dest_info['latitude']
        lon2 = dest_info['longitude']
        dist = haversine(lat1, lon1, lat2, lon2)
        distances.append(dist)

    dataset['new_distance'] = distances
    dataset.to_csv(dataset_name, index=False)

def add_dist2(dataset, dataset_name):
    distances = []
    for index, route in dataset.iterrows():
        dest_value = route['destination_city']
        dep_value = route['departure_city']

        dest_info = cities.loc[cities['city'] == dest_value]
        dep_info = cities.loc[cities['city'] == dep_value]
        
        if dest_info.empty or dep_info.empty:
            distances.append('NA')
            continue
        lat1 = dep_info['latitude']
        lon1 = dep_info['longitude']
        lat2 = dest_info['latitude']
        lon2 = dest_info['longitude']
        dist = haversine(lat1, lon1, lat2, lon2)
        distances.append(dist)

    dataset['new_distance'] = distances
    dataset.to_csv(dataset_name, index=False)


add_dist(flight_routes, '../data/flight_connections_emissions_v2.csv')
add_dist2(train_routes, '../data/train_connections_emissions_v2.csv')