import pandas as pd
import os

def split_data(input_file, output_dir):
    df = pd.read_csv(input_file)
    df['OFFENSE_DATE'] = pd.to_datetime(df['OFFENSE_DATE'])
    df['Year'] = df['OFFENSE_DATE'].dt.year

    for year in df['Year'].unique():
        year_data = df[df['Year'] == year]
        output_file = os.path.join(output_dir, f"analysis_yoy_analysis_{year}.csv")
        year_data.to_csv(output_file, index=False)

# Run this function once to split your data
split_data("analysis_yoy_analysis.csv", "")
