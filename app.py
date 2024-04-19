import eventlet
eventlet.monkey_patch()  # Patch the standard library for compatibility with eventlet

from flask import Flask, render_template
from flask_socketio import SocketIO
from codecarbon import EmissionsTracker
import pickle
import numpy as np
import pandas as pd
import time
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")  # Use eventlet for better WebSocket performance

# Load multiple models
model_files = ['model1.pkl', 'model2.pkl', 'model3.pkl', 'model4.pkl', 'model5.pkl']
models = {}
for model_file in model_files:
    try:
        with open(model_file, 'rb') as file:
            models[model_file] = pickle.load(file)
    except Exception as e:
        print(f"Error loading {model_file}: {e}")
        exit(1)  # Exit if any model cannot be loaded

# Base sample data
input_data = {
    "fixed acidity": 7.0,
    "volatile acidity": 0.27,
    "citric acid": 0.36,
    "residual sugar": 20.7,
    "chlorides": 0.045,
    "free sulfur dioxide": 45.0,
    "total sulfur dioxide": 170.0,
    "density": 1.001,
    "pH": 3.0,
    "sulphates": 0.45,
    "alcohol": 8.8
}

def generate_random_wine_sample(base_data):
    sample_data = {key: [np.random.normal(val, 0.1 * val)] for key, val in base_data.items()}
    sample_df = pd.DataFrame(sample_data)
    return sample_df

def model_predict_and_track(model_name, model, sample_df):
    tracker = EmissionsTracker()
    tracker.start()
    prediction = model.predict(sample_df)[0]  # Assuming the model predicts correctly
    emissions = tracker.stop()  # Stop tracking and retrieve the emissions data
    return {
        'model': model_name,
        'prediction': int(prediction),  # Convert prediction to int
        'emissions': emissions
    }

def generate_random_test_samples():
    with ThreadPoolExecutor(max_workers=len(models)) as executor:
        while True:
            sample_df = generate_random_wine_sample(input_data)
            future_to_model = {executor.submit(model_predict_and_track, model_name, model, sample_df): model_name for model_name, model in models.items()}
            results = [future.result() for future in future_to_model]
            print(f"Emitting results: {results}")
            socketio.emit('new_data', {'results': results})
            time.sleep(4)  # Emit new data every 4 seconds

@app.route('/')
def index():
    return render_template('Main.html')

@socketio.on('connect')
def on_connect():
    print('Client connected, starting data emission...')
    eventlet.spawn(generate_random_test_samples)  # Start generating and emitting in a separate green thread

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')  # Listen on all public IPs
