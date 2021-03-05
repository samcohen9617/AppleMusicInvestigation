import pandas as pd
import numpy as np
import re
import datetime
from collections import Counter
import math
import matplotlib.pyplot as plt

appleActifityDF = pd.read_csv("Apple Music Play Activity12.2.20.csv")

# Starting to clean up the appleActivityDF
pd.set_option('display.max_columns', None)
# Renaming Artist and Song Name columns
appleActifityDF.rename(columns={"Artist Name": "Artist", "Content Name": "Song"})

# Accurate time column
appleActifityDF["Timestamp"] = appleActifityDF["Event Start Timestamp"].fillna(appleActifityDF["Event End Timestamp"])
nulls = np.where(pd.isnull(appleActifityDF["Timestamp"]))
if (nulls[0].size > 0):
    print("There are nulls in Timestamp col")

# Add basic date column
appleActifityDF["DateFull"] = appleActifityDF["Timestamp"].str[0: 10]

# Adding year month and time columns

# Year column
appleActifityDF["Year"] = appleActifityDF["Timestamp"].str[0: 4]

# Month column
appleActifityDF["Month"] = appleActifityDF["Timestamp"].str[5: 7]

# Day column
appleActifityDF["Day"] = appleActifityDF["Timestamp"].str[8: 10]

# Time
appleActifityDF["UTCTime"] = appleActifityDF["Timestamp"].str[11: 19]

# UTC time in seconds
ftr = [3600, 60, 1]


def sumTime(y):
    y = y.split(':')
    sumTime = sum([a * b for a, b in zip(ftr, map(int, y))])
    return sumTime


appleActifityDF["UTCTimeSeconds"] = appleActifityDF["UTCTime"].apply(sumTime)
index = 0
# Local Time
appleActifityDF["LocalTimeSeconds"] = appleActifityDF["UTCTimeSeconds"] + appleActifityDF["UTC Offset In Seconds"]


def convertLocalSecondsToLocalTime(localTimeSeconds):
    global index
    index = index + 1
    if math.isnan(localTimeSeconds):
        return "00:00:00"
    else:
        if localTimeSeconds < 0:
            localTimeSeconds = 86400 + localTimeSeconds
        elif localTimeSeconds > 86400:
            localTimeSeconds = localTimeSeconds - 86400
        localTime = str(datetime.timedelta(seconds=int(localTimeSeconds)))
        return localTime

appleActifityDF["LocalTime"] = appleActifityDF["LocalTimeSeconds"].apply(convertLocalSecondsToLocalTime)

appleActifityDF["LocalTimeFloorHours"] = appleActifityDF["LocalTime"].apply(
    lambda a: int(re.search("[^:]*", a).group(0)))

# histogram of hours most listend during
#appleActifityDF["LocalTimeFloorHours"].value_counts().plot(kind='bar')
#plt.show()

# Removing songs played on the sonos?
# print(appleActifityDF["Build Version"].value_counts())
appleActifityDF = appleActifityDF[~appleActifityDF["Build Version"].str.contains("sonos", na=False)]

# creating a play percentage column
appleActifityDF["ListenedPercent"] = appleActifityDF["Play Duration Milliseconds"] / appleActifityDF[
    "Media Duration In Milliseconds"]

# Creating A played partial, all or not enough
appleActifityDF["PartialOrComplete"] = appleActifityDF["ListenedPercent"].apply(lambda p: 1 if p > 0.95 else 0)

# Create flag if more than a third
appleActifityDF["FifthOrMoreListened"] = appleActifityDF["ListenedPercent"].apply(lambda p: 1 if p > 0.2 else 0)

# listening duration in minutes
appleActifityDF["ListenedDurationInMinutes"] = (appleActifityDF["Play Duration Milliseconds"] / 1000) / 60

# remove outliers of listening duration
appleActifityDF = appleActifityDF[
    appleActifityDF["ListenedDurationInMinutes"].between(appleActifityDF["ListenedDurationInMinutes"].quantile(0),
                                                         appleActifityDF["ListenedDurationInMinutes"].quantile(.99))]

appleActifityDF = appleActifityDF.drop(["Apple Id Number", "Apple Music Subscription", "Client IP Address", "Content Specific Type",
"Device Identifier", "Event End Timestamp", "Event Reason Hint Type", "Event Received Timestamp", "Item Type", "Metrics Bucket Id", "Metrics Client Id", "Original Title", "Store Country Name", "UTC Offset In Seconds", "End Position In Milliseconds", "Event End Timestamp", "Event Start Timestamp", ], axis=1)

# Next steps returning chart of most frequently listened to artists
#Top 20 most frequently played artists
top20Artists = appleActifityDF["Artist Name"].value_counts()[:20].index.tolist()

#df with only the top 20 artists
appleActifityDFTop20 = appleActifityDF[pd.DataFrame(appleActifityDF["Artist Name"].tolist()).isin(top20Artists).any(1).values]


top20ByMonthYear = appleActifityDFTop20.groupby(["Artist Name", 'Year', "Month"])["Artist Name"].count()
print(top20ByMonthYear.tail(65))