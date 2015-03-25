import xlrd
import csv
import matplotlib as mpl
import matplotlib.pyplot as plt

aliases = {
  "Income after taxes 1/" : "Income after taxes",
  "Income after taxes(1)" : "Income after taxes",
  "Income after taxes a/" : "Income after taxes",
  "Main., rep., ins., other expenses" : "Owned dwelling maintenance, repairs, insurance, other expenses",
  "Maint., rep., ins., other expenses" : "Owned dwelling maintenance, repairs, insurance, other expenses",
  "Maintenance, rep., ins., oth. exp" : "Owned dwelling maintenance, repairs, insurance, other expenses",
  "Maintenance, repairs, insurance, other expenses" : "Owned dwelling maintenance, repairs, insurance, other expenses",
  "insurance, other expenses" : "Owned dwelling maintenance, repairs, insurance, other expenses",
  "expenses" : "Owned dwelling maintenance, repairs, insurance, other expenses",
  "Maintenance and repairs" : "Vehicle maintenance and repairs",
  "Mortgage interest" : "Mortgage interest and charges",
  "Mortgage principal paid, owned property" : "Mortgage principal paid on owned property",
  "property" : "Mortgage principal paid on owned property",
  "Other entertainment supplies, equipment and services" : "Other entertainment supplies, equipment, and services",
  "Other ent. sup., equip., and services" : "Other entertainment supplies, equipment, and services",
  "Other ent. supplies, equip., and services" : "Other entertainment supplies, equipment, and services",
  "Other supplies, equip., and services" : "Other entertainment supplies, equipment, and services",
#  "Other entertainment" : "Other entertainment supplies, equipment, and services",
  #"Public and other transportation" : "Public transportation" # Is this really an alias? I can't find what year it's from
  "Telephone services" : "Telephone"
}

serviceNames = [
    "Education",
    "Electricity",
    "Entertainment",
    "Fees and admissions",
    "Food away from home",
    "Health insurance",
    "Household operations",
    "Income after taxes",
    "Owned dwelling maintenance, repairs, insurance, other expenses",
    "Vehicle maintenance and repairs",
    "Medical services",
    "Mortgage interest and charges",
    "Mortgage principal paid on owned property",
    "Other entertainment supplies, equipment, and services",
    "Other lodging",
    "Personal care products and services",
    "Personal services",
    "Public transportation",
    "Rented dwellings",
    "Telephone"
    ]

incomeName = "Income after taxes"    
giftsHeader = "Gifts of goods and services"
xlsFirstYear = 2005
xlsLastYear = 2011
txtFirstYear = 1984
txtLastYear = 2004
firstYear = txtFirstYear
lastYear = xlsLastYear
allTXTYears = range(txtFirstYear, txtLastYear+1)
allXLSYears = range(xlsFirstYear, xlsLastYear+1)
allYears = range(firstYear, lastYear+1)

def getVal(item):
    return item.value

def loadTxtPCEData(pceData):
    for year in allTXTYears:
        pceData[year] = {}
        print "Processing", year
        with open("data/quintile%d.txt" % year, 'rb') as datafile:
            for i in range(3):
                datafile.readline()
            for line in datafile:
                # Gross fix, this should work though
                endofname = line.rfind('..')
                if endofname == -1:
                    endofname = line.rfind('.')

                row = line[endofname + 1:].replace('$','').replace(',','').replace('(','-').replace(')','').replace('|','').replace('n.a.','0').replace('b/','0').replace('c/','').replace('d/','').split()
                item = line[:endofname].strip('. ')

                if ("Gift" in item) or (len(row) > 0 and "Gift" in row[0]):
                  break

                if len(row) < 7 or endofname == -1 or (item not in serviceNames and item not in aliases):
                    continue

                serviceName = item
                if aliases.has_key(item):
                  serviceName = aliases[item]
            
                if year == 1984:
                  print serviceName
                # We skip the first and last column, which contain "TOTAL and INCMPL"
                values = map(float, row[1:6])
                pceData[year][serviceName] = values

def loadXlsPCEData(pceData):
    for year in allXLSYears:
        pceData[year] = {}
        dataBook = xlrd.open_workbook(filename = ("data/quintile%d.xls" % year))
        if len(dataBook.sheets()) > 1:
            print "Too many sheets in file: %d" % year
            continue
        allSheets = dataBook.sheets()
        sheet = allSheets[0]
        
        for rowIndex in range(sheet.nrows): 
            row = sheet.row(rowIndex)
            item = row[0].value.strip()
            values = map(getVal, row[1:])

            # We don't want to include gifts. Stop once we hit them.
            if item == giftsHeader:
              break

            if item not in serviceNames and item not in aliases:
                # skip non-service rows
                continue

            serviceName = item
            if aliases.has_key(item):
              serviceName = aliases[item]

            # 0 = all quintiles
            # 1 = Bottom 20%
            # ... 
            # 5 = Top 20%
            pceData[year][serviceName] = values

    return pceData
    
def percentifyField(field, group, data):
  income = data[group][incomeName]
  fieldData = data[group][field]
  result = []
  for i in range(len(income)):
    result.append(fieldData[i]/income[i])
  return result

def plotData(field, pceData):
    print "Plotting", field
    fig = plt.figure(field, figsize=(9,6))
    ax = plt.subplot(111)
    ax.set_title(field)
    x_formatter = mpl.ticker.ScalarFormatter(useOffset=False)
    ax.xaxis.set_major_formatter(x_formatter)
    legendNames = []
    for group in pceData:
        ax.plot(allYears, percentifyField(field, group, pceData))
        legendNames.append(group)
    ax.legend(legendNames, loc=1)
    filename = "figures/" + field + ".png"
    plt.savefig(filename)
    print 'saved file to %s' % filename

def printAllFields(pceData):
    fields = set()

    for year in allYears:
        yearFields = pceData[year]
        for field in yearFields:
            fields.add(field)

    listOfFields = list(fields)
    listOfFields.sort()
    for field in listOfFields:
        print field

def convertData(pceData):
  """ Takes in Dict(year, Dict(field, List(percentile values))), gives out same data as
      Dict(percentile name, Dict(field, List(year values)))) """
  result = {}
  groupNames = ["All", "0-20", "20-40", "40-60", "60-80", "80-100"]
  for i in range(len(groupNames)):
    groupDict = {}
    for service in serviceNames:
      serviceValues = []
      for year in allYears:
        print year
        serviceValues.append(pceData[year][service][i])
      groupDict[service] = serviceValues
    result[groupNames[i]] = groupDict
  return result

def main():
    pceData = {}
    loadXlsPCEData(pceData)
    loadTxtPCEData(pceData)
    cleanData = convertData(pceData)
    for service in serviceNames:
      plotData(service, cleanData)
#    printAllFields(pceData)

if __name__ == "__main__":
    main()
