import pandas as pd
import numpy as np
from typing import Optional, List, Tuple
import matplotlib.pyplot as plt
from scipy import stats
import os

def generate_interpolated_points(x1: float, y1: float, x2: float, y2: float, num_points: int = 10) -> List[Tuple[float, float]]:
    """
    Generate interpolated points between two points.
    
    Args:
        x1, y1: First point coordinates
        x2, y2: Second point coordinates
        num_points: Number of points to generate (including endpoints)
        
    Returns:
        List of (x, y) tuples representing interpolated points
    """
    x_points = np.linspace(x1, x2, num_points)
    y_points = np.linspace(y1, y2, num_points)
    return list(zip(x_points, y_points))

def create_extended_lookup_table(num_points: int = 10) -> pd.DataFrame:
    """
    Create an extended lookup table with interpolated values between each pair of points.
    
    Args:
        num_points: Number of points to generate between each pair of original points
        
    Returns:
        DataFrame containing the extended lookup table
    """
    if LOOKUP_COMPACT.empty:
        return pd.DataFrame()
    
    extended_data = []
    
    # Process each segment
    for i in range(len(LOOKUP_COMPACT) - 1):
        x1 = LOOKUP_COMPACT.iloc[i]['return_value']
        y1 = LOOKUP_COMPACT.iloc[i]['input_value']
        x2 = LOOKUP_COMPACT.iloc[i + 1]['return_value']
        y2 = LOOKUP_COMPACT.iloc[i + 1]['input_value']
        
        # Generate interpolated points
        points = generate_interpolated_points(x1, y1, x2, y2, num_points)
        
        # Add points to extended data
        for x, y in points:
            extended_data.append({
                'input_value': round(y, 3),
                'return_value': round(x, 3)
            })
    
    # Create DataFrame and sort by input_value
    extended_df = pd.DataFrame(extended_data)
    extended_df = extended_df.sort_values('input_value').reset_index(drop=True)
    
    return extended_df

def save_extended_lookup_table(num_points: int = 10, output_path: str = 'data/float_lookup_extended.csv') -> None:
    """
    Create and save an extended lookup table with interpolated values.
    
    Args:
        num_points: Number of points to generate between each pair of original points
        output_path: Path to save the extended lookup table
    """
    extended_df = create_extended_lookup_table(num_points)
    if not extended_df.empty:
        extended_df.to_csv(output_path, index=False)
        print(f"Extended lookup table saved to {output_path}")
        print(f"Generated {len(extended_df)} points from {len(LOOKUP_COMPACT)} original points")

def calculate_segment_parameters() -> List[Tuple[float, float, float, float]]:
    """
    Calculate parameters for each segment between points in the lookup table.
    
    Returns:
        List of tuples containing (x1, y1, x2, y2) for each segment
    """
    if LOOKUP_COMPACT.empty:
        return []
    
    segments = []
    for i in range(len(LOOKUP_COMPACT) - 1):
        x1 = LOOKUP_COMPACT.iloc[i]['return_value']
        y1 = LOOKUP_COMPACT.iloc[i]['input_value']
        x2 = LOOKUP_COMPACT.iloc[i + 1]['return_value']
        y2 = LOOKUP_COMPACT.iloc[i + 1]['input_value']
        segments.append((x1, y1, x2, y2))
    
    return segments

def plot_lookup_table(save_path: Optional[str] = None, show_segments: bool = True) -> None:
    """
    Plot the lookup table values with return values on x-axis and input values on y-axis.
    Optionally show the linear segments between points.
    
    Args:
        save_path (Optional[str]): If provided, save the plot to this path
        show_segments (bool): Whether to show the linear segments between points
    """
    if LOOKUP_COMPACT.empty:
        print("No data available to plot")
        return
    
    plt.figure(figsize=(12, 8))
    
    # Plot the points
    plt.scatter(LOOKUP_COMPACT['return_value'], LOOKUP_COMPACT['input_value'], 
                color='blue', s=100, label='Lookup Values')
    
    # Add segments between points if requested
    if show_segments:
        segments = calculate_segment_parameters()
        for i, (x1, y1, x2, y2) in enumerate(segments):
            # Calculate slope and intercept for this segment
            slope = (y2 - y1) / (x2 - x1)
            intercept = y1 - slope * x1
            
            # Extend the line beyond the points
            x_extended = np.array([x1 - (x2 - x1), x2 + (x2 - x1)])
            y_extended = slope * x_extended + intercept
            
            # Plot the extended segment
            plt.plot(x_extended, y_extended, 'r--', alpha=0.3, 
                    label=f'Segment {i+1}' if i == 0 else "")
    
    # Customize the plot
    plt.title('Lookup Table Values with Piecewise Linear Segments')
    plt.xlabel('Return Value')
    plt.ylabel('Input Value')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    
    # Set y-axis limits with some padding
    y_min = LOOKUP_COMPACT['input_value'].min() - 0.1
    y_max = LOOKUP_COMPACT['input_value'].max() + 0.1
    plt.ylim(y_min, y_max)
    
    # Add value labels to points
    for x, y in zip(LOOKUP_COMPACT['return_value'], LOOKUP_COMPACT['input_value']):
        plt.annotate(f'{y}', (x, y), textcoords="offset points", 
                    xytext=(0,10), ha='center')
    
    if save_path:
        plt.savefig(save_path)
        print(f"Plot saved to {save_path}")
    else:
        plt.show()
    
    plt.close()

