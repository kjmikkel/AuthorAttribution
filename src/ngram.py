#!/usr/bin/python
#
# This is part of "ngram". A Python module to compute the similarity between
# strings
# Copyright (C) 2005   Michel Albert
#
# This library is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#

from types import StringType, ListType, FloatType, IntType, BooleanType
from cStringIO import StringIO
import pprint
import re
import probability as prob
import json

class ngram:
   """ Used to compute similarities between strings. Can easily be used to
   compare one string to a whole batch of strings or pick the best string out
   of a list

   This code was *largely* inspired by String::Trigram by Tarek Ahmed. Actually
   I just translated it to python ;)

   You can find the original Perl-Module at
   http://search.cpan.org/dist/String-Trigram/
   """

   def __init__(self, haystack, **kwargs):
      """ Constructor

      PARAMETERS:
         haystack -  String or list of strings. This is where we will look for
                     matches

      OPTIONAL PARAMETERS:
         min_sim     - minimum similarity score for a string to be considered
                       worthy. Default = 0.0
         warp        - If warp > 1 short strings are getting away better, if
                       warp < 1 they are getting away worse. Default = 1.0
         ic          - Ignore case? Default = False
         only_alnum  - Only consider alphanumeric characters? Default = False
         ngram_len   - n-gram size. Default = 3 (trigram)
         padding     - padding size. Default = ngram_len - 1
         noise       - noise characters that should be ignored when comparing

      """

      self.__min_sim    = 0.0
      self.__warp       = 1.0 
      self.__ic         = False     # ignore case
      self.__only_alnum = False
      self.__noise      = ''
      self.__debug      = False
      self.__ngram_len  = 3
      self.__padding    = self.__ngram_len - 1
      self.__corp       = None
      self.__rememberDict = None
      self.__rememberBetaDict = None
      self.__GoodTur = None

      if kwargs.has_key('min_sim'):    self.min_sim(kwargs['min_sim'])
      if kwargs.has_key('warp'):       self.warp(kwargs['warp'])
      if kwargs.has_key('ic'):         self.ic(kwargs['ic'])
      if kwargs.has_key('only_alnum'): self.only_alnum(kwargs['only_alnum'])
      if kwargs.has_key('ngram_len'):  self.ngram_len(kwargs['ngram_len'])
      if kwargs.has_key('padding'):    self.padding(kwargs['padding'])
      if kwargs.has_key('noise'):      self.noise(kwargs['noise'])

      if type(haystack) is ListType:
         self.__ngram_index = self.total_ngram(haystack)
      else:
         raise TypeError, "Comparison base must be a list of strings"

   def total_ngram(self, haystack):
        gram = {}
        list = []
        for i in range(1, self.__ngram_len):
            (newGram, newList) = self.ngramify(haystack, i)
            gram.update(newGram)
            list.extend(newList)
        return (gram, list)

   def ngramify(self, haystack, ngram_length = 3, ic = None, only_alnum = None, padding = None, noise = None):
      """
      Takes list of strings and puts them into an index of ngrams. KEY is a
      ngram, VALUE a list of strings containing that ngram. VALUE has two KEYS:
         grams: count of ngram occurring in string
         len:   length of string with padding (if ignoring non alphanumerics,
                this gets determined after those characters have been removed)

      PARAMETERS:
         haystack    - List of strings to be indexed
         ic          - Ignore Case?
         only_alnum  - Only alphanumeric charactes?
         padding     - Size of the padding
         noise       - Noise characters that should be removed

      RETURNS:
         N-Gram index

         Structure:
         {
            'abc': 'string1':{'grams':0, 'len':11},
            'bcd': 'string2':{'grams':0, 'len':11},
            'ing': 'string3':{'grams':1, 'len':11},
            ...
         }
      """
      if ic is None:          ic = self.__ic
      if only_alnum is None:  only_alnum = self.__only_alnum
      if padding is None:     padding = 'X' * self.__padding
      if noise is None:       noise   = self.__noise
        
      seen  = {}
      grams = {}
      list = []
    
      for stri in haystack:
         # start modified -fixit
         stri = re.sub('[0-9]','\v', stri)
         # end modified
         tmpstr = stri
         if only_alnum: raise NotImplementedError
         if ic:         tmpstr = tmpstr.lower()
         for char in noise:
            tmpstr = tmpstr.replace(char, '')
         if seen.has_key(tmpstr): continue
         seen[tmpstr] = 1
         
         # start modified by me
         tmpstr = padding + tmpstr + padding
         length = len(tmpstr)
         for i in xrange( length - ngram_length + 1 ):
            ngram = tmpstr[i:i+ ngram_length]
            if not grams.has_key(ngram):
               grams[ngram] = 0
           # if not grams[ngram].has_key(stri):
           #    grams[ngram][stri] = {'grams':0}
            grams[ngram] += 1
            list.append(ngram)
      # end modified by me
      return (grams, list)
  
   def reInit(self, base):
      """
      Reinitialises the search space.

      PARAMETERS:
         base - The new search space
      """
      if type(base) is not ListType:
         raise NotImplementedError, "Only lists are supported as comparison base!"
      self.__ngram_index = self.ngramify(base)

   def getSimilarStrings(self, string):
      """
      Retrieves all strings that have a similarity higher than min_sim with
      "string"

      PARAMETERS:
         - string:   The string to compare with the search space

      RETURNS:
         Dictionary of scoring strings.
         Example output:

         {'askfjwehiuasdfji': 1.0, 'asdfawe': 0.17391304347826086}
      """
      ngram_buf = {}

      # KEY = potentially similar string, VALUE = number of identical ngrams
      siminfo     = {}

      if self.__only_alnum: raise NotImplementedError
      if self.__ic:         string = string.lower()
      for char in self.__noise:
         string = string.replace(char, '')
      string = 'X' * self.__padding + string + 'X' * self.__padding

      numgram = len(string) - self.__ngram_len + 1

      for i in xrange(numgram):
         ngram = string[i:i+self.__ngram_len]
         if not self.__ngram_index.has_key(ngram): continue
         matches = self.__ngram_index[ngram]

         for match in matches:
            actName = match
            ngram_count = matches[match]
            if not ngram_buf.has_key(ngram): ngram_buf[ngram] = {}
            if not ngram_buf[ngram].has_key(actName):
               ngram_buf[ngram][actName] = ngram_count
            if ngram_buf[ngram][actName] > 0:
               ngram_buf[ngram][actName] -= 1
               """ start modified"""
               if not siminfo.has_key(actName): siminfo[actName] = {'name': 0}
               siminfo[actName]['name'] += 1
               """ """
               
      return self.computeSimilarity(string, siminfo)

   def computeSimilarity(self, string, siminfo):
      """
      Calculates the similarity of the given some information about n-grams.
      PARAMETERS:
         string   - This is what we want to get the score of
         siminfo  - A dictionary containing info about n-gram distribution.
                    (see getSimilarStrings)
      RETURNS: 
         the score as float
      """
      result = {}
      strCount = 0
      allgrams = 0
      samegrams = 0
      actSim = 0
      length = len(string)
      for key in siminfo:
         samegrams = siminfo[key]['name']
         allgrams = length + siminfo[key]['len'] - 2 * self.__ngram_len - samegrams + 2;
         actSim = self.computeActSimOld(samegrams, allgrams)

         if actSim > self.__min_sim:
            result[key] = actSim

      return result

   def computeActSimOld(self, samegrams, allgrams, warp = None):
      """
      Computes the similarity score between two sets of n-grams according to
      the following formula:

      (a = all trigrams, d = different trigrams, e = warp)

      (a**e - d**e)/a**e

      PARAMETERS:
         samegrams   - n-grams that were found in the string
         allgrams    - All n-grams in the search space
         warp        - the warp factor. See __init__ for explanation

      RETURNS:
         Similarity score as float

      """
      diffgrams   = -1
      actSim      = -1

      if warp is None: warp = self.__warp

      if warp == 1:
         actSim = float(samegrams) / allgrams
      else:
         diffgrams = allgrams - samegrams
         actSim = ((allgrams**warp) - (diffgrams**warp)) / (allgrams**warp)
      return actSim

   def getBestMatch(self, needle, count=1):
      """
      Returns the best match for the given string

      PARAMETERS:
         needle:  The string to search for
         count:     How many results to return

      RETURNS:
         String that best matched the supplied parameter and the score with
         which it matched.
      """

      if type(needle) is not StringType: raise TypeError, "needle must be of type string!"
      if type(count)  is not IntType: raise TypeError, "count must be of type int!"

      # convert the dictionary into a list of tuples
      temp = self.getSimilarStrings(needle).items()

      # sort the resulting list by the second field
      temp.sort(cmp = lambda x,y: cmp(y[1], x[1]))

      # return the top <count> items from the list
      return temp[:count]

   def min_sim(self, *args):

      if len(args) == 0: return self.__min_sim

      if type(args[0]) is not FloatType:
         raise TypeError, "min_sim must be a float"
      if args[0] < 0 or args[0] > 1:
         raise ValueError, "min_sim must range between 0 and 1"
      self.__min_sim = args[0]

   def warp(self, *args):

      if len(args) == 0: return self.__warp

      if type(args[0]) is not FloatType:
         raise TypeError, "warp must be a float"
      if args[0] < 0:
         raise ValueError, "warp must be bigger than 1"
      self.__warp = args[0]

   def ic(self, *args):

      if len(args) == 0: return self.__ic

      if type(args[0]) is not BooleanType:
         raise TypeError, "ic must be a boolean"
      self.__ic = args[0]

   def only_alnum(self, *args):

      if len(args) == 0: return self.__only_alnum

      if type(args[0]) is not BooleanType:
         raise TypeError, "only_alnum must be a boolean"
      self.__only_alnum = args[0]

   def noise(self, *args):

      if len(args) == 0: return self.__noise

      if type(args[0]) is not StringType:
         raise TypeError, "noise must be a string"
      self.__noise = args[0]

   def ngram_len(self, *args):

      if len(args) == 0: return self.__ngram_len

      if type(args[0]) is not IntType:
         raise TypeError, "ngram_len must be an integer "
      if args[0] < 0:
         raise ValueError, "ngram_len must be bigger than 1"
      self.__ngram_len = args[0]

   def padding(self, *args):

      if len(args) == 0: return self.__padding

      if type(args[0]) is not IntType:
         raise TypeError, "padding must be an integer "
      if args[0] < 0:
         raise ValueError, "padding must be bigger than 1"
      self.__ngram_len = args[0]

   def newRemember(self):
    self.__rememberDict = {}
    self.__rememberBetaDict = {}

   def compare(self, s1, s2):
      """
      Simply compares two strings and returns the similarity score.

      This is a class method. It can be called without instantiating
      the ngram class first. Example:

      >>> from ngram import ngram
      >>> ngram.compare('sfewefsf', 'sdfafwgah')
      >>> 0.050000000000000003

      PARAMETERS:
         s1 -  First string
         s2 -  Last string

      """
      if s1 is None or s2 is None:
         if s1 == s2: return 1.0
         else: return 0.0

      result = ngram([s1]).getSimilarStrings(s2)
      if result == {}: return 0.0
      else: return result[s1]
   compare = classmethod(compare)

   #methods written by me
   def probabilityNorm(self, words):
       prob = 1
       self.__rememberDict = {}
       for i in rangef(0, len(words) -1):
           prob *= probability(words[i],words[0:i-1])
       return prob
   
   def propability(self, word, number):
    # If we have already calculated the value, then we can just return that
    if self.__rememberDict.has_key(word):
        #print "hit:", self.__rememberDict[word]
        return self.__rememberDict[word]
    divValue = 0
    newWord = word[:-1]
    divValue = self.corp.count(word)
    #for corp in self.corp:
    #    divValue += corp.count(word)
    if divValue > 0:
        self.__rememberDict[word] = self.probHat(word)
        return self.__rememberDict[word]
    else:
        newWord = word[1:]
        if len(newWord) > 0:
            self.__rememberDict[word] = self.beta(word) * self.propability(newWord, number)
            return self.__rememberDict[word]
        else:
            self.__rememberDict[word] = 0
            return 0
      
   def beta(self, words):
       
       upperSum = 0
       index = 0
       for i in range(0, len(words)):
            x = words[i]
            if not self.__rememberBetaDict.has_key(words + x):
                result = self.probHat(words + x)
                self.__rememberBetaDict[words + x] = result
                upperSum += result
            else:
                upperSum += self.__rememberBetaDict[words + x]
       lowerSum = 0
       
       lessWords = words[1:]
       for i in range(0, len(lessWords)):
           x = lessWords[i]
           if not self.__rememberBetaDict.has_key(lessWords + x):
                result = self.probHat(lessWords + x)
                self.__rememberBetaDict[lessWords + x] = result
                lowerSum += result
           else:
                lowerSum += self.__rememberBetaDict[lessWords + x]
        
       upper = float(1 - upperSum)
       lower = float(1 - lowerSum)
       return upper / lower

   def probHat(self, words):
        if not self.__GoodTur:
            freq = prob.FreqDist(self.corp)
            self.__GoodTur = prob.GoodTuringProbDist(freq)
        upper = 0
        list = []
        upper = self.__GoodTur.prob(words)
        divValue = 0
        divValue = self.corp.count(words[:-1])
