import workOnJSON as JSON
import random as ran
import reportData

"""
    The number of posts
"""
fewPosts = (35, 68)
somePosts = (69, 102)
manyPosts = (103, 9999)

def OnePost():
    worker = JSON.workOnJSON()
    list = worker.read_JSON_file(location + "newData.json")
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
    
    worker.save_JSON_file(corpora + "singlePostCorpora.json", finalTexts) 
    
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
        worker.save_JSON_file(authors + filename_save, list)

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
    
    worker.save_JSON_file(tests + filename_save, authorPosts)



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
            writeAuthors("testData.json", location + filename + str(i + 1) + ".json", 1)
            worker = JSON.workOnJSON()
            author = worker.read_JSON_file(location + filename + str(i + 1) + ".json")[0]
            list = worker.read_JSON_file(location + "newData.json")
            value = findPost(author, list, 1, length)

        worker.save_JSON_file(authors + filename_save + str(i + 1) + ".json", value)

"""
Preform the test of the single Authors and save the result as a text table in the folder designated below
"""
def AuthorTest(num, filename_test, corpora_name, foldername, filename_save):
    print filename_test
    folder = "../report/tabeller/" + foldername + "/"
    if (corpora_name != "newData" and corpora_name != "testData"):
        corpora_name = corpora + corpora_name
    else:
        corpora_name = location + corpora_name
    print "corpora:", corpora_name
    if filename_test.count("Ul"):
        worker = JSON.workOnJSON()
        authorText = worker.read_JSON_file(tests + filename_test + ".json")
        value = reportData.runTest(authorText, corpora_name + ".json", folder + filename_save, 0 )
    else:
        for i in range(0, num):
            index = i + 1
            worker = JSON.workOnJSON()
            authorText = worker.read_JSON_file(tests + filename_test + str(index) + ".json")
            value = reportData.runTest(authorText, corpora_name + ".json", folder + filename_save, index)

"""
Find out how many posts each author has made, and then choose one of these randomly
"""
def chooseAuthorFromNumber(filename_save, num, number_of_posts):
    worker = JSON.workOnJSON()
    list =worker.read_JSON_file(location + "newData.json")
    
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
        number = authorDict[author][0] 
        if (number >= number_of_posts[0] and number <= number_of_posts[1]):
            print "append"
            authorList.append(author)

    ran.seed()
    for i in range(0, min(num, len(authorList))):
        refNumber = i + 1
        index = ran.randint(0, len(authorList) - 1)
        choosenAuthor = authorList[index]
        finalList.append(choosenAuthor)
        authorList.remove(choosenAuthor)
        (number, texts) = authorDict[choosenAuthor]
        print texts
        worker.save_JSON_file(corpora + filename_save + str(refNumber) + ".json", texts)

def chooseAuthorsWithNumber(filename_save, number_of_posts):
    worker = JSON.workOnJSON()
    list =worker.read_JSON_file(location + "newData.json")
    
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
    
    worker.save_JSON_file(corpora + filename_save + ".json", textList)
    
""" 
* Find random authors who combined have written over half the texts in the corpus
There are no checks or feedback functions, so in the pathalogical case, all the authors
who have written 1 post might be choosen

* Extract the text from the authors in the ultimateStressTest and save them to a json file
"""
def findUtimateTexts(filename_save, num):
    worker = JSON.workOnJSON()
    list = worker.read_JSON_file(location + "dataSave.json")
    totalPosts = 0
    authorDict = {}
    
    for entry in list:
        author = entry[0]
        entry = entry[1]
        totalPosts += entry["textNumber"]
        authorDict[author] = entry["textNumber"]
    
    #we now know the total number of posts
    for i in range(0, num):
        refNumber = i + 1
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
            
        pickedAuthors.sort()
        
        worker.save_JSON_file(authors + "UltimateAuthors" + str(refNumber) + ".json", pickedAuthors)
        extractRandomAuthorTexts(location + "newData.json", authors + "UltimateAuthors" + str(refNumber) + ".json", filename_save + str(refNumber) + ".json")

def createLengthCorpora():
    #chooseAuthorFromNumber(corpora + "few", 3, fewPosts)
    chooseAuthorsWithNumber("Some",  somePosts)
    chooseAuthorsWithNumber("Many",  manyPosts)

