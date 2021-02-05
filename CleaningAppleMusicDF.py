import pandas as pd
import numpy as np
import re
import datetime
from collections import Counter
import matplotlib.pyplot as plt
appleActifityDF = pd.read_csv("Apple Music Play Activity12.2.20.csv")

#Starting to clean up the appleActivityDF

#Renaming Artist and Song Name columns
appleActifityDF.rename(columns={"Artist Name" : "Artist", "Content Name": "Song"})

#Accurate time column
appleActifityDF["Timestamp"] = appleActifityDF["Event Start Timestamp"].fillna(appleActifityDF["Event End Timestamp"])
nulls = np.where(pd.isnull(appleActifityDF["Timestamp"]))
if(nulls[0].size > 0):
    print("There are nulls in Timestamp col")

#Add basic date column
appleActifityDF["DateFull"] = appleActifityDF["Timestamp"].str[0 : 10]

#Adding year month and time columns

#Year column
appleActifityDF["Year"] = appleActifityDF["Timestamp"].str[0 : 4]

#Month column
appleActifityDF["Month"] = appleActifityDF["Timestamp"].str[5 : 7]

#Day column
appleActifityDF["Day"] = appleActifityDF["Timestamp"].str[8 : 10]

#Time
appleActifityDF["UTCTime"] = appleActifityDF["Timestamp"].str[11 : 19]

#UTC time in seconds
ftr = [3600,60,1]
def sumTime(y):
    y = y.split(':')
    return sum([a * b for a, b in zip(ftr, map(int, y))])

appleActifityDF["UTCTimeSeconds"] = appleActifityDF["UTCTime"].apply(sumTime)

#Local Time
appleActifityDF["LocalTimeSeconds"] = appleActifityDF["UTCTimeSeconds"] + appleActifityDF["UTC Offset In Seconds"]

appleActifityDF["LocalTime"] = appleActifityDF["UTCTimeSeconds"].apply(lambda a: str(datetime.timedelta(seconds=int(a))))

appleActifityDF["LocalTimeFloorHours"] = appleActifityDF["LocalTime"].apply(lambda a: int(re.search("[^:]*", a).group(0)))


#histogram of hours most listend during
#appleActifityDF["LocalTimeFloorHours"].value_counts().plot(kind='bar')
#plt.show()



print(appleActifityDF["LocalTimeFloorHours"].head(10))