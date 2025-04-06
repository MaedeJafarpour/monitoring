from flask import Flask, jsonify, request
import logging
import time
import random
import uuid
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(message)s')

# Prometheus Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'http_status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'Request latency', ['endpoint'])

@app.before_request
def start_timer():
    request.start_time = time.time()
    request.request_id = str(uuid.uuid4())

@app.after_request
def record_metrics(response):
    latency = time.time() - request.start_time
    REQUEST_COUNT.labels(request.method, request.path, response.status_code).inc()
    REQUEST_LATENCY.labels(request.path).observe(latency)

    log_data = {
        "level": "info",
        "request_id": request.request_id,
        "method": request.method,
        "path": request.path,
        "status": response.status_code,
        "duration": round(latency, 4)
    }
    app.logger.info(log_data)
    return response

@app.route("/")
def index():
    if random.random() < 0.1:
        return "Simulated error", 500
    return jsonify({"message": "Welcome to Service 1!"})

@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)