#       for corp in self.corp:
 #          divValue += corp.count(words[:-1])
        
        if divValue > 0:
            return (float(upper) / float(divValue))
        else:
            return 0.0

def ngram_to_list(grams):
    list = []
    for val in grams:
        tempList = [val for i in range(0, grams[val])]
        list.extend(tempList)
    return list

#end methods written by me
#begin toplevel methods written by me
def makeAuthor(base):
    tg = ngram(base, min_sim=0.0)
    (gram, list) = tg.total_ngram(base)
    tg.corp = list
    tg.newRemember()
    return tg


def compareAuthors(authors, compareDict, authorDict):
    authorMade = {}
    resultDict = {}    
    for value in compareDict:
        textToCompare = value["text"]
        realAuthor = value["user_id"]
        sum = 0
            
        # Compare value
        compareTo = [textToCompare]
        com = ngram(compareTo, min_sin=0.0)
        (gram, workList) = com.total_ngram(compareTo)
        dataDist = {}
            # We do the actual testing
        for author in authors: 
            tg = makeAuthor(authors[author])
            for word in workList:
                sum += tg.propability(word, 0)
            dataDist[author] = sum
            print "Done with", author
            
        (author, time) = largestDictKey(dataDist)
        print dataDist
        print author        
        print "Real author:", authorDict[realAuthor]
        if not authorMade.has_key(author):
            authorMade[author] = [id]
        else:
            authorMade[author].append(realAuthor)
            
        if not resultDict.has_key(realAuthor):
            resultDict[realAuthor] = {author : 1}
        else:
            if resultDict[realAuthor].has_key(author):
                resultDict[realAuthor] = {author : 1}
            else:
                resultDict[realAuthor][author] += 1
    return (authorMade, resultDict)

