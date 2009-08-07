import workOnJSON as JSON
import random as ran
import constants

"""
Corpora's
"""
#Compilations

def makeCorpora():
    #Bogus corpora
    shortBogusCorpora(3) 
   
    # Few, Some and More
  #  createLengthCorpora()
    
    # Single post Corpora
 #   singlePostCorpora()

def createLengthCorpora():
   #chooseAuthorsWithNumber("Few",  constants.fewPosts , 3)
    chooseAuthorsWithNumber("Some", constants.somePosts, 3)
    chooseAuthorsWithNumber("Many", constants.manyPosts, 3)


#Utility methods
def shortBogusCorpora(num) :
    worker = JSON.workOnJSON()
    list = worker.read_JSON_file(constants.corpora + "Many.json")

    authorDict = {}
    for entry in list:
        author = entry["user_id"]
        authorDict[author] = 1
            
    authorList = authorDict.keys()
    ran.seed()
    for i in range(0, num):
        index = i + 1
 
        ranInt = ran.randint(0, len(authorList) - 1)
        author = authorList[ranInt]
        # I update the authorList 
        del authorList[ranInt]
            
        finalList = []            
        for entry in list:
            user_id = entry["user_id"]
            if user_id == author:
                finalList.append(entry)
            
        # I find the text that is to be used for the tests
        ranInt = ran.randint(0, len(finalList) - 1)
        randomEntry = finalList[ranInt]
    
        finalList.append({"user_id": "Bogus", "text": "hello", "post_id": "B1"})
        finalList.append({"user_id": "Bogus", "text": "Why, hello again!", "post_id": "B2"})
        worker.save_JSON_file(constants.corpora + "shortBogusCorpora" + str(index) + ".json", finalList)
        worker.save_JSON_file(constants.tests + "ShortBogusText" + str(index) + ".json", [randomEntry])

def singlePostCorpora():
    worker = JSON.workOnJSON()
    list = worker.read_JSON_file(constants.location + "newData.json")
    authorDict = {}
    
    for entry in list:
        author = entry["user_id"]
        text = entry["text"]
        id = entry["post_id"]
        value = {"text": text, "post_id": id}
        if authorDict.has_key(author):
            authorDict[author].append(value)
        else:
            authorDict[author] = [value]
    
    finalTexts = []
    for author in authorDict.keys():
        textList = authorDict[author]
        ran.seed()
        index = ran.randint(0, len(textList) - 1)
        entry = textList[index]
        value = {"user_id": author, "text":  entry["text"], "post_id": entry["post_id"]}
        finalTexts.append(value)
    
    worker.save_JSON_file(constants.corpora + "singlePostCorpora.json", finalTexts) 
  
def chooseAuthorsWithNumber(filename_save, number_of_posts, num):
    worker = JSON.workOnJSON()
    list = worker.read_JSON_file(constants.location + "newData.json")
    
    authorDict = {}
    for entry in list:
        author = entry["user_id"]
        value = {"text": entry["text"], "user_id": author, "post_id": entry["post_id"]}
        if authorDict.has_key(author):
            (number, texts) = authorDict[author]
            texts.append(value)
            authorDict[author] = (number + 1, texts)
        else:
            authorDict[author] = (1, [value])
            
    authorList = []
    textList = []
    authorKeyList = authorDict.keys()
    for author in authorKeyList:
        number = authorDict[author][0] 
        if (number >= number_of_posts[0] and number <= number_of_posts[1]):
            authorList.append(author)
            textList.extend(authorDict[author][1])
    
    worker.save_JSON_file(constants.corpora + filename_save + ".json", textList)
   
    for i in range(0, num):
        author = None
        index = i + 1
        ran.seed ()
        if len(authorKeys) != 0:
            ranIndex = ran.randint(0, len(authorList) -1)
            author = authorList[ranIndex]
            authorList.remove(author)
            worker.save_JSON_file(constants.tests + "Author" + name +"Post" + str(index) + ".json", authorDict[author][1])

def makeTimeTest():
    i = 100
    worker = JSON.workOnJSON()
    fromDirectory = constants.corpora + "newData.json"
    posts = worker.read_JSON_file(fromDirectory)    
    while i < 1400:
        saveFile = constants.corpora + "timeTest" + str(i) + ".json"
        listToSave = posts[0: i - 1]
        worker.save_JSON_file(saveFile, listToSave)
        i += 100
    
    i = 1329
    saveFile = constants.corpora + "timeTest" + str(i) + ".json"
    listToSave = posts[0: i - 1]
    worker.save_JSON_file(saveFile, listToSave)
            
if __name__ == '__main__':          
    #makeTimeTest()
    makeCorpora()
