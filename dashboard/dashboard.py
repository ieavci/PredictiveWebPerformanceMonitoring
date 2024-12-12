from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

@app.route('/')
def dashboard():
    data = pd.read_csv('../outputs/results.csv')
    avg_response_time = data['elapsed'].mean()
    max_response_time = data['elapsed'].max()

    return render_template('dashboard.html', avg=avg_response_time, max=max_response_time)

if __name__ == "__main__":
    app.run(debug=True)
