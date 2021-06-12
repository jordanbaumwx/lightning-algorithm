# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

import pygrib
import numpy as np
import pygeohash as pgh

from Sounding import Sounding

import conda, os
conda_file_dir = conda.__file__
conda_dir = conda_file_dir.split('lib')[0]
proj_lib = os.path.join(os.path.join(conda_dir, 'share'), 'proj')
os.environ["PROJ_LIB"] = proj_lib

from mpl_toolkits.basemap import Basemap


def get_grb_information():
    grbs = pygrib.open('hrrr.t00z.wrfprsf00.grib2.txt')
    temps = {}
    dewps = {}
    us = {}
    vs = {}
    for grb in grbs:
        if grb.parameterName == "Temperature":
            if grb.level != 0:
                temps[grb.level] = grb.values
        if grb.parameterName == "Dew point temperature":
            if grb.level != 0:
                dewps[grb.level] = grb.values
        if grb.parameterName == "u-component of wind":
            if grb.level != 0:
                us[grb.level] = grb.values
        if grb.parameterName == "v-component of wind":
            if grb.level != 0:
                vs[grb.level] = grb.values
    lats, lons = grb.latlons()

    return lats, lons, temps, dewps, us, vs


def get_profile_from_data_dict(lat_pos, lon_pos, dict):
    values = []
    for key in sorted(dict.keys(), reverse=True):
        if key == 10 or key == 2:
            values.insert(0, value)
        else:
            value = dict[key][lon_pos, lat_pos]
            values.append(value)

    return values


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.

    lats, lons, temps, dewps, us, vs = get_grb_information()

    soundings = []
    for i in range(0, len(lons), 10):
        for j in range(0, len(lats), 10):
            geohash = pgh.encode(lats[j, 0], lons[i, 0], precision=9)
            pres = sorted(temps.keys())[1:]
            pres.reverse()

            pres = pres
            temp = get_profile_from_data_dict(i, j, temps)
            dewp = get_profile_from_data_dict(i, j, dewps)
            u = get_profile_from_data_dict(i, j, us)
            v = get_profile_from_data_dict(i, j, vs)
            sounding = Sounding(geohash, pres, temp, dewp, u, v)
            sounding.get_lightning_index()
            #sounding.create_sharppy_profile()

            soundings.append(sounding)

    from matplotlib import pyplot as plt
    import cartopy.crs as ccrs



    lis = []

    coords = [[], []]
    lons = set()
    lats = set()
    for sounding in soundings:
        lis.append(sounding.li)
        geohash = pgh.decode(sounding.geohash)

        coords[0].append(geohash[1])
        coords[1].append(geohash[0])

        lons.add(geohash[1])
        lats.add(geohash[0])

    values = []

    x,y = np.meshgrid(list(lons), list(lats))
    for i in range(len(x)):
        v = []
        for j in range(len(y)):
            v.append(lis[i+j])
        values.append(v)

    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.coastlines()


    plt.contourf(x, y, values, 20,
                 transform=ccrs.PlateCarree(), vmin=0, vmax=15)

    plt.show()

    plt.savefig('books_read.png')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
