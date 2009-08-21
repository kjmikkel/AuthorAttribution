import workOnJSON as JSON
from cStringIO import StringIO
import random as ran
import os
import ngram
import constants
import reportData
import time
from operator import itemgetter


runTimeTest = 0
corpNumber = 0

"""
Run all tests
"""
def doAllTests():
    num = 3
    doStressTest(num)
    
    #Short Bogus Test
    AuthorTest(num, "ShortBogusText", "shortBogusCorpora", "shortBogusText", "shortBogusText") 
    
    #All of the number tests
    doNumberTest(num)
    
    #Do the ultimate tests
    AuthorTest(num, "UltimateTexts", "newData" ,"UltimateTest", "UltimateTest")
    
def doNumberTest(num):
    #AuthorSomePost
    AuthorTest(num, "AuthorSomePost", "Some", "AuthorSomePost", "AuthorSomePost")
    
    #AuthorManyPost
    AuthorTest(num, "AuthorManyPost", "Many", "AuthorManyPost", "AuthorManyPost")

def doStressTest(num):

    # StressTest1
#    AuthorTest(num, "singleAuthorData", "newData" ,"StressTest", "StressTest1")
    
    # StressTest2
    # No tests in this category
    
    #StressTest 3
    AuthorTest(num, "someStress", "Some" ,"StressTest", "StressTest3")
        
    # StressTest 4
   # AuthorTest(num, "manyStress", "Many" ,"StressTest", "StressTest4")
       
    # StressTest5
 #   AuthorTest(num, "singleAuthorData", "singlePostCorpora" ,"StressTest", "StressTest5")

# Do the test that checks the time consumption
def timeTest():
    corpora = [i * 100 for i in range(1,14)]
    corpora.append(1329)
    runTimeTest = 1
    
    for corp in corpora:
        corpNumber = corp
        AuthorTest(0, "singleAuthorData", "timeTest" + str(corp), "UltimateTest", "junkData")
    
    runTimeTest = 0

#Perform the test of the single Authors and save the result as a text table in the folder designated below
def AuthorTest(num, filename_test, corpora_name, foldername, filename_save):
    print "Test:", filename_test
    folder = constants.tableSave + foldername + "/"
    
    if (corpora_name != "newData" or corpora_name != "testData"):
        corpora_name = constants.corpora + corpora_name
    else:
        corpora_name = constants.location + corpora_name
      
    worker = JSON.workOnJSON()
    if num == 0:
        authorText = worker.read_JSON_file(constants.tests + filename_test + ".json")
        value = runTest(authorText, corpora_name + ".json", folder + filename_save, 0)
    else:
        for i in range(0, num):
            index = i + 1
            authorText = worker.read_JSON_file(constants.tests + filename_test + str(index) + ".json")
            corpora_final_name = corpora_name
            if filename_save.count("shortBogusText"):
                corpora_final_name = corpora_name + str(index)
            value = runTest(authorText, corpora_final_name + ".json", folder + filename_save, index)
            
# Runs the inards of an actual test
def runTest(compareDict, filename, name, num):
    # files to work on
    tempName = name.rpartition("/")[-1]
    
    # we load the comparisons
    if runTimeTest:
        startTime = time.time()
        print startTime

    (ngramLists, tg_dict) = makeNgram(filename)
    worker = JSON.workOnJSON()
    if runTimeTest:
        ngramTime = time.time() - startTime
        file = open(constants.results + "ngramTime.dat", "a")
        file.write(str(corpNumber)+  "\t" + str(ngramTime) + "\n")
        file.close()

    # the list of posts we want to compare to the corpus
    if runTimeTest:
        startTime = time.time()
        
    (id, authorData) = compareAuthors(ngramLists,  compareDict, tg_dict)   
    
    if runTimeTest:
        compareTime = time.time() - startTime
        file = open(constants.results + "workTime.dat", "a")
        file.write(str(corpNumber)+  "\t" + str(compareTime) + "\n")
        file.close()

    worker.save_JSON_file(constants.resultDir + tempName + str(num) + ".json", (id, authorData, name, num))            
            
def compareAuthors(authors, compareDict, tg_dict):

    # this dict contains how many texts (that we are comparing against the corpus) each author has written
    authorMade = {}
    
    # The dict that contains which authors have had their text attributed to whom
    resultDict = {}        
            
    for value in compareDict:
        textToCompare = value["text"]
        realAuthor = value["user_id"]
        
        # Compare value
        compareTo = [textToCompare]
        com = ngram.ngram(compareTo)
        
        (gram, workList) = com.total_ngram(compareTo)
        dataDist = {}

        # We do the actual testing        
        for author in authors:
            sum = 0.0
            tg = tg_dict[author]
            for word in workList:
                sum += tg.propability(word, 0)
            
            dataDist[author] = sum
        
        value = -1
        for an in dataDist.keys():
            newValue = dataDist[an]
            if newValue > value:
                value = newValue 
                author = an
                
        print "Real author:", realAuthor
        print "Most likely author:", author

        if not authorMade.has_key(author):
            authorMade[author] = [realAuthor]
        else:
            authorMade[author].append(realAuthor)
            
        # We take score of the attributions
        if not resultDict.has_key(realAuthor) :
            resultDict[realAuthor] = {author: 1}
        elif not resultDict[realAuthor].has_key(author):
            resultDict[realAuthor][author] = 1
        else:
            resultDict[realAuthor][author] += 1
    return (authorMade, resultDict)    

def makeNgram(filename):
    worker = JSON.workOnJSON()
    dict = worker.read_JSON_file(filename)
    authorDict = {}
    authorWrittenDict = {}
    tg_dict = {}
    authorNameDirec = {}
    num = 0

    for entry in dict:
        author = entry["user_id"]
        id = entry["post_id"]
         
        value = {"user_id": author, "text": entry["text"]}
        
        if authorDict.has_key(author):
            authorDict[author].append(value)
            authorWrittenDict[author].append(id)
        else:
            authorDict[author] = [value]
            authorWrittenDict[author] = [id]
    
    newAuthorDict = {}
    authorTexts = {}
    
    for authorName in authorDict.keys():
        author = authorDict[authorName]
        newAuthorDictTemp = {}
        
        listOfEntries = [entry["text"] for entry in author]
        newAuthorDict[authorName] = listOfEntries
        text = ''.join(listOfEntries)
        
        tg = ngram.ngram(listOfEntries)
        tg.corp = text
        tg.newRemember()
        tg_dict[authorName] = tg
            
    return (newAuthorDict, tg_dict)

if __name__ == '__main__':          
    num = 3
    doStressTest(num)