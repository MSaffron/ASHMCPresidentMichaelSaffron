import xlrd
import matplotlib.pyplot as plt

serviceNames = [
    "xxx",
    "yyy",
    "zzz"]
incomeName = "Income after taxes"    
firstYear = 2011
lastYear = 2011

pceData = dict()

def getVal(item):
	return item.value

def loadPCEData():
    for year in range(firstYear, lastYear+1):
    	pceData[year] = {}
        dataBook = xlrd.open_workbook(filename = ("data/quintile%d.xls" % year))
        if len(dataBook.sheets()) > 1:
            print "Too many sheets in file: %d" % year
            continue
        allSheets = dataBook.sheets()
        sheet = allSheets[0]
        
        # Expected format: row 0 has table title, row 1 is empty, row 2 has headers
        columnHeaders = map(getVal, sheet.row(2)[1:])
        for rowIndex in range(3,sheet.nrows):
            row = sheet.row(rowIndex)
            item = row[0].value.strip()
            values = map(getVal, row[1:])
            if row[0] == '' or len(values) == 0:
                # skip empty rows/dataless rows
                continue

            
            # 0 = all quintiles
            # 1 = Bottom 20%
            # ... 
            # 5 = Top 20%
            pceData[year][item] = values
    
    print pceData[2011]

def main():
    loadPCEData()







if __name__ == "__main__":
    main()