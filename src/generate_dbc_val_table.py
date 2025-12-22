#!/usr/bin/env python3
"""
Generate DBC VAL_TABLE_ format from DTC CSV files
"""
import pandas as pd
import sys
import os

def csv_to_dbc_val_table(csv_file, table_name="DTC"):
    """Convert DTC CSV to DBC VAL_TABLE_ format."""
    
    try:
        # Read the CSV
        df = pd.read_csv(csv_file, delimiter=';', encoding='latin-1')
        print(f"Loaded {len(df)} DTC codes from {csv_file}\n")
        
        # Build the VAL_TABLE_ entries
        entries = []
        
        for idx, row in df.iterrows():
            decimal_code = int(row['Codigo Decimal'])
            macro_name = str(row['Macro Name']).strip()
            
            # Remove 'DTC_' prefix if present (DBC format usually doesn't include it)
            if macro_name.startswith('DTC_'):
                macro_name = macro_name[4:]
            
            # Format: decimal "MACRO_NAME"
            entries.append(f'{decimal_code} "{macro_name}"')
        
        # Build the complete VAL_TABLE_ line
        val_table = f'VAL_TABLE_ {table_name} '
        val_table += ' '.join(entries)
        val_table += ' ;'
        
        return val_table, entries
    
    except Exception as e:
        print(f"Error: {e}")
        return None, []

def csv_to_dbc_formatted(csv_file, table_name="DTC", columns=5):
    """Convert DTC CSV to DBC VAL_TABLE_ format with line breaks for readability."""
    
    try:
        # Read the CSV
        df = pd.read_csv(csv_file, delimiter=';', encoding='latin-1')
        print(f"Loaded {len(df)} DTC codes from {csv_file}\n")
        
        # Build the VAL_TABLE_ entries
        entries = []
        
        for idx, row in df.iterrows():
            decimal_code = int(row['Codigo Decimal'])
            macro_name = str(row['Macro Name']).strip()
            
            # Remove 'DTC_' prefix if present
            if macro_name.startswith('DTC_'):
                macro_name = macro_name[4:]
            
            # Format: decimal "MACRO_NAME"
            entries.append(f'{decimal_code} "{macro_name}"')
        
        # Build the complete VAL_TABLE_ with formatting
        lines = [f'VAL_TABLE_ {table_name}']
        
        # Add entries in groups for readability
        for i in range(0, len(entries), columns):
            chunk = entries[i:i+columns]
            lines.append('  ' + ' '.join(chunk))
        
        lines[-1] += ' ;'  # Add semicolon to last line
        
        return '\n'.join(lines), entries
    
    except Exception as e:
        print(f"Error: {e}")
        return None, []

def generate_summary(csv_file):
    """Generate a summary report of the DTC codes."""
    try:
        df = pd.read_csv(csv_file, delimiter=';', encoding='latin-1')
        
        print(f"{'='*80}")
        print(f"DTC Summary for {csv_file}")
        print(f"{'='*80}")
        print(f"Total codes: {len(df)}")
        print(f"\nCodes by System:")
        print(df['System'].value_counts().to_string())
        print(f"\nCode Range: {df['Codigo Decimal'].min()} - {df['Codigo Decimal'].max()}")
        print(f"Hex Range: {hex(df['Codigo Decimal'].min())} - {hex(df['Codigo Decimal'].max())}")
        print(f"{'='*80}\n")
        
    except Exception as e:
        print(f"Error generating summary: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print(f"  python {sys.argv[0]} <csv_file> [--compact|--formatted] [--summary]")
        print()
        print("Examples:")
        print(f"  python {sys.argv[0]} data/DTC_T2.csv --formatted")
        print(f"  python {sys.argv[0]} data/DTC_Q3.csv --compact")
        print(f"  python {sys.argv[0]} data/DTC_T2.csv --summary")
        print()
        print("Options:")
        print("  --compact   : Single line output (default)")
        print("  --formatted : Multi-line output for readability")
        print("  --summary   : Show statistics summary")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    mode = '--formatted' if '--formatted' in sys.argv else '--compact'
    show_summary = '--summary' in sys.argv
    
    if not os.path.exists(csv_file):
        print(f"Error: File '{csv_file}' not found!")
        sys.exit(1)
    
    # Show summary if requested
    if show_summary:
        generate_summary(csv_file)
    
    # Generate VAL_TABLE_
    if mode == '--formatted':
        val_table, entries = csv_to_dbc_formatted(csv_file)
        print("DBC VAL_TABLE_ Format (Formatted):")
        print("="*80)
    else:
        val_table, entries = csv_to_dbc_val_table(csv_file)
        print("DBC VAL_TABLE_ Format (Compact):")
        print("="*80)
    
    if val_table:
        print(val_table)
        print()
        print(f"Total entries: {len(entries)}")
    else:
        print("Failed to generate VAL_TABLE_")
        sys.exit(1)

# python src/generate_dbc_val_table.py data/DTC_Q2.csv --formatted --summary > Q2_dbc.txt