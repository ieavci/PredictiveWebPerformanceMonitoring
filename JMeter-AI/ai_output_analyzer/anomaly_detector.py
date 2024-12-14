from sklearn.cluster import KMeans
import pandas as pd

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
