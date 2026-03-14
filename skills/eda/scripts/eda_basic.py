"""
Basic EDA (Exploratory Data Analysis) Script

This script performs basic exploratory data analysis on tabular datasets.
Supports CSV, Excel (xlsx, xls), and TSV files.

Usage: python eda_basic.py <file_path>
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np

def format_bytes(bytes_size):
    """Format bytes to human-readable size."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"

def analyze_dataset(file_path):
    """
    Perform basic EDA on the dataset.
    
    Args:
        file_path: Path to the dataset file
    """
    # Read the file
    file_ext = Path(file_path).suffix.lower()
    
    try:
        if file_ext == '.csv':
            df = pd.read_csv(file_path)
        elif file_ext in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        elif file_ext == '.tsv':
            df = pd.read_csv(file_path, sep='\t')
        else:
            print(f"❌ Unsupported file format: {file_ext}")
            print("Supported formats: .csv, .xlsx, .xls, .tsv")
            return
    except Exception as e:
        print(f"❌ Error reading file: {str(e)}")
        return
    
    # Get file info
    file_name = Path(file_path).name
    file_size = os.path.getsize(file_path)
    
    # Start report
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 15 + "EXPLORATORY DATA ANALYSIS REPORT" + " " * 11 + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    
    # Dataset Overview
    print("📊 Dataset Overview")
    print("━" * 60)
    print(f"File: {file_name}")
    print(f"Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
    print(f"Memory Usage: {format_bytes(df.memory_usage(deep=True).sum())}")
    print()
    
    # Column Information
    print("📋 Column Information")
    print("━" * 60)
    print(f"{'Column Name':<25} {'Data Type':<12} {'Non-Null':<12} {'Missing %'}")
    print("─" * 60)
    
    for col in df.columns:
        dtype = str(df[col].dtype)
        non_null = df[col].count()
        missing_pct = (df[col].isna().sum() / len(df)) * 100
        print(f"{col:<25} {dtype:<12} {non_null:<12} {missing_pct:.1f}%")
    
    print()
    
    # Missing Values Summary
    missing_data = df.isna().sum()
    missing_data = missing_data[missing_data > 0].sort_values(ascending=False)
    
    if len(missing_data) > 0:
        print("⚠️  Missing Values Summary")
        print("━" * 60)
        for col, count in missing_data.items():
            pct = (count / len(df)) * 100
            print(f"{col}: {count:,} missing ({pct:.1f}%)")
        print()
    else:
        print("✅ No Missing Values")
        print("━" * 60)
        print("All columns have complete data!")
        print()
    
    # Data Types Summary
    print("📊 Data Types Summary")
    print("━" * 60)
    dtype_counts = df.dtypes.value_counts()
    for dtype, count in dtype_counts.items():
        print(f"{dtype}: {count} columns")
    print()
    
    # Numerical Columns Statistics
    numerical_cols = df.select_dtypes(include=[np.number]).columns
    if len(numerical_cols) > 0:
        print("📈 Numerical Columns Statistics")
        print("━" * 60)
        
        stats_df = df[numerical_cols].describe()
        
        # Display statistics for each numerical column
        for col in numerical_cols[:5]:  # Show first 5 numerical columns
            print(f"\n{col}:")
            print(f"  Mean:   {stats_df.loc['mean', col]:.2f}")
            print(f"  Median: {stats_df.loc['50%', col]:.2f}")
            print(f"  Std:    {stats_df.loc['std', col]:.2f}")
            print(f"  Min:    {stats_df.loc['min', col]:.2f}")
            print(f"  Max:    {stats_df.loc['max', col]:.2f}")
        
        if len(numerical_cols) > 5:
            print(f"\n... and {len(numerical_cols) - 5} more numerical columns")
        print()
    
    # Categorical Columns Info
    categorical_cols = df.select_dtypes(include=['object']).columns
    if len(categorical_cols) > 0:
        print("📝 Categorical Columns Info")
        print("━" * 60)
        
        for col in categorical_cols[:5]:  # Show first 5 categorical columns
            unique_count = df[col].nunique()
            top_value = df[col].mode()[0] if len(df[col].mode()) > 0 else "N/A"
            print(f"\n{col}:")
            print(f"  Unique values: {unique_count}")
            print(f"  Most common:   {top_value}")
        
        if len(categorical_cols) > 5:
            print(f"\n... and {len(categorical_cols) - 5} more categorical columns")
        print()
    
    # Sample Data
    print("🔍 Sample Data (First 5 Rows)")
    print("━" * 60)
    
    # Display first few rows
    sample = df.head(5)
    
    # Format for display
    for idx, row in sample.iterrows():
        print(f"\nRow {idx + 1}:")
        for col in df.columns[:8]:  # Show first 8 columns
            value = row[col]
            # Truncate long strings
            if isinstance(value, str) and len(value) > 30:
                value = value[:27] + "..."
            print(f"  {col}: {value}")
        
        if len(df.columns) > 8:
            print(f"  ... and {len(df.columns) - 8} more columns")
    
    print()
    
    # Summary
    print("📌 Summary")
    print("━" * 60)
    print(f"✓ Dataset has {df.shape[0]:,} rows and {df.shape[1]} columns")
    print(f"✓ {len(numerical_cols)} numerical columns")
    print(f"✓ {len(categorical_cols)} categorical/text columns")
    
    if len(missing_data) > 0:
        total_missing = missing_data.sum()
        print(f"⚠️  {total_missing:,} total missing values across {len(missing_data)} columns")
    else:
        print("✓ No missing values - clean dataset!")
    
    print()
    print("═" * 60)
    print("Analysis Complete! ✓")
    print("═" * 60)
    print()

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print()
        print("╔" + "═" * 58 + "╗")
        print("║" + " " * 19 + "EDA Script - Usage" + " " * 19 + "║")
        print("╚" + "═" * 58 + "╝")
        print()
        print("Usage: python eda_basic.py <file_path>")
        print()
        print("Supported file formats:")
        print("  • CSV files (.csv)")
        print("  • Excel files (.xlsx, .xls)")
        print("  • TSV files (.tsv)")
        print()
        print("Example:")
        print("  python eda_basic.py data/sales_data.csv")
        print()
        return
    
    file_path = sys.argv[1]
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"\n❌ Error: File not found: {file_path}\n")
        return
    
    # Perform analysis
    analyze_dataset(file_path)

if __name__ == "__main__":
    main()