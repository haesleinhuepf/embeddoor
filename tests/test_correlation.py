"""Test script to verify the correlation panel functionality."""

import pandas as pd
import numpy as np
from io import BytesIO
from embeddoor.visualization import create_correlation_matrix_image

def test_correlation_matrix():
    """Test the correlation matrix visualization function."""
    
    # Create sample data with correlations
    np.random.seed(42)
    n_samples = 100
    
    # Create correlated variables
    x1 = np.random.randn(n_samples)
    x2 = x1 + np.random.randn(n_samples) * 0.5  # Positively correlated with x1
    x3 = -x1 + np.random.randn(n_samples) * 0.5  # Negatively correlated with x1
    x4 = np.random.randn(n_samples)  # Independent
    
    df = pd.DataFrame({
        'var1': x1,
        'var2': x2,
        'var3': x3,
        'var4': x4,
        'category': np.random.choice(['A', 'B', 'C'], n_samples),  # Non-numeric
        'selection': np.random.choice([0, 1], n_samples)  # Selection column (should be ignored)
    })
    
    print("Test DataFrame shape:", df.shape)
    print("\nNumeric columns:", df.select_dtypes(include=[np.number]).columns.tolist())
    
    # Test with default method (Pearson)
    print("\n--- Testing Pearson correlation ---")
    try:
        png_bytes = create_correlation_matrix_image(df, method='pearson', width=800, height=600)
        print(f"✓ Pearson correlation matrix generated successfully ({len(png_bytes)} bytes)")
    except Exception as e:
        print(f"✗ Pearson correlation failed: {e}")
        return False
    
    # Test with Spearman method
    print("\n--- Testing Spearman correlation ---")
    try:
        png_bytes = create_correlation_matrix_image(df, method='spearman', width=800, height=600)
        print(f"✓ Spearman correlation matrix generated successfully ({len(png_bytes)} bytes)")
    except Exception as e:
        print(f"✗ Spearman correlation failed: {e}")
        return False
    
    # Test with Kendall method
    print("\n--- Testing Kendall correlation ---")
    try:
        png_bytes = create_correlation_matrix_image(df, method='kendall', width=800, height=600)
        print(f"✓ Kendall correlation matrix generated successfully ({len(png_bytes)} bytes)")
    except Exception as e:
        print(f"✗ Kendall correlation failed: {e}")
        return False
    
    # Test with specific columns
    print("\n--- Testing with specific columns ---")
    try:
        png_bytes = create_correlation_matrix_image(df, method='pearson', columns=['var1', 'var2'], width=800, height=600)
        print(f"✓ Correlation matrix with specific columns generated successfully ({len(png_bytes)} bytes)")
    except Exception as e:
        print(f"✗ Specific columns test failed: {e}")
        return False
    
    # Test error cases
    print("\n--- Testing error cases ---")
    
    # Test with no numeric columns
    try:
        df_no_numeric = pd.DataFrame({'text': ['a', 'b', 'c']})
        png_bytes = create_correlation_matrix_image(df_no_numeric, method='pearson')
        print("✗ Should have raised error for no numeric columns")
        return False
    except ValueError as e:
        print(f"✓ Correctly raised error for no numeric columns: {e}")
    
    # Test with only one numeric column
    try:
        df_one_col = pd.DataFrame({'value': [1, 2, 3]})
        png_bytes = create_correlation_matrix_image(df_one_col, method='pearson')
        print("✗ Should have raised error for single numeric column")
        return False
    except ValueError as e:
        print(f"✓ Correctly raised error for single numeric column: {e}")
    
    print("\n" + "="*60)
    print("All tests passed! ✓")
    print("="*60)
    return True

if __name__ == '__main__':
    success = test_correlation_matrix()
    exit(0 if success else 1)
