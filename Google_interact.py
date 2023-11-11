import os
import gspread

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


def format_for_upload(data):
    for i in range(len(data)):
        data[i] = "".join(filter(lambda x: x != "[" and x != "]" and x != "'" and x != '"', str(data[i])))
    return data


def append_data_to_worksheet(data, sheet_name, page_index):
    # Open the spreadsheet by its title
    spreadsheet = gc.open(sheet_name)  # Replace with your spreadsheet name

    # Select the worksheet
    worksheet = spreadsheet.get_worksheet(page_index)  # Replace with the index of your desired worksheet

    # Find the next empty row
    next_row = len(worksheet.get_all_values()) + 1

    # Append the data as a new row
    worksheet.append_rows([data], value_input_option='USER_ENTERED', insert_data_option='INSERT_ROWS', table_range=f"A{next_row}")
