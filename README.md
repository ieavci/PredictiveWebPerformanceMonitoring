# AI-Powered Load Testing and Performance Monitoring System

## Project Overview
This project aims to develop an AI-Powered Load Testing and Performance Monitoring System that optimizes traffic distribution and monitors website performance under high traffic conditions. The system collects and analyzes traffic data, generates performance predictions, and detects anomalies to suggest improvements. This enables websites to operate efficiently during periods of high traffic.

---

## Features
- **Performance Testing:** Analyze website speed and response time under current traffic conditions.
- **Load Testing:** Measure website efficiency under high traffic loads.
- **AI-Powered Predictions and Anomaly Detection:** Generate performance forecasts and detect anomalies using AI-based models.

---

## Methodologies
### Load Testing
- **Tool:** Apache JMeter
- **Purpose:** Simulate virtual users to test website response under traffic.
- **Process:**
  - Simulate high user request scenarios.
  - Collect performance metrics like response times and error rates.
  - Record and visualize results using CSV files, Pandas, and Plotly.

### Anomaly Detection
- **Model:** LSTM (Long Short-Term Memory)
- **Process:**
  - Use time-series data for response times.
  - Normalize data with MinMaxScaler.
  - Train LSTM model with historical data.
  - Detect anomalies based on deviation thresholds.
- **Visualization:** Graphs for total requests, anomalies, anomaly rates, and thresholds.

---

## Technologies and Tools
- **Backend Framework:** Flask (Python)
- **Frontend Technologies:** HTML, CSS, Bootstrap
- **Visualization:** Plotly
- **Data Processing:** Pandas, NumPy, Scikit-learn
- **Load Testing Tool:** JMeter
- **AI Model:** LSTM (using Keras)

---

## How to Run the Project
1. **Clone the Repository:**
   ```bash
   git clone <https://github.com/ieavci/PredictiveWebPerformanceMonitoring>
   cd <PredictiveWebPerformanceMonitoring>
   ```

2. **Install Python Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure JMeter Path:**
   - Open `execute_test.py`.
   - Set the correct path for `jmeter_path` to match your local JMeter installation.

4. **Run Flask Application:**
   ```bash
   python app.py
   ```
   The application will be available at `http://127.0.0.1:5000/`.

5. **Perform Load Testing:**
   - Navigate to the **Test Execution** page.
   - Start load testing with configured parameters.

6. **View Results:**
   - Analyze test metrics and anomalies on the results page.


---

## Results and Recommendations
### Key Results
- **Test Metrics:**
  - User count, iterations, average response time, error rate, and more.
- **Visualizations:**
  - Response time box plots, success/failure charts, and distribution graphs.
- **Anomaly Detection:**
  - Anomalies identified with LSTM and visualized with detailed metrics.

### Recommendations
1. **Optimization:** Enhance test and monitoring efficiency using advanced model optimization techniques.
2. **Real-Time Monitoring:** Enable real-time anomaly detection and performance tracking.
3. **Performance Suggestions:** Provide actionable insights for improving application performance.

---

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Contact
For inquiries or contributions, please contact <a href="https://linkedin.com/in/ismail-avci-tr" target="_blank">LinkedIn</a>.

---

## Screenshots
Below are the key screenshots of the application:

1. **Homepage**
   ![Homepage](https://github.com/ieavci/PredictiveWebPerformanceMonitoring/blob/main/ss/baslik.png?raw=true)

2. **Test Execution Page**
   ![Test Execution](https://github.com/ieavci/PredictiveWebPerformanceMonitoring/blob/main/ss/teststart.png?raw=true)

3. **LSTM Anomaly Results**
   ![LSTM Anomaly Results](https://github.com/ieavci/PredictiveWebPerformanceMonitoring/blob/main/ss/lstmsummary.png?raw=true)

4. **Error List**
   ![Error List](https://github.com/ieavci/PredictiveWebPerformanceMonitoring/blob/main/ss/error.png?raw=true)

5. **Anomaly List**
   ![Anomaly List](https://github.com/ieavci/PredictiveWebPerformanceMonitoring/blob/main/ss/anomaly.png?raw=true)

6. **Test Results Overview**
   ![Test Results](https://github.com/ieavci/PredictiveWebPerformanceMonitoring/blob/main/ss/summary.png?raw=true)

7. **Success and Failure Over Time Graph**
   ![Success vs Failure Over Time](https://github.com/ieavci/PredictiveWebPerformanceMonitoring/blob/main/ss/g1.png?raw=true)

8. **Response Code Distribution Graph**
   ![Response Code Distribution](https://github.com/ieavci/PredictiveWebPerformanceMonitoring/blob/main/ss/g2.png?raw=true)

9. **Success vs Failure Bar Chart**
   ![Success vs Failure Bar Chart](https://github.com/ieavci/PredictiveWebPerformanceMonitoring/blob/main/ss/g3.png?raw=true)

10. **Response Time Box Plot**
    ![Response Time Box Plot](https://github.com/ieavci/PredictiveWebPerformanceMonitoring/blob/main/ss/g4.png?raw=true)


