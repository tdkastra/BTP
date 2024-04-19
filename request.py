import requests

# Replace with the actual URL where your Flask server is running
url = "http://127.0.0.1:5000/predict"

# Sample input data (replace with actual features from the Wine Quality dataset)
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

# Send HTTP POST request with JSON data
response = requests.post(url, json=input_data)

# Print the response
print("Response Code:", response.status_code)
print("Response JSON:", response.json())
