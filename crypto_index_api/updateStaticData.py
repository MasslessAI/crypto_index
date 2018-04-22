#!/usr/bin/python3

import importUtilities
import cli.app
@cli.app.CommandLineApp

## sample command:
## python3 /home/zizhan/massless/gitHub/crypto_index/updateStaticData.py /home/zizhan/massless/data csv 

def main(app):
	print('Running updateStaticData.py ...')
	baseUrlCfg = '%s/baseUrl.cfg' % os.path.dirname(__file__)
	
	print('- outDir = %s' % app.params.outDir)
	print('- format = %s' % app.params.format)

	
	print('- Getting Url Type Map ...')
	urlMap = importUtilities.getUrlTypeMappingFromJson(baseUrlCfg)
	
	for urlKey in urlMap.keys():
		if urlMap[urlKey] == 'static':
			print('- Updating the Static Data %s:' % urlKey)
			importUtilities.getStaticDataFromAPI(urlKey,app.params.format,app.params.outDir)

#main.add_param("baseUrlCfg",type=str,help="full path to baseUrl.cfg, containing the url name, url, and url type")
main.add_param("outDir",type=str,help="output directory")
main.add_param("format",default="csv",type=str,help="data format, can be csv, pickle or database")


if __name__ == "__main__":
    main.run()
	