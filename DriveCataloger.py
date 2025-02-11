import os
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# CONFIGURATION VARIABLES
trial_name = 'ay7'                                                  # Specifies the name of the current trial being cataloged
start_row = 384                                                     # Indicates the starting row in the Google Sheet for data entry
name_of_sheet = 'HDD Catalog 1-30-24'                               # Name of the Google Sheet where data will be uploaded
path_of_drive = '/Volumes'                                          # Root path of the mounted drive to be scanned
path_on_drive = '/Untitled/turing_backup_ACUTE/' + trial_name       # Specific path within the drive related to 'trial_name'
path_to_catalog = path_of_drive + path_on_drive                     # Full path combining drive and specific trial paths
path_of_credentials = '/Users/gorislab/Downloads/sheets_creds.json' # Location of the Google Sheets API credentials file

def extract_identifier(filename):
    # Use regex to extract the identifier pattern 'xxx_xxx'
    match = re.search(r'(\d{3}_\d{3})', filename)
    return match.group(1) if match else None

def scan_files(startpath):
    # Dictionary to hold the presence of each file type for each identifier
    file_presence = {}
    paths = [path_to_catalog + '/AnalyzerFiles', path_to_catalog + '/logFiles', path_to_catalog + '/recordings']
    
    for path in paths:
        for root, dirs, files in os.walk(path):
            print(root)
            for f in files:
                identifier = extract_identifier(f)
                if identifier:
                    if identifier not in file_presence:
                        # Initialize a dictionary for this identifier
                        file_presence[identifier] = {
                            '.analyzer': False, 
                            '.mat': False, 
                            '.cache': False, 
                            '.nev': False, 
                            '.ns2': False, 
                            '.ns5': False
                        }

                    # Check and update the file type presence
                    _, ext = os.path.splitext(f)
                    if ext in file_presence[identifier]:
                        file_presence[identifier][ext] = True
    
    return file_presence

# Create dictionary to hold the presence of different file types (e.g. .analyzer, .mat...) for each trial (e.g. ay3_001_002)
file_presence = scan_files(path_to_catalog)

# Convert the dictionary to a list of lists for uploading to Google Sheets and sort it by the trial name
file_list = [[id] + list(presence.values()) for id, presence in file_presence.items()]
file_list.sort(key=lambda x: x[0])

# Add trial name and path to file details
for file in file_list:
    file[0] = trial_name + "_" + file[0]
    file.append(path_on_drive)

# Upload the file details to a Google Sheet with a given batch size
def upload_to_sheet(sheet, data, batch_size=100):
    for start in range(0, len(data), batch_size):
        end = start + batch_size
        batch = data[start:end]
        
        # Calculate the range considering the start_row offset
        range_start = start + start_row
        range_end = range_start + len(batch) - 1

        range_str = f'A{range_start}:H{range_end}'
        sheet.update(range_name=range_str, values=batch)
        print(f"Uploaded rows {range_start} to {range_end}")

# Set up Google Sheets connection
scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(path_of_credentials, scope)
client = gspread.authorize(creds)

# Open the Google Sheet
sheet = client.open(name_of_sheet).sheet1

# Batch update
upload_to_sheet(sheet, file_list)

print("Data upload complete.")