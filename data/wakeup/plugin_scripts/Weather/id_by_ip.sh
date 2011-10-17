#!/bin/bash
# plugin script for Weather to get closest metar station based on ip geolocation
# Copyright (C) 2011 David Glass <dsglass@gmail.com>
# Copyright is GPLv3 or later, see /usr/share/common-licenses/GPL-3

# Get ISP longitude and latitude, as well as country code and state
wget -q -U DummyBrowser/1.0 -O /tmp/ip_tracer www.ip-adress.com/ip_tracer
latln=$(grep GLatLng /tmp/ip_tracer)
my_lat=$(echo $latln | grep -oP "\([0-9\-\.]+" | sed 's/(//')
my_lon=$(echo $latln | grep -oP "[0-9\-\.]+\)" | sed 's/)//')
countrycode=$(grep -A 2 "country code" /tmp/ip_tracer | grep -oP "[A-Z]{2}" | sed '/IP/d')
state=$(grep -A 2 "state" /tmp/ip_tracer |  tr '\n' ' ' | grep -oP "<td>.*</td>" | sed -r 's/\s*<\/?td>\s*//g')
rm /tmp/ip_tracer

# filter metar stations by country, or by state if in United States or Canada
wget -q http://aviationweather.gov/adds/metars/stations.txt -O /tmp/metar_stations
if [[ $countrycode == "US" || $countrycode == "CA" ]]; then
    statecode=$(grep -i -A 2 "$state" /tmp/metar_stations | grep -P "US$|CA$" | grep -oP "^[A-Z]{2}")
    grep "^$statecode" /tmp/metar_stations > /tmp/Stations
else
    grep "$countrycode$" /tmp/metar_stations > /tmp/Stations
fi
rm /tmp/metar_stations

# find closest metar station
distance=40000.0 # km, approximate circumference of the earth (starting minimum dist)
my_metar=""
while IFS='' read line; do
    # skip useless lines
    if [[ $line =~ ^!.* || $line =~ ^$ ]]; then flag=1; continue
    elif [[ $flag == 1 ]]; then flag=0; continue
    elif [[ $line =~ " ICAO " ]]; then continue
    fi

    # get metar ID and skip metar stations without ID
    id=${line:20:4}
    if [[ $id == "    " ]]; then continue; fi
    # convert longitude and latitude to decimal format
    lat=${line:39:6}
    lon=${line:47:7}
    lat_deg=$(echo "${lat:0:2}" | sed 's/^0//')
    lat_min=$(echo "${lat:3:2}" | sed 's/^0//')
    lat_sign=$(if [[ ${lat:5:1} == "S" ]]; then echo "-"; fi)
    lon_deg=$(echo "${lon:0:3}" | sed 's/^0//')
    lon_min=$(echo "${lon:4:2}" | sed 's/^0//')
    lon_sign=$(if [[ ${lon:6:1} == "W" ]]; then echo "-"; fi)
    lat_dec="$lat_sign$lat_deg.$(( 10000 * lat_min / 60 ))"
    lon_dec="$lon_sign$lon_deg.$(( 10000 * lon_min / 60 ))"
    
    # find shortest distance
    d=$($(dirname $0)/sphereDist.pl $my_lat $my_lon $lat_dec $lon_dec)
    d_whole=$(echo $d | grep -oP "^[0-9]+")
    d_dec=$(echo $d | grep -oP "[0-9]+$")
    dist_whole=$(echo $distance | grep -oP "^[0-9]+")
    dist_dec=$(echo $distance | grep -oP "[0-9]+$")
    if [[ $d_whole -lt $dist_whole
          || ($d_whole -eq $dist_whole && ${d_dec:1:4} < ${dist_dec:1:4}) ]]; then
        distance=$d
        my_metar=$id
        min_lat=$lat_dec
        min_lon=$lon_dec
    fi
done < /tmp/Stations
# output closest metar station
echo "$my_metar"
rm /tmp/Stations
