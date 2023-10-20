# WORKING SCRIPT TO GET LIST OF ALL BACKENDS AND TIERS IN CONTROLLER USING REST API ON SAAS CONTROLLER!
import pandas as pd
import requests
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Replace with your AppDynamics controller info and API token
CONTROLLER_HOST = "<YOUR HOST HERE>"
CONTROLLER_PORT = 443
API_TOKEN = "<YOUR API TOKEN HERE>"
ACCOUNT_NAME = "<YOUR ACCOUNT NAME HERE>"
#YOUR LIST OF APPLICATION ID'S THAT YOU WOULD LIKE TO ITERATE OVER
APPLICATION_LIST = ["######", "#######"]

# LEAVE THE APPLICATION ID BLANK
APPLICATION_ID = ""


def make_api_request(application_id, endpoint):
    url = f"https://{CONTROLLER_HOST}:{CONTROLLER_PORT}/controller/rest/applications/{application_id}/{endpoint}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_TOKEN}"
    }
    params = {"output": "JSON"}

    try:
        response = requests.get(url, headers=headers,
                                params=params, verify=False)

        if response.status_code == 200:
            data = response.json()
            if endpoint == "backends":
                return [{"name": item['name'], "exitPointType": item['exitPointType']} for item in data]
            else:
                return [item['name'] for item in data]
        else:
            print(
                f"Failed to fetch {endpoint}. Status code: {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to the AppDynamics API: {e}")
        return None


def get_backends(application_id):
    return make_api_request(application_id, "backends")


def get_tiers(application_id):
    return make_api_request(application_id, "tiers")


# Create an empty DataFrame to store the data from all applications
all_data = pd.DataFrame(
    columns=["Application ID", "Backend Name", "Exit Point Type", "Tier"])


def save_all_to_excel(data, file_path):
    # Get the user's home directory
    home_dir = os.path.expanduser("~")

    # Construct the file path in the user's home directory
    file_path = os.path.join(home_dir, file_path)

    # Write the DataFrame to the Excel file with sorting enabled
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        data.to_excel(writer, sheet_name='Data', index=False)
        worksheet = writer.sheets['Data']

        # Add sorting options to the table
        worksheet.auto_filter.ref = worksheet.dimensions


if __name__ == "__main__":
    for application_id in APPLICATION_LIST:
        backends = get_backends(application_id)
        tiers = get_tiers(application_id)

        # print(f"Application ID: {application_id}")
        if backends:
            data = pd.DataFrame([{"Application ID": application_id, "Backend Name": backend['name'],
                                "Exit Point Type": backend['exitPointType'], "Tier": None} for backend in backends])
            all_data = pd.concat([all_data, data])
        if tiers:
            data = pd.DataFrame([{"Application ID": application_id, "Backend Name": None,
                                "Exit Point Type": None, "Tier": tier} for tier in tiers])
            all_data = pd.concat([all_data, data])

        print()

# Save all the combined data to a single Excel file with sorting enabled
if not all_data.empty:
    save_all_to_excel(all_data, "all_app_data.xlsx")
    print(f"Combined data saved to Excel in {os.path.expanduser('~')}.")
else:
    print("No data found")


# OLD CODE FOR PRINTING OUT THE DATA. DATA IS NOW STORED IN AN EXCE FILE USING PANDAS IN THE USER HOME DIRECTORY CALLED ALL APP DATA
    # for application_id in APPLICATION_LIST:
    #     backends = get_backends(application_id)
    #     tiers = get_tiers(application_id)

    # print(f"Application ID: {application_id}")
    # if backends:
    #     for backend in backends:
    #         print(
    #             f"Backend Name: {backend['name']} | Exit Point Type: {backend['exitPointType']}")
    # else:
    #     print("No backends found")

    # print(f"Tiers: {', '.join(tiers) if tiers else 'No tiers found'}")
    # print()
