#!/usr/bin/env python3
"""
Local Bot Tester - Test bot commands without Telegram
Run this script to test bot functionality locally
"""
import sys
sys.path.insert(0, 'src')

from bot import fault_codes
from float_lookup import lookup_float_value

def test_fault_code(message):
    """Test fault code lookup logic."""
    message = message.upper().strip()
    
    # Check if it's a CATL command
    if message.startswith('CATL'):
        parts = message.split()
        if len(parts) != 2:
            return "[ERROR] Invalid CATL format. Use: CATL <value>"
        
        value = parts[1]
        result = lookup_float_value(value)
        
        if result is not None:
            return f"CATL Lookup Result:\n  Input Value: {value}\n  SOC Value: {result}"
        else:
            return f"[ERROR] Invalid input value: {value}\nPlease provide a value between 2.800 and 3.700"
    
    # Parse fault code lookup
    parts = message.split()
    if len(parts) != 2:
        return "[ERROR] Invalid format. Use: <product> <code>\nExample: Q1 16897"
    
    product, code = parts
    
    # Validate product
    if product not in ['Q1', 'Q2', 'T2', 'Q3']:
        return f"[ERROR] Invalid product: {product}\nAvailable: Q1, Q2, T2, Q3"
    
    # Add 0x prefix if it's a hex code without it
    if len(code) == 4 and all(c in '0123456789ABCDEF' for c in code):
        code = '0x' + code
    
    # Look up the code
    product_dict = fault_codes[product]
    if code in product_dict:
        fault_info = product_dict[code]
        return (
            f"Fault Code: {code}\n"
            f"  Name: {fault_info['name']}\n"
            f"  Description: {fault_info['description']}\n"
            f"  System: {fault_info['system']}\n"
            f"  Severity: {fault_info['level']}\n"
            f"  Product: {fault_info['product']}"
        )
    else:
        return f"[ERROR] Code {code} not found for {product}"

def interactive_mode():
    """Run in interactive mode."""
    print("="*60)
    print("Local Bot Tester - Interactive Mode")
    print("="*60)
    print(f"Q1: {len(fault_codes['Q1'])} codes loaded")
    print(f"Q2: {len(fault_codes['Q2'])} codes loaded")
    print(f"T2: {len(fault_codes['T2'])} codes loaded")
    print(f"Q3: {len(fault_codes['Q3'])} codes loaded")
    print("="*60)
    print("\nExamples:")
    print("  Q1 16897")
    print("  Q2 0x4201")
    print("  T2 14592")
    print("  Q3 17445")
    print("  CATL 3.247")
    print("\nType 'quit' or 'exit' to stop\n")
    
    while True:
        try:
            message = input("Enter command: ").strip()
            
            if message.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if not message:
                continue
            
            result = test_fault_code(message)
            print(f"\n{result}\n")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")

def batch_mode(commands):
    """Run in batch mode with provided commands."""
    print("="*60)
    print("Local Bot Tester - Batch Mode")
    print("="*60)
    
    for i, cmd in enumerate(commands, 1):
        print(f"\n[Test {i}] Command: {cmd}")
        print("-" * 60)
        result = test_fault_code(cmd)
        print(result)
    
    print("\n" + "="*60)
    print(f"Completed {len(commands)} test(s)")
    print("="*60)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Batch mode - test commands from arguments
        batch_mode(sys.argv[1:])
    else:
        # Interactive mode
        interactive_mode()

# python test_bot_locally.py "Q1 16897" "T2 14592" "Q3 17445" "CATL 3.247"
# python test_bot_locally.py
# python test_bot_locally.py "Q2 0x4201"