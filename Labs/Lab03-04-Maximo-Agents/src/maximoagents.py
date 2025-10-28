from flask import Flask, request, jsonify
from dotenv import load_dotenv
from datetime import datetime, timedelta
import requests
import json
import os
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

MAXIMO_URL = os.getenv('MAXIMO_BASE_URL')  # Maximo URL from .env
API_KEY = os.getenv('API_KEY')        # API Key from .env

@app.route('/get-asset/<assetnum>', methods=['GET'])
def get_asset(assetnum):
    try:
        if not assetnum:
            return jsonify({"error": "Asset number is required"}), 400

        # Build full URL with query parameters
        url = f"{MAXIMO_URL}/maximo/api/os/MXAPIASSET"
        params = {
        "lean": "1",
        "oslc.where": f'assetnum="{assetnum}"',
        "oslc.select": (
            "assetnum,description,status,installdate,replacecost,assethealth,"
            "ahhealthtrendvalue,ahhealthtrenddirection,lastcalcdate,lastcalctime,"
            "priority,location.location,siteid,"
            "apm_scorecriticality.apmnumval,apm_scorecriticality.scoretrendvalue,apm_scorecriticality.scoretrenddirection,"
            "apm_scoreeol.apmnumval,apm_scoreeol.scoretrendvalue,apm_scoreeol.scoretrenddirection,"
            "apm_scoreMTBF.apmnumval,apm_scoreMTBF.scoretrendvalue,apm_scoreMTBF.scoretrenddirection,"
            "apm_scoreeffectiveage.apmnumval"
        )
        }

        headers = {
            "Accept": "application/json",
            "apikey": API_KEY
        }

        logger.debug(f"Requesting asset info from Maximo: assetnum={assetnum}")

        response = requests.get(url, headers=headers, params=params, verify=False)

        logger.debug(f"Maximo response status: {response.status_code}")

        if response.status_code == 200:
            try:
                data = response.json()
                logger.debug(f"JSON response data: {json.dumps(data, indent=2)}")
                return jsonify(data), 200
            except ValueError:
                logger.error(f"Invalid JSON. Response text: {response.text}")
                return jsonify({
                "error": "Invalid JSON response from Maximo",
                "details": response.text or "No response body"
                }), 500

        else:
            try:
                error_response = response.json()
            except ValueError:
                error_response = response.text
            return jsonify({"error": "Failed to fetch asset", "details": error_response}), response.status_code

    except Exception as e:
        logger.error(f"Exception occurred while fetching asset: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/get_asset_health_by_siteid/<siteid>', methods=['GET'])
def get_asset_health_by_siteid(siteid):
    try:
        if not siteid:
            return jsonify({"error": "Site ID is required"}), 400

        # Build full URL with query parameters
        url = f"{MAXIMO_URL}/maximo/api/os/MXAPIASSET"
        params = {
            "lean": "1",
            "oslc.where": f'siteid="{siteid}"',
            "oslc.select": (
                "assetnum,description,status,installdate,replacecost,assethealth,"
                "ahhealthtrendvalue,ahhealthtrenddirection,lastcalcdate,lastcalctime,"
                "priority,location.location,siteid,"
                "apm_scorecriticality.apmnumval,apm_scorecriticality.scoretrendvalue,apm_scorecriticality.scoretrenddirection,"
                "apm_scoreeol.apmnumval,apm_scoreeol.scoretrendvalue,apm_scoreeol.scoretrenddirection,"
                "apm_scoreMTBF.apmnumval,apm_scoreMTBF.scoretrendvalue,apm_scoreMTBF.scoretrenddirection,"
                "apm_scoreeffectiveage.apmnumval"
            ),
            "oslc.pageSize": "10"
        }

        headers = {
            "Accept": "application/json",
            "apikey": API_KEY
        }

        logger.debug(f"Requesting asset info from Maximo for siteid={siteid}")
        response = requests.get(url, headers=headers, params=params, verify=False)

        logger.debug(f"Maximo response status: {response.status_code}")

        if response.status_code == 200:
            try:
                data = response.json()
                logger.debug(f"JSON response data: {json.dumps(data, indent=2)}")
                return jsonify(data), 200
            except ValueError:
                logger.error(f"Invalid JSON. Response text: {response.text}")
                return jsonify({
                    "error": "Invalid JSON response from Maximo",
                    "details": response.text or "No response body"
                }), 500
        else:
            try:
                error_response = response.json()
            except ValueError:
                error_response = response.text
            return jsonify({"error": "Failed to fetch asset", "details": error_response}), response.status_code

    except Exception as e:
        logger.error(f"Exception occurred while fetching assets: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)