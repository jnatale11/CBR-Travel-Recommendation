"""
Case Based Reasoner for Travel Recommendation
Script to perform k-NN algorithm and provide top options
Jason Natale
CSC767 - Assignment 2
"""
import sqlite3
import math
import geopy
import tkinter
import tkinter.messagebox
from geopy.geocoders import Nominatim
from geopy.distance import great_circle
from socket import timeout

#Get Top Recs for a given input query
#HolidayType, Price, NumberOfPersons, Region, Transportation, Duration, Season, and Accommodation
def TopRecommendations():
    #Scrubbing input fields
    num_outputs=int(E9.get())
    if int(CheckVar3.get())==1:
        val_E3 = None
    else:
        try:
            val_E3 = int(E3.get())
        except ValueError:
            print("Make sure to enter numerical values where applicable!")
            return []
    if int(CheckVar4.get())==1:
        val_E4=None
    else:
        try:
            val_E4 = int(E4.get())
        except ValueError:
            print("Make sure to enter numerical values where applicable!")
            return []
    if int(CheckVar6.get())==1:
        val_E6=None
    else:
        try:
            val_E6=int(E6.get())
        except ValueError:
            print("Make sure to enter numerical values where applicable!")
            return []
    try:
        input_query=[E2.get(),val_E3,val_E4]
    except ValueError:
        print("Make sure to enter numerical values where applicable!")
        return []
    #calc lat and long of region entered, if possible
    skip_regions = CheckVar1.get()
    if skip_regions == 0:
        geolocator = Nominatim()
        while True:
            try:
                loc = geolocator.geocode(E1.get())
                if loc is None or loc.latitude is None or loc.longitude is None:
                    skip_regions = 1
                    print("Location searched for could not be found. Skipping over regional analysis...")
                    input_query.append(None)
                    break
                input_query.append([loc.latitude,loc.longitude])
                break
            except geopy.exc.GeocoderServiceError:
                print("Issue finding geolocation of "+E1.get()+". Trying again.")
            except timeout:
                print("Issue finding geolocation of "+E1.get()+". Trying again.")
    else:
        input_query.append(None)
    try:
        ending_vars = [E5.get(),val_E6,E7.get(),E8.get()]
    except ValueError:
        print("Make sure to enter numerical values where applicable!")
        return []
    input_query = input_query + ending_vars
    print("Searching on..."+str(input_query))
    output=[]
    local_val = 0
    global_sim = 0
    case_locals = []
    #Calculating global sim for each case
    for case in cases:
        local_val = 0
        global_sim = 0
        case_locals=[]
        if int(CheckVar2.get()) == 0:
            global_sim+= TypeSimilarity(input_query[local_val],case[2])*w[local_val]
            case_locals.append(global_sim)
        else:
            case_locals.append(None)
        local_val+=1
        #Less is perfect for price
        if int(CheckVar3.get()) == 0:
            if case[3] <= input_query[local_val]:
                price_sim = 1
            else:
                price_sim= (ranges[0][2] - input_query[local_val] - abs(case[3]-input_query[local_val]))/(ranges[0][2]-input_query[local_val])
            global_sim+= price_sim*w[local_val]
            case_locals.append(price_sim*w[local_val])
        else:
            case_locals.append(None)
        local_val+=1
        #More is perfect for persons
        if int(CheckVar4.get())==0:
            if case[4] >= input_query[local_val]:
                persons_sim = 1
            else:
                persons_sim = (input_query[local_val]-ranges[1][1] - abs(case[4]-input_query[local_val]))/(input_query[local_val]-ranges[1][1])
            global_sim+= persons_sim*w[local_val]
            case_locals.append(persons_sim*w[local_val])
        else:
            case_locals.append(None)
        local_val+=1
        #Getting region similarity
        if skip_regions==0:
            region_sim = (ranges[2][2] - great_circle([case[5],case[6]],input_query[local_val]).meters)/ranges[2][2]
            global_sim+=region_sim*w[local_val]
            case_locals.append(region_sim*w[local_val])
        else:
            case_locals.append(None)
        local_val+=1
        if int(CheckVar5.get())==0:
            transport_sim = TransportSimilarity(input_query[local_val],case[8])
            global_sim+=transport_sim*w[local_val]
            case_locals.append(transport_sim*w[local_val])
        else:
            case_locals.append(None)
        local_val+=1
        #More is perfect for duration
        if int(CheckVar6.get())==0:
            if case[9] > input_query[local_val]:
                dur_sim = 1
            else:
                dur_sim = (input_query[local_val]-ranges[3][1] - abs(case[9] - input_query[local_val]))/(input_query[local_val]-ranges[3][1])
            global_sim+= dur_sim*w[local_val]
            case_locals.append(dur_sim*w[local_val])
        else:
            case_locals.append(None)
        local_val+=1
        #Calculation of Season Sim
        if int(CheckVar7.get())==0:
            season_sim = SeasonSimilarity(case[10],input_query[local_val])
            global_sim+= season_sim*w[local_val]
            case_locals.append(season_sim*w[local_val])
        else:
            case_locals.append(None)
        local_val+=1
        if int(CheckVar8.get())==0:
            accomm_sim = AccommSimilarity(input_query[local_val],case[11])
            global_sim+= accomm_sim*w[local_val]
            case_locals.append(accomm_sim*w[local_val])
        else:
            case_locals.append(None)
        output = ProcessAsRecommendation(output, global_sim/w_sum,case, case_locals,num_outputs)
    #Make message boxes for output
    for i in range(len(output)):
        msg="Trip Name: "+output[i][1][0]+"\nTrip Code: "+str(output[i][1][1])+"\nLocation: "+output[i][1][7]
        msg+="\nHoliday Type: "+output[i][1][2]+"\nPrice: "+str(output[i][1][3])+"\nNumber of People: "+str(output[i][1][4])
        msg+="\nTransportation: "+output[i][1][8]+"\nTrip Length: "+str(output[i][1][9])
        msg+="\nMonth of Trip: "+output[i][1][10]+"\nAccommodation: "+output[i][1][11]+"\nHotel: "+output[i][1][12]
        msg+="\nSimilarity Measure: "+str(output[i][0])
        tkinter.messagebox.showinfo("Suggestion #"+str(i+1),msg)
        print(str(i+1))
        print(msg)
        print("Local Similarity Metrics: "+str(output[i][2]))
        print("\n")

