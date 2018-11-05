import pandas as pd
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
    TC = os.path.join(_, "TimeCorrections.csv")
    dfTimeCorr = pd.read_csv(TC,sep=",")
    dfTimeCorr = dfTimeCorr.dropna(axis=0,how='any')
    day_ac = []
    for i in dfTimeCorr['Flight']:
        ii = i[:8]
        day_ac += [ii]
    dfTimeCorr['date_aircraft'] = day_ac
    correction = []
    for i in dfTimeCorr['TimeChange']:
        ii = i.replace(":","")
        iii = int(ii)
        correction += [ii]
    dfTimeCorr['TimeCorrection'] = correction
    for day_aircraft in day_aircraft_dirs:
        day_aircraft = os.path.join(mypath, day_aircraft)

        for (_, flights, filenames) in os.walk(day_aircraft): # descending into daily dirs for each craft
            print(day_aircraft)

            aircraft_type = day_aircraft[-1] # aircraft type is designated by the final char

            for flight in flights: # iterate through all flights on this day with this platform
                print(fl)
                flight = os.path.join(day_aircraft, flight)
                for (_, flight_data_dirs, filenames) in os.walk(flight): # descending into flight dir to retrieve flight log
                    if aircraft_type == "L":
                        alt_measurements = []
                        if "Sony" in flight_data_dirs:
                            img_files = os.listdir(os.path.join(flight, "Sony"))
                            for i in img_files:
                                if i.endswith(".JPG"):
                                    fold = "Sony\\" + i
                                    imgF = os.path.join(flight, fold)
                                    #print (imgF)
                                    img = PIL.Image.open(imgF)
                                    exif_data = img._getexif()
                                    dt = exif_data[36867]
                                    #print(datetime)
                                    timestamp = dt[11:]
                                    #print (timestamp[3:5])
                                    timestamp = timedelta(hours = int(timestamp[:2]), minutes = int(timestamp[3:5]), seconds = int(timestamp[6:8]))
                                    timecorrecting = timedelta(hours = int(timecorr[:2]), minutes = int(timecorr[3:5]), seconds = int(timecorr[6:8]))
                                    correctedtime = timestamp + timecorrecting
                                    correctedtime = str(correctedtime)
                                    print(correctedtime)

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
                        alt_measurements = []
                        if "Sony" in flight_data_dirs:
                            img_files = os.listdir(os.path.join(flight, "Sony"))
                            for i in img_files:
                                if i.endswith(".JPG"):
                                    fold = "Sony\\" + i
                                    imgF = os.path.join(flight, fold)
                                    #print (imgF)
                                    img = PIL.Image.open(imgF)
                                    exif_data = img._getexif()
                                    dt = exif_data[36867]
                                    #print(datetime)
                                    timestamp = dt[11:]
                                    #print (timestamp[3:5])
                                    timestamp = timedelta(hours = int(timestamp[:2]), minutes = int(timestamp[3:5]), seconds = int(timestamp[6:8]))
                                    timecorrecting = timedelta(hours = int(timecorr[:2]), minutes = int(timecorr[3:5]), seconds = int(timecorr[6:8]))
                                    correctedtime = timestamp + timecorrecting
                                    correctedtime = str(correctedtime)
                                    print(correctedtime)

                                    if "Flight_Log" in flight_data_dirs:
                                        log_files = os.listdir(os.path.join(flight, "Flight_Log"))
                                        log = str(log_files)
                                        log = log.replace("[","")
                                        log= log.replace("]","")
                                        log = log.replace("'","")
                                        print(log)
                                        path = os.path.join(flight, "Flight_Log")
                                        item = os.path.join(path, log)
                                        print(item)

                                        df_baro =pd.read_csv(item, sep = ',', header = [11])
                                        l = list(df_baro)
                                        #print(l)
                                        for time, baro in zip(df_baro['GPS Time'], df_baro['Baro Alt']):
                                            time = str(time)
                                            if time == correctedtime:
                                                #print(time)
                                                ts = time
                                                baroalt = baro
                                                #print(baroalt)
                                                alt_measurements.append([ts, baroalt.split(",")[0]])
                                                #print(alt_measurements)
                                    if "Laser_Altimeter" in flight_data_dirs:
                                        laser_files = os.listdir(os.path.join(flight,"Laser_Altimeter"))
                                        for item in laser_files:
                                            i = item[12]
                                            if i == "G":
                                                path = os.path.join(flight,"Laser_Altimeter")
                                                imgpath = os.path.join(path, item)
                                                df_laser = pd.read_csv(imgpath, sep = ",", names = ["loopCounter", "curr_buffer", "curr_length", "loopBackIntCnt", "externalTrigIntCnt","Time",
                                                                                                   "ValidAok", "Latt", "NS", "Long", "EW", "Speedkts", "TrueCourse","Date","Variation", "EtWt",
                                                                                                    "CheckSum", "Altimeter", "Alt1", "Alt2", "Alt3", "Alt4", "Alt5", "Alt6", "Alt7", "Alt8",
                                                                                                    "Alt9", "Alt10", "Alt11", "Alt12", "Alt13", "Alt14", "Alt15", "Alt16", "Alt17", "Alt18",
                                                                                                   "Alt19", "Alt20", "Alt21", "Alt22", "Alt23", "Alt24", "Alt25", "Alt26", "Alt27", "Alt28",
                                                                                                   "Alt29", "Alt30","Alt31", "Alt32", "Alt33", "Alt34", "Alt35", "Alt36", "Alt37", "Alt38",
                                                                                                   "Alt39", "Alt40", "Alt41", "Alt42", "Alt43", "Alt44", "Alt45", "Alt46", "Alt47", "Alt48"])
                                                df_laser = df_laser.drop([0])
                                                #print(df_laser)
                                                dfl = df_laser.filter(regex='Alt')
                                                dfl = dfl.drop(['Altimeter'], axis = 1)

                                                df_laser['MedianAlt'] =  dfl.median(axis=1, skipna = True)

                                                for time, laser, lat, lon in zip(df_laser['Time'], df_laser['MedianAlt'], df_laser["Latt"], df_laser["Long"]): #need to fix this part bc table is weird
                                                    #print(time)
                                                    time = str(time)
                                                    time = time[:6]
                                                    corrtime = correctedtime.replace(":","")
                                                    if time == corrtime:
                                                        laserG = laser
                                                        lat = lat
                                                        lon = lon
                                            if i == "L":
                                                path = os.path.join(flight, "Laser_Altimeter")
                                                fpath = os.path.join(path, item)
                                                df_laser2 = pd.read_csv(fpath, sep = "  ", header = [2])
                                                for time, laser2 in zip(df_laser2['gmt_time'], df_laser2['laser_altitude_cm']):
                                                    time = str(time)
                                                    if time ==correctedtime:
                                                        l = laser2
                                                        l = float(laser2)
                                                        laserL = l/100

                        pass
                         # TODO for Clara

                    break # out of flight dir

            break # out of daily dirs for each aircraft walk

    break # break out of high level walk