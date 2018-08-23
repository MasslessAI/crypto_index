
'''
Define basic time series objects here that utilizes the array_ops
'''


import numpy as np
import pandas as pd
import numba
import array_ops as aop


class Base1DSeries:
    def __init__(self,
                 dataValueArray=None,
                 indexValueArray=None,
                 name=None,
                 metaDataDict=None):
        
        self.__dataValueArray = dataValueArray
        self.__indexValueArray = indexValueArray
        self.__name = name
        self.__metaDataDict = metaDataDict
    
    def getDataValues(self):
        return self.__dataValueArray

    def setDataValues(self, dataValueArray):
        self.__dataValueArray = dataValueArray

    def getIndexValues(self):
        return self.__indexValueArray

    def setIndexValues(self, indexValueArray):
        self.__indexValueArray = indexValueArray

    def getName(self):
        return self.name

    def setName(self, name):
        self.__name = name

    def getMetaDataDict(self):
        return self.__metaDataDict

    def setMetaDataDict(self, metaDataDict):
        self.__metaDataDict = metaDataDict

    def toDataFrame(self);
        df = pd.DataFrame()
        df['index_value'] = self.__indexValueArray
        df[self.__name] = self.__dataValueArray


class ScenSeries(Base1DSeries):
    def __init__(self,
                 dataValueArray=None,
                 indexValueArray=None,
                 name=None,
                 metaDataDict=None,
                 liquidityHorizon=None,
                 scenType=None):
        
        self.__dataValueArray = dataValueArray
        self.__indexValueArray = indexValueArray
        self.__name = name
        self.__metaDataDict = metaDataDict
        self.__liquidityHorizon = liquidityHorizon
        self.__scenType = scenType

    def getScenType(self):
        return self.__scenType

    def getLiquidityHorizon(self):
        return self.__liquidityHorizon

class SpotSeries(Base1DSeries):
    
    def getAbsoluteReturnArray(self, 
                               liquidityHorizon=1):
        returnArray = aop.getAbsoluteReturn(self.__dataValueArray,
                                            liquidityHorizon=liquidityHorizon)
        return returnArray

    def getRelativeReturnArray(self, 
                               liquidityHorizon=1):
        returnArray = aop.getAbsoluteReturn(self.__dataValueArray,
                                            liquidityHorizon=liquidityHorizon)
        return returnArray
    
    def getLogReturnArray(self, 
                           liquidityHorizon=1): 
        returnArray = aop.getLogReturn(self.__dataValueArray,
                                       liquidityHorizon=liquidityHorizon)
        return returnArray

    def getAbsoluteScen(self, liquidityHorizon=1):
        
        shockDataValueArray = self.getAbsoluteReturnArray(liquidityHorizon)
        shockIndexValueArray = self.__indexValueArray[liquidityHorizon:]
        scen = ScenSeries(shockDataValueArray, 
                          shockIndexValueArray,
                          name=self.__name,
                          liquidityHorizon=liquidityHorizon,
                          scenType ='absolute')    
        return scen

    def getRelativeScen(self, liquidityHorizon=1):
        
        shockDataValueArray = self.getRelativeReturnArray(liquidityHorizon)
        shockIndexValueArray = self.__indexValueArray[liquidityHorizon:]
        scen = ScenSeries(shockDataValueArray, 
                          shockIndexValueArray,
                          name=self.__name,
                          liquidityHorizon=liquidityHorizon,
                          scenType ='relative')    
        return scen

    def getLogReturnScen(self, liquidityHorizon=1):
        
        shockDataValueArray = self.getLogReturnArray(liquidityHorizon)
        shockIndexValueArray = self.__indexValueArray[liquidityHorizon:]
        scen = ScenSeries(shockDataValueArray, 
                          shockIndexValueArray,
                          name=self.__name,
                          liquidityHorizon=liquidityHorizon,
                          scenType ='log_return')    
        return scen

    def getMeanOfLastNElem(self, n=1):
        return aop.getMeanOfLastNElem(self.__dataValueArray, 
                                      n=n)

    def indicatorShorLongtWindowMean(self, 
                                     shortWindowWidth=1,
                                     longWindowWidth=2)

        return aop.indicatorShorLongtWindowMean(self.__dataValueArray,
                                                shortWindowWidth=shortWindowWidth,
                                                longWindowWidth=longWindowWidth)
        



# class OCLHVSeries:
#     def __init__(self):
#         pass