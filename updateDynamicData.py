#!/usr/bin/python3

import importUtilities
import cli.app
from datetime import datetime, date, time
import os
@cli.app.CommandLineApp

def main(app):
	print('Running updateOHLCVHistoryData.py ...')

	
	baseUrlCfg = '%s/baseUrl.cfg' % os.path.dirname(__file__)
	
	print('- outDir = %s' % app.params.outDir)
	print('- format = %s' % app.params.format)
	print('- symbol = %s' % app.params.symbol)
	print('- periodID = %s' % app.params.periodID)
	print('- timeStart = %s' % app.params.timeStart)
	print('- timeEnd = %s' % app.params.timeEnd)
	print('- includeEmptyItems = %s' % app.params.includeEmptyItems)
	print('- limit = %s' % app.params.limit)
		
	if app.params.timeEnd == '':
		timeEnd = datetime.today().isoformat()
	else:
		timeEnd = datetime.strptime(app.params.timeEnd,"%y/%m/%d %H:%M:%S").isoformat()
	
	timeStart = datetime.strptime(app.params.timeStart,"%y/%m/%d %H:%M:%S").isoformat()
		
	print('- Getting base Url for ohlcv ...')
	baseUrl = importUtilities.getBaseUrl('ohlcv')

	print('- Building full URL for OHLCV History...')
	fullUrl = importUtilities.buildOHLCVHistoryUrl(app.params.symbol,timeStart,baseUrl,app.params.periodID,timeEnd,app.params.includeEmptyItems,app.params.limit )
	
	fileName = '%s_%s_%s_%s' % (app.params.symbol,app.params.periodID,timeStart.replace(':','-'),timeEnd.replace(':','-'))
	
	print('- Updating the dynamic data ohlcv:' )
	importUtilities.getDynamicDataFromAPI(fileName,fullUrl,app.params.format,app.params.outDir)

main.add_param("outDir",type=str,help="output directory")
main.add_param("format",default="csv",type=str,help="data format, can be csv, pickle or database")
main.add_param("symbol", type=str, help="symbol for data, please refer to symbols.csv")
main.add_param("periodID",type=str,help="period ID, please refer to ohlcv_periods.csv")
main.add_param("timeStart",type=str,help="Start Time, format: YY/MM/DD HH:MM:SS (eg. 16/12/31 13:32:45)")
main.add_param("timeEnd", type=str, default='',help="End Time, format: YY/MM/DD HH:MM:SS (eg. 16/12/31 13:32:45)")
main.add_param("includeEmptyItems", default="false", type=str, help="include Empty Items, boolean variable")
main.add_param("limit", default='100000', type=str, help="data limit per request, min=1, max=100000")


if __name__ == "__main__":
    main.run()
	