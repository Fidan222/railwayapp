#!/usr/bin/env python3
import os
import io
import pandas as pd
from flask import Flask, request, redirect, render_template_string, jsonify
from datetime import datetime, timedelta
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# Read configuration from environment variables
INFLUX_TOKEN = os.environ.get("INFLUX_TOKEN", "FUX4nm4dQ5xdWnKBF6WdPFCbw7akHHVr6CLjHJdv3I_MjCOLbPw86CUk15fyP_TwJr2fJSsvcMBfs9eR3RQLcg")
INFLUX_URL = os.environ.get("INFLUX_URL", "https://us-east-1-1.aws.cloud2.influxdata.com")
INFLUX_ORG = os.environ.get("INFLUX_ORG", "interview_grader")
INFLUX_BUCKET = os.environ.get("INFLUX_BUCKET", "newbucket")

app = Flask(__name__)

# HTML template for the file upload page.
UPLOAD_HTML = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>CSV to InfluxDB Upload</title>
  </head>
  <body>
    <h1>Upload CSV File</h1>
    <form method="post" action="/convert_and_upload" enctype="multipart/form-data">
        <input type="file" name="file" accept=".csv" required>
        <input type="submit" value="Upload and Convert">
    </form>
  </body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    return render_template_string(UPLOAD_HTML)

@app.route('/convert_and_upload', methods=['POST'])
def convert_and_upload():
    try:
        file = request.files.get('file')
        if file is None:
            return jsonify({"error": "No file uploaded"}), 400

        # Read CSV into a DataFrame
        df = pd.read_csv(io.StringIO(file.read().decode('utf-8')))

        # Determine today's date and set the start time to midnight
        today = datetime.now().date()
        start_dt = datetime.combine(today, datetime.min.time())

        # Connect to InfluxDB and write data points synchronously
        with InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG) as client:
            write_api = client.write_api(write_options=SYNCHRONOUS)

            for _, row in df.iterrows():
                try:
                    # Parse the CSV "Timestamp" (assumed format m:ss)
                    minutes, seconds = map(int, row["Timestamp"].split(":"))
                    delta = timedelta(minutes=minutes, seconds=seconds)
                    time_dt = start_dt + delta
                except Exception:
                    # Skip rows with an invalid timestamp format
                    continue

                # Convert "Is Dangerous" to 1 (TRUE) or 0 (FALSE)
                is_dangerous = 1 if str(row["Is Dangerous"]).strip().upper() == "TRUE" else 0

                # Read emotion field from CSV row
                emotion = str(row["Emotion"]).strip()

                # Create an InfluxDB point. "interview" is the measurement.
                point = (
                    Point("interview")
                    .tag("emotion", emotion)
                    .field("is_dangerous", is_dangerous)
                    .time(time_dt, WritePrecision.S)
                )
                write_api.write(bucket=INFLUX_BUCKET, record=point)

        # Redirect the user to the Influx Cloud UI once done.
        return redirect(INFLUX_URL)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # For local testing, use port 5000. Railway will override the port via the Procfile.
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
