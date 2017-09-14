"""
Case Based Reasoner for Travel Recommendation
Script to populate .sqlite file
Jason Natale
CSC767 - Assignment 2
"""
import sqlite3
import xlrd
import geopy
from geopy.geocoders import Nominatim
from geopy.distance import great_circle
from socket import timeout

#Parsing through entire XLS file & collecting cases
workbook = xlrd.open_workbook('TRAVEL.XLS')
sheet = workbook.sheet_by_name('Sheet1')
#geographical locator
geolocator = Nominatim()
#Each case comprises of indexed  and unindexed vars
#indexed are: HolidayType, Price, NumberOfPersons, Region, Transportation, Duration, Season, and Accommodation
#unindexed are: case, JourneyCode, and Hotel
cases = []
r = 0
var = None
loc = None
price_r=[5000,0,"Price"]
persons_r=[5,0,"Persons"]
dist_r=[0,0,"Distance"]
duration_r=[30,0,"Duration"]

print("Scanning In Case Bases...")
while(True):
    if sheet.cell(r,1).value == "case":
        ind = []
        unind = []
        var = sheet.cell(r,2).value
        print(var)
        unind.append(var)
        r+=1
        var = sheet.cell(r,2).value
        unind.append(var)
        r+=1
        var = sheet.cell(r,2).value
        var = var[:-1]
        ind.append(var)
        r+=1
        #Get Price
        var = sheet.cell(r,2).value
        if var < price_r[0]:
            price_r[0] = var
        if var > price_r[1]:
            price_r[1] = var
        ind.append(var)
        r+=1
        #Get Persons
        var = sheet.cell(r,2).value
        if var < persons_r[0]:
            persons_r[0] = var
        if var > persons_r[1]:
            persons_r[1] = var
        ind.append(var)
        r+=1
        var = sheet.cell(r,2).value
        #scrub region data, change Teneriffe to Tenerife, add spaces before capital letters, fix SalzbergerLand
        var = var[:-1]
        if var == "Teneriffe":
            var = "Tenerife"
        elif var == "SalzbergerLand":
            var = "Salzburgerland"
        elif var != "ErzGebirge" and var!="CotedAzur":
            i = 1
            while i < len(var):
                if var[i:i+1].isupper():
                    var = var[:i]+" "+var[i:]
                    i+=1
                i+=1
        #calc lat and long of region, record Region as [[lat,long],name]
        while True:
            try:
                loc = geolocator.geocode(var)
                if loc is None or loc.latitude is None or loc.longitude is None:
                    raise ValueError("Shouldn't be null")
                ind.append([[loc.latitude,loc.longitude],var])
                break
            except ValueError:
                print("Issue finding geolocation of "+var+". Trying again.")
            except geopy.exc.GeocoderServiceError:
                print("Issue finding geolocation of "+var+". Trying again.")
            except timeout:
                print("Issue finding geolocation of "+var+". Trying again.")
        r+=1
        var = sheet.cell(r,2).value
        var = var[:-1]
        ind.append(var)
        r+=1
        #Get Duration
        var = sheet.cell(r,2).value
        if var < duration_r[0]:
            duration_r[0] = var
        if var > duration_r[1]:
            duration_r[1] = var
        ind.append(var)
        r+=1
        var = sheet.cell(r,2).value
        var = var[:-1]
        #Convert season to point on 1/2 unit circle
        ind.append(var)
        r+=1
        var = sheet.cell(r,2).value
        var = var[:-1]
        ind.append(var)
        r+=1
        var = sheet.cell(r,2).value
        unind.append(var)
        #append new case
        cases.append([ind,unind])
        if r== 16378:
            break
    else:
            r+=1

#Calculate max of distance range
dist = None
for r1 in cases:
    for r2 in cases:
        dist = great_circle(r1[0][3][0],r2[0][3][0]).meters
        if dist > dist_r[1]:
            dist_r[1] = dist

#Populate db file
print("Populating db file")
conn = sqlite3.connect('Jason_Natale_CBR_db.sqlite')
c = conn.cursor()
try:
    c.execute('CREATE TABLE Cases (Name VARCHAR(15), JC INTEGER, HT VARCHAR(15), Price INTEGER, Persons INTEGER, LAT FLOAT, LON FLOAT, Region VARCHAR(45), Transport VARCHAR(15), Duration INTEGER, Season VARCHAR(25), Accomm VARCHAR(20), Hotel VARCHAR(45))')
except sqlite3.OperationalError:
    print("Existing Case Base Table Updating...")
c.execute("DELETE FROM Cases")
for case in cases:
    query = 'INSERT INTO Cases (Name,JC, HT, Price, Persons, LAT, LON, Region, Transport, Duration, Season, Accomm , Hotel ) VALUES ("'+case[1][0]+'", '+str(case[1][1])+',"'+case[0][0]+'",'+str(case[0][1])+','+str(case[0][2])+','+str(case[0][3][0][0])+','+str(case[0][3][0][1])+',"'+case[0][3][1]+'","'+case[0][4]+'",'+str(case[0][5])+',"'+case[0][6]+'","'+case[0][7]+'","'+case[1][2]+'")' 
    c.execute(query)
try:
    c.execute('CREATE TABLE Ranges (variable VARCHAR(10), min INTEGER, max INTEGER)')
except sqlite3.OperationalError:
    print("Existing Range Table Updating...")
c.execute("DELETE FROM Ranges")
ranges = [price_r,persons_r,dist_r,duration_r]
for r in ranges:
    query="INSERT INTO Ranges (variable, min, max) VALUES ('"+r[2]+"',"+str(r[0])+","+str(r[1])+")"
    c.execute(query)
conn.commit()
conn.close()

print("Database Population Complete")
