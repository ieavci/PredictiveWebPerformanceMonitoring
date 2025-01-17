import io
import matplotlib
matplotlib.use('Agg')

import os
import sys
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler  
from keras.models import Sequential #type: ignore
from keras.layers import LSTM, Dense, Dropout #type: ignore
from sklearn.model_selection import train_test_split
from flask import Flask, jsonify, render_template, request, redirect, url_for
import matplotlib.pyplot as plt
import base64
from io import BytesIO

# Flask app setup
app = Flask(__name__)

# Ensure necessary directories exist
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
INPUTS_DIR = os.path.join(BASE_DIR, 'inputs')
OUTPUTS_DIR = os.path.join(BASE_DIR, 'outputs')
os.makedirs(INPUTS_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# LSTM Anomaly Detection Function
def lstm_anomaly_detection(file_path, time_steps=10, dynamic_threshold=True, threshold_factor=3):
    try:
        data = pd.read_csv(file_path)
        if 'elapsed' not in data.columns:
            raise ValueError("Required column 'elapsed' is missing in the CSV file.")

        elapsed = data['elapsed'].values.reshape(-1, 1)
        scaler = MinMaxScaler()
        scaled_data = scaler.fit_transform(elapsed)

        sequences = []
        targets = []
        for i in range(len(scaled_data) - time_steps):
            sequences.append(scaled_data[i:i + time_steps])
            targets.append(scaled_data[i + time_steps])
        sequences, targets = np.array(sequences), np.array(targets)

        X_train, X_test, y_train, y_test = train_test_split(sequences, targets, test_size=0.2, random_state=42, shuffle=False)

        model = Sequential([
            LSTM(50, activation='relu', return_sequences=True, input_shape=(time_steps, 1)),
            Dropout(0.2),
            LSTM(50, activation='relu'),
            Dropout(0.2),
            Dense(1)
        ])
        model.compile(optimizer='adam', loss='mse')

        model.fit(X_train, y_train, epochs=20, batch_size=32, verbose=1, validation_data=(X_test, y_test))

        predictions = model.predict(X_test)
        reconstruction_errors = np.mean((y_test - predictions) ** 2, axis=1)

        if dynamic_threshold:
            mean_error = reconstruction_errors.mean()
            std_error = reconstruction_errors.std()
            threshold = mean_error + threshold_factor * std_error
        else:
            threshold = 0.1

        anomalies = data.iloc[len(X_train) + time_steps:]
        anomalies.loc[:, 'reconstruction_error'] = reconstruction_errors
        anomalies.loc[:, 'is_anomaly'] = anomalies['reconstruction_error'] > threshold

        anomaly_summary = {
            "Total Requests": len(data),
            "Total Anomalies": anomalies['is_anomaly'].sum(),
            "Anomaly Percentage (%)": (anomalies['is_anomaly'].sum() / len(data)) * 100 if len(data) > 0 else 0,
            "Threshold Used": threshold
        }

        # Grafik oluşturma ve base64 encode etme
        plt.figure(figsize=(10, 6))
        plt.plot(reconstruction_errors, label="Reconstruction Error")
        plt.axhline(y=threshold, color='r', linestyle='--', label="Threshold")
        plt.title("Reconstruction Errors")
        plt.xlabel("Samples")
        plt.ylabel("Error")
        plt.legend()

        # Grafik base64 encode
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        plot_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()

        return anomalies[anomalies['is_anomaly']], anomaly_summary, {
        "reconstruction_errors": reconstruction_errors.tolist(),
        "threshold": threshold
}

    except Exception as e:
        print(f"An error occurred in LSTM anomaly detection: {e}")
        return pd.DataFrame(), {}, None