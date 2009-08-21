from types import StringType, ListType, FloatType, IntType, BooleanType
from cStringIO import StringIO
from operator import itemgetter
from decimal import *
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
    
    makeTable("ShortBogusText", "ShortBogusTest", "shortBogusCorpora", num) 
    
    #All of the number tests
    doNumberTables(num)
    
    doStressTable(num)
    
def doNumberTables(num):
    #AuthorSomePost
    makeTable("AuthorSomePost", "AuthorSomePost", "Some", num)
    
    #AuthorManyPost
    makeTable("AuthorManyPost", "AuthorManyPost", "Many", num)

def doStressTable(num):

    # StressTest1
    makeTable("StressTest1", "StressTest", "newData", num)
    
    # StressTest2
    # No one in this category
    
    #StressTest 2
    makeTable("StressTest3", "StressTest", "Some",num)
        
    # StressTest 3
    makeTable("StressTest4", "StressTest", "Many", num)
       
    # StressTest4
    makeTable("StressTest5", "StressTest", "singlePostCorpora", num)

#Produce the main table
def makeTable(filename, foldername, corpora, givenNum):
    getcontext().prec = 3
    worker = JSON.workOnJSON()
    for index in range(1, givenNum + 1):
        (id, authorData, name, num) = worker.read_JSON_file(constants.resultDir + filename + str(index) + ".json")
        placeToSave = constants.folderLocation + "report/tabeller/" + foldername + "/" + filename
        (authorAttri, averageFMeasure, authorList, overall) = makeTableData(id, authorData, placeToSave, num)
        if filename.count("ShortBogusText"):
            finalCorporaName = corpora + str(index)
        else:
            finalCorporaName = corpora
        produceTable(authorAttri, averageFMeasure, authorList, authorList, id, authorData, placeToSave, num, overall, finalCorporaName)
    
def makeTableData(attributedList, authorData, name, num):
    averageFMeasure = Decimal("0.0")
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
        averageFMeasure = Decimal("0.0")
    
    totalNumber = 0
    correctNumber = 0
    
    for outerName in authorList:
        for innerName in authorList:
            if (authorData.has_key(outerName) and authorData[outerName].has_key(innerName)):
                totalNumber += authorData[outerName][innerName]
                if outerName == innerName:
                    correctNumber += authorData[outerName][innerName]
    
    if totalNumber > 0:
        overall = Decimal(str(correctNumber)) / Decimal(str(totalNumber))
    else:
        overall = Decimal("0.0")
    
    return (authorAttri, averageFMeasure, authorList, overall) 
    