def largestDictKey(resultDict):
    b = dict(map(lambda item: (item[1],item[0]),resultDict.items()))
    max_key = b[max(b.keys())]
    return (max_key, resultDict[max_key])

def listify(fileLoad, fileSave, firstDict = None):
    if not firstDict:
        dict = read_JSON_file(fileLoad)
    else:
        dict = firstDict
    
    saveDict = {}
    for author in dict:
        saveDict[author] =  ngram_to_list(dict[author])
    
    if not firstDict:
        save_JSON_file(fileSave, saveDict)
    
    return saveDict

def makeJsonFile(filename, fileToSave_name):
    dict = read_JSON_file(filename)
    authorDict = {}
    authorWrittenDict = {}

    authorNameDirec = {}
    num = 0

    for entry in dict:
        author = entry["user_id"]
        if authorNameDirec.has_key(author):
            author = authorNameDirec[author]
        else:
            authorNameDirec[author] = "A" + str(num)
            author = "A" + str(num)
            num += 1
        
        value = {"user_id": author, "text": entry["text"], "timestamp": entry["timestamp"]}
        id = entry["post_id"]
        if authorDict.has_key(author):
            authorDict[author].append(value)
            authorWrittenDict[author].append(id)
        else:
            authorDict[author] = [value]
            authorWrittenDict[author] = [id]
    
    newAuthorDict = {}
    
    for authorName in authorDict.keys():
        author = authorDict[authorName]
        newAuthorDictTemp = {}
        
        listOfEntries = [entry["text"] for entry in author]
        print authorName,":", listOfEntries
        #for entry in author:
        #    listOfEntries.append(entry["text"])
            
        tg = ngram(listOfEntries)
        (gramfied, list) = tg.total_ngram(listOfEntries)
        newAuthorDict[authorName] = list
        
    save_JSON_file(fileToSave_name, newAuthorDict)
    
    return (authorDict, newAuthorDict, authorNameDirec)
    
