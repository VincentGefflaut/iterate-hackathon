#!/usr/bin/env python3
"""
Interactive Demo Server

Provides a web interface for running the alerts pipeline on demand.
Perfect for demos and presentations.

Usage:
    python demo_server.py
    # Then open http://localhost:5000
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import subprocess
import json
from pathlib import Path
from datetime import datetime, timedelta
import threading
import time
import os

app = Flask(__name__)
CORS(app)

# Global state for pipeline execution
pipeline_status = {
    'running': False,
    'progress': 0,
    'step': '',
    'error': None,
    'last_run': None
}


def get_available_dates():
    """Get available dates from sales data or generate sample dates"""
    dates = []

    # Check if we have sales data
    sales_file = Path("data/input/Retail").glob("retail_sales_data_*.csv")

    try:
        # If we have real data, read the dates
        import pandas as pd
        for file in sales_file:
            df = pd.read_csv(file, encoding='utf-8-sig')
            if 'Transaction_Date' in df.columns:
                df['Transaction_Date'] = pd.to_datetime(df['Transaction_Date'])
                unique_dates = df['Transaction_Date'].dt.date.unique()
                dates.extend([d.isoformat() for d in unique_dates])
                break
    except Exception as e:
        print(f"⚠️  Could not read sales data: {e}")

    # If no real data, generate sample dates (last 30 days)
    if not dates:
        today = datetime.now().date()
        dates = [(today - timedelta(days=i)).isoformat() for i in range(30)]

    return sorted(dates, reverse=True)


def run_pipeline_async(target_date: str, use_real_data: bool, demo_mode: bool):
    """Run the pipeline in a background thread"""
    global pipeline_status

    pipeline_status['running'] = True
    pipeline_status['progress'] = 0
    pipeline_status['error'] = None
    pipeline_status['step'] = 'Initializing...'

    try:
        # Step 1: Build features (if using real data)
        if use_real_data and not demo_mode:
            pipeline_status['step'] = 'Building alert features...'
            pipeline_status['progress'] = 10
            result = subprocess.run(
                ['python', 'build_alert_features.py', '--date', target_date],
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode != 0:
                raise Exception(f"Feature building failed: {result.stderr}")

        # Step 2: Fetch news and detect events
        pipeline_status['step'] = 'Fetching news and detecting events...'
        pipeline_status['progress'] = 30

        if demo_mode:
            # Run test suite to generate demo events
            result = subprocess.run(
                ['python', 'test_data_integration.py'],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode != 0:
                raise Exception(f"Demo event generation failed: {result.stderr}")
        else:
            # Run real news alerts
            result = subprocess.run(
                ['python', 'run_news_alerts.py', '--max-articles', '20'],
                capture_output=True,
                text=True,
                timeout=180
            )
            if result.returncode != 0:
                raise Exception(f"News fetching failed: {result.stderr}")

        # Step 3: Context matching
        pipeline_status['step'] = 'Matching context and generating alerts...'
        pipeline_status['progress'] = 60

        cmd = ['python', 'run_context_matcher.py', '--date', target_date, '--no-llm']
        if use_real_data and not demo_mode:
            cmd.append('--use-real-data')

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode != 0:
            raise Exception(f"Context matching failed: {result.stderr}")

        # Step 4: Generate dashboard
        pipeline_status['step'] = 'Generating dashboard...'
        pipeline_status['progress'] = 90

        result = subprocess.run(
            ['python', 'morning_dashboard.py', '--days', '1'],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            raise Exception(f"Dashboard generation failed: {result.stderr}")

        # Complete
        pipeline_status['step'] = 'Complete!'
        pipeline_status['progress'] = 100
        pipeline_status['last_run'] = datetime.now().isoformat()
        time.sleep(1)  # Show complete message briefly

    except Exception as e:
        pipeline_status['error'] = str(e)
        pipeline_status['step'] = f'Error: {str(e)}'
    finally:
        pipeline_status['running'] = False


@app.route('/')
def index():
    """Serve the interactive demo dashboard"""
    return send_from_directory('.', 'demo_dashboard.html')


@app.route('/api/dates')
def api_dates():
    """Get available dates"""
    dates = get_available_dates()
    return jsonify({
        'dates': dates[:60],  # Limit to 60 days
        'count': len(dates)
    })


@app.route('/api/run', methods=['POST'])
def api_run():
    """Trigger pipeline run"""
    global pipeline_status

    if pipeline_status['running']:
        return jsonify({'error': 'Pipeline already running'}), 409

    data = request.json
    target_date = data.get('date')
    use_real_data = data.get('use_real_data', False)
    demo_mode = data.get('demo_mode', True)

    if not target_date:
        return jsonify({'error': 'Date is required'}), 400

    # Validate date format
    try:
        datetime.fromisoformat(target_date)
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    # Start pipeline in background thread
    thread = threading.Thread(
        target=run_pipeline_async,
        args=(target_date, use_real_data, demo_mode)
    )
    thread.daemon = True
    thread.start()

    return jsonify({
        'status': 'started',
        'date': target_date
    })


@app.route('/api/status')
def api_status():
    """Get pipeline status"""
    return jsonify(pipeline_status)


@app.route('/api/alerts')
def api_alerts():
    """Get current alerts"""
    alerts_dir = Path('data/alerts')
    alerts = []

    if alerts_dir.exists():
        for alert_file in sorted(alerts_dir.glob('alert_*.json'), reverse=True):
            try:
                with open(alert_file, 'r', encoding='utf-8') as f:
                    alert = json.load(f)
                    alerts.append(alert)
            except Exception as e:
                print(f"⚠️  Error loading {alert_file.name}: {e}")

    # Calculate statistics
    total = len(alerts)
    critical = sum(1 for a in alerts if a.get('severity') == 'critical')
    high = sum(1 for a in alerts if a.get('severity') == 'high')
    moderate = sum(1 for a in alerts if a.get('severity') == 'moderate')
    avg_confidence = sum(a.get('decision', {}).get('confidence', 0) for a in alerts) / total if total > 0 else 0

    locations = set()
    for alert in alerts:
        locations.update(alert.get('decision', {}).get('affected_locations', []))

    return jsonify({
        'alerts': alerts[:20],  # Limit to 20 most recent
        'stats': {
            'total': total,
            'critical': critical,
            'high': high,
            'moderate': moderate,
            'avg_confidence': avg_confidence,
            'locations': len(locations)
        }
    })


@app.route('/dashboard/<path:filename>')
def serve_dashboard(filename):
    """Serve generated dashboard files"""
    return send_from_directory('data/dashboard', filename)


def main():
    print("╔" + "="*78 + "╗")
    print("║" + " "*25 + "INTERACTIVE DEMO SERVER" + " "*30 + "║")
    print("╚" + "="*78 + "╝")
    print()
    print("🚀 Starting server...")
    print()
    print("📍 Server URL: http://localhost:5000")
    print("📊 Dashboard:  http://localhost:5000")
    print()
    print("💡 Press Ctrl+C to stop")
    print()

    # Check if demo_dashboard.html exists
    if not Path('demo_dashboard.html').exists():
        print("⚠️  demo_dashboard.html not found. Creating it now...")
        # Will be created by the next script

    app.run(host='0.0.0.0', port=5000, debug=False)


if __name__ == '__main__':
    main()
