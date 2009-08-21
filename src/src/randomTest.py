import constants
import reportData
import workOnJSON as JSON
import copy
import random as ran
import os

def randomTest(tests, corpora, save_file, times):
    print tests
    
    worker = JSON.workOnJSON()
    corpora = worker.read_JSON_file(constants.corpora + corpora + ".json")
    tests = worker.read_JSON_file(constants.tests + tests + ".json")
    tempDict = {}    
    permTestList = []
    permCorporaList = []
    for entry in tests:
        permTestList.append(entry["user_id"])
         
    for entry in corpora:
        permCorporaList.append(entry["user_id"])
        
    resultDict= {}
    corpora = copy.deepcopy(permCorporaList)
    tests = copy.deepcopy(permTestList)
    
    numAuthor = len(tests)
    authorsDone = 1
    for realAuthor in tests:
        for i in range(0, times):
            ran.seed()
            if i > 0 and i % 1000 == 0:
                print (float(i * authorsDone) / float(times * numAuthor)) * 100 , "percent done"
            ranInt = ran.randint(0, len(corpora) - 1)
            author = corpora[ranInt]
            
            if not resultDict.has_key(realAuthor) :
                resultDict[realAuthor] = {author: 1}
            elif not resultDict[realAuthor].has_key(author):
                resultDict[realAuthor][author] =1
            else:
                resultDict[realAuthor][author] += 1
        
        authorsDone += 1
    
    for oAuthor in resultDict.keys():
        entry = resultDict[oAuthor] 
        for iAuthor in entry.keys():
            entry[iAuthor] = float(entry[iAuthor]) / float(constants.testTimes)
                    
    worker.save_JSON_file(constants.randomTest + save_file + ".json", resultDict)

def runRandomTest():
    times = constants.testTimes
    doStressTest(times)
    
    #Short Bogus Test
    randomTest("ShortBogusText1", "shortBogusCorpora1", "ShortBogusText", times) 
    
    #All of the number tests
    doNumberTest(times)
    
    #Do the ultimate tests
    randomTest("UltimateTexts1", "newData" ,"UltimateTest", times)
    
def doNumberTest(times):
    #AuthorSomePost
    randomTest("AuthorSomePost1", "Some", "AuthorSomePost", times)
    
    #AuthorManyPost
    randomTest("AuthorManyPost1", "Many", "AuthorManyPost", times)

def doStressTest(times):

    # StressTest1
    randomTest("singleAuthorData", "newData" , "StressTest1", times)
    
    #StressTest 3
    randomTest("someStress1", "Some", "StressTest3", times)
        
    # StressTest 4
    randomTest("manyStress1", "Many", "StressTest4", times)
       
    # StressTest5
    randomTest("singleAuthorData", "singlePostCorpora", "StressTest5", times)

def fix(null, dir, files):
    worker = JSON.workOnJSON()
    for file in files:
        path = dir + file
        dict = worker.read_JSON_file(path)

        for oAuthor in dict.keys():
            entry = dict[oAuthor]
            for iAuthor in entry.keys():
                entry[iAuthor] = float(entry[iAuthor]) / float(constants.testTimes)
        
        worker.save_JSON_file(path, dict)
        
def fixValues():
    os.path.walk(constants.randomTest, fix, None)


if __name__ == '__main__':
    randomTest("singleAuthorData", "newData" , "StressTest1", constants.testTimes)
    #runRandomTest()
   # fixValues()