def combine_ngrams(author): 
    finalDict = {}
    for authorKey in author:
        #print authorKey
        tempDict = {}
        gram = author[authorKey]
 
        for entryKey in gram.keys():
            thisNumber = gram[entryKey]
            number = 0
                
            if (tempDict.has_key(entryKey)):
                number = tempDict[entryKey] + thisNumber
            else:
                number = thisNumber                
            tempDict[entryKey] = number
        finalDict[authorKey] = tempDict
    return finalDict

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

def merge_author_data(filename, merged_filename, firstDict = None):
    if not firstDict:
        dict = read_JSON_file(filename)
        #print filename +"\n\n\n"
    else:
        dict = firstDict
    newAuthorDict = combine_ngrams(dict)
    if not firstDict:
        save_JSON_file(merged_filename, newAuthorDict)
    return newAuthorDict

def getAndMerge():
    filename = "data.json"     
    fileToSave_name = "data_save_test2.json"  
    fileToSave_final = "data_temp_save_test2.json"
    fileToSave_listed = "data_listify_test2.json"
    (result, ngramLists, authorNameDict) = makeJsonFile(filename, fileToSave_name)
    
    # TODO remove code
    #mergeDict = merge_author_data(fileToSave_name, fileToSave_final)
    
#    listifyDict = listify(fileToSave_name, fileToSave_listed, newAuthorDict)
    
    compareDict = [{"post_id": "412f267787a9d496ee6afe13722754f441555b6679928bcc0820fccc196b8bc6", "user_id": "f910fcc9118d65480b0f7fd459115bcbf6035743e9d4ec402a036181f865c766", "timestamp": 1061545161, "title": "det nye board", "text": "s\u00e5 er det nye board ved at fungere ligesom jeg gerne vil have det og \\r\\ndet vil derfor snart v\u00e6re tilg\u00e6ngeligt for alle danske juggalos.", "thread_id": 917564}]
    print "Compare\n"
    (id, authorData) = compareAuthors(ngramLists,  compareDict, authorNameDict) # result)   
    print "Produce\n"
    produceResultTable(result, id, authorData)
    
    
