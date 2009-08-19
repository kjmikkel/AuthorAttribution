import constants
import reportData
import workOnJSON as JSON
import copy
import random as ran

def bozo(tests, corpora, save_file, times):
    print tests
    
    worker = JSON.workOnJSON()
    corpora = worker.read_JSON_file(constants.corpora + corpora + ".json")
    tests = worker.read_JSON_file(constants.tests + tests + ".json")
    permTestList = []
    permCorporaList = []
    for entry in tests:
        permTestList.append(entry["user_id"])
        
    for entry in corpora:
        permCorporaList.append(entry["user_id"])
        
    resultDict= {}
    corpora = copy.deepcopy(permCorporaList)
    tests = copy.deepcopy(permTestList)
    for i in range(0, times):
        # I prepare to run a round
        
        if i > 0 and i % 1000 == 0:
            print (float(i) / float(times)) * 100 , "percent done"
            
        ran.seed()
        
        for realAuthor in tests:
            ranInt = ran.randint(0, len(corpora) - 1)
            author = corpora[ranInt]
            
            if not resultDict.has_key(realAuthor) :
                resultDict[realAuthor] = {author: 1}
            elif not resultDict[realAuthor].has_key(author):
                resultDict[realAuthor][author] = 1
            else:
                resultDict[realAuthor][author] += 1
    
    for authorName in resultDict.keys():
        entry = resultDict[authorName]
        for keys in entry.keys():
            entry[keys] = float(entry[keys]) / float(times)
             
    worker.save_JSON_file(constants.bozo + save_file + ".json", resultDict)

def runBozo():
    times = 1000000
   # doStressTest(times)
    
    #Short Bogus Test
    #bozo("ShortBogusText1", "shortBogusCorpora1", "ShortBogusText", times) 
    
    #All of the number tests
    #doNumberTest(times)
    
    #Do the ultimate tests
    bozo("UltimateTexts1", "newData" ,"UltimateTest", times)
    
def doNumberTest(times):
    #AuthorSomePost
    bozo("AuthorSomePost1", "Some", "AuthorSomePost", times)
    
    #AuthorManyPost
    bozo("AuthorManyPost1", "Many", "AuthorManyPost", times)

def doStressTest(times):

    # StressTest1
    bozo("singleAuthorData", "newData" , "StressTest1", times)
    
    #StressTest 3
    bozo("someStress1", "Some", "StressTest3", times)
        
    # StressTest 4
    bozo("manyStress1", "Many", "StressTest4", times)
       
    # StressTest5
    bozo("singleAuthorData", "singlePostCorpora", "StressTest5", times)

    
if __name__ == '__main__':
    runBozo()