def shortBogusCorp(num) :
        worker = JSON.workOnJSON()
        idList = ["A1", "A4", "A35"]
        for i in range(0, num):
            index = i + 1
            list = worker.read_JSON_file(corpora + "many" + str(index) + ".json")
            
            finalList = []
            for text in list:
                print te
                finalList.append({"user_id": idList[i], "text": text,})
            
            finalList.append({"user_id": "Bogus", "text": "hello", "post_id": b1})
            finalList.append({"user_id": "Bogus", "text": "Why, hello again!", "post_id": b2})
            worker.save_JSON_file(corpora + "shortBogusCorpora" + str(index) + ".json", finalList)

def shortBogusTest(num):
    worker = JSON.workOnJSON()
    list = worker.read_JSON_file(location + "newData.json")
    
    textList = []
    for entry in list:
        text = entry["text"]
        leng = len(text)
        if (leng >= longLength[0] and leng <= longLength[1]): 
                textList.append(text)
 
    for i in range(0, num):
        index = i + 1
        ran.seed()
        ranIndex = ran.randint(0, len(textList) -1)
        worker.save_JSON_file(tests + "ShortBogusText" + str(index) + ".json", [textList[ranIndex]])

def makeAllTexts():
    findUtimateTexts(3)
    shortBogusTest(3)
    findUtimateTexts("UltimateTexts", 3)

def doAllTests():
    num = 3
    #doStressTest(num)
    
    #Short Bogus Test
    #AuthorTest(num, "ShortBogusText", "shortBogusCorpora", "shortBogusText", "shortBogusText") 
    
    doNumberTest(num)
    
    #UltimateTexts
    
    AuthorTest(num, "testUl", "testData" ,"UltimativeTest", "UltimativeTest")

    AuthorTest(num, "UltimateTexts", "testData" ,"UltimateTest", "UltimateTest")

def doNumberTest(num):
    #AuthorSomePost
    #AuthorTest(num, "AuthorSomePost", "Some", "AuthorSomePost", "AuthorSomePost")
    
    #AuthorManyPost/
    AuthorTest(num, "AuthorManyPost", "Many", "AuthorManyPost", "AuthorManyPost")

def doStressTest(num):

    # StressTest1
    AuthorTest(num, "singleAuthorData", "newData" ,"StressTest", "StressTest1")
    
    # StressTest2
    # No one in this category
    #AuthorTest(num, "singleAuthorData", "few" ,"StressTest", "StressTest"
    
    #StressTest 3
    AuthorTest(num, "singleAuthorData", "Some" ,"StressTest", "StressTest3")
        
    # StressTest 4
    AuthorTest(num, "singleAuthorData", "Many" ,"StressTest", "StressTest4")
       
    # StressTest5
    AuthorTest(num, "singleAuthorData", "singlePostCorpora" ,"StressTest", "StressTest5")
    
def makeCorpora():
    makeShortBogusText(3) 
    AuthorTest(3, "singleAuthorData", "savefile.json")
    createLengthCorpora()
    OnePost()
    
"""
AuthorFewPost
Corpora and Test
"""
def AuthorLengthTestCorpora(length, name, num):
    worker = JSON.workOnJSON()
    list = worker.read_JSON_file(location + "newData.json")
    authorDict = {}
    for entry in list:
        
        text = entry["text"]
        author = entry["user_id"]
        postId = entry["post_id"]
        value = {"text": text, "user_id": author, "post_id": postId} 
        if authorDict.has_key(author):
            authorDict[author].append(value)
        else:
            authorDict[author] = [value]
    
    # I only keep the authors who has the correct number of posts
    newAuthorDict = {}
    for author in authorDict.keys():
        number = len(authorDict[author])
        if (number >= length[0] and number <= length[1]):
            newAuthorDict[author] = authorDict[author]
    
    if len(newAuthorDict):
        worker.save_JSON_file(corpora + "Author" + name + "Post.json", newAuthorDict)

    authorKeys = newAuthorDict.keys()
    for i in range(0, num):
        author = None
        index = i + 1
        ran.seed()
        if len(authorKeys) != 0:
            ranIndex = ran.randint(0, len(authorKeys) -1)
            author = authorKeys[ranIndex]
            authorKeys.remove(author)
            worker.save_JSON_file(tests + "Author" + name +"Post" + str(index) + ".json", newAuthorDict[author])

def makeLengthTests():
  #  AuthorLengthTestCorpora(fewPosts, "Few", 3)
    AuthorLengthTestCorpora(somePosts, "Some", 3)
    AuthorLengthTestCorpora(manyPosts, "Many", 3)
    
location = "data/"
authors = location + "Authors/"
corpora = location + "Corpora/"
tests = location + "Tests/"
#createLengthCorpora()

doAllTests()