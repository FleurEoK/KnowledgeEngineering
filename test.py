import pandas as pd
import requests
import time 
stations = pd.read_csv('stationids.csv')
print(len(stations[stations['DBid'].isna()]))

for station in stations[stations['DBid'].isna()].itertuples():
    city = station[3],
    country=station[15]
    print(city)
    print(country)
    r = requests.get('https://v6.db.transport.rest/locations?query=' + str(city) + str(country) + '&fuzzy=true&results=10&stops=true&addresses=true&poi=true&linesOfStops=false&language=en')
    res = r.json()
    print(res)
    time.sleep(1)