def produceTable(authorAttri, averageFMeasure, authorList2, authorList1, attributedList, authorData, name, num, overall, corpora): 
    # I use a very primitive algorithm to sort the values properly
    authorList1 = sortKeys(authorList1)
    authorList2 = sortKeys(authorList2)
    # The dictionary to store the new "real" names, so that they do not have to be recomputed
    newNameDict = {}
    
    # I find out which authors have only made 1 post - and how many posts each author has made
    (listOfOne, writtenDict) = getAuthorWrittenData(1, corpora)
    
    # produce the table to contain the information
    stringResult = StringIO()
    numElements = len(authorList1)
    next = "\\\\"    
    line = "\\hline \n"
    stringResult.write("\\begin{tabular}{|c||" + "c|" * numElements + "|c|}\n")
    stringResult.write(line )
    stringResult.write("\\multicolumn{" + str(numElements + 2)+ "}{|c|}{Computer Estimate}" + next + "\n")
    stringResult.write(line)
    stringResult.write("True Label & ")
    activeAuthor = "\\aAuthor{"
    veryFew = "\\veryFew{"
    
    for authorName in authorList1:
        oriName = authorName
        
        if authorData.has_key(oriName):
            authorName = activeAuthor + authorName + "}"
        
        if listOfOne.count(oriName):
            authorName = veryFew + authorName + "}"
        authorName += "$^{" + str(writtenDict[oriName]) + "}$"
        
        # I store the name so that we do not have to recompute it 
        newNameDict[oriName] = authorName
        stringResult.write(authorName + " & ")
    stringResult.write("Recall " + next + "\n")
    stringResult.write(line)

    totalAuthors = {}
    for oAuthor in authorList1:
        oriName = oAuthor
        if newNameDict.has_key(oriName):
            oAuthor = newNameDict[oriName]    
        
        stringResult.write(oAuthor + " & ")
        
        # Go through a line - this is the main part
        for iAuthor in authorList2:
            if not (authorData.has_key(oriName) and authorData[oriName].has_key(iAuthor)):
                stringResult.write(" & ")
            else:
                value = authorData[oriName][iAuthor]
                stringResult.write(str(value) + " & ")
        
        # print the result
        if authorAttri.has_key(oriName):
            stringResult.write(" " + str(authorAttri[oriName]["recall"]) + next + "\n")
        else:
            stringResult.write(" 0.0" + next + "\n")
    
    stringResult.write(line)
    stringResult.write("Precision & ")
    
    for authorName in authorList1:
        if authorAttri.has_key(authorName):
            precision = authorAttri[authorName]["precision"]
        else:
            precision = "0.0"
            
        stringResult.write(str(precision) + " & ")
    
    stringResult.write(next + "\n")
    stringResult.write(line)
    totalNumber = 0
    correctNumber = 0

    for outerName in authorList1:
        for innerName in authorList2:
            if (authorData.has_key(outerName) and authorData[outerName].has_key(innerName)):
                totalNumber += authorData[outerName][innerName]
                if outerName == innerName:
                    correctNumber += authorData[outerName][innerName]
    
    if totalNumber > 0:
        overall = Decimal(correctNumber) / Decimal(totalNumber)
    else:
        overall = 0.0
        
    stringResult.write("\\multicolumn{" + str(numElements + 2)+ "}{|c|}{Overall Accuracy: " + str(overall) + " Macro-average F-measure: " + str(averageFMeasure ) + "}" + next + "\n")
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
        
        attributed = Decimal("0.0")
        for name in authorData.keys():
            if authorData[name].has_key(authorName):
                attributed += Decimal(str(authorData[name][authorName]))
            
        if attributed:
            precision = Decimal(str(correctlyAttributed)) / Decimal(str(attributed))
        else:
            precision = Decimal("0.0")
        
        if writtenByAuthor and correctlyAttributed > 0:    
            recall = Decimal(str(correctlyAttributed)) / Decimal(str(writtenByAuthor))
        else:
            recall = 0.0

        if (precision and recall):
                fMeasure = Decimal((Decimal(2) * precision * recall) / (precision + recall))
        else:
            fMeasure = Decimal("0.0")
        
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

    keys = sortKeys(authorData.keys())
    worker.save_JSON_file(filename_save, authorData)

    
    header = "\\begin{tabular}{cccccc}\n Name & Number of Texts & Min Length& Max Length & Average Length\\\\\n"
    stringWriter = StringIO()
    stringWriter.write(header)
    
    count = 0
    endCount = 35
    
    numberOnePost = 0
    for name in keys:
        entry = authorData[name]
        number = str(entry["textNumber"])
        if number == "1":
            numberOnePost += 1
            
        stringWriter.write(str(name[0:15]) + " & " + number + " & " + str(entry["min"]) + " & " +  str(entry["max"]) + " & " + str(entry["average"]) + "\\\\\n")
        
        if count == endCount:
            stringWriter.write("\\end{tabular}\n")
            stringWriter.write("\\newpage\n")
            stringWriter.write(header)
            count = 0
        
        count += 1
        
    stringWriter.write("& & & & & \\\\ \n")
    stringWriter.write("Number of Authors & Number of Texts & Total Min & Total Max & Total Average \\\\ \n")
    stringWriter.write(str(len(authorData)) + " & " + str(numberTexts) + " & " + str(minNumber) + " & " + str(maxNumber) +  " & " + str(round(Decimal(length) / Decimal(numberTexts), 3)) + "\\\\ \n")
    oneAuthor = str(float(numberOnePost) / float(len(authorData)) * 100)
    stringWriter.write("\\multicolumn{5}{c}{Percentage of authors who have only written 1 post: " +  oneAuthor[:5] + " \\%}")
    stringWriter.write("\\end{tabular}\n")
    
    FILE_TO_SAVE = open(constants.tableSave + "reportFile.tex","w")
    FILE_TO_SAVE.write(stringWriter.getvalue())
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
      
