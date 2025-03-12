"""
Test script for the Billing V2 API
"""
import requests
import json
import sys
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000"  # Update this if different
API_ENDPOINT = "/billing-v2/reports/generate/"

# Authentication (token or session authentication as needed)
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer development_token"  # Update with actual token or auth method
}

# Test data
today = datetime.now()
start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
end_date = today.strftime("%Y-%m-%d")

test_data = {
    "customer_id": 1,  # Update with an actual customer ID
    "start_date": start_date,
    "end_date": end_date,
    "output_format": "json"
}

def test_generate_report():
    """Test the report generation endpoint"""
    
    url = BASE_URL + API_ENDPOINT
    print(f"Sending POST request to: {url}")
    print(f"Headers: {headers}")
    print(f"Data: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(
            url,
            headers=headers,
            json=test_data
        )
        
        print(f"Status Code: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
            
            # Check for expected response structure
            if "success" in response_data:
                print(f"Success: {response_data['success']}")
                
                if response_data.get("success"):
                    if "data" in response_data:
                        print("✅ Valid response with data")
                    else:
                        print("❌ Missing 'data' in successful response")
                else:
                    if "error" in response_data:
                        print(f"Error message: {response_data['error']}")
                    else:
                        print("❌ Missing 'error' in error response")
            else:
                print("❌ Response missing 'success' property")
                
        except ValueError:
            print("❌ Response is not valid JSON")
            print(f"Raw response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception making request: {str(e)}")
        
if __name__ == "__main__":
    test_generate_report()
