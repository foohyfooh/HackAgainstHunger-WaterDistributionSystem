# Part 1 - Read the csv data
import csv
dataFile = open('aquastat.csv')
csvFile = csv.reader(dataFile ,delimiter='\t')

# Part 2 - Seperate the data by country and year
csvData = []
years = set()
variables = set()
countryData = {}
passedHeader = False
for row in csvFile:
    country = row[0].strip()
    if country == '': # Ignore empty rows
        pass
    elif passedHeader:
        if not country in countryData:
            countryData[country] = {}
        year = row[4]
        variable = row[2];
        years.add(year)
        variables.add(variable)
        if not year in countryData[country]:
            countryData[country][year] = {}
        countryData[country][year][variable] = float(row[5])
    else: # Ignore the headings
        print(row)
        passedHeader = True
dataFile.close()

# Part 2.5 - Fill in missing data
for country in countryData.keys():
    for year in years:
        if not year in countryData[country]:
            countryData[country][year] = {}
        for variable in variables:
            if not variable in countryData[country][year]:
                countryData[country][year][variable] = 0

# Part 3 - Generate averages for the data in each year (Do simple average rather than using correct count of the countries that meet the criteria)
yearSumsforVariables = {}
for country, data in countryData.items():
    for year in years:
        if not year in yearSumsforVariables:
            yearSumsforVariables[year] = {}
        for variable in variables:
            if not variable in yearSumsforVariables[year]:
                yearSumsforVariables[year][variable] = 0
            yearSumsforVariables[year][variable] += countryData[country][year][variable]

numCountries = len(countryData)
yearAveragesforVariables = {}
for year in yearSumsforVariables.keys():
    if not year in yearAveragesforVariables:
        yearAveragesforVariables[year] = {}
    for variable in variables:
        yearAveragesforVariables[year][variable] = yearSumsforVariables[year][variable] / numCountries    

# Part 4 - Get geographical data for the countries to do proximity detection
from geopy.geocoders import Nominatim
geolocator = Nominatim()
locations = {}
for country in countryData.keys():
    try:
        l = geolocator.geocode(country)
        locations[country] = [l.latitude, l.longitude]
    except:
        locations[country] = []

# Part 5 - Determine the distance between countries (using distance between on a plane for simplicity)
locationMapping = {} # Country to Number
reverseLocationMapping = {} # Number to Country
c = 0
for country in countryData.keys():
    locationMapping[country] = c
    reverseLocationMapping[c] = country
    c += 1

import numpy
from scipy.spatial import distance
locationMatrix = numpy.zeros((numCountries, numCountries))
for c1 in countryData.keys():
    m1 = locationMapping[c1]
    l1 = locations[c1]
    for c2 in countryData.keys():
        m2 = locationMapping[c2]
        l2 = locations[c2]
        
        if m1 == m2:
            locationMatrix[m1][m2] = 0
        if len(l1) != 2 or len(l2) != 2:
            locationMatrix[m1][m2] = -1
        else:
            locationMatrix[m1][m2] = distance.euclidean(l1, l2)

# Part 6 - Export the data to a useable format
outputFile = open('data.csv', 'w', newline='')
outputCSV = csv.writer(outputFile)
#outputCSV.writerow(['Country', 'Year', 'Variable', 'Value', 'Above Average', 'Location'])
outputCSV.writerow(['Country', 'Year', 'Variable', 'Value', 'Above Average'])
latestYear = max(years)
for country, data in countryData.items():
    for variable in data[latestYear]:
        value = data[latestYear][variable]
        avg = yearAveragesforVariables[latestYear][variable]
        location = str(locations[country])[1:-1]
        #outputCSV.writerow([country, latestYear, variable, value, 1 if value > avg else 0, location])
        outputCSV.writerow([country, latestYear, variable, value, 1 if value > avg else 0])
outputFile.close()

# Part 7 - Export distance information
import json
distanceFile = open('distances.json', 'w')
distanceInfo = {
    'mappings': locationMapping,
    'reverseMappings': reverseLocationMapping,
    'distances': locationMatrix.tolist()
}
json.dump(distanceInfo, distanceFile)
distanceFile.close()