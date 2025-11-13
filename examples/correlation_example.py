"""
Example demonstrating the Pairwise Correlation panel in embeddoor.

This script creates sample data with known correlations and shows
how to visualize them using the correlation matrix panel.
"""

import pandas as pd
import numpy as np
from pathlib import Path

def create_correlated_data():
    """Create sample data with interesting correlations."""
    np.random.seed(42)
    n_samples = 200
    
    # Create correlated variables
    temperature = np.random.uniform(10, 35, n_samples)
    
    # Ice cream sales (positively correlated with temperature)
    ice_cream_sales = 50 + 3 * temperature + np.random.normal(0, 10, n_samples)
    
    # Heating costs (negatively correlated with temperature)
    heating_costs = 100 - 2 * temperature + np.random.normal(0, 5, n_samples)
    
    # Independent variable
    rainfall = np.random.uniform(0, 50, n_samples)
    
    # Variable correlated with rainfall
    umbrella_sales = 20 + 1.5 * rainfall + np.random.normal(0, 8, n_samples)
    
    df = pd.DataFrame({
        'temperature_celsius': temperature,
        'ice_cream_sales': ice_cream_sales,
        'heating_costs': heating_costs,
        'rainfall_mm': rainfall,
        'umbrella_sales': umbrella_sales,
        'date': pd.date_range('2024-01-01', periods=n_samples, freq='D'),
        'category': np.random.choice(['Store_A', 'Store_B', 'Store_C'], n_samples)
    })
    
    # Save to CSV
    output_path = Path('correlation_example.csv')
    df.to_csv(output_path, index=False)
    print(f"Sample data saved to: {output_path.absolute()}")
    
    return df

def print_correlations(df):
    """Print actual correlations to verify visualization."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    print("\n" + "="*60)
    print("Expected Correlations (Pearson):")
    print("="*60)
    
    corr_matrix = df[numeric_cols].corr()
    print(corr_matrix)
    
    print("\n" + "="*60)
    print("Key Correlations to Observe:")
    print("="*60)
    print("• Temperature ↔ Ice Cream Sales: POSITIVE (hot weather → more ice cream)")
    print("• Temperature ↔ Heating Costs: NEGATIVE (hot weather → less heating)")
    print("• Rainfall ↔ Umbrella Sales: POSITIVE (more rain → more umbrellas)")
    print("• Temperature ↔ Rainfall: ~ZERO (independent)")

if __name__ == '__main__':
    df = create_correlated_data()
    
    print("\nSample data preview:")
    print(df.head(10))
    print(f"\nShape: {df.shape}")
    
    print_correlations(df)
    
    print("\n" + "="*60)
    print("How to Use:")
    print("="*60)
    print("1. Run: embeddoor")
    print("2. Load the file: correlation_example.csv")
    print("3. Create a new panel and select 'Pairwise Correlation'")
    print("4. Choose correlation method from dropdown (Pearson, Spearman, Kendall)")
    print("5. Click 'Update' to regenerate with different method")
    print("\nThe correlation matrix shows relationships between all numeric columns.")
    print("Blue intensity indicates correlation strength (-1 to 1).")
    print("="*60)
