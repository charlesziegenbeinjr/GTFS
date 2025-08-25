import pandas as pd
import numpy as np
import folium
import enum

lines = enum.Enum(
    "Lines",
    {
        "A": "#0062CF",
        "B": "#EB6800",
        "C": "#0062CF",
        "D": "#EB6800",
        "E": "#0062CF",
        "F": "#EB6800",
        "G": "#799534",
        "J": "#8E5C33",
        "L": "#7C858C",
        "M": "#EB6800",
        "N": "#F6BC26",
        "Q": "#F6BC26",
        "R": "#F6BC26",
        "S": "#7C858C",
        "SI":"#008EB7",
        "W": "#F6BC26",
        "Z": "#8E5C33",
        "1": "#D82233",
        "2": "#D82233",
        "3": "#D82233",
        "4": "#009952",
        "5": "#009952",
        "6": "#009952",
        "7": "#9A38A1",
    }
)

icon_image_path = 'mta.jpeg'
custom_icon = folium.features.CustomIcon(
    icon_image=icon_image_path,
    icon_size=(10,10)
)
m = folium.Map((40.889248,-73.898583), tiles="cartodb positron")

stops = pd.read_csv("../supplemented/stops.txt", header=0)
df_filtered = stops[pd.isnull(stops['parent_station'])]

shapes = pd.read_csv("../supplemented/shapes.txt", header=0)
shapes["prefix"] = shapes["shape_id"].str.split(r"\.\.", n=1).str[0]

shapes = shapes.groupby("prefix", group_keys=False).apply(
    lambda g: g[g["shape_id"] == g["shape_id"].iloc[0]]
)
print(len(shapes))
tf = shapes.duplicated(subset=['shape_pt_lat','shape_pt_lon'])
df_unique = shapes.drop_duplicates(
    subset=["prefix", "shape_pt_lat", "shape_pt_lon"])

point_counts = (
    df_unique.groupby(["shape_pt_lat", "shape_pt_lon"])["prefix"]
    .nunique()
    .reset_index(name="prefix_count")
)

step = 0.00005 


def jitter_group(group):
    n = len(group)
    if n == 1:
        return group
    offsets = np.linspace(-(n-1)/2*step, (n-1)/2*step, n)
    group = group.copy()
    group["shape_pt_lat"] = group["shape_pt_lat"] + offsets
    group["shape_pt_lon"] = group["shape_pt_lon"] + offsets
    return group


df_jittered = (
    df_unique.groupby(["shape_pt_lat", "shape_pt_lon"], group_keys=False)
      .apply(jitter_group)
)

print(df_jittered.head(20))
print(df_jittered['shape_id'].unique())


# exit()

shapes = df_jittered.groupby(['shape_id'])
for id, group in shapes:
    if len(id) != 7:
        continue
    line = id.split("..")[0]
    group_pts = group[['shape_pt_lat','shape_pt_lon']]
    try:
        folium.PolyLine(group_pts.values.tolist(),color=lines[line].value).add_to(m)
    except KeyError:
        folium.PolyLine(group_pts.values.tolist()).add_to(m)
            

for idx, row in df_filtered.iterrows():
    folium.Marker(
        location=[row['stop_lat'],row['stop_lon']],
        popup=row['stop_name'],
        weight=2,
        icon=custom_icon
    ).add_to(m)

m.save("map.html")

