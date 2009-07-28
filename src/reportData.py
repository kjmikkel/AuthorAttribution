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
from datetime import datetime

tg_dict = {}

def ngram_to_list(grams):
    list = []
    for val in grams:
        tempList = [val for i in range(0, grams[val])]
        list.extend(tempList)
    return list

#end methods written by me
#begin toplevel methods written by me
def makeAuthor(base):
    tg = ngram.ngram(base, min_sim=0.0)
    (gram, list) = tg.total_ngram(base)
    tg.corp = list
    tg.newRemember()
    return tg


def compareAuthors(authors, compareDict):
    # this dict contains how many texts (that we are comparing against the corpus) each author has written
    authorMade = {}
    # The dict that contains which authors have had their text attributed to whom
    resultDict = {}        
    
    for value in compareDict:
        textToCompare = value["text"]
        realAuthor = value["user_id"]
        sum = 0
        
        # Compare value
        compareTo = [textToCompare]
        com = ngram.ngram(compareTo, min_sin=0.0)
        
        (gram, workList) = com.total_ngram(compareTo)
        dataDist = {}
            # We do the actual testing
        for author in authors: 
            if tg_dict.has_key(author):
                break
   #         timeStart = time.time()
            tg_dict[author] = makeAuthor(authors[author])
   #         endTime = time.time()
#            print "Start:", timeStart 
#            print "End:", endTime
#            print "compareTo_tgr:", str(endTime - timeStart)

        for author in authors:
            timeStart = time.time()
            tg = copy.deepcopy(tg_dict[author])
            for word in workList:
                sum += tg.propability(word, 0)
            
            dataDist[author] = sum
            endTime = time.time()
            print "Done with", author, "took", str(endTime - timeStart), "seconds"
        
        (author, usedTime) = largestDictKey(dataDist)
        
        print "Most likely author:", author
        print "Real author:", realAuthor
        
        if not authorMade.has_key(author):
            authorMade[author] = [realAuthor]
        else:
            authorMade[author].append(realAuthor)
            
        # We take score of the attributions
        if not resultDict.has_key(author) :
            resultDict[author] = {realAuthor: 1}
        elif not resultDict[author].has_key(realAuthor):
            resultDict[author][realAuthor] = 1
        else:
            resultDict[author][realAuthor] += 1
    return (authorMade, resultDict)

def largestDictKey(resultDict):
    b = dict(map(lambda item: (item[1],item[0]),resultDict.items()))
    max_key = b[max(b.keys())]
    return (max_key, resultDict[max_key])

def makeJsonFile(filename):
    dict = read_JSON_file(filename)
    authorDict = {}
    authorWrittenDict = {}

    authorNameDirec = {}
    num = 0

    for entry in dict:
        author = entry["user_id"]
        id = entry["post_id"]
        
        #if authorNameDirec.has_key(author):
        #    author = authorNameDirec[author]
        #else:
        #    print author
        #    authorNameDirec[author] = "A" + str(num)
        #    author = "A" + str(num)
        #  num += 1
        
        value = {"user_id": author, "text": entry["text"]}
        
        if authorDict.has_key(author):
            authorDict[author].append(value)
            authorWrittenDict[author].append(id)
        else:
            authorDict[author] = [value]
            authorWrittenDict[author] = [id]
    
    newAuthorDict = {}
    
    for authorName in authorDict.keys():
        author = authorDict[authorName]
        newAuthorDictTemp = {}
        
        listOfEntries = [entry["text"] for entry in author]
            
        tg = ngram.ngram(listOfEntries)
        (gramfied, list) = tg.total_ngram(listOfEntries)
        newAuthorDict[authorName] = list
        
    return (authorDict, newAuthorDict)
    
def combine_ngrams(author): 
    finalDict = {}
    for authorKey in author:
        tempDict = {}
        gram = author[authorKey]
 
        for entryKey in gram.keys():
            thisNumber = gram[entryKey]
            number = 0
                
            if (tempDict.has_key(entryKey)):
                number = tempDict[entryKey] + thisNumber
            else:
                number = thisNumber                
            tempDict[entryKey] = number
        finalDict[authorKey] = tempDict
    return finalDict

