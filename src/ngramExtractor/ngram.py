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
import pprint
import re
import probability as prob

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

      if kwargs.has_key('min_sim'):    self.min_sim(kwargs['min_sim'])
      if kwargs.has_key('warp'):       self.warp(kwargs['warp'])
      if kwargs.has_key('ic'):         self.ic(kwargs['ic'])
      if kwargs.has_key('only_alnum'): self.only_alnum(kwargs['only_alnum'])
      if kwargs.has_key('ngram_len'):  self.ngram_len(kwargs['ngram_len'])
      if kwargs.has_key('padding'):    self.padding(kwargs['padding'])
      if kwargs.has_key('noise'):      self.noise(kwargs['noise'])

      if type(haystack) is ListType:
         self.__ngram_index = self.ngramify(haystack)
      else:
         raise TypeError, "Comparison base must be a list of strings"

   def ngramify(self, haystack, ic = None, only_alnum = None, padding = None, noise = None):
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

      for string in haystack:
         # start modified -fixit
         string = re.sub('[0-9]','\v', string)
         # end modified
         tmpstr = string
         if only_alnum: raise NotImplementedError
         if ic:         tmpstr = tmpstr.lower()
         for char in noise:
            tmpstr = tmpstr.replace(char, '')
         if seen.has_key(tmpstr): continue
         seen[tmpstr] = 1
         
         # start modified by me
         tmpstr = padding + tmpstr + padding
         length = len(tmpstr)
         for i in xrange( length - self.__ngram_len + 1 ):
            ngram = tmpstr[i:i+self.__ngram_len]
            if not grams.has_key(ngram):
               grams[ngram] = {'grams':0}
           # if not grams[ngram].has_key(string):
           #    grams[ngram][string] = {'grams':0}
            grams[ngram]['grams'] += 1
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
            actMatch = matches[match]
            ngram_count = actMatch['grams']
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
       for i in range(0, len(words) -1):
           prob *= probability(words[i],words[0:i-1])
       return prob
   
   def propability(self, word, number):
       divValue = 0
       # I look through every n-gram of the corpus, to see whether the
       # word appers
       for corp in self.corp:
           divValue += corp.count(word)           
       if divValue > 0:
           return self.probHat(word, number, divValue)
       else:
           newWord = word[1:]
           if len(newWord) > 0:
               return self.beta(word) * self.propability(newWord, number)
           else:
               return 0
      
   def beta(self, words):
       upperSum = 0
       index = 0
       for i in range(0, len(words)):
           x = words[i]
           divValue = words.count(x)
           upperSum += self.probHat(words, i, divValue)
       lowerSum = 0
       
       lessWords = words[1:]
       for i in range(0, len(lessWords)):
           x = lessWords[i]
           divVaule = lessWords.count(x)
           lowerSum += self.probHat(lessWords, i, divValue)
        
       upper = float(1 - upperSum)
       lower = float(1 - lowerSum)
       # print "beta ", lower, upper, upper / lower
       return upper / lower

   def probHat(self, words, number, divValue):
        freq = prob.FreqDist(self.corp)
        goodTur = prob.GoodTuringProbDist(freq)
        sum = 0
        list = []
     #   print words
     #   for i in range(0, len(words)):
     #       print goodTur.prob(words[i])
     #       sum += goodTur.prob(words[i])
        upper = float(goodTur.prob(words))
        if upper > 0:
            print words, ":", str(upper), ":", divValue
        return (upper / float(divValue))
   
   def ngram_to_list(self, grams):
        list = []
        for val in grams:
            for i in range(0, grams[val]['grams']):
                list.append(val)
        return  list
        
#end methods written by me
def makeAuthor(text):
    base = [text]
    tg = ngram(base, min_sim=0.0)
    (gram, list) = tg.ngramify(base)
    tg.corp = list
    return tg

def makeAuthors(authorDict):
    finalDict = {}
    for name in authorDict:
        finalDict[name] = makeAuthor(authorDict[name])
    return finalDict

