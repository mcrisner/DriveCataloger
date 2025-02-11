# DriveCataloger
Python script for cataloging experimental data files across directories and uploading records to Google Sheets.

## Prerequisites
Python 3.x: Ensure you have the latest version installed.

### Required Libraries:
os: For interacting with the operating system.\
re: For regular expression operations.\
gspread: For Google Sheets API interactions.\
oauth2client.service_account: For authenticating with Google APIs.

## Notes
The script will scan directories, extract file identifiers, and upload data to Google Sheets in batches of 100 rows.
