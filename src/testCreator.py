import workOnJSON as JSON
import random as ran
import reportData

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

def writeAuthors(filename, filename_save, numAuthors):
        worker = JSON.workOnJSON()
        list = worker.read_JSON_file(filename)
        list = pickAuthors(list, numAuthors)
        worker.save_JSON_file(filename_save, list)

def extractRandomAuthorTexts(filename, author_filename, filename_save):
    worker = JSON.workOnJSON()
    authorList = worker.read_JSON_file(author_filename)
    
    posts = JSON.read_JSON_file(filename)
    authorPosts = []

    for entry in posts:
        if authorList.count(entry["user_id"]) > 0:
            authorPosts.append(entry)
    
    JSON.save_JSON_file(authorPosts, filename_save)

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

def findShortPost(author, list, num):
    length = (0, 100)
    return findPost(author, length, list, num)

def findMediumPost(author, list, num):
    length = (100, 1000)
    return findPost(author, length, list, num)

def findLongPost(author, list, num):
    length = (1000, 3000)
    return findPost(author, length, list, num)

def findRantPost(author, list, num):
    length = (3000, 9999999)
    return findPost(author, length, list, num)

def findSingleAuthors(num):
    value = []
    for i in range(0, num):
        while value == []:
            writeAuthors("testData.json", "singleAuthor" + str(i + 1) + ".json", 1)
            worker = JSON.workOnJSON()
            author = worker.read_JSON_file("singleAuthorData" + str(i + 1) + ".json")[0]
            list = worker.read_JSON_file("newData.json")
            value = findLongPost(author, list, 1)

        worker.save_JSON_file("singleAuthorData" + str(i + 1) + ".json", value)

def singleAuthorTest(num, filename_save):
    for i in range(0, num):
        index = i + 1
        worker = JSON.workOnJSON()
        authorText = worker.read_JSON_file("singleAuthorData" + str(index) + ".json")
        value = reportData.runTest(authorText)
        worker.save_JSON_file(filename_save, value)
        
#randomSelectUltimateAuthors("dataSave.json", "utilmateTest3.json") 
singleAuthorTest(1, "savefile.json")