# Produce a table containing the information for each author
def produceStats():
    startFile = constants.corpora + "data.json"
    newFile = constants.corpora + "newData.json"
    saveStats = constants.corpora + "dataSave.json"
    produceStatisticalData(newFile, saveStats)

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
        if entry["textNumber"] == number:
            listOfAuthors.append(authorName)
    
    # With the list of authors I now find all the texts they have written 
    for entry in file_data:
        authorName = entry["user_id"]
        if listOfAuthors.count(authorName):
            texts.append(entry)
    
    worker.save_JSON_file(postFiles + str(number) + ".json", texts)
    
location = "data/"
resultDir = location + "Results/"

# Produce the 12 * 12 table, containing the time
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
    worker = JSON.workOnJSON()
    filename = "UltimateTest"
    folderName = "UltimateTest"
    corpora = "newData"
    placeToSave = folderName + filename
    givenNum = 3
    for index in range(1, givenNum + 1):
        (id, authorData, name, num) = worker.read_JSON_file(constants.resultDir + filename + str(index) + ".json")
        placeToSave = constants.folderLocation + "report/tabeller/" + folderName + "/" + filename + str(index)
        (authorAttri, averageFMeasure, authorList, overall) = makeTableData(id, authorData, placeToSave, num)
        produceUltimateTables(authorAttri, averageFMeasure, authorList, id, authorData, placeToSave, num, overall, corpora)

def produceUltimateTables(authorAttri, averageFMeasure, authorList, id, authorData, placeToSave, num, overall, corpora, ultimate = 1): 
        if len(authorList) > 1 or ultimate:
            randomTest = 0
        else:
            randomTest = 1
            
        (listOfOne, writtenDict) = getAuthorWrittenData(1, corpora) 
        
        numberALine = min(2, len(authorData))
        numElements = len(authorData)
        lines = int(math.ceil(float(numElements) / float(numberALine)))
        
        # I ensure that the values are sorted
        keys = sortKeys(authorList)
        
        stringResult = StringIO()
            
        next = "\\\\ \n"    
        line = "\\hline \n"
        activeAuthor = "\\aAuthor{"
        veryFew = "\\veryFew{"
        if randomTest:
            values = 4
        else:
            values = 5
        print values
        
        middleLine = ("c|" * values + "|") * numberALine
        middleLine = middleLine[:-1]
        stringResult.write("\\begin{tabular}{|" +  middleLine + "}\n")
        stringResult.write(line)
        if not randomTest:
            precision = "Precision &"
        else:
            precision = ""
            
        stringResult.write((("Name & Recall & " + precision + " Hits & Miss &") * numberALine)[:-1] + next)
        stringResult.write(line)

        lessThan10 = 0
        totalPosts = 0.0    
        getcontext().prec = 2
        for i in range(0, lines):        
            authors = keys[:numberALine]
            keys = keys[numberALine:]
            lineStr = StringIO()

            for authorName  in authors:
                if authorData.has_key(authorName) and authorData[authorName].has_key(authorName):
                    numberHits = authorData[authorName][authorName]
                else:
                    numberHits = 0
            
                numberMisses = 0
                for authorName2 in authorList:
                    if authorData.has_key(authorName2) and authorData[authorName2].has_key(authorName):
                        numberMisses += authorData[authorName2][authorName]
    
                numberMisses -= numberHits
                
                oriName = authorName
                if listOfOne.count(oriName):
                        lessThan10 += numberMisses + numberHits 

                totalPosts += float(numberMisses + numberHits)
                
                authorName = authorName + "$^{" +  str(writtenDict[authorName]) + "}$"
                if listOfOne.count(oriName):
                        authorName =  veryFew + authorName + "}"
                
                resol = 4
                if authorData.has_key(oriName):
                    entry = authorAttri[oriName]
                    authorName = activeAuthor + authorName + "}"
                    recall = Decimal(str(entry["recall"])[:resol])
                    if not randomTest:
                        precision = str(Decimal(str(entry["precision"])[:resol])) + " & "
                    else:
                        precision = ""
                    lineStr.write(authorName + " & " + str(recall) + " & " + precision + str(numberHits)[:resol] + " & " + str(numberMisses)[:5] + " & ") 
                else:
                    lineStr.write(authorName + " & 0.0 & 0 & " + str(numberHits)[:resol] + " & " + str(numberMisses)[:resol] + " & ") 
                
            stringResult.write(lineStr.getvalue()[:-2])
            stringResult.write(next)
            stringResult.write(line) 
            
        stringResult.write("\\multicolumn{" + str(numberALine * values)+ "}{|c|}{Overall Accuracy: " + str(overall)[:7] + "  Macro-average F-measure: " + str(averageFMeasure )[:7] + " }" + next)
        if ultimate:
            stringResult.write("\\multicolumn{" + str(numberALine * values)+ "}{|c|}{Total number of posts attributed to authors with less than 1 posts: " + str(lessThan10) + "}" + next)
            percentage = Decimal(str(float(lessThan10) / float(totalPosts) * 100)[:5])        
            stringResult.write("\\multicolumn{" + str(numberALine * values)+ "}{|c|}{Percentage of posts attributed authors with 1 post: " + str(percentage) + " \\%}" + next)
        stringResult.write(line)
        stringResult.write("\\end{tabular}")
        
        FILE = open(placeToSave + ".tex", "w")
        FILE.write(stringResult.getvalue())
        FILE.close()

