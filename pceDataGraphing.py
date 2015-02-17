import xlrd
import matplotlib.pyplot as plt

serviceNames = [
    "xxx",
    "yyy",
    "zzz"]
firstYear = 2011
lastYear = 2011

pceData = dict()


def loadPCEData():
    for year in range(firstYear, lastYear+1):
        dataBook = xlrd.open_workbook(filename = ("quintile%d.xls" % year))
        if len(dataBook.sheets()) > 1:
            print "Too many sheets in file: %d" % year
            continue
        allSheets = dataBook.sheets()
        sheet = allSheets[0]
        for rowIndex in range(sheet.nrows):
            row = sheet.row(rowIndex)
            if row[0] == '':
                continue
            item = row[0].encode('ascii')
            values = row[1:]
            
            # 0 = all quintiles
            # 1 = Bottom 20%
            # ... 
            # 5 = Top 20%
            for index in range(len(values)):
                pceData((item, year, index)) = values[index]

def main():
    loadPCEData()







if __name__ == "__main__":
    main()