def TypeSimilarity(t1,t2):
    if t1==t2:
        return 1
    #Find closest shared parent in tree, return value at node
    else:
        path1=SearchTree(HT_taxonomy,t1)
        path2=SearchTree(HT_taxonomy,t2)
        shared_path = []
        if len(path1) < len(path2):
            short = path1
            long = path2
        else:
            short = path2
            long = path1
        for x in range(len(short)):
            if short[x] != long[x]:
                break
            else:
                shared_path.append(short[x])
        node = HT_taxonomy
        for val in shared_path:
            node = node[val]
        return node[0][1]

#Recursive search method on tree, returns path to a node or empty list if node not found
def SearchTree(tree,node_name):
    if tree[0][0] == node_name:
        return [0]
    elif tree[0] == node_name:
        return [0]
    else:
        branch = 1
        while branch < len(tree):
            sub_path = SearchTree(tree[branch],node_name)
            if len(sub_path) > 0:
                sub_path.insert(0,branch)
                return sub_path
            branch+=1
        return []

def TransportSimilarity(desired,actual):
    desired_val = 0
    actual_val = 0
    if desired == "Plane":
        desired_val = 0
    elif desired == "Car":
        desired_val = 1
    elif desired == "Train":
        desired_val = 2
    else:
        desired_val = 3
    if actual == "Plane":
        actual_val = 0
    elif actual == "Car":
        actual_val = 1
    elif actual == "Train":
        actual_val = 2
    else:
        actual_val = 3
    return Transport_matrix[actual_val][desired_val]

def SeasonSimilarity(s1,s2):
    s1_val = None
    s2_val = None
    for x in range(12):
        if s1 == Seasons[x]:
            s1_val = x
        if s2 == Seasons[x]:
            s2_val = x
    ind = abs(s1_val-s2_val)
    if ind>6:
        ind = 6-abs(ind-6)
    return 1-Seasons_dist[ind]

def AccommSimilarity(desired,actual):
    d_val = None
    a_val = None
    for x in range(6):
        if desired == Accomms[x]:
            d_val = x
        if actual == Accomms[x]:
            a_val = x
    return Accomm_matrix[a_val][d_val]

def ProcessAsRecommendation(current_recs, new_sim, new_case, case_locals, max_len):
    if len(current_recs) == 0:
        current_recs.insert(0,[new_sim,new_case,case_locals])
    else:
        for x in range(len(current_recs)):
            if current_recs[x][0] < new_sim:
                current_recs.insert(x,[new_sim,new_case,case_locals])
                break
    if len(current_recs) > max_len:
        current_recs = current_recs[:-1]
    return current_recs

