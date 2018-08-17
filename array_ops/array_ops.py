

'''
The goal of this script is to define a set operatiors on 1d or n-d arrays, 
shared by different components and authors of this package.(i.e. cqt, RL
strategy can share some of the opeartions defined here on arrays, and use them inside 
the method of their respective class)
The goal is also to increase the coersion, and reduce the coupling in the design.
'''

import numpy as np
import numba

@numba.jit
def getMeanOfLastNElem(dataValueArray, n=1):
	
	'''
	get the mean of last N elements from 1d array.
	The function should be a common component of any 
	moving average based signal indicators 
	'''

	return np.mean(dataValueArray[-n:])



# now we build a momentum indicator using the previous component
# we can use python's functools.partial to make the following function
# a 90-30 indicator, or a 10-5 indicator
@numba.jit
def indicatorShorLongtWindowMean(dataValueArray, 
									shortWindowWidth=1,
									longWindowWidth=2):
	'''
	compare the average from long and short window
	return:
	* an indicator regarding who is bigger
	* the difference shortWindowAvg - long windowAvg
	'''
	longWindowMean = getAbsoluteReturn(dataValueArray, longWindowWidth)
	shortWindowMean = getAvgOfLastNElem(dataValueArray, shortWindowWidth)
	diff = shortWindowMean - longWindowMean
	if diff > 0:
		return 1, diff
	elif diff == 0:
		return 0, diff
	elif diff > 0:
		return 1, diff

@numba.jit
def getAbsoluteReturn(dataValueArray, liquidityHorizon=1):
	'''
	b - a  operator
	b and a index are off the by liquidity horizon integer
	'''
	aArray = dataValueArray[0:-liquidityHorizon]
	bArray = dataValueArray[liquidityHorizon:]
	shockArray =  bArray - aArray
	return shockArray

@numba.jit
def getRelativeReturn(dataValueArray, liquidityHorizon=1):

	'''
	b / a  operator
	b and a index are off the by liquidity horizon integer
	'''
	aArray = dataValueArray[0:-liquidityHorizon]
	bArray = dataValueArray[liquidityHorizon:]
	shockArray =  np.divide(bArray, aArray)
	return shockArray

@numba.jit
def getLogReturn(dataValueArray, liquidityHorizon=1):

	'''
	log(b/a)  operator
	b and a index are off the by liquidity horizon integer
	'''
	aArray = dataValueArray[0:-liquidityHorizon]
	bArray = dataValueArray[liquidityHorizon:]
	shockArray =  np.log(np.divide(bArray, aArray))
	return shockArray