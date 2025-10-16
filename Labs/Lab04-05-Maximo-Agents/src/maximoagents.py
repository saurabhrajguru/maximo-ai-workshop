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

today = datetime.strptime("2025-05-23", "%Y-%m-%d")

asset_data = [
    {
        "asset_number": "11430",
        "description": "Boiler- 50,000 Lb/Hr/ Gas Fired/ Water Tube",
        "predicted_failure_date": (today + timedelta(weeks=8)).strftime("%Y-%m-%d"),
        "weeks_to_failure": 8,
        "time_to_failure": "56 days",
        "predicted_remaining_life": "56 days",
        "end_of_life_score": 45,
        "last_prediction_date": today.strftime("%Y-%m-%d"),
        "prediction_method": "DEFAULTRISK",
        "repair_cost": "$50,000",
        "replacement_cost": "$120,000",
        "historical_failures": 3,
        "work_orders": [
            {"wo_id": "WO-20145", "date": "2025-05-01", "type": "Corrective", "issue": "Steam leakage in upper drum"},
            {"wo_id": "WO-19877", "date": "2025-04-10", "type": "Corrective", "issue": "Burner control fault - intermittent ignition"},
        ],
        "preventive_maintenance": [
            {"pm_id": "PM-9001", "task": "Annual Hydrostatic Pressure Test", "scheduled_date": "2025-03-20", "actual_date": "2025-03-21", "status": "Completed On Time"},
            {"pm_id": "PM-8990", "task": "Safety Valve Calibration", "scheduled_date": "2025-01-10", "actual_date": "2025-01-15", "status": "Completed Late"}
        ]
    },
    {
        "asset_number": "26200",
        "description": "Motor Controlled Valve",
        "predicted_failure_date": (today + timedelta(weeks=12)).strftime("%Y-%m-%d"),
        "weeks_to_failure": 12,
        "time_to_failure": "84 days",
        "predicted_remaining_life": "84 days",
        "end_of_life_score": 42,
        "last_prediction_date": today.strftime("%Y-%m-%d"),
        "prediction_method": "DEFAULTRISK",
        "repair_cost": "$3,000",
        "replacement_cost": "$7,000",
        "historical_failures": 5,
        "work_orders": [
            {"wo_id": "WO-20088", "date": "2025-04-18", "type": "Corrective", "issue": "Actuator failed to close valve"},
            {"wo_id": "WO-19991", "date": "2025-03-29", "type": "Corrective", "issue": "Valve stuck due to sediment buildup"}
        ],
        "preventive_maintenance": [
            {"pm_id": "PM-8855", "task": "Valve Positioner Calibration", "scheduled_date": "2025-03-01", "actual_date": "2025-03-03", "status": "Completed Late"},
            {"pm_id": "PM-8799", "task": "Seal Inspection and Replacement", "scheduled_date": "2025-01-15", "actual_date": "2025-01-15", "status": "Completed On Time"}
        ]
    },
    {
        "asset_number": "13144",
        "alias": "CNC-011",
        "description": "Carton Escapement Assembly #1",
        "predicted_failure_date": (today + timedelta(weeks=6)).strftime("%Y-%m-%d"),
        "weeks_to_failure": 6,
        "time_to_failure": "42 days",
        "predicted_remaining_life": "42 days",
        "end_of_life_score": 48,
        "last_prediction_date": today.strftime("%Y-%m-%d"),
        "prediction_method": "DEFAULTRISK",
        "repair_cost": "$1,500",
        "replacement_cost": "$4,000",
        "historical_failures": 4,
        "work_orders": [
            {"wo_id": "WO-10233", "date": "2025-05-14", "type": "Corrective", "issue": "Overheating during high load operation"},
            {"wo_id": "WO-10217", "date": "2025-05-08", "type": "Corrective", "issue": "Coolant pressure low - emergency stop triggered"},
            {"wo_id": "WO-10198", "date": "2025-05-02", "type": "Corrective", "issue": "Coolant system blocked - heat sensor warning"},
            {"wo_id": "WO-10185", "date": "2025-04-28", "type": "Corrective", "issue": "Overheating at startup - thermal fuse replaced"}
        ],
        "preventive_maintenance": [
            {"pm_id": "PM-7890", "task": "Coolant System Flush & Filter Replacement", "scheduled_date": "2025-03-01", "actual_date": "2025-05-01", "status": "Completed Late"},
            {"pm_id": "PM-7742", "task": "Spindle Alignment & Vibration Check", "scheduled_date": "2025-02-01", "actual_date": "2025-02-01", "status": "Completed On Time"}
        ]
    },
    {
        "asset_number": "11500",
        "description": "Filler And Lifter System",
        "predicted_failure_date": (today + timedelta(weeks=4)).strftime("%Y-%m-%d"),
        "weeks_to_failure": 4,
        "time_to_failure": "28 days",
        "predicted_remaining_life": "28 days",
        "end_of_life_score": 50,
        "last_prediction_date": today.strftime("%Y-%m-%d"),
        "prediction_method": "DEFAULTRISK",
        "repair_cost": "$4,500",
        "replacement_cost": "$9,000",
        "historical_failures": 4,
        "work_orders": [
            {"wo_id": "WO-19734", "date": "2025-04-05", "type": "Corrective", "issue": "Hydraulic cylinder failure"},
            {"wo_id": "WO-19680", "date": "2025-03-22", "type": "Corrective", "issue": "Sensor misalignment"}
        ],
        "preventive_maintenance": [
            {"pm_id": "PM-8611", "task": "Hydraulic Oil Change", "scheduled_date": "2025-02-25", "actual_date": "2025-02-26", "status": "Completed Late"},
            {"pm_id": "PM-8509", "task": "Sensor Calibration", "scheduled_date": "2025-01-20", "actual_date": "2025-01-20", "status": "Completed On Time"}
        ]
    }
]

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
    
@app.route('/get_asset_predict_data/<asset_number>', methods=['GET'])
def get_asset_predict_data(asset_number):
    try:
        logger.debug(f"Fetching predictive data for asset: {asset_number}")

        result = next(
            (asset for asset in asset_data if asset["asset_number"] == asset_number or asset.get("alias") == asset_number),
            None
        )

        if result:
            return jsonify(result), 200
        else:
            return jsonify({"error": f"Asset '{asset_number}' not found"}), 404

    except Exception as e:
        logger.error(f"Exception while processing request: {e}", exc_info=True)
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)