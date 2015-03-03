import xlrd
import matplotlib as mpl
import matplotlib.pyplot as plt

serviceNames = [
    "xxx",
    "yyy",
    "zzz"]
incomeName = "Income after taxes"    
firstYear = 2005
lastYear = 2013

allYears = range(firstYear, lastYear+1)

def getFieldValue(fieldName, year, pceData):
  for name in aliases[fieldName]:
    if pceData[year].has_key(name):
      return pceData[year][name]
  # TODO: error
  return []

def getVal(item):
    return item.value

def loadPCEData():
    pceData = {}
    for year in range(firstYear, lastYear+1):
        pceData[year] = {}
        dataBook = xlrd.open_workbook(filename = ("data/quintile%d.xls" % year))
        if len(dataBook.sheets()) > 1:
            print "Too many sheets in file: %d" % year
            continue
        allSheets = dataBook.sheets()
        sheet = allSheets[0]
        
        # Expected format: row 0 has table title, row 1 is empty, row 2 has headers
        columnHeaders = map(getVal, sheet.row(2)[1:]) # currently unused
        for rowIndex in range(2,sheet.nrows): 
        # Going from 2 on means we'll have the headers as a column
            row = sheet.row(rowIndex)
            item = row[0].value.strip()
            values = map(getVal, row[1:])
            if item == '' or len(row[1:]) == 0:
                # skip empty rows/dataless rows
                continue

            
            # 0 = all quintiles
            # 1 = Bottom 20%
            # ... 
            # 5 = Top 20%
            pceData[year][item] = values
    return pceData

# pceData is a dictionary of with year keys and dictionary values. 
# The dictionary values are dictionaries from fields to a list of values.
def plotData(field, pceData):
    print "Plotting", field
    data = {}
    groups = pceData[lastYear]["Item"]
    for group in groups:
        data[group] = []
    years = sorted(pceData.keys())
    for year in years:
        groupedData = pceData[year][field]
        for i in range(len(groupedData)):
            data[groups[i]].append(groupedData[i])

    fig = plt.figure(field, figsize=(9,6))
    ax = plt.subplot(111)
    ax.set_title(field)
    x_formatter = mpl.ticker.ScalarFormatter(useOffset=False)
    ax.xaxis.set_major_formatter(x_formatter)
    legendNames = []
    for group in groups:
        ax.plot(years, data[group])
        legendNames.append(group)
    ax.legend(legendNames, loc=1)
    filename = "figures/" + field + ".png"
    plt.savefig(filename)
    print 'saved file to %s' % filename

    compilationGroups = ["Top vs. Total", "Bottom vs. Total", "Top vs. Bottom"]
    data["Top vs. Total"] = [(data[groups[5]][i] / data[groups[0]][i]) for i in range(len(years))]
    data["Bottom vs. Total"] = [(data[groups[1]][i] / data[groups[0]][i]) for i in range(len(years))]
    data["Top vs. Bottom"] = [(data[groups[5]][i] / data[groups[1]][i]) for i in range(len(years))]

    fig = plt.figure(field, figsize=(9,6))
    ax = plt.subplot(110)
    ax.set_title(field)
    x_formatter = mpl.ticker.ScalarFormatter(useOffset=False)
    ax.xaxis.set_major_formatter(x_formatter)
    legendNames = []
    for group in compilationGroups:
        ax.plot(years, data[group])
        legendNames.append(group)
    ax.legend(legendNames, loc=1)
    filename = "figures/" + field + "_relative.png"
    plt.savefig(filename)
    print 'saved file to %s' % filename


def printAllFields():
    pceData = loadPCEData()
    fields = set()

    for year in allYears:
        yearFields = pceData[year]
        for field in yearFields:
            fields.add(field)

    listOfFields = list(fields)
    listOfFields.sort()
    for field in listOfFields:
        print field

def main():
    pceData = loadPCEData()
    incomeData = isolateIncome(pceData)
    for field in pceData[lastYear]:
      if (field != "Item") and (field != "Never attended and other"):
        plotData(field, pceData)

if __name__ == "__main__":
    main()