from types import StringType, ListType, FloatType, IntType, BooleanType
from cStringIO import StringIO
from operator import itemgetter
from decimal import *
import pprint
import json
import workOnJSON as JSON
import ngram
import testCreator

def ngram_to_list(grams):
    list = []
    for val in grams:
        tempList = [val for i in range(0, grams[val])]
        list.extend(tempList)
    return list

#end methods written by me
#begin toplevel methods written by me
def makeAuthor(base):
    tg = ngram(base, min_sim=0.0)
    (gram, list) = tg.total_ngram(base)
    tg.corp = list
    tg.newRemember()
    return tg


def compareAuthors(authors, compareDict, authorDict):
    authorMade = {}
    resultDict = {}    
    for value in compareDict:
        textToCompare = value["text"]
        realAuthor = value["user_id"]
        sum = 0
            
        # Compare value
        compareTo = [textToCompare]
        com = ngram(compareTo, min_sin=0.0)
        (gram, workList) = com.total_ngram(compareTo)
        dataDist = {}
            # We do the actual testing
        for author in authors: 
            tg = makeAuthor(authors[author])
            for word in workList:
                sum += tg.propability(word, 0)
            dataDist[author] = sum
            print "Done with", author
            
        (author, time) = largestDictKey(dataDist)
        print dataDist
        print author        
        print "Real author:", authorDict[realAuthor]
        if not authorMade.has_key(author):
            authorMade[author] = [id]
        else:
            authorMade[author].append(realAuthor)
            
        if not resultDict.has_key(realAuthor):
            resultDict[realAuthor] = {author : 1}
        else:
            if resultDict[realAuthor].has_key(author):
                resultDict[realAuthor] = {author : 1}
            else:
                resultDict[realAuthor][author] += 1
    return (authorMade, resultDict)

def largestDictKey(resultDict):
    b = dict(map(lambda item: (item[1],item[0]),resultDict.items()))
    max_key = b[max(b.keys())]
    return (max_key, resultDict[max_key])

def makeJsonFile(filename, fileToSave_name):
    dict = read_JSON_file(filename)
    authorDict = {}
    authorWrittenDict = {}

    authorNameDirec = {}
    num = 0

    for entry in dict:
        author = entry["user_id"]
        if authorNameDirec.has_key(author):
            author = authorNameDirec[author]
        else:
            authorNameDirec[author] = "A" + str(num)
            author = "A" + str(num)
            num += 1
        
        value = {"user_id": author, "text": entry["text"], "timestamp": entry["timestamp"]}
        id = entry["post_id"]
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
        print authorName,":", listOfEntries
            
        tg = ngram(listOfEntries)
        (gramfied, list) = tg.total_ngram(listOfEntries)
        newAuthorDict[authorName] = list
        
    save_JSON_file(fileToSave_name, newAuthorDict)    
    return (authorDict, newAuthorDict, authorNameDirec)
    
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
        value = {"user_id": author, "text": entry["text"], "timestamp": entry["timestamp"]}
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
            
        tg = ngram(listOfEntries)
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
    filename = "data.json"     
    fileToSave_name = "data_save_test2.json"  
    fileToSave_final = "data_temp_save_test2.json"
    fileToSave_listed = "data_listify_test2.json"
    # we load the comparisons
    (result, ngramLists, authorNameDict) = makeJsonFile(filename, fileToSave_name)
    
    # the list of posts we want to compare to the corpus
    compareDict = [{"post_id": "412f267787a9d496ee6afe13722754f441555b6679928bcc0820fccc196b8bc6", "user_id": "f910fcc9118d65480b0f7fd459115bcbf6035743e9d4ec402a036181f865c766", "timestamp": 1061545161, "title": "det nye board", "text": "s\u00e5 er det nye board ved at fungere ligesom jeg gerne vil have det og \\r\\ndet vil derfor snart v\u00e6re tilg\u00e6ngeligt for alle danske juggalos.", "thread_id": 917564}]
    print "Compare\n"
    (id, authorData) = compareAuthors(ngramLists,  compareDict, authorNameDict)   
    print "Produce\n"
    produceResultTable(result, id, authorData)
    
    
def produceResultTable(authorMade, attributedList, authorData):
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
    
    stringResult = ""
    for authorName in authorAttri.keys():
        stringResult += authorName + " &"
    
    stringResult += "Precision & & "
    for authorName in authorAttri.keys():
        stringResult += str(finalResults[authorName]["precision"]) + " & "
    stringResult += " & & & \\"
    stringResult += "Overall Accuracy: " + "PLACEHOLDER" + " Macro-average F-measure: " + str(averageFMeasure) + " \\"
    print averageFMeasure    
    print stringResult
    return finalResults
    
def produceResults(authorMade, attributedDict):
    authorAttri = {}
    for name in authorMade.keys(): 
        authorAttri[name] = producreAuthorResult(name, attributedDict, authorMade[name])
    return authorAttri
    
def produceResult(authorData, authorList):
    endResults = {}
    for authorName in authorData.keys():
        
        writtenByAuthor = len(authorList)
        if authorData[authorName].has_key(authorName):
            correctlyAttributed = authorData[authorName][authorName]
        else:
            correctlyAttributed = 0
            
        attributed = 0.0

        for entry in authorData[authorName].keys():
            attributed += float(authorData[authorName][entry])
            
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
    
    
def runTest(compareDict):
    # files to work on
    filename = "newData.json"     
    fileToSave_name = "data_save_test2.json"  
    #fileToSave_final = "data_temp_save_test2.json"
    #fileToSave_listed = "data_listify_test2.json"
    # we load the comparisons
    (result, ngramLists, authorNameDict) = makeJsonFile(filename, fileToSave_name)
    
    # the list of posts we want to compare to the corpus
    (id, authorData) = compareAuthors(ngramLists,  compareDict, authorNameDict)   
    print "Produce\n"
    return produceResultTable(result, id, authorData)

    
    # files to work on
    filename = "data.json"     
    fileToSave_name = "data_save_test2.json"  
    fileToSave_final = "data_temp_save_test2.json"
    fileToSave_listed = "data_listify_test2.json"
    # we load the comparisons
    (result, ngramLists, authorNameDict) = makeJsonFile(filename, fileToSave_name)
    
    # the list of posts we want to compare to the corpus
    compareDict = [{"post_id": "412f267787a9d496ee6afe13722754f441555b6679928bcc0820fccc196b8bc6", "user_id": "f910fcc9118d65480b0f7fd459115bcbf6035743e9d4ec402a036181f865c766", "timestamp": 1061545161, "title": "det nye board", "text": "s\u00e5 er det nye board ved at fungere ligesom jeg gerne vil have det og \\r\\ndet vil derfor snart v\u00e6re tilg\u00e6ngeligt for alle danske juggalos.", "thread_id": 917564}]
    print "Compare\n"
    (id, authorData) = compareAuthors(ngramLists,  compareDict, authorNameDict)   
    print "Produce\n"
def produceStats():    
    startFile = "data.json"
    newFile = "newData.json"
    saveStats = "dataSave.json"
    number = 50
    produceStatisticalData(newFile, saveStats)
    getAuthorWithOverXPosts(newFile, saveStats, number)