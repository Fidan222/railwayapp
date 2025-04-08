# CSV to InfluxDB Uploader

This Flask application converts an uploaded CSV file into InfluxDB data points and writes them into your InfluxDB bucket. Once processing is done, the application redirects users to the Influx Cloud UI.

## Files

- **app.py**: Main Flask application with the file upload endpoint.
- **requirements.txt**: Lists project dependencies.
- **Procfile**: Tells Railway how to run the app using Gunicorn.
- **README.md**: Project description and instructions.

## Environment Variables

Before deploying, set the following environment variables in Railway:

- `INFLUX_TOKEN`: Your InfluxDB access token.
- `INFLUX_URL`: The InfluxDB URL (e.g., https://us-east-1-1.aws.cloud2.influxdata.com).
- `INFLUX_ORG`: Your InfluxDB organization name.
- `INFLUX_BUCKET`: Your target InfluxDB bucket.