#Structuring GUI
window =tkinter.Tk()
window.title("Vacation Recommendation System")
tkinter.Label(window,text='Enter details for your dream vacation and hit search!',font=24).pack()
query_details=tkinter.LabelFrame(window)
query_details.pack(fill="both",expand="yes")
tkinter.Label(query_details,text="Location: ").grid(row=1,column=1)
E1=tkinter.Entry(query_details)
E1.grid(row=1,column=2)
CheckVar1 = tkinter.IntVar()
R1=tkinter.Checkbutton(query_details,text="Don't care", variable=CheckVar1, onvalue=1, offvalue=0).grid(row=1,column=3)
tkinter.Label(query_details,text="Holiday Type: ").grid(row=2,column=1)
E2=tkinter.Spinbox(query_details,values=("Bathing","Active","Education","City","Recreation","Wandering","Language","Skiing"))
E2.grid(row=2,column=2)
CheckVar2 = tkinter.IntVar()
R2=tkinter.Checkbutton(query_details,text="Don't care", variable=CheckVar2, onvalue=1, offvalue=0).grid(row=2,column=3)
tkinter.Label(query_details,text="Price: ").grid(row=3,column=1)
E3=tkinter.Entry(query_details)
E3.grid(row=3,column=2)
CheckVar3 = tkinter.IntVar()
R3=tkinter.Checkbutton(query_details,text="Don't care", variable=CheckVar3, onvalue=1, offvalue=0).grid(row=3,column=3)
tkinter.Label(query_details,text="Number of People: ").grid(row=4,column=1)
E4=tkinter.Entry(query_details)
E4.grid(row=4,column=2)
CheckVar4 = tkinter.IntVar()
R4=tkinter.Checkbutton(query_details,text="Don't care", variable=CheckVar4, onvalue=1, offvalue=0).grid(row=4,column=3)
tkinter.Label(query_details,text="Transportation: ").grid(row=5,column=1)
E5=tkinter.Spinbox(query_details,values=("Plane","Car","Train","Coach"))
E5.grid(row=5,column=2)
CheckVar5 = tkinter.IntVar()
R5=tkinter.Checkbutton(query_details,text="Don't care", variable=CheckVar5, onvalue=1, offvalue=0).grid(row=5,column=3)
tkinter.Label(query_details,text="Trip Length: ").grid(row=6,column=1)
E6=tkinter.Entry(query_details)
E6.grid(row=6,column=2)
CheckVar6 = tkinter.IntVar()
R6=tkinter.Checkbutton(query_details,text="Don't care", variable=CheckVar6, onvalue=1, offvalue=0).grid(row=6,column=3)
tkinter.Label(query_details,text="Month of Trip: ").grid(row=7,column=1)
E7=tkinter.Spinbox(query_details,values=("January","February","March","April","May","June","July","August","September","October","November","December"))
E7.grid(row=7,column=2)
CheckVar7 = tkinter.IntVar()
R7=tkinter.Checkbutton(query_details,text="Don't care", variable=CheckVar7, onvalue=1, offvalue=0).grid(row=7,column=3)
tkinter.Label(query_details,text="Accommodation: ").grid(row=8,column=1)
E8=tkinter.Spinbox(query_details,values=("HolidayFlat","OneStar","TwoStars","ThreeStars","FourStars","FiveStars"))
E8.grid(row=8,column=2)
CheckVar8 = tkinter.IntVar()
R8=tkinter.Checkbutton(query_details,text="Don't care", variable=CheckVar8, onvalue=1, offvalue=0).grid(row=8,column=3)
tkinter.Label(query_details,text="Number of Results: ").grid(row=9,column=1)
E9=tkinter.Spinbox(query_details, from_=1,to=15)
E9.grid(row=9,column=2)
Search = tkinter.Button(window,text="Search",command=TopRecommendations)
Search.pack()


#Weighting for construction of global similarity value
w=[1.2,1.4,2,1.4,1,1.1,1.5,1.1]
w_sum=10.7

#Read all cases from db
print("Reading in cases from database")
conn = sqlite3.connect("Jason_Natale_CBR_db.sqlite")
c = conn.cursor()
c.execute("Select * from Cases")
cases = c.fetchall()
c.execute("Select * from Ranges")
ranges = c.fetchall()
conn.close()

#Construct data structures necessary to calc local sim
HT_taxonomy=[["All",.2],[["Sporty",.5],[["Recreation",.7],["Wandering"],["Bathing"]],[["Active",.7],["Skiing"]]],[["Education",.8],["Language"]],["City"]]
Transport_matrix=[[1,.6,.7,.8],[.3,1,.3,1],[.5,.4,1,1],[.2,.2,.2,1]]
Seasons=["January","February","March","April","May","June","July","August","September","October","November","December"]
Seasons_dist = []
for i in range(7):
    Seasons_dist.append(math.sin(i*math.pi/6/2))
Accomms = ["HolidayFlat","OneStar","TwoStars","ThreeStars","FourStars","FiveStars"]
Accomm_matrix=[[1,.6,.6,.6,.6,.6],[.6,1,.8,.6,.4,.2],[.6,1,1,.8,.6,.4],[.6,1,1,1,.8,.6],[.6,1,1,1,1,.8],[.6,1,1,1,1,1]]

window.mainloop()
