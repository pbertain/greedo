#!/usr/bin/env python3
"""
Gree.do - Star Wars Holonet Timestamp Web Service

A Flask web application that serves both a dynamic webpage and API endpoints
for Star Wars-themed timestamp data.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

# Add the holonet-stamp directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'holonet-stamp'))

from holonet_stamp_module import build_payload, _now_utc, _fetch_quote, _final_request_id
from sw_time import datetime_to_swet, datetime_to_cgt, format_cgt, bby_to_gsc

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'greedo-secret-key')
DEFAULT_TZ = "America/Los_Angeles"

class DummyArgs:
    """Dummy args class to work with holonet_stamp functions"""
    def __init__(self, json_mode=False, quiet=False, one_line=False):
        self.json = json_mode
        self.quiet = quiet
        self.one_line = one_line
        self.request_id = None
        self.request_id_mode = "uuid"
        self.rid_prefix = None

def get_timestamp_data(include_quote=True):
    """Generate timestamp data using holonet-stamp functionality"""
    now_utc = _now_utc()
    
    # Generate request ID
    args = DummyArgs(json_mode=True)
    request_id = _final_request_id(args)
    
    # Fetch quote if requested
    quote = None
    if include_quote:
        quote = _fetch_quote(
            "http://swquotesapi.digitaljedi.dk/api/SWQuote/RandomStarWarsQuote",
            request_id,
            timeout_s=2.0
        )
    
    # Build the payload
    payload = build_payload(
        now_utc=now_utc,
        tz_name=DEFAULT_TZ,
        include_sw=True,
        epoch_mode="current",
        request_id=request_id,
        quote=quote
    )
    
    return payload

def format_text_response(payload):
    """Format the payload as text for the cURL endpoint"""
    dt_utc = datetime.fromisoformat(payload["time"]["utc"].replace("Z", "+00:00"))
    dt_local = datetime.fromisoformat(payload["time"]["local"])
    unix = payload["unix"]
    
    lines = [
        f"Fact: {payload['fact']}"
    ]
    
    if "quote" in payload and payload["quote"]:
        lines.append(f"Rando Factissian: {payload['quote']}")
    
    lines.extend([
        "",
        "Real Time:",
        f"  UTC   : {dt_utc:%a %Y-%m-%d %H:%M:%S}",
        f"  Local : {dt_local:%a %Y-%m-%d %H:%M:%S} {dt_local:%Z}",
        "",
        "Unix Epoch:",
        f"  Unix  : {unix}",
    ])
    
    if "sw" in payload:
        sw = payload["sw"]
        lines.extend([
            "",
            "Star Wars Time:",
            f"  SWET  : {sw['swet']}",
            f"  CGT   : {sw['cgt_str']}",
            f"  GSC   : {sw['gsc_year']}"
        ])
    
    return "\n".join(lines)

# Routes
@app.route('/')
def index():
    """Main webpage with dynamic content"""
    return render_template('index.html')

@app.route('/api/v1/greedo')
def api_greedo():
    """JSON API endpoint"""
    try:
        data = get_timestamp_data(include_quote=True)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/curl/v1/greedo')
def curl_greedo():
    """Text-based cURL endpoint"""
    try:
        data = get_timestamp_data(include_quote=True)
        return format_text_response(data), 200, {'Content-Type': 'text/plain'}
    except Exception as e:
        return f"Error: {str(e)}", 500, {'Content-Type': 'text/plain'}

@app.route('/health')
def health_check():
    """Health check endpoint with detailed system information"""
    return render_template('health.html')

@app.route('/about')
def about():
    """About page with SWET information"""
    return render_template('about.html')

@app.route('/api/health')
def api_health():
    """API health check with JSON response"""
    now_utc = _now_utc()
    
    health_data = {
        "status": "healthy",
        "timestamp": now_utc.isoformat(),
        "version": "1.0.0",
        "service": "gree.do",
        "endpoints": {
            "/api/v1/greedo": "JSON timestamp data",
            "/curl/v1/greedo": "Text timestamp data", 
            "/health": "Health check page",
            "/about": "About SWET and Star Wars time"
        },
        "fact": "Han shot first."
    }
    
    return jsonify(health_data)

@app.route('/docs')
def swagger_docs():
    """Swagger/OpenAPI documentation"""
    return render_template('docs.html')

@app.route('/redoc')
def redoc_docs():
    """ReDoc API documentation"""
    return render_template('redoc.html')

@app.route('/openapi.json')
def openapi_spec():
    """OpenAPI specification"""
    spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "Gree.do API",
            "description": "Star Wars Holonet Timestamp System API",
            "version": "1.0.0",
            "contact": {
                "name": "Gree.do",
                "url": "https://github.com/pbertain/greedo"
            }
        },
        "servers": [
            {"url": request.url_root.rstrip('/'), "description": "Current server"}
        ],
        "paths": {
            "/api/v1/greedo": {
                "get": {
                    "summary": "Get timestamp data (JSON)",
                    "description": "Returns current timestamp data in JSON format with Star Wars time systems",
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "fact": {"type": "string"},
                                            "quote": {"type": "string"},
                                            "time": {
                                                "type": "object",
                                                "properties": {
                                                    "utc": {"type": "string"},
                                                    "local": {"type": "string"},
                                                    "tz": {"type": "string"}
                                                }
                                            },
                                            "unix": {"type": "integer"},
                                            "sw": {
                                                "type": "object",
                                                "properties": {
                                                    "swet": {"type": "integer"},
                                                    "cgt_str": {"type": "string"},
                                                    "gsc_year": {"type": "integer"}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/curl/v1/greedo": {
                "get": {
                    "summary": "Get timestamp data (Text)",
                    "description": "Returns current timestamp data in plain text format for cURL usage",
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "text/plain": {
                                    "schema": {
                                        "type": "string"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    return jsonify(spec)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)