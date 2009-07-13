from types import StringType, ListType, FloatType, IntType, BooleanType
from cStringIO import StringIO
from operator import itemgetter
from decimal import *
import pprint
import json

def read_JSON_file(filename):
    FILE = open(filename,"r")
    file_str = StringIO()
    
    for line in FILE:
        file_str.write(line)

    FILE.close()
    dict = json.loads(file_str.getvalue())
    return dict

def save_JSON_file(filename, dict):
    fileToSave = json.dumps(dict)
    FILE_TO_SAVE = open(filename,"w")
    FILE_TO_SAVE.write(fileToSave)
    FILE_TO_SAVE.close()

def produceStatisticalData():
    filename = "data.json"
    filename_save = "dataSave.json"
    result = read_JSON_file(filename)
    
    authorData = {}
    for entry in result:
        authorName = entry["user_id"]
        if not authorData.has_key(authorName):
            textLength = len(entry["text"])
            authorData[authorName] = {"textNumber": 1, "min": textLength, "max": textLength, "totalLength": textLength}
        else:
            authorEntry = authorData[authorName]
            
            authorData[authorName]["textNumber"] += 1
            textLength = len(entry["text"])
            
            authorEntry["min"] = min(authorEntry["min"], textLength)
            authorEntry["max"] = max(authorEntry["max"], textLength)
            authorEntry["totalLength"] += textLength
    
    getcontext().prec = 2        
    for authorName in authorData.keys():
        authorEntry = authorData[authorName]
        authorEntry["average"] = round(float(authorEntry["totalLength"]) / float(authorEntry["textNumber"]), 3)
        
    length = 0
    numberTexts = 0
    minNumber = 1000000
    maxNumber = -1
    for key in authorData.keys():
        entry = authorData[key]
        length += entry["totalLength"]
        numberTexts += entry["textNumber"]
        minNumber = min(minNumber, entry["totalLength"])
        maxNumber = max(maxNumber, entry["totalLength"])
    
    print "Number of authors:", len(authorData)
    print "Length:", length
    print "Number of texts:", numberTexts
    print "Average:", str(round(Decimal(length) / Decimal(numberTexts), 3))
        
#    authorData = sorted(authorData.iteritems(), key=lambda (k,v): (v,k))
    authorData = sorted(authorData.iteritems(), key=itemgetter(1))

    save_JSON_file(filename_save, authorData)

    FILE_TO_SAVE = open("reportFile.tex","w")
    
    FILE_TO_SAVE.write("\\documentclass[letter, 12pt, english]{article}\n")
    FILE_TO_SAVE.write("\\begin{document}\n")
    #FILE_TO_SAVE.write("\\title{Test data}\n")
    #FILE_TO_SAVE.write("\maketitle")
    FILE_TO_SAVE.write("\\begin{tabular}{cccccc}\n")
    FILE_TO_SAVE.write("Name & Number of Texts & Min & Max & Average\\\\\n")
    
    count = 0
    endCount = 35
    
 #   for key in authorData.keys():
 #       entry = authorData[key]
    for entry in authorData:
        name = entry[0]
        entry = entry[1]
        FILE_TO_SAVE.write(str(name[0:15]) + " & " + str(entry["textNumber"]) + " & " + str(entry["min"]) + " & " +  str(entry["max"]) + " & " + str(entry["average"]) + "\\\\\n")
        
        if count == endCount:
            FILE_TO_SAVE.write("\\end{tabular}\n")
            FILE_TO_SAVE.write("\\newpage\n")
            FILE_TO_SAVE.write("\\begin{tabular}{cccccc}\n")
            FILE_TO_SAVE.write("Name & Number of Texts & Min & Max & Average\\\\\n")
            count = 0
        
        count += 1
        
    FILE_TO_SAVE.write("& & & & & \\\\ \n")
    FILE_TO_SAVE.write("& Total Number of Texts & Total Min & Total Max & Total Average \\\\ \n")
    FILE_TO_SAVE.write(" & " + str(len(authorData)) + " & " + str(minNumber) + " & " + str(maxNumber) +  " & " + str(round(float(length) / float(numberTexts), 3)) + "\\\\\n")
    FILE_TO_SAVE.write("\\end{tabular}\n")
    FILE_TO_SAVE.write("\\end{document}\n")
    FILE_TO_SAVE.close()

def fixAuthorNames(fileName, fileNameToSave):
    list = read_JSON_file(fileName)
    print dict
    returnList = []
    compareDict = {}
    number = 0
    authorName = ""
    for entry in list:
        if not compareDict.has_key(entry["user_id"]):
            compareDict[entry["user_id"]] = "A" + str(number)
            number += 1
        
        print compareDict[entry["user_id"]]
        entry["user_id"] = compareDict[entry["user_id"]]
        
    
    print list[0], list[1], list[50]
    save_JSON_file(fileNameToSave, list)    
        
#produceStatisticalData()

fixAuthorNames("data.json", "newData.json")