import sys
sys.path.append('../')

import cqt
import cqt.datagen as dg
import cqt.dbutility.dbutility as db
import cqt.model.asset_model as md
import cqt.model.asset_model_component_spot as comp_spot
import pandas as pd
import numpy as np

from datetime import datetime
from datetime import timedelta
import matplotlib.pyplot as plt
from matplotlib import pyplot

from statsmodels.tsa import arima_model as arma
from sklearn.metrics import mean_squared_error

from sqlalchemy import create_engine
import cli
import cli.app
@cli.app.Application


def main(app):
	
	key = "59103194-7503-441E-A849-1B961471734B"
	source = app.param.source
	
	request_dict = {'request_type' : app.param.type \
				   'symbol_id' : app.param.symbol, \
				   'period_id' : app.param.period, \
				   'time_start' : app.param.timestart, \
				   #'time_end' : '2017-09-01T00:00:00', \
				   'limit' : app.param.limit}
				   
	if not app.param.timeend is None:
		request_dict['time_end'] = app.param.timeend
	
	df= dg.data_gen(source, request_dict, key,write_to_file=False, returnDF=True)

	tbl_name = dg.get_req_str(source, request_dict, False)

	db.dump_to_db(df, tbl_name, 'key')
	
main.add_param("symbol", help='Mandatory, symbol id for the request')
main.add_param("period", help='Mandatory, period for the request')
main.add_param("-source", default='coinapi' help='Optional, source of the request, default to coinapi')
main.add_param("-type", default="ohlcv", help='Optional, the type of the request, default to ohlcv')
main.add_param("-timestart", default='2001-01-01T00:00:00', help='Optional, the start time of the request, default to 2001-01-01T00:00:00')
main.add_param("-timeend", default=None, help='Optional, the end time of the request, default to None')
main.add_param("-limit", default='100000', help='Optional, the limit of the request, default to 100000')
	
if __name__ == "__main__":
	main.run()