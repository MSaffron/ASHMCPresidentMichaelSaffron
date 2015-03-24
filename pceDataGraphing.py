import xlrd
import csv
import matplotlib as mpl
import matplotlib.pyplot as plt

aliases = {
  "xXx" : "xxx",
  "ye olde zzz" : "zzz",
  "z" : "zzz"
}

serviceNames = [
    "Income after taxes",
    "Maintenance, repairs, insurance, other expenses",
    "Utilities, fuels, and public services",
    "Household operations",
    "Maintenance and repairs",
    "Health insurance",
    "Medical services",
    "Personal care products and services",
    "Personal insurance and pensions"
    ]

incomeName = "Income after taxes"    
firstYear = 2005
lastYear = 2013
txtFirstYear = 1984
txtLastYear = 2004
allYears = range(txtFirstYear, lastYear+1)

def getVal(item):
    return item.value

def loadTxtPCEData():
    pceData = {}
    for year in range(txtFirstYear, txtLastYear+1):
        print year
        pceData[year] = {}
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
                if len(row) < 8 or endofname == -1:
                    continue

                # We skip the first and last column, which contain "TOTAL and INCMPL"
                values = map(float, row[1:6])
                pceData[year][item] = values

    return pceData

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
        
        for rowIndex in range(sheet.nrows): 
            row = sheet.row(rowIndex)
            item = row[0].value.strip()
            values = map(getVal, row[1:])
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

def printAllFields():
    pceData = loadPCEData()
    txtPCEData = loadTxtPCEData()
    fields = set()

    for year in range(firstYear, lastYear):
        yearFields = pceData[year]
        for field in yearFields:
            fields.add(field)

    for year in range(txtFirstYear, txtLastYear+1):
        yearFields = txtPCEData[year]
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
        serviceValues.append(pceData[year][service][i])
      groupDict[service] = serviceValues
    result[groupNames[i]] = groupDict
  return result

def main():
    # pceData = loadPCEData()
    # incomeData = isolateIncome(pceData)
    # for field in pceData[lastYear]:
    #   if (field != "Item") and (field != "Never attended and other"):
    #     plotData(field, pceData)

    printAllFields()

if __name__ == "__main__":
    main()
