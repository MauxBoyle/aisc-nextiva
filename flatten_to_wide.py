import pandas as pd

# 1. Define the Agent Mapping
AGENT_MAP = {
    "4290": "reception",
    "5705": "subscriptions",
    "9999": "to VM",
    "3126707012": "Deidre",
    "3126705411": "Martin",
    "3126708315": "Dita",
    "3126705447": "Ed",
    "3126702401": "Mebership HG",
    "3126700319": "Garrett",
    "3126707520": "Cert Hunt Group",
    "3126707524": "Karla",
    "3126705444": "Leah",
    "3126707525": "Loren",
    "8662752472": "SSC",
    "3126707526": "Taylor",
    "3126705435": "Tye"
}

def get_agent_name(phone_val):
    phone_str = str(phone_val).strip()
    for num, name in AGENT_MAP.items():
        if phone_str.endswith(num):
            return name
    return "Other"

def flatten_to_wide():
    # Read the data we've been collecting
    df = pd.read_csv('NextivaCallData.csv')
    df['Time of Call'] = pd.to_datetime(df['Time of Call'], format='%m/%d/%y %I:%M %p', errors='coerce')
    
    # Sort chronologically to follow the call 'path'
    df = df.sort_values(['Time of Call'])

    flattened_rows = []
    current_call = None
    agent_names = list(set(AGENT_MAP.values())) + ["Other"]

    for _, row in df.iterrows():
        # Check if this row is a continuation of the previous row's call
        # (Same caller AND within 30 mins)
        is_same_caller = current_call and str(row['From']) == str(current_call['Caller_ID'])
        
        time_diff = 0
        if current_call:
            time_diff = (row['Time of Call'] - current_call['Last_Event_Time']).total_seconds() / 60
        
        if is_same_caller and time_diff < 30:
            # --- This is a 'Hop' or 'Transfer' within the same call ---
            agent_hit = get_agent_name(row['To'])
            
            # Record the status for this agent
            current_call[agent_hit] = row['Answered']
            
            # If this hop was the successful one, update the final call stats
            if row['Answered'] == 'Yes':
                current_call['Final_Answered'] = 'Yes'
                current_call['Total_Duration'] = row['Duration']
            
            current_call['Last_Event_Time'] = row['Time of Call']
            current_call['Hops'] += 1
            
        else:
            # --- This is a brand NEW call session ---
            if current_call:
                flattened_rows.append(current_call)
            
            new_call = {
                'Caller_ID': row['From'],
                'First_Destination': row['To'],
                'Start_Time': row['Time of Call'],
                'Last_Event_Time': row['Time of Call'],
                'Final_Answered': row['Answered'],
                'Total_Duration': row['Duration'],
                'Hops': 1,
                'Direction': row['Direction']
            }
            
            # Initialize all agent columns as empty
            for name in agent_names:
                new_call[name] = None
            
            # Mark the first agent's result
            agent_hit = get_agent_name(row['To'])
            new_call[agent_hit] = row['Answered']
            
            current_call = new_call

    # Add the last group
    if current_call:
        flattened_rows.append(current_call)

    # Save the 'Wide' table
    final_df = pd.DataFrame(flattened_rows)
    final_df.to_csv('Nextiva_Flattened_Wide.csv', index=False)
    print(f"Done! Flattened into {len(final_df)} unique call sessions.")

if __name__ == "__main__":
    flatten_to_wide()