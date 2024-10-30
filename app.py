from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from xgboost import XGBRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

app = Flask(__name__)

# Model nesnelerini başlatma
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
gb_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
svr_model = SVR(kernel='rbf')
xgb_model = XGBRegressor(n_estimators=100, random_state=42)

# Özellikleri ölçekleyici
scaler = StandardScaler()

# Veri yükleme ve ön işleme
column_names = [
    "timeStamp", "elapsed", "label", "responseCode", "responseMessage", 
    "threadName", "dataType", "success", "failureMessage", "bytes", 
    "sentBytes", "grpThreads", "allThreads", "URL", "Latency", 
    "IdleTime", "Connect"
]
data = pd.read_csv('Kozmetik500.csv', names=column_names)

# elapsed sütununu sayısal formata dönüştürme
data['elapsed'] = pd.to_numeric(data['elapsed'], errors='coerce')

# Özellikleri seçme
features = data[['grpThreads', 'allThreads', 'Latency', 'bytes', 'sentBytes', 'success']].copy()
target = data['elapsed']

# Özelliklerin tümünü sayısal formata dönüştürme
features.loc[:, 'grpThreads'] = pd.to_numeric(features['grpThreads'], errors='coerce')
features.loc[:, 'allThreads'] = pd.to_numeric(features['allThreads'], errors='coerce')
features.loc[:, 'Latency'] = pd.to_numeric(features['Latency'], errors='coerce')
features.loc[:, 'bytes'] = pd.to_numeric(features['bytes'], errors='coerce')
features.loc[:, 'sentBytes'] = pd.to_numeric(features['sentBytes'], errors='coerce')

# 'success' sütunundaki sadece 'true' ve 'false' değerlerini tutun
features = features[features['success'].isin(['true', 'false'])]

# 'true' ve 'false' değerlerini 1 ve 0 olarak değiştirin ve integer tipe çevirin
features.loc[:, 'success'] = features['success'].replace({'true': 1, 'false': 0}).astype(int)

# NaN değerlerini 0 ile doldurma
features.fillna(0, inplace=True)
target.fillna(0, inplace=True)

# features ve target veri çerçevelerini eşit uzunlukta yapmak için en küçük boyuta göre dilimleme
min_len = min(len(features), len(target))
features = features.iloc[:min_len].reset_index(drop=True)
target = target.iloc[:min_len].reset_index(drop=True)

# Veriyi eğitim ve test olarak böl
X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)

# Özellikleri ölçeklendirme
scaler.fit(X_train)
X_train_scaled = scaler.transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Modelleri eğitme
rf_model.fit(X_train, y_train)
gb_model.fit(X_train, y_train)
svr_model.fit(X_train_scaled, y_train)
#xgb_model.fit(X_train, y_train)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # JSON formatında gelen veriyi al
        data = request.get_json()
        input_data = pd.DataFrame([data])

        # Özellikleri uygun şekilde ölçeklendirme
        input_data_scaled = scaler.transform(input_data)

        # Modellerle tahmin yapma
        pred_rf = rf_model.predict(input_data_scaled)[0]
        pred_gb = gb_model.predict(input_data_scaled)[0]
        pred_svr = svr_model.predict(input_data_scaled)[0]
       # pred_xgb = xgb_model.predict(input_data_scaled)[0]

        # Tahminleri JSON formatında döndürme
        results = {
            "RandomForest": pred_rf,
            "GradientBoosting": pred_gb,
            "SupportVectorRegressor": pred_svr,
          #  "XGBoost": pred_xgb
        }

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(port=5000, debug=True)


