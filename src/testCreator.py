import workOnJSON as JSON
import random as ran
import reportData

"""
Pick numAuthor authors randomly from the list and
return the result
"""
def pickAuthors(list, numAuthor):
    authorDict = {}
    for entry in list:
        authorDict[entry["user_id"]] = 1
    
    authorList = authorDict.keys()
    
    #shortcut if numAuthor is either greater or equal to the number of authors
    if len(authorList) <= numAuthor:
        return authorList
    
    pickedAuthors = []
    ran.seed()  
    for i in range(0, numAuthor):
        randInt = ran.randint(0, len(authorList) - 1)
        author = authorList[randInt]
        authorList.remove(author)
        pickedAuthors.append(author)
        
    print pickedAuthors
    return pickedAuthors

"""
Write a number of authors 
"""
def writeAuthors(filename, filename_save, numAuthors):
        worker = JSON.workOnJSON()
        list = worker.read_JSON_file(filename)
        list = pickAuthors(list, numAuthors)
        worker.save_JSON_file(filename_save, list)

"""
Extract the texts (found in the file filename) from the authors (who are mentioned in the author_filename file),
and save them to the file filename_save
"""
def extractRandomAuthorTexts(filename, author_filename, filename_save):
    worker = JSON.workOnJSON()
    authorList = worker.read_JSON_file(author_filename)
    
    posts = worker.read_JSON_file(filename)
    authorPosts = []

    for entry in posts:
        if authorList.count(entry["user_id"]):
            authorPosts.append(entry)
    
    worker.save_JSON_file(filename_save, authorPosts)

"""
Find random authors who combined have written over half the texts in the corpus
There are no checks or feedback functions, so in the pathalogical case, all the authors
who have written 1 post might be choosen
"""
def randomSelectUltimateAuthors(filename, filename_save):
    worker = JSON.workOnJSON()
    list = worker.read_JSON_file(filename)
    totalPosts = 0
    authorDict = {}
    
    for entry in list:
        author = entry[0]
        entry = entry[1]
        totalPosts += entry["textNumber"]
        authorDict[author] = entry["textNumber"]
    
    #we now know the total number of posts
    
    authorList = authorDict.keys()
    pickedAuthors = []
    pickedNumber = 0
    ran.seed()  
    while 1:
        randInt = ran.randint(0, len(authorList) - 1)
        author = authorList[randInt]
        authorList.remove(author)
        pickedNumber += authorDict[author]
        pickedAuthors.append(author)
        if pickedNumber >= (totalPosts / 2):
            break
    
    worker.save_JSON_file(filename_save, pickedAuthors)

"""
Wrapers to ensure that the definitions of short, medion etc. remain
consistent
"""

shortLength = (0, 100)
mediumLength = (100, 1000)
longLength = (1000, 3000)
rantLength = (3000, 9999999)


"""
Find a post of a given length (neither to short or too long)
Should not be called directly, but rather using the wrapper functions,
which should be found above
"""
def findPost(author, length, list, num):
    texts = []
    for entry in list:
        textLength = len(entry["text"])
        
        if author.count(entry["user_id"]):
            print textLength
            if textLength > length[0] and textLength <= length[1]:
                texts.append(entry)
                num -= 1
                if num <= 0:
                    break
    return texts

"""
Find a single author who has written a long post
"""

def findSingleAuthors(filename, filename_save, num, length):
    value = []
    for i in range(0, num):
        while value == []:
            writeAuthors("testData.json", "data/" + filename + str(i + 1) + ".json", 1)
            worker = JSON.workOnJSON()
            author = worker.read_JSON_file("data/" + filename + str(i + 1) + ".json")[0]
            list = worker.read_JSON_file("data/newData.json")
            value = findPost(author, list, 1, length)

        worker.save_JSON_file("data/" + filename_save + str(i + 1) + ".json", value)

"""
Preform the test of the single Authors and save the result as a text table in the folder designated below
"""
def AuthorTest(num, filename, filename_save):
    folder = "../report/tabeller/"
    for i in range(0, num):
        index = i + 1
        worker = JSON.workOnJSON()
        authorText = worker.read_JSON_file("data/" + filename + str(index) + ".json")
        value = reportData.runTest(authorText, folder + filename_save, index)

"""
Find out how many posts each author has made, and then choose one of these randomly
"""
def chooseAuthorFromNumber(filename_save, num, number_of_posts):
    
    worker = JSON.workOnJSON()
    list =worker.read_JSON_file("data/newData.json")
    
    authorDict = {}
    for entry in list:
        author = entry["user_id"]
        if authorDict.has_key(author):
            (number, texts) = authorDict[author]
            texts.append(entry["text"])
            authorDict[author] = (number + 1, texts)
        else:
            authorDict[author] = (1, [ entry["text"]] )
            
    authorList = []
    authorKeyList = authorDict.keys()
    for author in authorKeyList:
        if (authorDict[author][0] >= number_of_posts[0] and authorDict[author][0] <= number_of_posts[1]):
            authorList.append(author)

    ran.seed()
    finalList = []
    for i in range(0, min(num, len(authorList))):
        refNumber = i + 1
        index = ran.randint(0, len(authorList) - 1)
        choosenAuthor = authorList[index]
        finalList.append(choosenAuthor)
        authorList.remove(choosenAuthor)
        (number, texts) = authorDict[choosenAuthor]
        worker.save_JSON_file("data/" + filename_save + str(refNumber) + ".json", texts)
    
""" 
Extract the text from the authors in the ultimateStressTest and save them to a json file
"""
def findUtimateTexts(num, filname_save):
    for i in range(0, num):
            refNumber = i + 1
            extractRandomAuthorTexts("data/newData.json", "data/utilmateTest" + str(refNumber) + ".json", "data/" + filname_save + str(refNumber) + ".json")
            

def createLengthTests():
    """
    The number of posts
    """
    fewPosts = (35, 68)
    somePosts = (69, 102)
    manyPosts = (103, 9999)
    
    chooseAuthorFromNumber("few", 3, fewPosts)
    chooseAuthorFromNumber("some", 3, somePosts)
    chooseAuthorFromNumber("many", 3, manyPosts)

def makeShortBogusText() :
        worker = JSON.workOnJSON()
        list = worker.read_JSON_file("data/many3.json")
        
        finalList = []
        for text in list:
            finalList.append({"user_id": "A35", "text": text})
        
        finalList.append({"user_id": "Bogus", "text": "hello"})
        finalList.append({"user_id": "Bogus", "text": "Why, hello again!"})
        worker.save_JSON_file("data/shortBogusText", finalList)


#randomSelectUltimateAuthors("dataSave.json", "utilmateTest3.json") 

#AuthorTest(3, "singleAuthorData", "savefile.json")
#findUtimateTexts(3, "utilmateTexts")
#AuthorTest(3, "utilmateTexts", "UltimateTest")
#createLengthTests()
makeShortBogusText()