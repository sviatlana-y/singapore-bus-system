import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cf
import seaborn as sns
import networkx as nx

# importing data frames and merging them together

filename = "../bus_stops.csv"
bus_stops = pd.read_csv(filename)
filename = "../bus_routes.csv"
bus_routes = pd.read_csv(filename)
filename = "../bus_services.csv"
bus_services = pd.read_csv(filename)
route_service = pd.merge(bus_routes, bus_services,
                         left_on=["ServiceNo", "Operator", "Direction"],
                         right_on=["ServiceNo", "Operator", "Direction"])

bus_stops['BusStopCode'] = bus_stops['BusStopCode'].astype(str)
merged_bus_data = pd.merge(route_service, bus_stops, on='BusStopCode')

# sorting the final data frame by Service Number, Direction and Sequence

sorted_buses = merged_bus_data.sort_values(['ServiceNo', 'Direction', 'StopSequence'])

# *** Exercise 1: On the map, connect the dots from a same bus line together ***

# This question uses the cartopy package for generating a map of Singapore and
# seaborn for plotting and color coding the routes
# The code will take a while to run

lo1 = sorted_buses["Longitude"].min()
la1 = sorted_buses["Latitude"].min()
lo2 = sorted_buses["Longitude"].max()
la2 = sorted_buses["Latitude"].max()

extent = [lo1, lo2, la1, la2]
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_extent(extent)

# in order to to get higher coastline resolution we use the GSHHSFeature of cartopy
ax.add_feature(cf.GSHHSFeature(scale='high'))
ax.connected_plot = sns.lineplot(list(sorted_buses["Longitude"]), list(sorted_buses["Latitude"]),
                                 hue=list(sorted_buses['ServiceNo']), sort=False, lw=1, legend=False)

# *** Exercise 2: Build a graph of the network using networkx package and save it as a DOT file ***

# In order to include all intermediate bus stops in our graph we create two new columns
# containing the next stop and the distance to it

next_stop = []
distance_to_next = []

for x in list(sorted_buses['ServiceNo'].unique()):
    one_bus = sorted_buses[sorted_buses['ServiceNo'] == str(x)]  # single out routes by service number
    for y in list(one_bus['Direction'].unique()):
        one_bus_direction = one_bus[one_bus['Direction'] == y]  # single out routes by direction
        for i in range(len(one_bus_direction)):
            if i != len(one_bus_direction) - 1:
                next_stop.append(one_bus_direction.iloc[i + 1]['BusStopCode'])  # if it is not the final stop,
                # append the code of the next bus stop to the next_stop column
                distance_to_next.append(one_bus_direction.iloc[i + 1]['Distance'] -
                                        one_bus_direction.iloc[i]['Distance'])  # get the distance between stops
                # by subtracting the cumulative distance at current stop from the cumulative distance at the next stop
            else:
                next_stop.append(one_bus_direction.iloc[i]['BusStopCode'])  # if it is the final stop append its code
                # to the next_stop column
                distance_to_next.append(0)  # the distance between stops at the final stop is going to be zero

# add our newly created columns to the data frame
sorted_buses['NextStop'] = next_stop
sorted_buses['DistanceToNext'] = distance_to_next

# create the dot file
G = nx.from_pandas_edgelist(sorted_buses, 'BusStopCode', 'NextStop', edge_attr='DistanceToNext')
nx.drawing.nx_pydot.write_dot(G, "Singapore_Entire_Bus_Network.dot")


# *** Exercise 3: Build an algorithm to find the shortest path from a point A to B ***

# I use the inbuilt networkx function to find the shortest path

def find_path(x, y):
    try:  # if the path exists
        result = nx.shortest_path(G, source=str(x), target=str(y), weight='DistanceToNext')
        print('The shortest path from bus stop', x,
              'to bus stop', y, 'is the following:')
        for i in result:
            name = sorted_buses.loc[sorted_buses['BusStopCode'] == i]['Description'].values[0]
            print(i, '-', name)
        return "\n"
    except:  # if there is no path
        return "No Path \n"


print(find_path(84009, 77009))
print(find_path(17179, 78121))
print(find_path(16009, 84009))
