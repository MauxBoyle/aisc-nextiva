import pandas as pd

def remove_duplicates():
    # Load the data
    df = pd.read_csv('NextivaCallData.csv')
    
    # Count rows before
    before = len(df)
    
    # Remove duplicates
    df.drop_duplicates(inplace=True)
    
    # Save back to CSV
    df.to_csv('NextivaCallData.csv', index=False)
    
    after = len(df)
    print(f"Cleaned! Removed {before - after} duplicate rows.")

if __name__ == "__main__":
    # You might need to: pip install pandas
    remove_duplicates()