def makeCompareAgainst(list):
    authorDict = {}
    authorWrittenDict = {}
    
    listOfEntries = []
    for entry in list:
        value = {"user_id": author, "text": entry["text"]}
        id = entry["post_id"]
        if authorDict.has_key(author):
            authorDict[author].append(value)
            authorWrittenDict[author].append(id)
        else:
            authorDict[author] = [value]
            authorWrittenDict[author] = [id]
        
    newAuthorDict = {}
    
    # we need to this authorwise, since we need to 
    #find the likely for each author, not just the combined  
    for authorName in authorDict.keys():
        author = authorDict[authorName]
        newAuthorDictTemp = {}
        
        listOfEntries = [entry["text"] for entry in author]
        print authorName,":", listOfEntries
            
        tg = ngram.ngram(listOfEntries)
        (gramfied, list) = tg.total_ngram(listOfEntries)
        newAuthorDict[authorName] = list
        
    return (authorDict, newAuthorDict)
    
def combine_ngrams(author): 
    finalDict = {}
    for authorKey in author:
        tempDict = {}
        gram = author[authorKey]
 
        for entryKey in gram.keys():
            thisNumber = gram[entryKey]
            number = 0
                
            if (tempDict.has_key(entryKey)):
                number = tempDict[entryKey] + thisNumber
            else:
                number = thisNumber                
            tempDict[entryKey] = number
        finalDict[authorKey] = tempDict
    return finalDict

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

def getAndMerge():
    # files to work on
    filename = reportData.location + "newData.json"     
 
    # we load the comparisons
    (result, ngramLists) = makeJsonFile(filename)
    
    # the list of posts we want to compare to the corpus
    compareDict = [{"post_id": "412f267787a9d496ee6afe13722754f441555b6679928bcc0820fccc196b8bc6", "user_id": "f910fcc9118d65480b0f7fd459115bcbf6035743e9d4ec402a036181f865c766", "title": "det nye board", "text": "s\u00e5 er det nye board ved at fungere ligesom jeg gerne vil have det og \\r\\ndet vil derfor snart v\u00e6re tilg\u00e6ngeligt for alle danske juggalos.", "thread_id": 917564}]
    print "Compare\n"
    (id, authorData) = (ngramLists,  compareDic)   
    print "Produce\n"
    produceResultTable(result, id, authorData)
    
    
def produceResultTable(authorMade, attributedList, authorData, name, num):
    averageFMeasure = 0.0
    
    finalResults = {}
    
    authorAttri = produceResult(authorData, authorMade)
    
    for authorName in authorAttri.keys():
        (precision, recall, fMeasure) = authorAttri[authorName]
        finalResults[authorName] = {"precision": precision, "recall": recall, "fMeasure": fMeasure}
        averageFMeasure += float(fMeasure)
        
    if len(authorAttri):
        averageFMeasure = averageFMeasure / float(len(authorAttri))
    else:
        averageFMeasure = 0
 
    #I find all the interesting authors 
    authorNameDict = {}
    for outerName in authorData:
        authorNameDict[outerName] = 1
        entry = authorData[outerName]
        entryNameList = entry.keys()
        for innerName in entryNameList:
            authorNameDict[innerName] = 1
            
    alist = sorted(authorNameDict.iteritems(), key=lambda (k,v): (v,k))

   # produce the table to contain the information
    stringResult = StringIO()
    numElements = len(authorNameDict)
    next = "\\\\"    
    line = "\\hline \n"
    stringResult.write("\\begin{tabular}{|c||" + "c|" * numElements + "|c|}\n")
    stringResult.write(line )
    stringResult.write("\\multicolumn{" + str(numElements + 2)+ "}{|c|}{Computer Estimate}" + next + "\n")
    stringResult.write(line)
    stringResult.write("True Label & ")

    for an in alist:
        authorName = an[0]
        stringResult.write(authorName + " & ")
    
    stringResult.write("Recall " + next + "\n")
    stringResult.write(line)

    totalAuthors = {}
    print authorData
    for authorName in alist:
        authorNameOuter = authorName[0]
        stringResult.write(authorNameOuter + " & ")
        # Go through a line - this is the main part
        for an in alist:
            authorNameInner = an[0]
            if not (authorData.has_key(authorNameOuter) and authorData[authorNameOuter].has_key(authorNameInner)):
                stringResult.write(" &")
            else:
                value = authorData[authorNameOuter][authorNameInner]
                stringResult.write(str(value) + " & ")
        # print the result
        if finalResults.has_key(an):
            stringResult.write(" " + str(finalResults[an]["recall"]) + next + "\n")
        else:
            stringResult.write(" 0.00" + next + "\n")
    
    stringResult.write(line)
    stringResult.write("Precision & ")
    
    for authorName in alist:
        authorName = authorName[0]
        if finalResults.has_key(authorName):
            precision = finalResults[authorName]["precision"]
        else:
            precision = 0.0
        stringResult.write(str(precision) + " & ")
    stringResult.write(next + "\n")
    stringResult.write(line)
    totalNumber = 0
    correctNumber = 0

    for outerName in alist:
        outerName = outerName[0]
        for innerName in alist:
            innerName = innerName[0]
            if (authorData.has_key(outerName) and authorData[outerName].has_key(innerName)):
                totalNumber += authorData[outerName][innerName]
                if outerName == innerName:
                    correctNumber += authorData[outerName][innerName]
    
    if totalNumber > 0:
        overall = float(correctNumber) / float(totalNumber)
    else:
        overall = 0.00
        
    stringResult.write("\\multicolumn{" + str(numElements + 2)+ "}{|c|}{Overall Accuracy: " + str(overall) + " Macro-average F-measure: " + str(averageFMeasure) + "}" + next + "\n")
    stringResult.write(line)
    stringResult.write("\\end{tabular} \n")

    FILE_TO_SAVE = open(name + str(num) + ".tex","w")
    
