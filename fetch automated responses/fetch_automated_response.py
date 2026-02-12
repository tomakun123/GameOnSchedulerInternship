import os
import requests
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

ATLAS_API_KEY = os.getenv("ATLAS_API_KEY")

def find_automated_word(api_key, id):
    
    headers = {
                "api-key": api_key,
                "Content-Type": "application/json"
            }
        
    try:

        url = f"https://api.youratlas.com/v1/api/call/{id}"

        response = requests.get(url, headers=headers)
        
        # raise exception for failed request
        response.raise_for_status()
        
        data = response.json()
        
        summary = data.get('summary', "").lower()
        
        # extracting call IDs where summary key words indicate an automated response
        if summary == "" or any(word in summary for word in ["voicemail", "automated", "transfer"]):
            return id

            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for automated responses: {e}")
        return None
    
    

def fetch_automated_ids(api_key, campaign_id):
    url = "https://api.youratlas.com/v1/api/call"
    
    # Headers for authentication
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }
    
    # Query parameters to filter by your specific campaign
    params = {
        "campaignId": campaign_id
    }
    
    automated_responses = []

    try:
        response = requests.get(url, headers=headers, params=params)
        
        # Raise an exception if the request failed (e.g., 401 Unauthorized)
        response.raise_for_status()
        
        data = response.json()
                
        # Extract the rowKey from each record in the 'value' list
        for record in data.get('value', []):
            call_id = record.get('rowKey')
            found_call_id = find_automated_word(api_key, call_id)
            if found_call_id:
                automated_responses.append(found_call_id)
        
        return automated_responses

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return []


    
MY_CAMPAIGN_ID = "2d68e99e-d4aa-48d2-b295-c2134f2b5502"
automated_response_ids = fetch_automated_ids(ATLAS_API_KEY, MY_CAMPAIGN_ID)
print("Automated Response Call IDs:", automated_response_ids)


# exporting data to txt file
def export_to_txt(data_list, folder_name="fetch automated responses", filename="automated_call_ids.txt"):
    
    output_dir = Path(folder_name)
    file_path = output_dir / filename
    
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(f"Total Automated Response IDs: {len(data_list)}\n")

            for call_id in data_list:
                file.write(f"{call_id}\n")
                
        print(f"Successfully saved IDs to {file_path}")
        
    except Exception as e:
        print(f"Error writing to TXT: {e}")
        
export_to_txt(automated_response_ids)