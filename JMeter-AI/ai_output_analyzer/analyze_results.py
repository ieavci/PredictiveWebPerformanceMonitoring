import os
import pandas as pd
from flask import Flask

# Flask uygulamasını oluşturun
app = Flask(__name__)



def analyze_detailed_results(file_path, output_dir, users, loop_count):
    try:
        # Load the results CSV file
        data = pd.read_csv(file_path)

        if 'elapsed' not in data.columns:
            raise KeyError("Missing required column 'elapsed' in results.csv")

        # Perform calculations
        avg_response_time = data['elapsed'].mean()
        max_response_time = data['elapsed'].max()
        min_response_time = data['elapsed'].min()
        error_rate = (data['responseCode'] >= 400).mean() * 100  # Error rate in %

        # Prepare summary data
        summary = {
            "Kullanıcı Sayısı": [users],
            "Döngü Sayısı": [loop_count],
            "Ortalama Yanıt Süresi (ms)": [avg_response_time],
            "Hata Oranı (%)": [error_rate],
            "Maksimum Yanıt Süresi (ms)": [max_response_time],
            "Minimum Yanıt Süresi (ms)": [min_response_time],
        }

        summary_df = pd.DataFrame(summary)
        summary_file = os.path.join(output_dir, "summary_results.csv")

        if os.path.exists(summary_file):
            existing_summary = pd.read_csv(summary_file)
            summary_df = pd.concat([existing_summary, summary_df], ignore_index=True)

        summary_df.to_csv(summary_file, index=False)

        error_codes=[400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 421, 422, 423, 424, 425, 426, 427, 428, 429, 431, 444, 451, 499, 500, 501, 502, 503, 504, 505, 506, 507, 508, 510, 511]
        error_data = data[data['responseCode'].isin(error_codes)]
        error_file = os.path.join(output_dir, "error_results.csv")
        error_data.to_csv(error_file, index=False)

    except Exception as e:
        raise


if __name__ == '__main__':
    app.run(debug=True)
