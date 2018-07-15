from cqt.strats.strategy import Strategy
import cqt
from cqt.env.mkt_env import MktEnv
from cqt.ledger.ledger import Ledger
from cqt.error_msg import error
from datetime import datetime
from datetime import timedelta
import matplotlib.pyplot as plt
import copy
import pandas as pd
import numpy as np
import sys
import keras
import tensorflow as tf
from keras.models import model_from_json
from talib.abstract import *
from sklearn.externals import joblib
from cqt.strats.strategy import Strategy
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.layers.recurrent import LSTM
from keras.optimizers import RMSprop, Adam
import random, timeit

from matplotlib import pyplot as plt
from sklearn import metrics, preprocessing
from talib.abstract import *
from sklearn.externals import joblib

np.random.seed(1335)

import backtest as twp

class StrategyTensorFlow(Strategy):
    #Take Action
    def take_action(self, state, xdata, action, signal, time_step):
        #this should generate a list of trade signals that at evaluation time are fed to the backtester
        #the backtester should get a list of trade signals and a list of price data for the assett

        #make necessary adjustments to state and then return it
        time_step += 1

        #if the current iteration is the last state ("terminal state") then set terminal_state to 1
        if time_step + 1 == xdata.shape[0]:
            state = xdata[time_step-1:time_step, 0:1, :]
            terminal_state = 1
            signal.loc[time_step] = 0

            return state, time_step, signal, terminal_state

        #move the market data window one step forward
        state = xdata[time_step-1:time_step, 0:1, :]
        #take action
        if action == 1:
            signal.loc[time_step] = 100
        elif action == 2:
            signal.loc[time_step] = -100
        else:
            signal.loc[time_step] = 0
        #print(state)
        terminal_state = 0
        #print(signal)

        return state, time_step, signal, terminal_state
    
        #Get Reward, the reward is returned at the end of an episode
    def get_reward(self,new_state, time_step, action, xdata, signal, terminal_state, eval=False, epoch=0):
        reward = 0
        signal.fillna(value=0, inplace=True)

        if eval == False:
            start_date = self.prices.index[time_step-1]
            end_date = self.prices.index[time_step]
            
            #==============
            #bt = twp.Backtest(pd.Series(data=[x for x in xdata[time_step-2:time_step]], index=signal[time_step-2:time_step].index.values), signal[time_step-2:time_step], signalType='shares')
            #reward = ((bt.data['price'].iloc[-1] - bt.data['price'].iloc[-2])*bt.data['shares'].iloc[-1])
            #==============
            reward = self.back_testing(start_date, end_date)['pnl'].iloc[-1]
            #==============
            
            #print("debug "+ str(reward))
            
        if terminal_state == 1 and eval == True:
            #save a figure of the test set
            #==============
            #bt = twp.Backtest(pd.Series(data=[x for x in xdata], index=signal.index.values), signal, signalType='shares')
            #reward = bt.pnl.iloc[-1]
            #==============
            reward = self.back_testing()['pnl'].iloc[-1]
            #==============
            
            print("debug final "+str(reward))
            #plt.figure(figsize=(3,4))
            #bt.plotTrades()
            #plt.axvline(x=400, color='black', linestyle='--')
            #plt.text(250, 400, 'training data')
            #plt.text(450, 400, 'test data')
            #plt.suptitle(str(epoch))
            #plt.savefig('plt/'+str(epoch)+'.png', bbox_inches='tight', pad_inches=1, dpi=72)
            #plt.close('all')
        #print(time_step, terminal_state, eval, reward)

        return reward
    
    def evaluate_Q(self,eval_data, eval_model, price_data, epoch=0):
        #This function is used to evaluate the performance of the system each epoch, without the influence of epsilon and random actions
        signal = pd.Series(index=np.arange(len(eval_data)))
        state, xdata, price_data = self.init_state(eval_data)
        status = 1
        terminal_state = 0
        time_step = 1
        while(status == 1):
            #We start in state S
            #Run the Q function on S to get predicted reward values on all the possible actions
            qval = eval_model.predict(state, batch_size=1)
            action = (np.argmax(qval))
            #Take action, observe new state S'
            new_state, time_step, signal, terminal_state = self.take_action(state, xdata, action, signal, time_step)
            #Observe reward
            eval_reward = self.get_reward(new_state, time_step, action, price_data, signal, terminal_state, eval=True, epoch=epoch)
            state = new_state
            if terminal_state == 1: #terminal state
                status = 0

        return eval_reward
    
    def train(self):
        self.is_training = True
        
        tsteps = 1
        batch_size = 1
        num_features = 7

        model = Sequential()
        model.add(LSTM(64,
                       input_shape=(1, num_features),
                       return_sequences=True,
                       stateful=False))
        model.add(Dropout(0.5))

        model.add(LSTM(64,
                       input_shape=(1, num_features),
                       return_sequences=False,
                       stateful=False))
        model.add(Dropout(0.5))

        model.add(Dense(4, init='lecun_uniform'))
        model.add(Activation('linear')) #linear output so we can have range of real-valued outputs

        rms = RMSprop()
        adam = Adam()
        model.compile(loss='mse', optimizer=adam)
        
        indata = self.load_data()
        test_data = self.load_data(test=True)
        
        epochs = 2
        buffer = 200
        replay = []
        learning_progress = []
        #stores tuples of (S, A, R, S')
        h = 0
        gamma = 0.95 #since the reward can be several time steps away, make gamma high
        epsilon = 1
        batchSize = 100
        
        self.signal = pd.Series(index=np.arange(len(indata)))
        for i in range(epochs):
            if i == epochs-1: #the last epoch, use test data set
                indata = self.load_data(test=True)
                state, xdata, price_data = self.init_state(indata, test=True)
            else:
                state, xdata, price_data = self.init_state(indata)
            status = 1
            terminal_state = 0
            #time_step = market_data.index[0] + 64 #when using market_data
            time_step = 14
            #while game still in progress
            while(status == 1):
                #We are in state S
                #Let's run our Q function on S to get Q values for all possible actions
                qval = model.predict(state, batch_size=1)
                if (random.random() < epsilon): #choose random action
                    action = np.random.randint(0,4) #assumes 4 different actions
                else: #choose best action from Q(s,a) values
                    action = (np.argmax(qval))
                #Take action, observe new state S'
                new_state, time_step, signal, terminal_state = self.take_action(state, self.xdata, action, self.signal, time_step)
                #Observe reward
                reward = self.get_reward(new_state, time_step, action, price_data, self.signal, terminal_state)

                #Experience replay storage
                if (len(replay) < buffer): #if buffer not filled, add to it
                    replay.append((state, action, reward, new_state))
                    #print(time_step, reward, terminal_state)
                else: #if buffer full, overwrite old values
                    if (h < (buffer-1)):
                        h += 1
                    else:
                        h = 0
                    replay[h] = (state, action, reward, new_state)
                    #randomly sample our experience replay memory
                    minibatch = random.sample(replay, batchSize)
                    X_train = []
                    y_train = []
                    for memory in minibatch:
                        #Get max_Q(S',a)
                        old_state, action, reward, new_state = memory
                        old_qval = model.predict(old_state, batch_size=1)
                        newQ = model.predict(new_state, batch_size=1)
                        maxQ = np.max(newQ)
                        y = np.zeros((1,4))
                        y[:] = old_qval[:]
                        if terminal_state == 0: #non-terminal state
                            update = (reward + (gamma * maxQ))
                        else: #terminal state
                            update = reward
                        y[0][action] = update
                        #print(time_step, reward, terminal_state)
                        X_train.append(old_state)
                        y_train.append(y.reshape(4,))

                    X_train = np.squeeze(np.array(X_train), axis=(1))
                    y_train = np.array(y_train)
                    model.fit(X_train, y_train, batch_size=batchSize, nb_epoch=1, verbose=0)

                    state = new_state
                if terminal_state == 1: #if reached terminal state, update epoch status
                    status = 0

            eval_reward = self.evaluate_Q(test_data, model, price_data, i)
            learning_progress.append((eval_reward))
            print("Epoch #: %s Reward: %f Epsilon: %f" % (i,eval_reward, epsilon))
            #learning_progress.append((reward))
            if epsilon > 0.1: #decrement epsilon over time
                epsilon -= (1.0/epochs)

            model_json = model.to_json()
            with open("./data/"+str(i)+"-model.json", "w") as json_file:
                json_file.write(model_json)
                # serialize weights to HDF5
                model.save_weights("./data/"+str(i)+"-model.h5")
                print("Saved model to disk")
        
        self.is_training = False
        self.loaded_model = model
        
    def load_data(self,test=False):
        x_train = self.prices.iloc[-2000:-300,]
        x_test= self.prices.iloc[-2000:,]
        if test:
            return x_test
        else:
            return x_train
        
    def init_state(self,indata, test=False):
        if (self.xdata.ndim <3):
            if test == False:
                scaler = preprocessing.StandardScaler()
                self.xdata = np.expand_dims(scaler.fit_transform(self.xdata), axis=1)
                joblib.dump(scaler, 'scaler.pkl')
            elif test == True:
                scaler = joblib.load('scaler.pkl')
                self.xdata = np.expand_dims(scaler.fit_transform(self.xdata), axis=1)
        state = self.xdata[0:1, 0:1, :]
        return state, self.xdata, self.close
 
    def __init__(self, mdl, ini_prtf, rules, model_path=None, weight_path=None, scaler_path=None):
        self.asset_model = mdl
        self.initial_portfolio = ini_prtf
        self.rules = rules
        
        self.env = mdl
        self.initial = ini_prtf
        
        self.is_training = False
        
        if model_path and weight_path:
            json_file = open(model_path, 'r')
            loaded_model_json = json_file.read()
            json_file.close()
            self.loaded_model = model_from_json(loaded_model_json)
            # load weights into new model
            self.loaded_model.load_weights(weight_path)
            print("Loaded model from disk")

        # convert data to  open        high         low       close        volume
        btc = 'btc'
        if self.asset_model.has_section(btc):
            self.prices = copy.deepcopy(self.asset_model.get_section(btc).data)
            self.prices.rename(columns={'price_open': 'open', 'price_high': 'high', 'price_low': 'low', 'price_close': 'close', 'volume_traded': 'volume'}, inplace=True)
            self.close = self.prices['close'].values
            diff = np.diff(self.close)
            diff = np.insert(diff, 0, 0)
            sma15 = SMA(self.prices, timeperiod=15)
            sma60 = SMA(self.prices, timeperiod=60)
            rsi = RSI(self.prices, timeperiod=14)
            atr = ATR(self.prices, timeperiod=14)

            xdata = np.column_stack((self.close, diff, sma15, self.close-sma15, sma15-sma60, rsi, atr))
            self.xdata = np.nan_to_num(xdata)
            if scaler_path:
                scaler = joblib.load(scaler_path)
                self.xdata = np.expand_dims(scaler.fit_transform(self.xdata), axis=1)

    def apply_event_logic(self, time, prtf):
        btc = 'btc'
        if self.asset_model.has_section(btc):
            comp_btc = self.asset_model.get_section(btc)
            #ind_btc = signal_double_dip(self.asset_model, btc, time, self.rules)
            # ind_btc = sdp.signal_double_dip(self.asset_model, btc, time, self.rules)
            time_step = self.prices.index.get_loc(time)
            action = 0
            if self.is_training:
                if time_step < self.signal.size:
                    if self.signal.iloc[time_step] == 100:
                        action = 1
                    if self.signal.iloc[time_step] == -100:
                        action = 2
            else:
                qval = self.loaded_model.predict(self.xdata[time_step-1:time_step, 0:1, :], batch_size=1)
                action = (np.argmax(qval))
                    
            
            price_btc = comp_btc.get_price_close(time)

            if action == 1:
                prtf.buy(btc, price_btc)
            elif action == 2:
                prtf.sell(btc, price_btc)

        return prtf

