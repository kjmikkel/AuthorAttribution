from types import StringType, ListType, FloatType, IntType, BooleanType
from cStringIO import StringIO
from operator import itemgetter
from decimal import *
import pprint
import pprint
import json
import workOnJSON as JSON
from cStringIO import StringIO
import ngram
import time
import copy
import constants
from datetime import datetime

def doTables():
    num = 3
    
  #  makeTable("ShortBogusText", "ShortBogusTest", num) 
    
    #All of the number tests
    doNumberTables(num)
    
    doStressTable(num)
    
    #Do the ultimate tests
    makeTable("UltimateTest", "UltimateTest", num)
    
def doNumberTables(num):
    #AuthorSomePost
    makeTable("AuthorSomePost", "AuthorSomePost", num)
    
    #AuthorManyPost
    makeTable("AuthorManyPost", "AuthorManyPost", num)

def doStressTable(num):

    # StressTest1
    makeTable("StressTest1", "StressTest", num)
    
    # StressTest2
    # No one in this category
    #AuthorTest(num, "singleAuthorData", "few" ,"StressTest", "StressTest"
    
    #StressTest 3
    makeTable("StressTest3", "StressTest", num)
        
    # StressTest 4
    makeTable("StressTest4", "StressTest", num)
       
    # StressTest5
    makeTable("StressTest5", "StressTest", num)

#Produce the main table
def makeTable(filename, foldername, givenNum):
    getcontext().prec = 2
    worker = JSON.workOnJSON()
    for index in range(1, givenNum + 1):
        (id, authorData, name, num) = worker.read_JSON_file(constants.resultDir + filename + str(index) + ".json")
        placeToSave = constants.folderLocation + "report/tabeller/" + foldername + "/" + filename
        produceTable(id, authorData, placeToSave, num)

def produceTable(attributedList, authorData, name, num):
    averageFMeasure = Decimal(0)
    print authorData
    finalResults = {}
    
    authorDict = {}
    for oAuthor in authorData.keys():
        authorDict[oAuthor] = 1
        for iAuthor in authorData[oAuthor].keys():
            authorDict[iAuthor] = 1
    authorList = authorDict.keys()
    
    authorAttri = produceResult(copy.deepcopy(authorData), authorList)
    
    for authorName in authorAttri.keys():
      averageFMeasure += authorAttri[authorName]["fMeasure"]
        
    if len(authorAttri):
        averageFMeasure = averageFMeasure / Decimal(len(authorAttri))
    else:
        averageFMeasure = Decimal(0.00)
         
    authorList.sort()
   # produce the table to contain the information
    stringResult = StringIO()
    numElements = len(authorList)
    next = "\\\\"    
    line = "\\hline \n"
    stringResult.write("\\begin{tabular}{|c||" + "c|" * numElements + "|c|}\n")
    stringResult.write(line )
    stringResult.write("\\multicolumn{" + str(numElements + 2)+ "}{|c|}{Computer Estimate}" + next + "\n")
    stringResult.write(line)
    stringResult.write("True Label & ")
    activeAuthor = "\\aAuthor{"
    
    for authorName in authorList:
        if authorData.has_key(authorName):
            stringResult.write(activeAuthor + authorName + "} & ")
        else:
            stringResult.write(authorName + " & ")
    
    stringResult.write("Recall " + next + "\n")
    stringResult.write(line)

    totalAuthors = {}
    print authorData
    for oAuthor in authorList:
        if authorData.has_key(oAuthor):
            stringResult.write(activeAuthor + oAuthor + "} & ")
        else:
            stringResult.write(oAuthor + " & ")
        # Go through a line - this is the main part
        for iAuthor in authorList:
            if not (authorData.has_key(oAuthor) and authorData[oAuthor].has_key(iAuthor)):
                stringResult.write(" & ")
            else:
                value = authorData[oAuthor][iAuthor]
                stringResult.write(str(value) + " & ")
        # print the result
        if authorAttri.has_key(oAuthor):
            stringResult.write(" " + str(authorAttri[oAuthor]["recall"]) + next + "\n")
        else:
            stringResult.write(" 0.00" + next + "\n")
    
    stringResult.write(line)
    stringResult.write("Precision & ")
    
    for authorName in authorList:
        if authorAttri.has_key(authorName):
            precision = authorAttri[authorName]["precision"]
        else:
            precision = 0.00
        stringResult.write(str(precision) + " & ")
    stringResult.write(next + "\n")
    stringResult.write(line)
    totalNumber = 0
    correctNumber = 0

    for outerName in authorList:
        for innerName in authorList:
            if (authorData.has_key(outerName) and authorData[outerName].has_key(innerName)):
                totalNumber += authorData[outerName][innerName]
                if outerName == innerName:
                    correctNumber += authorData[outerName][innerName]
    
    if totalNumber > 0:
        overall = Decimal(correctNumber) / Decimal(totalNumber)
    else:
        overall = 0.00
        
    stringResult.write("\\multicolumn{" + str(numElements + 2)+ "}{|c|}{Overall Accuracy: " + str(overall) + " Macro-average F-measure: " + str(averageFMeasure) + "}" + next + "\n")
    stringResult.write(line)
    stringResult.write("\\end{tabular} \n")

    FILE_TO_SAVE = open(name + str(num) + ".tex","w")
    FILE_TO_SAVE.write(stringResult.getvalue())
    FILE_TO_SAVE.close()
        
    return authorAttri