#  FILE_TO_SAVE.write("\\documentclass[letter, 12pt, english]{article}\n")
#    FILE_TO_SAVE.write("\\begin{document}\n")
    FILE_TO_SAVE.write(stringResult.getvalue())
#    FILE_TO_SAVE.write("\\end{document}")
    FILE_TO_SAVE.close()
        
    return finalResults
def produceResults(authorMade, attributedDict):
    authorAttri = {}
    for name in authorMade.keys(): 
        authorAttri[name] = producreAuthorResult(name, attributedDict, authorMade[name])
    return authorAttri
    
def produceResult(authorData, authorList):
    endResults = {}
    for authorName in authorData.keys():
        
        if authorData[authorName].has_key(authorName):
            correctlyAttributed = authorData[authorName][authorName]
        else:
            correctlyAttributed = 0
        
        writtenByAuthor = len(authorList)
        print "Written:", writtenByAuthor
        print "correctly:", correctlyAttributed
            
        attributed = 0.0

        for entry in authorData[authorName].keys():
            attributed += float(authorData[authorName][entry])
            
        if attributed:
            precision = float(correctlyAttributed) / float(attributed)
        else:
            precision = 0.0
        
        if writtenByAuthor:    
            recall = float(correctlyAttributed) / float(writtenByAuthor)
        else:
            print "Set recall to zero"
            recall = 0.0
        
        if (precision and recall):
            fMeasure = (2.0 * precision * recall) / (precision + recall)
        else:
            fMeasure = 0.0
        
        endResults[authorName] = (precision, recall, fMeasure)
    
    return endResults
    
def producreAuthorResult(authorName, attributedList, authorList):
    
    writtenByAuthor = float(len(authorList))
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
    FILE_TO_SAVE.write(" & " + str(len(authorData)) + " & " + str(minNumber) + " & " + str(maxNumber) +  " & " + str(round(float(length) / float(numberTexts), 3)) + "\\\\ \n")
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
    
    
def runTest(compareDict, filename, name, num):
    # files to work on
    tempName = name.rpartition("/")[-1]
    print resultDir + tempName
    
    # we load the comparisons
    print  filename
    (result, ngramLists) = makeJsonFile(filename)
    
    # the list of posts we want to compare to the corpus
    tg_dict.clear()
    (id, authorData) = compareAuthors(ngramLists,  compareDict)   

    print "Produce\n"
    save_JSON_file(resultDir + tempName + str(num) + ".json", (result, id, authorData, name, num))
    
    return produceResultTable(result, id, authorData, name, num)

def makeTable(filename, foldername, givenNum):
    (result, id, authorData, name, num) = read_JSON_file(resultDir + filename + str(givenNum) + ".json")
    produceResultTable(result, id, authorData, "../report/tabeller/" + foldername + "/" + filename, num)
    
def produceStats():    
    startFile = "data.json"
    newFile = "newData.json"
    saveStats = "dataSave.json"
    number = 50
    produceStatisticalData(newFile, saveStats)
    getAuthorWithOverXPosts(newFile, saveStats, number)
    
location = "data/"
resultDir = location + "Results/"