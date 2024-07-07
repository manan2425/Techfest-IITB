from flask import Flask, request, render_template, send_file
import pandas as pd
from io import BytesIO

app = Flask(__name__)

# Global variable to store the allocation DataFrame
allocation_df_global = None

# Route for the index page
@app.route('/', methods=['GET', 'POST'])
def index():
    global allocation_df_global
    if request.method == 'POST':
        # Get the uploaded CSV files
        group_csv = request.files['group_csv']
        hostel_csv = request.files['hostel_csv']

        # Read the CSV files into DataFrames
        group_df = pd.read_csv(group_csv)
        hostel_df = pd.read_csv(hostel_csv)

        # Perform room allocation
        allocation_df = allocate_rooms(group_df, hostel_df)
        allocation_df_global = allocation_df

        # Render the allocation template with the allocation table
        return render_template('allocation.html', tables=[allocation_df.to_html(classes='data')])

    # Render the index template for GET requests
    return render_template('index.html')

# Function to allocate rooms based on group and hostel data
def allocate_rooms(group_df, hostel_df):
    # Create an empty DataFrame for the allocation
    allocation_df = pd.DataFrame(columns=['Group ID', 'Hostel Name', 'Room Number', 'Members Allocated'])

    # Iterate over each group
    for index, group in group_df.iterrows():
        # Find a suitable hostel room for the group
        hostel_room = find_suitable_hostel_room(group, hostel_df)
        if hostel_room is not None:
            # Create a new row for the allocation DataFrame
            new_row = pd.DataFrame({
                'Group ID': [group['Group ID']],
                'Hostel Name': [hostel_room['Hostel Name']],
                'Room Number': [hostel_room['Room Number']],
                'Members Allocated': [group['Members']]
            })
            # Add the new row to the allocation DataFrame
            allocation_df = pd.concat([allocation_df, new_row], ignore_index=True)

    return allocation_df

# Function to find a suitable hostel room for a group
def find_suitable_hostel_room(group, hostel_df):
    # Filter the hostel DataFrame to find rooms that match the group's gender and have sufficient capacity
    filtered_hostel_df = hostel_df[(hostel_df['Gender'] == group['Gender']) & (hostel_df['Capacity'] >= group['Members'])]
    # Sort the filtered DataFrame by capacity
    filtered_hostel_df = filtered_hostel_df.sort_values(by='Capacity')
    # Return the first suitable room, or None if no suitable room is found
    return filtered_hostel_df.iloc[0] if not filtered_hostel_df.empty else None

# Route to download the allocation data as a CSV file
@app.route('/download_allocation', methods=['GET'])
def download_allocation():
    global allocation_df_global
    if allocation_df_global is None:
        # Return an error message if no allocation data is available
        return "No allocation data available. Please go back and upload the files first.", 400

    # Create a buffer to hold the CSV data
    csv_buffer = BytesIO()
    # Write the allocation DataFrame to the buffer
    allocation_df_global.to_csv(csv_buffer, index=False)
    # Seek to the start of the buffer
    csv_buffer.seek(0)

    # Send the buffer as a file attachment
    return send_file(csv_buffer, as_attachment=True, download_name='final.csv', mimetype='text/csv')

if __name__ == '__main__':
    # Run the Flask app in debug mode
    app.run(debug=True)