def produceResult(authorData, authorList):
    endResults = {}
    for authorName in authorData.keys():
        
        if (authorData.has_key(authorName) and authorData[authorName].has_key(authorName)):
            correctlyAttributed = authorData[authorName][authorName]
        else:
            correctlyAttributed = 0
        
        writtenByAuthor = 0
        for name in authorData[authorName].keys():
            writtenByAuthor += authorData[authorName][name]
        
        print "Written:", writtenByAuthor
        print "correctly:", correctlyAttributed
            
        attributed = Decimal(0)
        for name in authorData.keys():
            if authorData[name].has_key(authorName):
                attributed += Decimal(authorData[name][authorName])
            
        if attributed:
            precision = Decimal(correctlyAttributed) / Decimal(attributed)
        else:
            precision = Decimal(0)
        
        if writtenByAuthor and correctlyAttributed > 0:    
            recall = Decimal(correctlyAttributed) / Decimal(writtenByAuthor)
        else:
            recall = 0.00
        
        if (precision and recall):
            fMeasure = Decimal((Decimal(2) * precision * recall) / (precision + recall))
        else:
            fMeasure = Decimal(0)
        
        endResults[authorName] = {"precision": precision, "recall": recall, "fMeasure": fMeasure}  
    return endResults
    
def producreAuthorResult(authorName, attributedList, authorList):
    
    writtenByAuthor = Decimal(len(authorList))
    correctlyAttributed = 0.0
    attributed = 0.0

    for entry in attributedList:
        if authorName == entry:
            attributed += 1.0
            if authorList.count(entry):
                correctlyAttributed += 1.0
    
    if attributed:
        precision = correctlyAttributed / attributed
    else:
        precision = 0.0
    
    if writtenByAuthor:    
        recall = correctlyAttributed / writtenByAuthor
    else:
        recall = 0.0
    
    if (precision and recall):
            fMeasure = (2.0 * precision * recall) / (precision + recall)
    else:
        fMeasure = 0.0
    
    return (attributed, correctlyAttributed, precision, recall, fMeasure)

def makeExample():
    exampleStr = "abcdabceabc c"
    produceExample(exampleStr)

def produceExample(exampleStr):
    tg = ngram([exampleStr])
    (grams, list) = tg.ngramify([exampleStr])
    
    printList = []
    for item in list:
        stri = "\ngr{" + item + "}"
        stri.replace(" ","\_")
        stri.replace("'","")
        printList.append(str)
    print printList
        
    freqDict = {}
    for item in list:
        if freqDict.has_key(item):
            freqDict[item] = freqDict[item] + 1
        else: 
            freqDict[item] = 1
    
    freqfreqDict = {}
    for key in freqDict.keys():
        value = freqDict[key]
        if freqfreqDict.has_key(value):
            freqfreqDict[value] += 1
        else: 
            freqfreqDict[value] = 1
    print "\\begin{tabular}{|cc|}"
    print "\\hline"
    print "Frequency & Frequency of frequency \\\\"
    print "\\hline"
    print "r & N_r \\\\"
    for key in freqfreqDict.keys():
        print str(key) + " & " + str(freqfreqDict[key]) + "\\\\"
    print "\\hline"
    print "\\end{tabular}"
    
def produceStatisticalData(filename, filename_save):
    worker = JSON.workOnJSON()
    result = worker.read_JSON_file(filename)
    
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
        authorEntry["average"] = round(Decimal(authorEntry["totalLength"]) / Decimal(authorEntry["textNumber"]), 3)
        
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
        
    authorData = sorted(authorData.iteritems(), key=itemgetter(1))

    worker.save_JSON_file(filename_save, authorData)

    FILE_TO_SAVE = open(constants.tableSave + "reportFile.tex","w")
    
 #   FILE_TO_SAVE.write("\\documentclass[letter, 12pt, english]{article}\n")
  #  FILE_TO_SAVE.write("\\begin{document}\n")

    FILE_TO_SAVE.write("\\begin{tabular}{cccccc}\n")
    FILE_TO_SAVE.write("Name & Number of Texts & Min & Max & Average\\\\\n")
    
    count = 0
    endCount = 35
    
    for entry in authorData:
        name = entry[0]
        entry = entry[1]
        number = str(entry["textNumber"])
       # if (number > 1 and number < 10):
       # number = "\\emph{" + number + "}
       # elif (number >= 10 and number < 100):
       #     number = "\\texttt{" + number + "}"
       # elif number >= 100:
       #     number = "\\texttt{\\emph{" + number + "}}"
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
    FILE_TO_SAVE.write(" & " + str(len(authorData)) + " & " + str(minNumber) + " & " + str(maxNumber) +  " & " + str(round(Decimal(length) / Decimal(numberTexts), 3)) + "\\\\ \n")
    FILE_TO_SAVE.write("\\end{tabular}\n")
   # FILE_TO_SAVE.write("\\end{document}\n")
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
      
# Produce stats    
def produceStats():
    startFile = constants.location + "data.json"
    newFile = constants.location + "newData.json"
    saveStats = constants.location + "dataSave.json"
    number = 50
    produceStatisticalData(newFile, saveStats)
    getAuthorWithOverXPosts(newFile, saveStats, number)

def getAuthorWithOverXPosts(data_file, metadata_file, number):
    postFiles = "authorsWithOver"
    worker = JSON.workOnJSON()
    file_data = worker.read_JSON_file(data_file)
    file_metadata = worker.read_JSON_file(metadata_file)
    
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
    
    worker.save_JSON_file(postFiles + str(number) + ".json", texts)
    
location = "data/"
resultDir = location + "Results/"

if __name__ == '__main__':          
    produceStats()
