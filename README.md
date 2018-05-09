# The CQT (Crypto Quant Trading) Package

The CQT package is a package for crypto quant trading. It includes the following component:

1. **DataGen**: Unified interface for data query and processing. Specific data objects are designed to 
handle various trading data for crypto assets. It contains utility functions to query data from 
different exchanges/data providers, and restore them in a standard OCHLV data format indexed by query
dictionary

2. **Model**: Built from 'spot', 'forward' and 'vol' asset model components, the model class is used to 
hold the data from different types of assets. In each model (component), we attach the corresponding
model configurations as guideline to postprocess and analyze the input data, performance statistical 
inference, and provide interface functions for a large set of market signals (e.g. bear/bull, moving 
average crossing, and etc)

3. **Portfolio**: Standardized holding class, which provides the basic logics of buy/sell and set aside
functions to track the changes on the asset holdings and cash

4. **Strategy**: Valuation engine that combines Model and Portfolio. It takes the signals generated from
Model, and follow the strategy logic to update the Portfolio. Back testing is provided to test the 
strategy against the historical data in the Model. New strategies be derived from the base class simply
and one can implement their own trading logic

5. **Execution**: It provides linkage with certain exchange API, which can execute the strategy based
on the portfolio information