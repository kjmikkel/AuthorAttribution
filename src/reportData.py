from types import StringType, ListType, FloatType, IntType, BooleanType
from cStringIO import StringIO
from operator import itemgetter
from decimal import *
import pprint
import json
import workOnJSON as JSON

def produceStatisticalData(filename, filename_save):
    result = JSON.read_JSON_file(filename)
    
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
        number = str(entry["textNumber"])
        if (number > 1 and number < 10):
            number = "\\emph{" + number + "}"
        elif (number >= 10 and number < 100):
            number = "\\texttt{" + number + "}"
        elif number >= 100:
            number = "\\texttt{\\emph{" + number + "}}"
        FILE_TO_SAVE.write(str(name[0:15]) + " & " + number + " & " + str(entry["min"]) + " & " +  str(entry["max"]) + " & " + str(entry["average"]) + "\\\\\n")
        
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
    list = JSON.read_JSON_file(fileName)
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
    JSON.save_JSON_file(fileNameToSave, list)    

def getAuthorWithOverXPosts(data_file, metadata_file, number):
    postFiles = "authorsWithOver"
    file_data = JSON.read_JSON_file(data_file)
    file_metadata = JSON.read_JSON_file(metadata_file)
    
    listOfAuthors = []
    texts = []
    
    # I find the authors who have written over the needed number of texts
    for entry in file_metadata:
        authorName = entry[0]
        entry = entry[1]
        if entry["textNumber"] >= number:
            listOfAuthors.append(authorName)
    
    # With the list of authors I now find all the texts they have written 
    for entry in file_data:
        authorName = entry["user_id"]
        if listOfAuthors.count(authorName):
            texts.append(entry)
    
    JSON.save_JSON_file(postFiles + str(number) + ".json", texts)
    
startFile = "data.json"
newFile = "newData.json"
saveStats = "dataSave.json"
number = 50
#fixAuthorNames(startFile, newFile)
produceStatisticalData(newFile, saveStats)
getAuthorWithOverXPosts(newFile, saveStats, number)