def sortKeys(authorList):
    keys = []
    count = 0
    while count < 91:
        name = "A" + str(count)
        if authorList.count(name):
            keys.append(name)
        count += 1
    # take care of edge case with Bogus
    if authorList.count("Bogus"):
        keys.append("Bogus")
    return keys

def getAuthorWrittenData(num, corpora):
    worker = JSON.workOnJSON()
    corpora = worker.read_JSON_file(constants.corpora + corpora + ".json")
    listOfOne = []
    
    writtenDict = {}    
    for entry in corpora:
        authorName = entry["user_id"]
        if writtenDict.has_key(authorName):
            writtenDict[authorName] += 1
        else:
            writtenDict[authorName] = 1

    for authorName in writtenDict.keys():
        if writtenDict[authorName] == num:
            listOfOne.append(authorName)
    
    return (listOfOne, writtenDict)
   
def makeRandomTestTables(filename, corpora):
    folderName = "RandomTest"
    worker = JSON.workOnJSON()
    placeToSave = folderName + filename
    authorData = worker.read_JSON_file(constants.randomTest + filename + ".json")
    placeToSave = constants.folderLocation + "report/tabeller/" + folderName + "/" + filename
    (authorAttri, averageFMeasure, authorList, overall) = makeTableData({}, authorData, placeToSave, 1)
    
    ultimate = None
    if filename.count("Ultimate"):
        ultimate = 1
        
    produceUltimateTables(authorAttri, averageFMeasure, authorData.keys(), id, authorData, placeToSave, -1, overall, corpora, ultimate)

def randomTest():
   
    doRandomStressTest()
    
    #Short Bogus Test
    makeRandomTestTables("ShortBogusText", "shortBogusCorpora1") 
    
    #All of the number tests
    doNumberTest()
    
    #Do the ultimate tests
    makeRandomTestTables("UltimateTest", "newData")
    
def doRandomStressTest():
        # StressTest1
    makeRandomTestTables("StressTest1", "newData")
    
    #StressTest 3
    makeRandomTestTables("StressTest3", "Some")
        
    # StressTest 4
    makeRandomTestTables("StressTest4", "Many")
       
    # StressTest5
    makeRandomTestTables("StressTest5", "singlePostCorpora")
    

def doNumberTest():
    #AuthorSomePost
    makeRandomTestTables("AuthorSomePost", "Some")
    
    #AuthorManyPost
    makeRandomTestTables("AuthorManyPost", "Many")
 
    
if __name__ == '__main__':
    doTables()
     randomTest()
    produceStats()