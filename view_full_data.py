import pandas as pd

# Read the Excel file
file_path = "/home/esteban/tio cesar/Farmer's Fresh^J LLC_Profit and Loss Yearly.xlsx"
df = pd.read_excel(file_path)

# Display all rows
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

print(df)
