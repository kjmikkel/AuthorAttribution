from types import StringType, ListType, FloatType, IntType, BooleanType
from cStringIO import StringIO
import pprint
import json

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

def produceStatisticalData():
    filename = "data.json"
    filename_save = "dataSave.json"
    result = read_JSON_file(filename)
    
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
            
    for key in authorData.keys():
        authorEntry = authorData[authorName]
        authorData[authorName]["average"] = float(authorEntry["totalLength"]) / float(authorEntry["textNumber"])
    
    length = 0
    numberTexts = 0
    for key in authorData.keys():
        entry = authorData[key]
        length += entry["totalLength"]
        numberTexts += entry["textNumber"]

    print "Number of authors:", len(authorData)
    print "Length:", length
    print "Number of texts:", numberTexts
    print "Average:", float(length) / float(numberTexts)
        
    save_JSON_file(filename_save, authorData)
    for key in authorData.keys():
        
        
    
produceStatisticalData()