def produceResultTable(authorMade, attributedList, authorData):
    averageFMeasure = 0.0
    
    finalResults = {}
    
    authorAttri = produceResult(authorData, authorMade)
#    authorAttri = produceResults(authorMade, attributedList)    
    
    for authorName in authorAttri.keys():
        (precision, recall, fMeasure) = authorAttri[authorName]
        finalResults[authorName] = {"precision": precision, "recall": recall, "fMeasure": fMeasure}
        #finalResults[authorName]["recall"] = recall
        #finalResults[authorName]["fMeasure"] = fMeasure
        averageFMeasure += float(fMeasure)
        
    if len(authorAttri):
        averageFMeasure = averageFMeasure / float(len(authorAttri))
    else:
        averageFMeasure = 0
    
    stringResult = ""
    for authorName in authorAttri.keys():
        stringResult += authorName + " &"
    
    stringResult += "Precision & & "
    for authorName in authorAttri.keys():
        stringResult += str(finalResults[authorName]["precision"]) + " & "
    stringResult += " & & & \\"
    stringResult += "Overall Accuracy: " + "PLACEHOLDER" + " Macro-average F-measure: " + str(averageFMeasure) + " \\"
    print averageFMeasure    

def produceResults(authorMade, attributedDict):
    authorAttri = {}
    for name in authorMade.keys(): 
        authorAttri[name] = producreAuthorResult(name, attributedDict, authorMade[name])
    return authorAttri
    
