# cpp.py
# module for Charging Pattern Predictor
#

import os
import pickle
import pandas as pd
import numpy as np
import jdatetime
from matplotlib import pyplot as plt

from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import accuracy_score

home = os.path.join(os.path.expanduser('~'), 'AMD_Adaptive_Battery_Charging')

def transform_data(data_file_path: str) -> (np.ndarray, np.ndarray):
    df = pd.read_csv(data_file_path)

    count = df.groupby(['Day', 'Time']).size().reset_index().iloc[:, -1]
    df = df.groupby(['Day', 'Time'])[['Charging Status', 'Predicted Charging Time', 'State of Charge']].mean().reset_index()
    df.insert(0, "Count", count)

    os.remove(data_file_path)
    df.set_index('Count').to_csv(data_file_path)

    X = df[['Day', 'Time']].to_numpy(dtype=np.uint64)

    y = df[['Charging Status']].to_numpy(dtype=np.uint64)
    y = y.ravel()
    
    return X, y

def train_cpp(trainX: np.ndarray, trainY: np.ndarray, k: int = 15) -> KNeighborsRegressor:  
    cpp = KNeighborsRegressor(n_neighbors=k)
    trained_cpp = cpp.fit(trainX, trainY)
    
    return trained_cpp

def predict_cpp(cpp: KNeighborsRegressor, predictX: np.ndarray) -> np.ndarray:
    predict_Y = cpp.predict(predictX)
    
    return predict_Y

# def predict_cpp(cpp: KNeighborsClassifier, predictX: np.ndarray) -> (np.ndarray, np.ndarray):
#     predict_Y = cpp.predict(predictX)
#     predict_prob_Y = cpp.predict_proba(predictX)
    
#     return predict_Y, predict_prob_Y

def save_cpp(cpp: KNeighborsRegressor, k: int = 5):
    directory = os.path.join(home, 'MODELS')

    if not os.path.isdir(directory):
        os.makedirs(directory)
    
    # timestamp = jdatetime.datetime.now().strftime("_%w%d/%m/%Y%H:%M:%S")
    
    with open(os.path.join(directory, 'cpp_' + str(k)), 'wb') as f:
        pickle.dump(cpp, f)

def load_cpp(filename: str) -> KNeighborsRegressor:
    with open(os.path.join(home, 'DATASETS', filename), 'rb') as f:
        cpp = pickle.load(f)
    
    return cpp

class ChargingPatternPredictor:
    """
    cpp := Charging Pattern Predictor
    """
    def __init__(self, k):
        self.k = k
    
    def transform_data(self, data_file_path: str) -> np.ndarray:
        df = pd.read_csv(os.path.join(home, 'DATASETS', data_file_path))

        X = df[['Day', 'Time']]
        X.loc[:, ['Time']] = X['Time'].apply(convertTime)
        X = X.to_numpy(dtype=np.uint64)

        y = df[['Charging Status']].to_numpy(dtype=np.uint64)
        y = y.ravel()
        
        return X, y
    
    def train(self, trainX: np.ndarray, trainY: np.ndarray) -> KNeighborsRegressor:
        cpp = KNeighborsRegressor(n_neighbors=self.k)
        trained_cpp = cpp.fit(trainX, trainY)
        
        return trained_cpp
    
    def predict(self, cpp: KNeighborsRegressor, predictX: np.ndarray) -> np.ndarray:
        predict_Y = cpp.predict(predictX)
    
        return predict_Y
    
    def load(self, filename: str) -> KNeighborsRegressor:
        with open(os.path.join(directory, filename), 'rb') as f:
            cpp = pickle.load(f)
    
        return cpp

    def save(self, cpp: KNeighborsRegressor):
        directory = os.path.join(home, 'MODELS')

        if not os.path.isdir(directory):
            os.makedirs(directory)
    
        # timestamp = jdatetime.datetime.now().strftime("_%w%d/%m/%Y%H:%M:%S")
    
        with open(os.path.join(directory, 'cpp_' + str(self.k)), 'wb') as f:
            pickle.dump(cpp, f)
    

def plot_data(X: np.ndarray, y: np.ndarray, title: str) -> None: 
    plt.figure()
    
    for _i, _x in enumerate(X):
        if y[_i]:
            plt.scatter(_x[0], _x[1], color='blue')
    
    plt.legend(['charging'])
    plt.title(title)
    
    plt.xlabel('Day')
    plt.ylabel('Time')
    
    plt.xlim([-1, _days_in_week])
    plt.ylim([-1, _min_in_day])
    
    plt.show()
