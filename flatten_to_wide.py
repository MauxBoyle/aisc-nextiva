import pandas as pd
import re

# 1. Define the Agent Mapping (The Global Bulletin Board)
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

def clean_id(val):
    """Removes all non-numeric characters so +1(312) becomes 1312"""
    return re.sub(r'\D', '', str(val))

def get_agent_name(phone_val):
    """Matches the end of the phone string to our AGENT_MAP"""
    phone_str = str(phone_val).strip()
    for num, name in AGENT_MAP.items():
        if phone_str.endswith(num):
            return name
    return "Other"

def flatten_to_wide():
    # Load and clean the data
    df = pd.read_csv('NextivaCallData.csv')
    print(f"Total rows found in CSV: {len(df)}") # DIAGNOSTIC 1
    
    # Parse dates with the explicit format to avoid warnings
    #df['Time of Call'] = pd.to_datetime(df['Time of Call'], format='%m/%d/%y %I:%M %S %p', errors='coerce')
    
    # 1. Use flexible parsing (remove the 'format' argument)
    df['Time of Call'] = pd.to_datetime(df['Time of Call'], format='%m/%d/%y %I:%M:%S %p', errors='coerce')
    
    # 2. Add a print here to see if it worked
    valid_dates = df['Time of Call'].notnull().sum()
    print(f"Successfully parsed {valid_dates} out of {len(df)} dates.")

    # 3. Only then drop the failures
    df = df.dropna(subset=['Time of Call']).sort_values(by=['Time of Call']).reset_index(drop=True)

    # Drop any rows that failed to parse and sort by time
    df = df.dropna(subset=['Time of Call']).sort_values(by=['Time of Call']).reset_index(drop=True)

    active_calls = {}  # Tracks calls currently "in progress"
    final_sessions = []
    agent_names = list(set(AGENT_MAP.values())) + ["Other"]

    for _, row in df.iterrows():
        # NORMALIZATION: Clean the number immediately as it enters the loop
        phone_id = clean_id(row['From'])
        
        # Look for an existing call from this specific number
        existing_call = active_calls.get(phone_id)
        
        is_continuation = False
        if existing_call:
            # If the same number called within the last 30 minutes, it's the same session
            gap = (row['Time of Call'] - existing_call['Last_Event_Time']).total_seconds()
            if 0 <= gap <= 1800:
                is_continuation = True

        if is_continuation:
            # --- Update existing session ---
            agent_hit = get_agent_name(row['To'])
            existing_call[agent_hit] = row['Answered']
            existing_call['Last_Event_Time'] = row['Time of Call']
            existing_call['Hops'] += 1
            
            # Use 'startswith' to catch "Yes", "Yes - Forwarded", etc.
            if str(row['Answered']).startswith('Yes'):
                existing_call['Final_Answered'] = row['Answered']
                existing_call['Total_Duration'] = row['Duration']
            else:
                # If it's not a 'Yes', we still update status to see where it 'Leaked'
                existing_call['Final_Answered'] = row['Answered']
        else:
            # --- Start a brand new session ---
            # If there was a previous call from this number that finished/timed out, save it first
            if existing_call:
                final_sessions.append(existing_call)
            
            new_call = {
                'Caller_ID': row['From'], # Store original for display
                'Phone_Key': phone_id,    # Store cleaned for matching
                'Start_Time': row['Time of Call'],
                'Last_Event_Time': row['Time of Call'],
                'Final_Answered': row['Answered'],
                'Total_Duration': row['Duration'],
                'Hops': 1,
                'Direction': row['Direction']
            }
            # Initialize all agent columns to None
            for name in agent_names:
                new_call[name] = None
                
            # Log the first agent attempt
            agent_hit = get_agent_name(row['To'])
            new_call[agent_hit] = row['Answered']
            
            # Put it in the 'Active' bucket
            active_calls[phone_id] = new_call

    # Move all remaining active calls into the final list
    for call in active_calls.values():
        final_sessions.append(call)

    # 4. Save and export
    if final_sessions:
        final_df = pd.DataFrame(final_sessions)
        # Drop the helper key before saving to keep the CSV clean
        final_df = final_df.drop(columns=['Phone_Key'])
        # Sort by Start Time so the CSV is chronological
        final_df = final_df.sort_values(by=['Start_Time'])
        
        final_df.to_csv('Nextiva_Flattened_Wide.csv', index=False)
        print(f"Success! Flattened into {len(final_df)} unique call sessions.")
    else:
        print("No data found to flatten.")

if __name__ == "__main__":
    flatten_to_wide()
    