def produceResult(authorData, authorList):
    endResults = {}
    for authorName in authorData.keys():
        
        writtenByAuthor = len(authorList)
        if authorData[authorName].has_key(authorName):
            correctlyAttributed = authorData[authorName][authorName]
        else:
            correctlyAttributed = 0
            
        attributed = 0.0

        for entry in authorData[authorName].keys():
            attributed += float(authorData[authorName][entry])
            
        if attributed:
            precision = correctlyAttributed / attributed
        else:
            precision = 0.0
        
        if writtenByAuthor:    
            recall = correctlyAttributed / writtenByAuthor
        else:
            recall = 0.0
        
        if (precision and recall):
            fMeasure = (2.0 * precision * recall) / (precision + recall)
        else:
            fMeasure = 0.0
        
        endResults[authorName] = (precision, recall, fMeasure)
    
    return endResults
    
def producreAuthorResult(authorName, attributedList, authorList):
    
    writtenByAuthor = float(len(authorList))
    correctlyAttributed = 0.0
    attributed = 0.0

    for entry in attributedList:
        if authorName == entry:
            attributed += 1.0
            if authorList.count(entry):
                correctlyAttributed += 1.0
    
    if attributed:
        precision = correctlyAttributed / attributed
    else:
        precision = 0.0
    
    if writtenByAuthor:    
        recall = correctlyAttributed / writtenByAuthor
    else:
        recall = 0.0
    
    if (precision and recall):
            fMeasure = (2.0 * precision * recall) / (precision + recall)
    else:
        fMeasure = 0.0
    
    return (attributed, correctlyAttributed, precision, recall, fMeasure)

def makeExample():
    exampleStr = "abcdabceabc c"
    produceExample(exampleStr)

def produceExample(exampleStr):
    tg = ngram([exampleStr])
    (grams, list) = tg.ngramify([exampleStr])
    
    printList = []
    for item in list:
        stri = "\ngr{" + item + "}"
        stri.replace(" ","\_")
        stri.replace("'","")
        printList.append(str)
    print printList
        
    freqDict = {}
    for item in list:
        if freqDict.has_key(item):
            freqDict[item] = freqDict[item] + 1
        else: 
            freqDict[item] = 1
    
    freqfreqDict = {}
    for key in freqDict.keys():
        value = freqDict[key]
        if freqfreqDict.has_key(value):
            freqfreqDict[value] += 1
        else: 
            freqfreqDict[value] = 1
    print "\\begin{tabular}{|cc|}"
    print "\\hline"
    print "Frequency & Frequency of frequency \\\\"
    print "\\hline"
    print "r & N_r \\\\"
    for key in freqfreqDict.keys():
        print str(key) + " & " + str(freqfreqDict[key]) + "\\\\"
    print "\\hline"
    print "\\end{tabular}"
    
if __name__ == "__main__":
    getAndMerge()
