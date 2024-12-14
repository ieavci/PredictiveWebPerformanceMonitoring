import os
import pandas as pd

def analyze_detailed_results(file_path, output_dir):
    """
    Perform detailed analysis on JMeter results.
    """
    try:
        # Load CSV file
        data = pd.read_csv(file_path)
        print("CSV file successfully loaded.")

        # Ensure the required columns exist
        if 'responseCode' not in data.columns or 'elapsed' not in data.columns:
            raise ValueError("Required columns 'responseCode' or 'elapsed' are missing in the CSV file.")

        # Convert response codes to numeric and handle invalid values
        data['responseCode'] = pd.to_numeric(data['responseCode'], errors='coerce')
        data = data.dropna(subset=['responseCode'])  # Remove rows with invalid response codes

        # Calculate error rate (HTTP 500 and above)
        error_rate = (data['responseCode'] >= 500).mean() * 100
        print(f"Hata Oranı: {error_rate:.2f}%")

        # Calculate response times
        avg_response_time = data['elapsed'].mean()
        max_response_time = data['elapsed'].max()
        min_response_time = data['elapsed'].min()
        print(f"Ortalama Yanıt Süresi: {avg_response_time:.2f} ms")
        print(f"Maksimum Yanıt Süresi: {max_response_time:.2f} ms")
        print(f"Minimum Yanıt Süresi: {min_response_time:.2f} ms")

        # Ensure output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Save summary results to a new CSV
        summary = {
            "Hata Oranı (%)": [error_rate],
            "Ortalama Yanıt Süresi (ms)": [avg_response_time],
            "Maksimum Yanıt Süresi (ms)": [max_response_time],
            "Minimum Yanıt Süresi (ms)": [min_response_time]
        }
        summary_df = pd.DataFrame(summary)
        summary_df.to_csv(os.path.join(output_dir, 'summary_results.csv'), index=False)
        print("Özet sonuçlar 'summary_results.csv' dosyasına kaydedildi.")

    except FileNotFoundError:
        print(f"Error: File not found at {file_path}. Please check the file path and try again.")
    except ValueError as ve:
        print(f"Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
