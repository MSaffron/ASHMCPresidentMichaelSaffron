import xlrd
import csv
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import numpy as np

aliases = {
  "Income after taxes 1/" : "Income after taxes",
  "Income after taxes(1)" : "Income after taxes",
  "Income after taxes a/" : "Income after taxes",
  "Main., rep., ins., other expenses" : "Owned dwelling maintenance, repairs, insurance, other expenses",
  "Maint., rep., ins., other expenses" : "Owned dwelling maintenance, repairs, insurance, other expenses",
  "Maintenance, rep., ins., oth. exp" : "Owned dwelling maintenance, repairs, insurance, other expenses",
  "Maintenance, repairs, insurance, other expenses" : "Owned dwelling maintenance, repairs, insurance, other expenses",
  "Maintenance, repairs, insurance,other expenses" : "Owned dwelling maintenance, repairs, insurance, other expenses",
  "Maintenance and repairs" : "Vehicle maintenance and repairs",
  "Mortgage interest" : "Mortgage interest and charges",
  "Mortgage principal paid, owned property" : "Mortgage principal paid on owned property",
  "property" : "Mortgage principal paid on owned property",
  "Other entertainment supplies, equipment and services" : "Other entertainment supplies, equipment, and services",
  "Other entertainment supplies, equipment,and services" : "Other entertainment supplies, equipment, and services",
  "Other entertainment supplies, equipment and serv" : "Other entertainment supplies, equipment, and services",
  "Other ent. sup., equip., and services" : "Other entertainment supplies, equipment, and services",
  "Other ent. supplies, equip., and services" : "Other entertainment supplies, equipment, and services",
  "Other supplies, equip., and services" : "Other entertainment supplies, equipment, and services",
  "Public and other transportation" : "Public transportation",
  "Telephone services" : "Telephone",
  # Goods:
  "Household furnishings and equiptment" : "Household furnishings and equipment",
  "Vehicle purchases (net outlay)" : "Vehicle purchases",
  "Pets, toys, and playground equipment" : "Pets, toys, hobbies, and playground equipment"
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
    "Number of consumer units (in thousands)",
    "Owned dwelling maintenance, repairs, insurance, other expenses",
    "Vehicle maintenance and repairs",
    "Medical services",
    "Mortgage interest and charges",
    "Other entertainment supplies, equipment, and services",
    "Other lodging",
    "Personal care products and services",
    "Personal services",
    "Public transportation",
    "Rented dwellings",
    "Telephone",
    "Utilities, fuels, and public services",
    "Vehicle insurance",
    # Goods:
    "Food at home",
    "Alcoholic beverages",
    "Housekeeping supplies",
    "Household furnishings and equipment",
    "Footwear",
    "Vehicle purchases",
    "Gasoline and motor oil",
    "Drugs",
    "Medical supplies",
    "Pets, toys, hobbies, and playground equipment",
    "Tobacco products and smoking supplies"
    ]

incomeName = "Income after taxes"    
giftsHeader = "Gifts of goods and services"
incomeSourcesHeader = "Sources of income and personal taxes:"
consumerUnits = "Number of consumer units (in thousands)"
xlsFirstYear = 2005
xlsLastYear = 2013
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

                rowLen = 8
                if year == 2004:
                  rowLen = 7
                if len(row) < rowLen or endofname == -1 or (item not in serviceNames and item not in aliases):
                    continue

                serviceName = item
                if aliases.has_key(item):
                  serviceName = aliases[item]
            
                # We skip the first and last column, which contain "TOTAL and INCMPL"
                if year == 2004:
                  values = map(float, row[1:7])
                else:
                  values = map(float, row[2:8])
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
            if item == giftsHeader or item == incomeSourcesHeader:
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
  for i in range(len(allYears)-2):
    result.append(fieldData[i]/income[i] * 100)

  aggData = data["All"][field]
  consumerData = data[group][consumerUnits]
  for i in range(len(allYears) - 2, len(allYears)):
    if group == "All":
      result.append(aggData[i] * 1000 / consumerData[i] / income[i] * 100)
    else:
      result.append(aggData[i] * 1000 * fieldData[i] / consumerData[i] / income[i])
#  result.append(0)
#  result.append(0)
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
        data = percentifyField(field, group, pceData)
        trend = np.poly1d((np.polyfit(allYears, data, 1)))
        ax.plot(allYears, percentifyField(field, group, pceData))
        ax.plot(allYears, trend(allYears), 'k--')
        legendNames.append(group)
        legendNames.append("Slope %s: %.3f" % (group, trend[1]))

    fontP = FontProperties()
    fontP.set_size('small')
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.75, box.height])
    ax.legend(legendNames, loc='center left', bbox_to_anchor=(1, 0.5), prop=fontP)
    plt.xlabel("Year")
    plt.ylabel("Percentage of Income")
    plt.xlim([1984, 2011])
    filename = "figures/" + field + ".png"
    plt.savefig(filename)
    print 'saved file to %s' % filename
    plt.close()

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
