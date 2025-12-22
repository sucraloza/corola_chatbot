#!/usr/bin/env python3
"""
Extract unique DTC codes from CSV files and test them
"""
import pandas as pd
import sys
import os

# Add parent directory to path to import from src
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bot import fault_codes
from float_lookup import lookup_float_value

def extract_unique_dtcs(csv_file):
    """Extract unique DTC codes from a CSV file and convert to hex format."""
    print(f"Reading CSV file: {csv_file}")
    
    try:
        # Try to read the CSV - detect delimiter automatically
        df = pd.read_csv(csv_file, sep=None, engine='python')
        print(f"Loaded {len(df)} rows")
        print(f"Columns: {df.columns.tolist()}\n")
        
        # Look for DTC-like columns (codes that look like hex or decimal)
        dtc_codes_decimal = set()
        dtc_codes_hex = {}  # Map hex to decimal for reference
        
        for col in df.columns:
            col_lower = col.lower()
            # Check if column might contain DTC codes
            if any(keyword in col_lower for keyword in ['dtc', 'code', 'codigo', 'fault', 'error']):
                print(f"Checking column: {col}")
                for value in df[col].dropna().unique():
                    # Skip 0 values (no error)
                    if pd.isna(value) or value == 0:
                        continue
                    
                    # Convert to int if it's a float
                    if isinstance(value, float):
                        value = int(value)
                    
                    value_str = str(value).strip()
                    
                    # Check if it's already hex format
                    if value_str.startswith('0x'):
                        dtc_codes_hex[value_str.upper()] = value_str
                    # Check if it's a decimal number
                    elif value_str.isdigit():
                        decimal_val = int(value_str)
                        hex_val = hex(decimal_val).upper()  # Convert to hex (0xABCD format)
                        dtc_codes_hex[hex_val] = decimal_val
                        dtc_codes_decimal.add(decimal_val)
        
        # Print conversion table
        if dtc_codes_hex:
            print(f"\nDEC -> HEX Conversion:")
            print(f"{'-'*40}")
            for hex_code in sorted(dtc_codes_hex.keys()):
                dec_code = dtc_codes_hex[hex_code]
                print(f"  {dec_code:5d} -> {hex_code}")
            print()
        
        return sorted(dtc_codes_hex.keys()), dtc_codes_hex
    
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return [], {}

def test_dtc_code(product, code):
    """Test a single DTC code."""
    code = code.upper()
    
    # Add 0x prefix if it's a hex code without it
    if len(code) == 4 and all(c in '0123456789ABCDEF' for c in code):
        code = '0x' + code
    
    # Look up the code
    product_dict = fault_codes.get(product, {})
    if code in product_dict:
        fault_info = product_dict[code]
        return {
            'found': True,
            'code': code,
            'name': fault_info['name'],
            'description': fault_info['description'],
            'system': fault_info['system'],
            'level': fault_info['level'],
            'product': fault_info['product']
        }
    else:
        return {
            'found': False,
            'code': code
        }

def test_all_dtcs(dtc_codes, product='Q1'):
    """Test all DTC codes against a specific product."""
    print(f"\n{'='*80}")
    print(f"Testing {len(dtc_codes)} unique DTC codes against {product}")
    print(f"{'='*80}\n")
    
    found_codes = []
    not_found_codes = []
    
    for code in dtc_codes:
        result = test_dtc_code(product, code)
        
        if result['found']:
            found_codes.append(result)
            print(f"[FOUND] {result['code']} - {result['name']}")
        else:
            not_found_codes.append(code)
    
    # Summary
    print(f"\n{'='*80}")
    print(f"SUMMARY for {product}")
    print(f"{'='*80}")
    print(f"Total codes in CSV: {len(dtc_codes)}")
    print(f"Found in database: {len(found_codes)} ({len(found_codes)/len(dtc_codes)*100:.1f}%)")
    print(f"Not found: {len(not_found_codes)} ({len(not_found_codes)/len(dtc_codes)*100:.1f}%)")
    
    if not_found_codes:
        print(f"\nNot found codes (first 20):")
        for code in not_found_codes[:20]:
            print(f"  - {code}")
        if len(not_found_codes) > 20:
            print(f"  ... and {len(not_found_codes) - 20} more")
    
    return found_codes, not_found_codes

def test_all_products(dtc_codes):
    """Test DTC codes against all products."""
    all_results = {}
    
    for product in ['Q1', 'Q2', 'T2', 'Q3']:
        found, not_found = test_all_dtcs(dtc_codes, product)
        all_results[product] = {
            'found': found,
            'not_found': not_found
        }
    
    # Overall summary
    print(f"\n{'='*80}")
    print(f"OVERALL SUMMARY")
    print(f"{'='*80}")
    for product, results in all_results.items():
        found_count = len(results['found'])
        total = len(dtc_codes)
        print(f"{product}: {found_count}/{total} codes found ({found_count/total*100:.1f}%)")
    
    return all_results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print(f"  python {sys.argv[0]} <csv_file> [product]")
        print()
        print("Examples:")
        print(f"  python {sys.argv[0]} files/E327.csv Q1")
        print(f"  python {sys.argv[0]} files/E327.csv all")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    product = sys.argv[2] if len(sys.argv) > 2 else 'all'
    
    # Extract unique DTCs (returns hex codes and conversion map)
    dtc_codes_hex, conversion_map = extract_unique_dtcs(csv_file)
    
    if not dtc_codes_hex:
        print("\nNo DTC codes found in CSV file!")
        sys.exit(1)
    
    print(f"\nExtracted {len(dtc_codes_hex)} unique DTC codes (in HEX format)")
    print(f"Sample codes: {dtc_codes_hex[:10]}")
    
    # Test against products using hex codes
    if product.upper() == 'ALL':
        test_all_products(dtc_codes_hex)
    else:
        test_all_dtcs(dtc_codes_hex, product.upper())

# python src/extract_and_test_dtcs.py files/E327.csv all > E327_analysis.txt