#!/usr/bin/perl
# helper script for get_weather.sh that formats weather from weather-util
# Copyright (C) 2011 David Glass <dsglass@gmail.com>
# Copyright is GPLv3 or later, see /usr/share/common-licenses/GPL-3

my $plugin_file = "/home/$ARGV[1]/.wakeup/$ARGV[2]/plugins/Weather/Weather.config";
open(my $file, $plugin_file);
my @lines = <$file>;
my @temp_line = grep(/^temperature_units/, @lines);
my @wind_line = grep(/^wind_units/, @lines);
(my $blank, my $temp_units) = split(/\s*=\s*/, $temp_line[0]);
$temp_units =~ s/\s*$//;
(my $blank, my $wind_units) = split(/\s*=\s*/, $wind_line[0]);
$wind_units =~ s/\s*$//;
close($file);

my $weather = `weather -qi $ARGV[0]`;
$_ = $weather;
s/\n/.\n/g; # put periods to distinguish sentences
s/;/ and /g; # ; is used as an "and"
s/SE / south east /g; # directions, including NNE, SSW, etc.
s/NE / north east /g;
s/NW / north west /g;
s/SW / south west /g;
s/N /north /g;
s/E /east /g;
s/W /west /g;
s/S /south /g;
s/\(.*? degrees\)//g; # remove exact direction
if ($wind_units eq "mph") {
s/MPH \(.*? KT\)/miles per hour/g; # write out MPH, remove KT
}
else {
s/[0-9\.\-]*? MPH \((.*?) KT\)/\1 knots/g; # write out KT, remove MPH
}
if ($temp_units eq "F") {
s/F \(.*? C\)/degrees/g; # remove C, only prints degrees
}
else {
s/[0-9\.\-]*? F \((.*?) C\)/\1 degrees/g; # remove F, only prints degrees
}
s/  / /g; # clean up spaces

# set up for splitting into array
s/.\n/|/g;
s/: /|/g;

my $bl = "", $temperature = "", $humidity = "", $weather = "", $sky = "";
if (/Weather/) {
	($bl,$temp,$bl, $hum,$bl, $wind,$bl, $weather,$bl, $sky) = split(/\|/, $_);
}
else {
    ($bl,$temp,$bl, $hum,$bl, $wind, $bl, $sky) = split(/\|/, $_);
}

for my $to_output (@ARGV[3..$#ARGV]) {
    if ($to_output eq "temperature") {print "$temp\n\n";}
    if ($to_output eq "skyconditions") {print "$sky\n\n";}
    if ($to_output eq "humidity") {print "$hum\n\n";}
    if ($to_output eq "windconditions") {print "$wind\n\n";}
    if ($to_output eq "weatherconditions") {print "$weather\n\n";}
}