def validate_float_input(value: str) -> Optional[float]:
    """
    Validate and format the input float value.
    
    Args:
        value (str): Input value as string
        
    Returns:
        Optional[float]: Formatted float value if valid, None if invalid
    """
    try:
        # Convert to float and round to 3 decimal places
        float_value = round(float(value), 3)
        
        # Check if value is within range
        if 2.800 <= float_value <= 3.700:
            return float_value
        else:
            print(f"Value {float_value} is outside the valid range (2.800 - 3.700)")
            return None
    except ValueError:
        print("Invalid input. Please provide a valid number.")
        return None

def find_closest_value(input_value: float) -> Optional[str]:
    """
    Find the closest matching value in the lookup table.
    
    Args:
        input_value (float): Input value to look up
        
    Returns:
        Optional[str]: Return value from lookup table, None if not found
    """
    if LOOKUP_TABLE.empty:
        return None
    
    # Find the closest value in the lookup table
    closest_idx = (LOOKUP_TABLE['input_value'] - input_value).abs().idxmin()
    return LOOKUP_TABLE.loc[closest_idx, 'return_value']

def lookup_float_value(value: str) -> Optional[str]:
    """
    Main function to lookup a float value and return the corresponding value.
    
    Args:
        value (str): Input value as string
        
    Returns:
        Optional[str]: Return value from lookup table, None if not found
    """
    if LOOKUP_TABLE.empty:
        print("Lookup table is not available")
        return None
    
    # Validate input
    float_value = validate_float_input(value)
    if float_value is None:
        return None
    
    # Find closest value
    return find_closest_value(float_value)

# Load lookup tables once when module is imported
try:
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to the project root, then into data/
    project_root = os.path.dirname(script_dir)
    data_dir = os.path.join(project_root, 'data')
    
    # Load the compact (original) lookup table
    compact_path = os.path.join(data_dir, 'float_lookup.csv')
    LOOKUP_COMPACT = pd.read_csv(compact_path)
    LOOKUP_COMPACT['input_value'] = LOOKUP_COMPACT['input_value'].astype(float)
    LOOKUP_COMPACT['return_value'] = LOOKUP_COMPACT['return_value'].astype(float)
    
    # Load the extended lookup table
    extended_path = os.path.join(data_dir, 'float_lookup_extended.csv')
    LOOKUP_TABLE = pd.read_csv(extended_path)
    LOOKUP_TABLE['input_value'] = LOOKUP_TABLE['input_value'].astype(float)
    LOOKUP_TABLE['return_value'] = LOOKUP_TABLE['return_value'].astype(float)
    
except Exception as e:
    print(f"Error loading lookup tables: {e}")
    LOOKUP_COMPACT = pd.DataFrame()
    LOOKUP_TABLE = pd.DataFrame()

# Example usage
if __name__ == "__main__":
    # Create and save extended lookup table
    
    # # save_extended_lookup_table(num_points=10)
    # plot_lookup_table("table_compact",show_segments=True)

    
    # Test value sets
    test_sets = [
        # ("22-10-2025 10:10", ["3.338", "3.333", "3.332"]),
        # ("E327-1", ["3.282","0", "3.063"]),
        # ("E327-5", ["3.282","0", "3.063"]),
        ("E344", ["3.231","3.227","3.223","3.219","3.224","3.211","3.234","3.231"]) # OK
        
    ]

    for pack_name, test_values in test_sets:
        print(f"\n{pack_name}:")
        for value in test_values:
            result = lookup_float_value(value)
            if result is not None:  # This will work correctly even if result is 0
                print(f"Input: {value} -> Return value: {result}")
            else:
                print(f"Input: {value} -> No valid result found")

