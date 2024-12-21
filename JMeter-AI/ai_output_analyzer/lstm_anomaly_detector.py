import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential # type: ignore
from keras.layers import LSTM, Dense # type: ignore

def lstm_anomaly_detection(file_path, time_steps=10, threshold=0.1):
    """
    Detect anomalies using an LSTM model.

    Parameters:
    - file_path: Path to the JMeter results CSV file.
    - time_steps: Number of time steps for the LSTM model.
    - threshold: Anomaly detection threshold (based on reconstruction error).

    Returns:
    - anomalies: A DataFrame containing anomalies.
    - anomaly_summary: A dictionary summarizing anomaly stats.
    """
    try:
        # Load data
        data = pd.read_csv(file_path)
        if 'elapsed' not in data.columns:
            raise ValueError("Required column 'elapsed' is missing in the CSV file.")

        # Preprocess data
        scaler = MinMaxScaler()
        scaled_data = scaler.fit_transform(data['elapsed'].values.reshape(-1, 1))

        # Create sequences
        sequences = []
        for i in range(len(scaled_data) - time_steps):
            sequences.append(scaled_data[i:i + time_steps])
        sequences = np.array(sequences)

        # Split into train and test sets
        train_size = int(len(sequences) * 0.8)
        train_sequences, test_sequences = sequences[:train_size], sequences[train_size:]

        # Build LSTM model
        model = Sequential([
            LSTM(50, activation='relu', input_shape=(time_steps, 1)),
            Dense(1)
        ])
        model.compile(optimizer='adam', loss='mse')

        # Train model
        model.fit(train_sequences, train_sequences[:, -1], epochs=10, batch_size=32, verbose=0)

        # Predict on test set
        predictions = model.predict(test_sequences)
        test_errors = np.mean((test_sequences[:, -1] - predictions) ** 2, axis=1)

        # Detect anomalies
        anomalies = data.iloc[len(train_sequences) + time_steps:]
        anomalies['reconstruction_error'] = test_errors
        anomalies['is_anomaly'] = anomalies['reconstruction_error'] > threshold

        # Summarize anomalies
        anomaly_summary = {
            "Total Requests": len(data),
            "Total Anomalies": anomalies['is_anomaly'].sum(),
            "Anomaly Percentage (%)": (anomalies['is_anomaly'].sum() / len(data)) * 100 if len(data) > 0 else 0
        }

        return anomalies[anomalies['is_anomaly']], anomaly_summary

    except Exception as e:
        print(f"An error occurred in LSTM anomaly detection: {e}")
        return pd.DataFrame(), {}
