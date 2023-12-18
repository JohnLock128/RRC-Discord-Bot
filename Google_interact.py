import os
import gspread
import csv
from datetime import datetime

# Get the path of the current script
script_path = os.path.dirname(os.path.abspath(__file__))

# Construct the relative path to the JSON file
json_filename = "empirical-envoy-402616-355b694e8dcf.json"
json_keyfile_path = os.path.join(script_path, json_filename)

if os.path.exists(json_keyfile_path):
    gc = gspread.service_account(filename=json_keyfile_path)
else:
    print("No valid credentials found. Exiting...")
    exit()


def update_google_sheet_from_csv(sheet_name, page_index):
    # Construct the path to the CSV file
    csv_file_path = os.path.join(script_path, "data.csv")

    # Read data from CSV file
    with open(csv_file_path, 'r') as csv_file:
        data = list(csv.reader(csv_file))

    # Open the spreadsheet by its title
    spreadsheet = gc.open(sheet_name)  # Replace with your spreadsheet name

    # Select the worksheet
    worksheet = spreadsheet.get_worksheet(page_index)  # Replace with the index of your desired worksheet

    # Clear existing data in the worksheet
    worksheet.clear()

    # Append the data as new rows
    worksheet.append_rows(data, value_input_option='USER_ENTERED', insert_data_option='INSERT_ROWS', table_range="A1")


def backup_csv_file():
    # Construct the path to the CSV file
    csv_file_path = os.path.join(script_path, "data.csv")

    # Read data from CSV file
    with open(csv_file_path, 'r') as csv_file:
        data = list(csv.reader(csv_file))

    # Construct the path to the backup folder
    backup_folder_path = os.path.join(script_path, "Data_backups")

    # Create the backup folder if it doesn't exist
    os.makedirs(backup_folder_path, exist_ok=True)

    # Construct the backup file name with the format "dataMM_DD.csv"
    backup_file_name = f"Data{datetime.now().strftime('%m_%d')}.csv"
    backup_file_path = os.path.join(backup_folder_path, backup_file_name)

    # Write data to the backup file
    with open(backup_file_path, 'w', newline='') as backup_file:
        csv.writer(backup_file).writerows(data)


# Call the functions to update Google Sheets data and create a backup
update_google_sheet_from_csv("RPI Robotics Full Member List", 0)  # Replace with your spreadsheet name and worksheet index
backup_csv_file()