def compareAuthors(authors, textToCompare):
    sum = 0
    compareTo = [textToCompare]
    com = ngram(compareTo, min_sin=0.0)
    (gram, workList) = com.ngramify(compareTo)
    dataDist = {}
    for author in finalDict:
        tg = finalDict[author]
        for word in workList: 
            sum += tg.propability(word, 0)
        dataDist[author] = sum
    print dataDist
    print largestDictKey(dataDist)

def largestDictKey(resultDict):
    b = dict(map(lambda item: (item[1],item[0]),resultDict.items()))
    max_key = b[max(b.keys())]
    return (max_key, resultDict[max_key])

if __name__ == "__main__":
    authorDict = {}
    authorDict["Bram Stoker"] = "3 May. Bistritz.-Left Munich at 8:35 P.M., on 1st May, arriving at Vienna early next morning; should have arrived at 6:46, but train was an hour late.  Buda-Pesth seems a wonderful place, from the glimpse which I got of it from the train and the little I could walk through the streets.  I feared to go very far from the station, as we had arrived late and would start as near the correct time as possible. The impression I had was that we were leaving the West and entering the East; the most western of splendid bridges over the Danube, which is here of noble width and depth, took us among the traditions of Turkish rule. We left in pretty good time, and came after nightfall to Klausenburg. Here I stopped for the night at the Hotel Royale.  I had for dinner, or rather supper, a chicken done up some way with red pepper, which was very good but thirsty.  (Mem. get recipe for Mina.) I asked the waiter, and he said it was called paprika hendl, and that, as it was a national dish, I should be able to get it anywhere along the Carpathians. I found my smattering of German very useful here, indeed, I don't know how I should be able to get on without it. Having had some time at my disposal when in London, I had visited the British Museum, and made search among the books and maps in the library regarding Transylvania; it had struck me that some foreknowledge of the country could hardly fail to have some importance in dealing with a nobleman of that country. I find that the district he named is in the extreme east of the country, just on the borders of three states, Transylvania, Moldavia, and Bukovina, in the midst of the Carpathian mountains; one of the wildest and least known portions of Europe. I was not able to light on any map or work giving the exact locality of the Castle Dracula, as there are no maps of this country as yet to compare with our own Ordnance Survey Maps; but I found that Bistritz the post town named by Count Dracula, is a fairly well-known place.  I shall enter here some of my notes, as they may refresh my memory when I talk over my travels with Mina."
    authorDict["Corrow Doctorow"] = "I lived long enough to see the cure for death; to see the rise of the Bitchun Society, to learn ten languages; to compose three symphonies; to realize my boyhood dream of taking up residence in Disney World; to see the death of the workplace and of work. I never thought I'd live to see the day when Keep A-Movin' Dan would decide to deadhead until the heat death of the Universe. Dan was in his second or third blush of youth when I first met him, sometime late-XXI. He was a rangy cowpoke, apparent 25 or so, all rawhide squint-lines and sunburned neck, boots worn thin and infinitely comfortable. I was in the middle of my Chem thesis, my fourth Doctorate, and he was taking a break from Saving the World, chilling on campus in Toronto and core-dumping for some poor Anthro major. We hooked up at the Grad Students' Union -- the GSU, or Gazoo for those who knew -- on a busy Friday night, summer-ish. I was fighting a coral-slow battle for a stool at the scratched bar, inching my way closer every time the press of bodies shifted, and he had one of the few seats, surrounded by a litter of cigarette junk and empties, clearly encamped. Some duration into my foray, he cocked his head at me and raised a sun-bleached eyebrow. \"You get any closer, son, and we're going to have to get a pre-nup.\" I was apparent forty or so, and I thought about bridling at being called son, but I looked into his eyes and decided that he had enough realtime that he could call me son anytime he wanted. I backed off a little and apologized. He struck a cig and blew a pungent, strong plume over the bartender's head. \"Don't worry about it. I'm probably a little over accustomed to personal space.\" I couldn't remember the last time I'd heard anyone on-world talk about personal space. With the mortality rate at zero and the birth-rate at non-zero, the world was inexorably accreting a dense carpet of people, even with the migratory and deadhead drains on the population. \"You've been jaunting?\" I asked -- his eyes were too sharp for him to have missed an instant's experience to deadheading."   
    authorDict["Author Cannon Doyle"] = "To Sherlock Holmes she is always THE woman. I have seldom heard him mention her under any other name. In his eyes she eclipses and predominates the whole of her sex. It was not that he felt any emotion akin to love for Irene Adler. All emotions, and that one particularly, were abhorrent to his cold, precise but admirably balanced mind. He was, I take it, the most perfect reasoning and observing machine that the world has seen, but as a lover he would have placed himself in a false position. He never spoke of the softer passions, save with a gibe and a sneer. They were admirable things for the observer--excellent for drawing the veil from men's motives and actions. But for the trained reasoner to admit such intrusions into his own delicate and finely adjusted temperament was to introduce a distracting factor which might throw a doubt upon all his mental results. Grit in a sensitive instrument, or a crack in one of his own high-power lenses, would not be more disturbing than a strong emotion in a nature such as his. And yet there was but one woman to him, and that woman was the late Irene Adler, of dubious and questionable memory. I had seen little of Holmes lately. My marriage had drifted us away from each other. My own complete happiness, and the home-centred interests which rise up around the man who first finds himself master of his own establishment, were sufficient to absorb all my attention, while Holmes, who loathed every form of society with his whole Bohemian soul, remained in our lodgings in Baker Street, buried among his old books, and alternating from week to week between cocaine and ambition, the drowsiness of the drug, and the fierce energy of his own keen nature. He was still, as ever, deeply attracted by the study of crime, and occupied his immense faculties and extraordinary powers of observation in following out those clues, and clearing up those mysteries which had been abandoned as hopeless by the official police. From time to time I heard some vague account of his doings: of his summons to Odessa in the case of the Trepoff murder,"
    authorDict["Charles Dickens"] = "Whether I shall turn out to be the hero of my own life, or whether that station will be held by anybody else, these pages must show. To begin my life with the beginning of my life, I record that I was born (as I have been informed and believe) on a Friday, at twelve o'clock at night.  It was remarked that the clock began to strike, and I began to cry, simultaneously. In consideration of the day and hour of my birth, it was declared by the nurse, and by some sage women in the neighbourhood who had taken a lively interest in me several months before there was any possibility of our becoming personally acquainted, first, that I was destined to be unlucky in life; and secondly, that I was privileged to see ghosts and spirits; both these gifts inevitably attaching, as they believed, to all unlucky infants of either gender, born towards the small hours on a Friday night. I need say nothing here, on the first head, because nothing can show better than my history whether that prediction was verified or falsified by the result.  On the second branch of the question, I will only remark, that unless I ran through that part of my inheritance while I was still a baby, I have not come into it yet. But I do not at all complain of having been kept out of this property; and if anybody else should be in the present enjoyment of it, he is heartily welcome to keep it. I was born with a caul, which was advertised for sale, in the newspapers, at the low price of fifteen guineas.  Whether sea-going people were short of money about that time, or were short of faith and preferred cork jackets, I don't know; all I know is, that there was but one solitary bidding, and that was from an attorney connected with the bill-broking business, who offered two pounds in cash, and the balance in sherry, but declined to be guaranteed from drowning on any higher bargain.  Consequently the advertisement was withdrawn at a dead loss - for as to sherry, my poor dear mother's own sherry was in the market then - and ten years afterwards, the caul was put up in a raffle down in our part of the country," 
    
    finalDict = makeAuthors(authorDict)
    document = "5 May. The Castle. The gray of the morning has passed, and the sun is high over the distant horizon, which seems jagged, whether with trees or hills I know not, for it is so far off that big things and little are mixed. I am not sleepy, and, as I am not to be called till I awake, naturally I write till sleep comes. There are many odd things to put down, and, lest who reads them may fancy that I dined too well before I left Bistritz, let me put down my dinner exactly \"robber steak\" bits I dined on what they called of bacon, onion, and beef, seasoned with red pepper, and strung on sticks, and roasted over the fire, in simple style of the London cat's meat! The wine was Golden Mediasch, which produces a queer sting on the tongue, which is, however, not disagreeable. I had only a couple of glasses of this, and nothing else."    
    
    compareAuthors(finalDict, document)