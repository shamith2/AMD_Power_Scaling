import json
from random import randint
import os

import numpy as np
import plotly
import plotly.graph_objs as go
import tensorflow as tf
from server.plot import plot_single_prediction
from constants import NUM_SAMPLES, MODEL_DIR, SAMPLES_DIR
from trainer.split_model import Clippy, clipped_relu

from trainer.custom_metrics_losses import mae_current_cycle, mae_remaining_cycles


def load_model():
    global model  # bc YOLO
    model = tf.keras.models.load_model(MODEL_DIR, custom_objects={'clippy': Clippy(clipped_relu),
                                                                  'mae_current_cycle': mae_current_cycle,
                                                                  'mae_remaining_cycles': mae_remaining_cycles})

def make_prediction(cycle_data):
    cycles = { 'Qdlin': np.array(json.loads(cycle_data['Qdlin'])),
                #'Tdlin': np.array(json.loads(cycle_data['Tdlin'])),
                'IR': np.array(json.loads(cycle_data['IR'])),
                'Discharge_time': np.array(json.loads(cycle_data['Discharge_time'])),
                'QD': np.array(json.loads(cycle_data['QD']))
            }

    predictions = model.predict(cycles)

    print("Returning predictions:")
    print(type(predictions))
    print(predictions)

    return predictions


def make_plot(predictions):
    predictions = np.array(predictions)
    # The prediction endpoint can handle batches of battery data per request,
    # but for now we visualize only the first data example.
    first_pred = predictions[0]
    window_size = model.input_shape[0][1]
    scaling_factors_dict = {"Remaining_cycles": 2159.0}
    mean_cycle_life = 674  # calculated from training set
    figure = plot_single_prediction(first_pred,
                                  window_size,
                                  scaling_factors_dict,
                                  mean_cycle_life)
    
    return figure

def save_plot(plot, name):
  if not os.path.exists("plots"):
    os.mkdir("plots")
  
  full_path = os.path.join("plots", name)
  
  plot.write_image(full_path)

    
if __name__ == "__main__":
    print('--> Loading Keras Model and Predicting')
    model = None
    load_model()  

    rand = randint(1,NUM_SAMPLES) 
    filename = "sample_input_{}.json".format(rand)  
    with open(os.path.join(SAMPLES_DIR,"{}".format(filename)), "r") as json_file:
        json_data = json.load(json_file)   

    print('--> Predicting on sample_input_{}.json'.format(rand))
    pred = make_prediction(json_data)
    
    fig = make_plot(pred)
    fname = 'plot' + str(rand) + '.png'
    save_plot(fig, fname)

    