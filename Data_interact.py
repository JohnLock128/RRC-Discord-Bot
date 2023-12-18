import csv

filename = "Data.csv"


def add_data(data):
    # Read the existing data from the CSV file
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        rows = list(reader)

    # Find the index where the new data should be inserted
    insert_index = 0
    for index, row in enumerate(rows[1:], 1):  # Start from index 1 to skip the header
        if int(row[0]) > int(data[0]):  # Assuming the first column contains integers
            break
        insert_index = index

    # Insert the new data at the determined index
    rows.insert(insert_index + 1, data)

    # Write the updated data back to the CSV file
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)


def get_data(user_id, index=False):
    # Read the existing data from the CSV file
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        rows = list(reader)

    # Search for the target value in the first column
    i = 0
    for row in rows[1:]:  # Start from index 1 to skip the header
        i += 1
        if int(row[0]) == user_id:  # Assuming the first column contains integers
            if index:
                return i
            else:
                return row

    # Return False if the target value is not found
    return False


def rem_data(user_id):
    # Read the existing data from the CSV file
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        rows = list(reader)

    # Find the index of the row with the target value in the first column
    index_to_remove = None
    for index, row in enumerate(rows[1:]):  # Start from index 1 to skip the header
        if int(row[0]) == user_id:  # Assuming the first column contains integers
            index_to_remove = index + 1
            break

    del rows[index_to_remove]

    # Write the updated data back to the CSV file
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)


def data_validate(user_id):
    data = get_data(user_id)
    valid = [False, False, False, False, False, False, False, False, False]
    invalid = []
    for i in range(len(data)):
        if data[i] != '':
            valid[i] = True
        elif i == 4 and data[3] == "Alumni":
            valid[i] = True
        elif i == 6 and data[3] == "Faculty/Staff":
            valid[i] = True

        if not valid[i]:
            invalid.append(i)

    if invalid == []:
        return True
    else:
        return invalid


def get_headers():
    # Read the header row from the CSV file
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        headers = next(reader)  # Get the first row (header)

    return headers


def unique_on_col(value, column_index, ignore_row_index=None):
    # Read the existing data from the CSV file
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        rows = list(reader)

    if value != "":
        # Check if the value is unique in the specified column
        for index, row in enumerate(rows[1:], 1):  # Start from index 1 to skip the header
            if index == ignore_row_index:
                continue  # Skip checking in the specified row index

            if row[column_index] == str(value):
                return False  # Value is not unique

    return True  # Value is unique


def data_update(updated_data):
    # Read the existing data from the CSV file
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        rows = list(reader)

    # Find the index of the row with the matching first column
    index_to_update = None
    for index, row in enumerate(rows[1:]):  # Start from index 1 to skip the header
        if int(row[0]) == updated_data[0]:  # Assuming the first column contains integers
            index_to_update = index + 1
            break

    # Update the row if a matching row is found
    if index_to_update is not None:
        rows[index_to_update] = updated_data

        # Write the updated data back to the CSV file
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)
