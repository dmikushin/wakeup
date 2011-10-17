#!/usr/bin/perl
# plugin script for determining closest metar station. This finds distance
# between two latitude, longitude points (+/- decimal format)
# Copyright (C) 2011 David Glass <dsglass@gmail.com>
# Copyright is GPLv3 or later, see /usr/share/common-licenses/GPL-3
# See http://en.wikipedia.org/wiki/Haversine_formula

use Math::Trig;

$lat1 = $ARGV[0];
$lon1 = $ARGV[1];
$lat2 = $ARGV[2];
$lon2 = $ARGV[3];
$R = 6378; # km, earth's radius assuming perfect sphere
$havdoverR = &haversin($lat2 - $lat1) + cos($lat1)*cos($lat2)*&haversin($lon2-$lon1);
$distance = $R * &archaversin($havdoverR) * 3.14/180;


sub haversin {
    return (1 - cos(@_[0]))/2;
}
sub archaversin {
    return acos(1 - 2 * @_[0]);
}

print $distance;
