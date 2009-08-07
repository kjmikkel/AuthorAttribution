import workOnJSON as JSON
import random as ran
import constants


def makeAllTexts():
    findUtimateTexts(3)
    
    # The bogus texts are made by the corpora   
    findUtimateTexts("UltimateTexts", 3)
    
""" 
* Find random authors who combined have written over half the texts in the corpus
There are no checks or feedback functions, so in the pathalogical case, all the authors
who have written 1 post might be choosen

* Extract the text from the authors in the ultimateStressTest and save them to a json file
"""
def findUtimateTexts(filename_save, num):
    worker = JSON.workOnJSON()
    list = worker.read_JSON_file(constants.location + "dataSave.json")
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
        
        worker.save_JSON_file(constants.authors + "UltimateAuthors" + str(refNumber) + ".json", pickedAuthors)
        extractRandomAuthorTexts(constants.location + "newData.json", 
                                 constants.authors + "UltimateAuthors" + str(refNumber) + ".json", 
                                 filename_save + str(refNumber) + ".json")

#Extract the texts (found in the file filename) from the authors (who are mentioned in the author_filename file),
#and save them to the file filename_save
def extractRandomAuthorTexts(filename, author_filename, filename_save):
    worker = JSON.workOnJSON()
    authorList = worker.read_JSON_file(author_filename)
    
    posts = worker.read_JSON_file(filename)
    authorPosts = []

    for entry in posts:
        if authorList.count(entry["user_id"]):
            authorPosts.append(entry)
    
    worker.save_JSON_file(constants.tests + filename_save, authorPosts)
