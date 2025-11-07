"""Example script demonstrating embeddoor usage."""

import pandas as pd
import numpy as np
from pathlib import Path

# Create sample data
def create_sample_data():
    """Create a sample dataset for testing embeddoor."""
    np.random.seed(42)
    
    # Generate sample data
    n_samples = 200
    
    data = {
        'id': range(n_samples),
        'text': [f"Sample text {i}" for i in range(n_samples)],
        'category': np.random.choice(['A', 'B', 'C'], n_samples),
        'value1': np.random.randn(n_samples),
        'value2': np.random.randn(n_samples),
        'value3': np.random.randn(n_samples),
    }
    
    df = pd.DataFrame(data)
    
    # Save to CSV
    output_path = Path('sample_data.csv')
    df.to_csv(output_path, index=False)
    print(f"Sample data saved to: {output_path.absolute()}")
    
    return df

if __name__ == '__main__':
    df = create_sample_data()
    print("\nSample data preview:")
    print(df.head())
    print(f"\nShape: {df.shape}")
    print("\nYou can now run: embeddoor")
    print(f"Then load the file: {Path('sample_data.csv').absolute()}")
