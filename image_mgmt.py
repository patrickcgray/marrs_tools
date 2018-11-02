import pandas
import os
import xml.etree.ElementTree
import csv
import argparse

### Setting up the user input args

parser = argparse.ArgumentParser(description='Manage the flight imagery and flight logs.')
parser.add_argument('campaign_filepath', metavar='fp', type=str,
                    help='relative or abs filepath to the flight campaign data')

args = parser.parse_args()
mypath = args.campaign_filepath
print(mypath)

### walk through full campaign worth of imagery and pull out lat, lon, both altimeter measurements

for (_, day_aircraft_dirs, filenames) in os.walk(mypath): # descending into campaign dir

    for day_aircraft in day_aircraft_dirs:
        day_aircraft = os.path.join(mypath, day_aircraft)

        for (_, flights, filenames) in os.walk(day_aircraft): # descending into daily dirs for each craft
            print(day_aircraft)

            aircraft_type = day_aircraft[-1] # aircraft type is designated by the final char

            for flight in flights: # iterate through all flights on this day with this platform

                flight = os.path.join(day_aircraft, flight)
                for (_, flight_data_dirs, filenames) in os.walk(flight): # descending into flight dir to retrieve flight log
                    if aircraft_type == "L":
                        alt_measurements = []

                        if "Flight_Logs" in flight_data_dirs:
                            log_files = os.listdir(os.path.join(flight, "Flight_Logs"))
                            for item in log_files:
                                if item.upper().endswith(".GPX"):
                                    print(item)
                                    root = xml.etree.ElementTree.parse(os.path.join(flight, "Flight_Logs", item)).getroot()
                                    alt_collection = root[1][1]
                                    for alt_point in alt_collection.findall('trkpt'):
                                        time = alt_point.find('time').text
                                        if time == "2018-08-27T20:15:15.8Z":
                                        # if time in list of time from timecorrection.csv
                                            print("found it!!!")
                                            lat = alt_point.attrib['lat']
                                            lon = alt_point.attrib['lon']
                                            extensions = alt_point.find("extensions")
                                            laser = extensions.find('Laser').text
                                            alt = extensions.find('Altimeter').text
                                            print(lat, lon, laser, alt)
                                            alt_measurements.append([time, lat, lon, laser, alt.split(",")[0]])
                            print(alt_measurements)
                            with open(day_aircraft.split('/')[-1] + ".csv", 'w', newline='') as myfile:
                                wr = csv.writer(myfile)
                                wr.writerows(alt_measurements)

                            print(day_aircraft + ".csv")

                        for data_dir in flight_data_dirs:
                            pass


                    if aircraft_type == "A":
                        pass
                         # TODO for Clara

                    break # out of flight dir

            break # out of daily dirs for each aircraft walk

    break # break out of high level walk


