import numpy
import scipy

def hyperGeo(goodChoices, totalNumber, numberToPick):
    badChoices = totalNumber - goodChoices
    return numpy.random.hypergeometric(goodChoices, badChoices, numberToPick, totalNumber)

times = 100000
temp = hyperGeo(13, 52, times)
#result = sum(temp >= 7)/times + sum(temp <= 0 
