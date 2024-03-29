import pandas as pd
import numpy as np
import os
import xml.etree.ElementTree
import csv
import argparse
import PIL.Image
from datetime import datetime
from datetime import timedelta

### Setting up the user input args

# parser = argparse.ArgumentParser(description='Manage the flight imagery and flight logs.')
# parser.add_argument('campaign_filepath', metavar='fp', type=str,
                    # help='relative or abs filepath to the flight campaign data')

# args = parser.parse_args()
# mypath = args.campaign_filepath
# print(mypath)

mypath = "R:\\MarineUAS\\Projects\\Student Projects\\ClaraBird\\test"
### walk through full campaign worth of imagery and pull out lat, lon, both altimeter measurements
TC = os.path.join(mypath, "TimeCorrections.csv")
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
	
for (_, day_aircraft_dirs, filenames) in os.walk(mypath): # descending into campaign dir
	#create lists for variables
	DAFlist = []
	
	ImgList = []
	CorrTimeList = []
	BaroList = []
	LaserList = []
	Time130List = []
	LaserLList = []
	Time130LList = []
	LatList = []
	LonList = []
	LaserLTime = []
	BaroTime = []
	for day_aircraft in day_aircraft_dirs:
		if day_aircraft in day_ac:
			date_aircraft = day_aircraft
			day_aircraft = os.path.join(mypath, day_aircraft)

			for (_, flights, filenames) in os.walk(day_aircraft): # descending into daily dirs for each craft
				print(day_aircraft)

				aircraft_type = day_aircraft[-1] # aircraft type is designated by the final char

				for flight in flights: # iterate through all flights on this day with this platform
					date_aircraft_fl = []
					if flight[0] == 'F':
						num = flight[-1]
						fl = 'F' + num
						date_ac_fl = date_aircraft + '_' + fl
						date_aircraft_fl += [date_ac_fl]
						flight = os.path.join(day_aircraft, flight)
						for daf, timecorrection in zip(dfTimeCorr['Flight'], dfTimeCorr['TimeChange']):
							if daf == date_ac_fl:
								timecorr = str(timecorrection)
								
								for (_, flight_data_dirs, filenames) in os.walk(flight): # descending into flight dir to retrieve flight log
									
									
									
									DateAircraftFlight = daf
									if aircraft_type == "L":
										
										if "Sony" in flight_data_dirs:
											img_files = os.listdir(os.path.join(flight, "Sony"))
											for i in img_files:
												if i.endswith(".JPG"):
													image_name = i
													
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
																#print(item)
																root = xml.etree.ElementTree.parse(os.path.join(flight, "Flight_Logs", item)).getroot()
																alt_collection = root[1][1]
																for alt_point in alt_collection.findall('trkpt'):
																	time = alt_point.find('time').text
																	time = time[11:19]
																	tt = str(time)
																	#time = 
																	#print(time.format)
																	timeGPX = timedelta(hours = int(tt[:2]), minutes = int(tt[3:5]), seconds = int(tt[6:8]))
																	if timeGPX == correctedtime:
																		DAFlist += [daf]
																		ImgList += [i]
																		CorrTimeList += [correctedtime]
																	# if time in list of time from timecorrection.csv
																		print("found it!!!")
																		lat = alt_point.attrib['lat']
																		LatList += [lat]
																		lon = alt_point.attrib['lon']
																		LonList += [lon]
																		extensions = alt_point.find("extensions")
																		laser = extensions.find('Laser').text
																		if laser == 130:
																			tm = timedelta(hours = int(time[:2]), minutes = int(time[2:4]), seconds = int(time[4:6]))
																			#print(t)
																			upperbound = tm + timedelta(seconds = 5)
																			#print(upperbound)
																			lowerbound = tm - timedelta(seconds = 5)
																			#print (lowerbound)
																			windowtime = []
																			windowlaser = []
																			windowtimediff = []
																			for t, laser in zip(df_laser['Time'],df_laser['MedianAlt']):
																				#print (t)
																				t = timedelta(hours = int(t[:2]), minutes = int(t[2:4]), seconds = int(t[4:6]))
																				#print(t)
																				if t >= lowerbound and t <= upperbound:
																					#print (t)
																					windowtime += [t]
																					#laser = str(laser)
																					#print(laser)
																					windowlaser += [laser]
																					timediff = abs(t - tm)
																					#print(timediff)
																					windowtimediff += [timediff]
																			d = {'time': windowtime, 'timediff': windowtimediff, 'laser': windowlaser}
																			df_window = pd.DataFrame(data=d)
																			df_window = df_window.drop(df_window[df_window.laser == 130.000].index)
																			if df_window.empty == True:
																				laser = "130*"
																				time130 = t
																				LaserList+=[laser]
																				Time130List += [time130]
																			else:
																				#print(df_window)
																				values = df_window.loc[df_window['timediff'].idxmin()]
																				time130 = values['time']
																				las130 = values['laser']
																				las130 = str(las130)
																				laser = las130 + "*"
																				LaserList += [laser]
																				Time130List += [time130]
																		elif laser != 130:
																			laser = laser
																			time130 = np.nan
																			LaserList += [laser]
																			Time130List += [time130]
																		#make laser L variables so that all lists are same length
																		laserL = np.nan
																		time130L = np.nan
																		LaserLList += [laserL]
																		Time130LList += [time130L]
																		

																		baroalt = extensions.find('Altimeter').text
																		BaroList += [baroalt]
																		BaroTime += [t]
																		print(lat, lon, laser, alt)
																		
																		# #make all variables str
																		# correctedtime = str(correctedtime)
																		# lat = str(lat)
																		# lon = str(lon)
																		# baroalt = str(baroalt)
																		# time130 = str(time130)
																		# laser = str(laser)
																		# time130_L = str(time130_L)
																		# laserL = str(laserL)
																		
																		# alt_measurements.append([DateAircraftFlight, image_name, correctedtime, lat, lon, baroalt, time130, laser, time130_L, laserL .split(",")[0]])
																	
																


										#for data_dir in flight_data_dirs:
											#pass


									if aircraft_type == "A":
										
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
													
													#print(correctedtime)

													if "Flight_Log" in flight_data_dirs:
														log_files = os.listdir(os.path.join(flight, "Flight_Log"))
														log = str(log_files)
														log = log.replace("[","")
														log= log.replace("]","")
														log = log.replace("'","")
														#print(log)
														path = os.path.join(flight, "Flight_Log")
														item = os.path.join(path, log)
														#print(item)

														df_barometer =pd.read_csv(item, sep = ',', header = 11, dtype = str)
														#print(df_barometer)
														df_baro = df_barometer.iloc[:,[3, 143]]
														#print(df_baro)
														df_baro.columns = ['GPS Time', 'Baro Alt']
														#print(df_baro)
														#l = list(df_baro)
														#print(l)
														df_baro = df_baro.groupby(['GPS Time'])['Baro Alt'].first().reset_index()
														#print(df_baro)
														for time, baro in zip(df_baro['GPS Time'], df_baro['Baro Alt']):
															time = str(time)
															#baro = []
															if time == correctedtime:
															
																#print(time)
																ts = time
																BaroTime += [ts]
																if baro:
																	baroalt = baro
																	BaroList += [baroalt]
																else:
																	baroalt = np.nan
																	BaroList += [baroalt]	
																
															
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
																#print(df_laser)

																for time, laser, lat, lon in zip(df_laser['Time'], df_laser['MedianAlt'], df_laser["Latt"], df_laser["Long"]): #need to fix this part bc table is weird
																	#print(time)
																	time = str(time)
																	time = time[:6]
																	corrtime = correctedtime.replace(":","")
																	if time == corrtime:
																		ImgList += [item]
																		DAFlist += [daf]
																		CorrTimeList += [correctedtime]

																		lat = lat
																		lon = lon
																		LatList += [lat]
																		LonList += [lon]
																		if laser == 130:
																			tm = timedelta(hours = int(time[:2]), minutes = int(time[2:4]), seconds = int(time[4:6]))
																			#print(t)
																			upperbound = tm + timedelta(seconds = 5)
																			#print(upperbound)
																			lowerbound = tm - timedelta(seconds = 5)
																			#print (lowerbound)
																			windowtime = []
																			windowlaser = []
																			windowtimediff = []
																			for t, laser in zip(df_laser['Time'],df_laser['MedianAlt']):
																				#print (t)
																				t = timedelta(hours = int(t[:2]), minutes = int(t[2:4]), seconds = int(t[4:6]))
																				#print(t)
																				if t >= lowerbound and t <= upperbound:
																					#print (t)
																					windowtime += [t]
																					#laser = str(laser)
																					#print(laser)
																					windowlaser += [laser]
																					timediff = abs(t - tm)
																					#print(timediff)
																					windowtimediff += [timediff]
																			d = {'time': windowtime, 'timediff': windowtimediff, 'laser': windowlaser}
																			df_window = pd.DataFrame(data=d)
																			df_window = df_window.drop(df_window[df_window.laser == 130.000].index)
																			if df_window.empty == True:
																				laser = "130*"
																				time130 = np.nan
																				LaserList += [laser]
																				Time130List +=[time130]
																			else:
																				#print(df_window)
																				values = df_window.loc[df_window['timediff'].idxmin()]
																				time130 = values['time']
																				las130 = values['laser']
																				las130 = str(las130)
																				laser = las130 + "*"
																				LaserList += [laser]
																				Time130List +=[time130]
																		elif laser != 130:
																			laser = laser
																			time130 = np.nan
																			LaserList += [laser]
																			Time130List += [time130]
																		




															if i == "L":
																path = os.path.join(flight, "Laser_Altimeter")
																fpath = os.path.join(path, item)
																df_laser2 = pd.read_csv(fpath, sep = "\t", header = 2)
																#print (df_laser2)
																for time, laser2 in zip(df_laser2['gmt_time'], df_laser2['laser_altitude_cm']):
																	time = str(time)
																	if time ==correctedtime:
																		print(time)
																		l = laser2
																		l = float(laser2)
																		laserL = l/100
																		#if laser:
																		if laser == 130:
																			tm = timedelta(hours = int(time[:2]), minutes = int(time[3:5]), seconds = int(time[6:8]))
																			#print(t)
																			upperbound = tm + timedelta(seconds = 5)
																			#print(upperbound)
																			lowerbound = tm - timedelta(seconds = 5)
																			#print (lowerbound)
																			windowtime = []
																			windowlaser = []
																			windowtimediff = []
																			for t, laser in zip(df_laser['Time'],df_laser['MedianAlt']):
																				#print (t)
																				ltime = t
																				t =  timedelta(hours = int(t[0:2]), minutes = int(t[2:4]), seconds = int(t[4:6]))
																				#print(t)
																				if t >= lowerbound and t <= upperbound:
																					#print (t)
																					windowtime += [t]
																					#laser = str(laser)
																					#print(laser)
																					windowlaser += [laser]
																					timediff = abs(t - tm)
																					#print(timediff)
																					windowtimediff += [timediff]
																			d = {'time': windowtime, 'timediff': windowtimediff, 'laser': windowlaser}
																			df_window = pd.DataFrame(data=d)
																			df_window = df_window.drop(df_window[df_window.laser == 130.000].index)
																			#print(df_window)
																			if df_window.empty == True:
																				laserL = "130*"
																				time130_L = np.nan
																				LaserLList += [laserL]
																				Time130LList += [time130_L]
																				LaserLTime += [time]
																			else:
																				values = df_window.loc[df_window['timediff'].idxmin()]
																				time130_L = values['time']
																				las130 = values['laser']
																				las130 = str(las130)
																				laserL = las130 + "*"
																				LaserLList += [laserL]
																				Time130LList += [time130_L]
																				LaserLTime += [time]
																		elif laser != 130:
																			laserL = str(laser)
																			time130_L = np.nan
																			LaserLList += [laserL]
																			Time130LList += [time130_L]
																			LaserLTime += [time]
																		# else:
																			# laserL = np.nan
																			# time130_L = np.nan
																			# LaserLList += [laserL]
																			# Time130LList += [time130_L]
																		
														# #make all variables str
														# correctedtime = str(correctedtime)
														# lat = str(lat)
														# lon = str(lon)
														# baroalt = str(baroalt)
														# time130 = str(time130)
														# laser = str(laser)
														# time130_L = str(time130_L)
														# laserL = str(laserL)
																
														# alt_measurements.append([DateAircraftFlight, image_name, correctedtime, lat, lon, baroalt, time130, laser, time130_L, laserL .split(",")[0]])
										#print(alt_measurements)
										# with open(day_aircraft.split('/')[-1] + ".csv", 'w', newline='') as myfile:
											# wr = csv.writer(myfile)
											# wr.writerows(alt_measurements)

										# print(day_aircraft + ".csv")
	print(len(DAFlist), len(ImgList), len(CorrTimeList), len(BaroList), len(LaserList), len(Time130List), len(LaserLList), len(Time130LList),
			len(LatList), len(LonList))
	d = {'DayAircraftFlight':DAFlist, 'Image':ImgList, "CorrectedTime": CorrTimeList,
			"LaserAlt": LaserList, "Time130": Time130List,"Lat": LatList, "Lon":LonList}
	df_measurements = pd.DataFrame(data = d)
	#print(df_measurements)
	db = {'CorrectedTime':BaroTime, 'BaroAlt': BaroList}
	print(len(BaroTime), len(BaroList))
	df_baro = pd.DataFrame(data = db)
	#print(df_baro)
	dlas = {'CorrectedTime' : LaserLTime, 'Time130_L': Time130LList, 'LaserL': LaserLList}
	df_LaserL = pd.DataFrame(data = dlas)
	print(df_LaserL)
	df_measurements1 = df_measurements.set_index('CorrectedTime').join(df_baro.set_index('CorrectedTime'))
	print(df_measurements1)
	df_measurements2 = df_measurements1.set_index('CorrectedTime').join(df_LaserL.set_index('CorrectedTime'))
	print(df_measurements2)
	#print(df_measurements)
	df_measurements2.to_csv(mypath+"\\Image_Measurements.csv", sep = ',')
	df_LaserL.to_csv(mypath+"\\LaserL.csv",sep=',')
	df_baro.to_csv(mypath+"\\Baro.csv",sep=',')
	df_measurements.to_csv(mypath+"\\noBaro_noLaserL.csv",sep= ',')
							#pass
                         # TODO for Clara

				#break # out of flight dir

			#break # out of daily dirs for each aircraft walk

	break # break out of high level walk
