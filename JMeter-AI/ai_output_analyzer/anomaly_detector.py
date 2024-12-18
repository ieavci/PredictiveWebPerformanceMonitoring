from sklearn.cluster import KMeans
import pandas as pd

"""

def detect_anomalies(file_path):
    data = pd.read_csv(file_path)
    response_times = data['elapsed'].values.reshape(-1, 1)

    kmeans = KMeans(n_clusters=2)
    labels = kmeans.fit_predict(response_times)

    data['anomaly'] = labels
    anomalies = data[data['anomaly'] == 1]

    print(f"Toplam Anomali Sayısı: {len(anomalies)}")
    print(anomalies[['timeStamp', 'elapsed']].head())

    return anomalies

if __name__ == "__main__":
    anomalies = detect_anomalies('../outputs/results.csv')
"""


def detect_anomalies(file_path, threshold_response_time=2000, error_response_code=500):
    """
    Detect anomalies in the JMeter results file.

    Parameters:
    - file_path: Path to the results CSV file.
    - threshold_response_time: Threshold for response time to classify as anomaly.
    - error_response_code: Response code to classify as error.

    Returns:
    - anomalies: A DataFrame containing the anomalies.
    - anomaly_summary: A dictionary summarizing anomaly stats.
    """
    try:
        # Load CSV file
        data = pd.read_csv(file_path)
        print("CSV file successfully loaded for anomaly detection.")

        # Detect anomalies
        data['is_anomaly'] = (data['elapsed'] > threshold_response_time) | (data['responseCode'] >= error_response_code)
        anomalies = data[data['is_anomaly']]

        # Summarize anomalies
        anomaly_summary = {
            "Total Requests": len(data),
            "Total Anomalies": len(anomalies),
            "Anomaly Percentage (%)": (len(anomalies) / len(data)) * 100 if len(data) > 0 else 0,
            "Max Response Time (ms)": anomalies['elapsed'].max() if not anomalies.empty else None,
            "Error Codes Count": anomalies[anomalies['responseCode'] >= error_response_code].shape[0],
        }

        return anomalies, anomaly_summary

    except FileNotFoundError:
        print(f"Error: File not found at {file_path}. Please check the file path and try again.")
        return pd.DataFrame(), {}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return pd.DataFrame(), {}
