from flask import Flask, render_template, request
import pandas as pd
import json
import plotly
import plotly.subplots
import plotly.express as px
import random
import numpy as np
import matplotlib.pyplot as plt
import time
import datetime
import cv2
from scipy.ndimage import gaussian_filter1d
import paho.mqtt.client as mqtt
from picamera2 import Picamera2

# ======== Initialize Logging ===========
import thing_file

# ======== Initialize flask app ===========
app = Flask(__name__)

# @app.route('/'+thing_file.thing_name)
@app.route('/')

# # Global logging configuration
# logging.basicConfig(level=logging.WARNING)  
# 
# # Logger for this module
# logger = logging.getLogger('main')
# 
# # Debugging for this file.
#app.logger.setLevel(logging.INFO)

# ======== Create function to gather data and render to html-frontend ===========
def notdash():
    global data, data_gaussian

    data = {
        'x location (pixels)': [],
        'Intensity': []
    }
    data_gaussian = {
        'x location (pixels)': [],
        'Intensity': []
    }

    # ======================================================================    
    # ===== Create the graph with subplots with layout and margins =========
    # ======================================================================
    # fig = plotly.tools.make_subplots(rows=2, cols=1, vertical_spacing=0.2)
    fig = plotly.subplots.make_subplots(rows=2, cols=1, vertical_spacing=0.2)

    fig['layout']['margin'] = {
        'l': 30, 'r': 10, 'b': 30, 't': 10
    }
    
    for i in range(len(center_slice_short)):
        
        data['Intensity'].append(center_slice_short[i])
        data['x location (pixels)'].append(i)
        
        data_gaussian['Intensity'].append(center_slice_short_g[i])
        data_gaussian['x location (pixels)'].append(i)

        # ======================================================================    
        # ===== Create traces for plotly =======================================
        # ======================================================================
        fig.append_trace({
            'x': data['x location (pixels)'],
            'y': data['Intensity'],
            'mode': 'lines+markers',
            'type': 'scatter'
        }, 1, 1)
        
        fig.append_trace({
            'x': data_gaussian['x location (pixels)'],
            'y': data_gaussian['Intensity'],
            'mode': 'lines+markers',
            'type': 'scatter'
        }, 2, 1)

    # ======================================================================    
    # ===== Serializing fig json object ====================================
    # ===== Writing data into a json-file ==================================
    # ====================================================================== 

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    # ======================================================================    
    # ===== Serializing raw data of Voltage and timeT into a json object ===
    # ===== Writing data into a json-file ==================================
    # ====================================================================== 
    json_object = json.dumps(data, sort_keys=True, default=str) 
#     print(json_object)
    with open("sample.json", "a") as outfile:
        json.dump(json_object, outfile)
    
    # ======================================================================    
    # ===== Rendering data to the html frontend ============================
    # ====================================================================== 
    return render_template('notdash.html', graphJSON=graphJSON)

    
def camera():
    #create an instance of the Picamera2
    picam2 = Picamera2()

    #set and load the configuration to be used
    capture_config = picam2.create_still_configuration(lores={"size": (320, 240)}, display="lores")

    #start the camera and display a preview
    picam2.start(show_preview=True)

    #countdown for picture
    countdown = 5
    while countdown != 0:

        #print the number of seconds left in countdown
        print(countdown)

        #wait for one second to pass
        time.sleep(1)

        #decrement the countdown variable by 1
        countdown-=1

    print("Say Cheese!")

    #buffer time to allow for people to say cheese
    time.sleep(0.5)

    #Take the picture and save it as "image.jpg" to the current directory
    picam2.switch_mode_and_capture_file(capture_config, "final.jpg")

    #Turn the camera and preview off
    picam2.stop()

    print("image taken, moving onto data processing###################")
# 
def data_process():
    global FWHM, center_slice_short, center_slice_short_g, max_i

    img  = cv2.imread('./final.jpg')
    #img  = cv2.imread('./final_unsat.jpg')
    #img  = cv2.imread('./final_sat.jpg')
    
    grayscaled = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    y_axis = np.shape(grayscaled)[0]

    center_y = int(y_axis/2)

    center_slice = grayscaled[center_y,:]

    data_step = 80

    center_slice_short = center_slice[0::data_step]
    center_slice_short_g = gaussian_filter1d(center_slice_short,1)

    print(len(center_slice))
    print(len(center_slice_short))

    max_i = np.max(center_slice_short)
    min_i = np.min(center_slice_short)
    half_max_i = (max_i - min_i)/2
     
    camera_pixel_size = 1.12e-3 # mm

    FWHM_short = len(np.where((center_slice_short[6:-6] >= half_max_i))[0])
    FWHM = FWHM_short * (data_step-1) * camera_pixel_size


def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    
    if len(np.where((center_slice_short[6:-6] == max_i))[0]) > 1:
        saturation = "Yes"
        FWHM_out = "N/A"
    else:
        saturation = "No"
        FWHM_out = np.round(FWHM,5)
    
    # The four parameters are topic, sending content, QoS and whether retaining the message respectively
    client.publish('Saturation:', payload=saturation, qos=0, retain=False)
    client.publish('FWHM:', payload=FWHM_out, qos=0, retain=False)
    print(f"sent to raspberry/topic")


# hostname = "broker.emqx.io"
# hostname = "192.168.86.37" # Home
hostname = "10.198.25.161" # School

def mqtt_run():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect(hostname, 1883, 60)
    client.loop_start()
    time.sleep(1)
    client.loop_stop()

        
if __name__ == '__main__':
    camera()
    data_process()
    mqtt_run()
    # If you have debug=True and receive the error "OSError: [Errno 8] Exec format error", then:
    # remove the execuition bit on this file from a Terminal, ie:
    # chmod -x flask_api_server.py
    #
    # Flask GitHub Issue: https://github.com/pallets/flask/issues/3189
    print()
    print('=======================================================')
    print('Welcome to My IoT device - %s' % thing_file.thing_name)
    print('http://localhost:5000')
    print('=======================================================')
    print()
    

    app.run(host="0.0.0.0", debug=True, use_reloader=False)
    #app.logger.setLevel(logging.INFO)
    # Default port is 5000
    # To change use port = <integer>
