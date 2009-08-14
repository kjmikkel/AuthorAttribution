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
import math
from datetime import datetime

def doTables():
    num = 3
    
    makeTable("ShortBogusText", "ShortBogusTest", num) 
    
    #All of the number tests
  #  doNumberTables(num)
    
  #  doStressTable(num)
    
    #Do the ultimate tests
 #   makeTable("UltimateTest", "UltimateTest", num)
    
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
        (authorAttri, averageFMeasure, authorList, overall) = produceTableData(id, authorData, placeToSave, num)
        produceTable(authorAttri, averageFMeasure, authorList,id, authorData, placeToSave + "Test", num, overall)
    
def produceTableData(attributedList, authorData, name, num):
    averageFMeasure = Decimal("0.00")
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
        averageFMeasure = Decimal("0.00")
    
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
        overall = Decimal(0.00)
    
    return (authorAttri, averageFMeasure, authorList, overall) 
    
def produceTable(authorAttri, averageFMeasure, authorList, attributedList, authorData, name, num, overall): 
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
    FILE_TO_SAVE.write("Number of Authors & Number of Texts & Total Min & Total Max & Total Average \\\\ \n")
    FILE_TO_SAVE.write(str(len(authorData)) + " & " + str(numberTexts) + " & " + str(minNumber) + " & " + str(maxNumber) +  " & " + str(round(Decimal(length) / Decimal(numberTexts), 3)) + "\\\\ \n")
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

def produceXtable():
    getcontext().prec = 4
    worker = JSON.workOnJSON()
    
    authorList = worker.read_JSON_file(constants.resultDir +"workTime.json")
    stringResult = StringIO()
    
    numElements = len(authorList)
    next = "\\\\ \n"    
    line = "\\hline \n"
    stringResult.write("\\begin{center}\n")
    stringResult.write("\\begin{tabular}{|c|" + "c|" * numElements + "}\n")
    stringResult.write(line )

    keys =  [str(i * 100) for i in range(1, 13)]  
    
    for time in keys:
        stringResult.write(" & " + str(time))

    stringResult.write(next)
    stringResult.write(line)
    
    for time1 in keys:
        stringResult.write(str(time1))
        for time2 in keys:
            result = +Decimal(str(authorList[time2][time1]))
            stringResult.write(" & " + str(result))
        
        stringResult.write(next)
        stringResult.write(line)
    
    stringResult.write("\\end{tabular}\n")
    stringResult.write("\\end{center}")
    
    FILE = open(constants.tableSave + "crossSave.tex", "w")  
    FILE.write(stringResult.getvalue())
    FILE.close()

    dict = {}
    for key in keys:    
        dict[key] = authorList[key]["1200"]
    makeGNUplot("ultimateGNUPlot", dict, keys)

    stringResult = StringIO()
    authorList = worker.read_JSON_file(constants.resultDir +"ngramTime.json")
    
    splitPoint = 6
    stringResult = printPartList(authorList, keys[:splitPoint], stringResult)
    stringResult.write("\n \n")
    stringResult = printPartList(authorList, keys[splitPoint:], stringResult)
    
    FILE = open(constants.tableSave + "ngramTime.tex", "w")    
    FILE.write(stringResult.getvalue())
    FILE.close()
    
    #make dat table
    makeGNUplot("ngramGNUPlot", authorList, keys)

def makeGNUplot(name, entry,keys):
    stringResult = StringIO()
    stringResult.write("# Number of texts\t Time to identify\n")
    for key in keys:
        stringResult.write(str(key) + "\t" + str(entry[str(key)] )+ "\n")
    
    FILE = open(constants.tableSave + name +".dat", "w")
    FILE.write(stringResult.getvalue())
    FILE.close()
    
def printPartList(authorList, keyList, stringResult):
    next = "\\\\ \n"    
    line = "\\hline \n"
    stringResult.write("\\begin{tabular}{|c|" + "c|" * len(keyList)+ "}\n")
    stringResult.write(line)
    stringResult.write("\# n-grams ")

    for time in keyList:
        stringResult.write("& " + str(time))
    stringResult.write(next)
    stringResult.write(line)
    
    stringResult.write("Time")    
    for time in keyList:
        dec = +Decimal(str(authorList[time]))
        stringResult.write("& " + str(dec))
    
    stringResult.write(next)
    stringResult.write(line)
    
    stringResult.write("\\end{tabular}")
    return stringResult
    
def doUltimateTable():
    getcontext().prec = 2
    worker = JSON.workOnJSON()
    filename = "UltimateTest"
    foldername = "UltimateTest"
    givenNum = 3
    for index in range(1, givenNum + 1):
        (id, authorData, name, num) = worker.read_JSON_file(constants.resultDir + filename + str(index) + ".json")
        placeToSave = constants.folderLocation + "report/tabeller/" + foldername + "/" + filename + str(index)
        (authorAttri, averageFMeasure, authorList, overall) = produceTableData(id, authorData, placeToSave, num)
        produceTableUltimate(authorAttri, averageFMeasure, authorList,id, authorData, placeToSave, num, overall)

def produceTableUltimate(authorAttri, averageFMeasure, authorList, id, authorData, placeToSave, num, overall):
    numberWant = 8
    numberALine = int(math.ceil(numberWant / 3))
    numElements = len(authorData)
    lines = int(math.ceil(numElements / numberALine))
    
    keys = list(authorData)
    keys.sort()
    stringResult = StringIO()
        
    next = "\\\\ \n"    
    line = "\\hline \n"
    activeAuthor = "\\aAuthor{"
    
    middleLine = ("c|" * 4 + "|") * numberALine
    middleLine = middleLine[:-1]
    stringResult.write("\\begin{tabular}{|" +  middleLine + "}\n")
    stringResult.write(line)
    stringResult.write(("Name & Recall & Precision & Hits &" * numberALine)[:-1] + next)
    stringResult.write(line)
    
    for i in range(0, lines):        
        authors = keys[:numberALine]
        keys = keys[numberALine:]
        
        lineStr = StringIO()
        for authorName  in authors:
            if authorData.has_key(authorName) and authorData[authorName].has_key(authorName):
                numberHits = str(authorData[authorName][authorName])
            else:
                numberHits = "0"
                
            entry = authorAttri[authorName]
            
            if authorData.has_key(authorName):
                authorName = activeAuthor + authorName + "}"
            
            lineStr.write(authorName + " & " + str(entry["recall"]) + " & " + str(entry["precision"]) + " & " + numberHits + " & ") 
        
        stringResult.write(lineStr.getvalue()[:-2])
        stringResult.write(next)
        stringResult.write(line) 
        
    stringResult.write("\\multicolumn{" + str(numberALine * 4)+ "}{|c|}{Overall Accuracy: " + str(overall) + " Macro-average F-measure: " + str(averageFMeasure) + "}" + next)
    stringResult.write(line)
    stringResult.write("\\end{tabular}")
    
    FILE = open(placeToSave + ".tex", "w")
    FILE.write(stringResult.getvalue())
    FILE.close()
        
if __name__ == '__main__':          
    makeTable("UltimateTest", "UltimateTest", 3)
    doUltimateTable()
    #produceXtable()
