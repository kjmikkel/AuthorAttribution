import workOnJSON as JSON
import random as ran

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

writeAuthors("newData.json", "newDataAuthor.json", 15)













