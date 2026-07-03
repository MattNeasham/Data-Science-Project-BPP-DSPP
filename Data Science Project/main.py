import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

#Establish root
root = Path(__file__).resolve().parent
archive_dir = root / "Data" / "archive"

########## Date range of races ##########

# Create df of races
races_df = pd.read_csv(archive_dir / "races.csv")

# Sort races df by date
races_sorted_df = races_df.sort_values(by="date", ascending= True)

#Find date range of races
date_index = races_sorted_df.columns.get_loc('date')

first_race_date = races_sorted_df.iloc[0, date_index]
#print("First race date: " + first_race_date)

last_race_date = races_sorted_df.iloc[len(races_sorted_df.index) - 1, date_index]
#print("Last race date: " + last_race_date)

########## Date range of pit stops ##########

#Create df of pit stops
pit_stops_df = pd.read_csv(archive_dir / "pit_stops.csv")
pit_stops_df['milliseconds'] = pit_stops_df['milliseconds'].astype(float)

#Merge pit stops and races so pit stops df has a date column
pit_stops_dated_df = pd.merge(pit_stops_df, races_df[['date', 'raceId']], on='raceId', how='left')

#Sort pit stops df by date
pit_stops_dated_sorted_df = pit_stops_dated_df.sort_values(by=["date"], ascending= True)

#Find date range of pit stops
first_pit_stop_date = pit_stops_dated_sorted_df.iloc[0, len(pit_stops_dated_sorted_df.columns) - 1]
#print("First pit stop date: " + first_pit_stop_date)

last_pit_stop_date = pit_stops_dated_sorted_df.iloc[len(pit_stops_dated_sorted_df.index) - 1, len(pit_stops_dated_sorted_df.columns) - 1]
#print("Last pit stop date: " + last_pit_stop_date)

########## Date range of sprint races ##########

#Create df of sprint results
sprint_results_df = pd.read_csv(archive_dir / "sprint_results.csv")

#Merge sprint results and races so sprint results df has a date column
sprint_results_dated_df = pd.merge(sprint_results_df, races_df[['sprint_date', 'raceId']], on='raceId', how='left')

#Sort sprint results dated df by date
sprint_results_dated_sorted_df = sprint_results_dated_df.sort_values(by=["sprint_date"], ascending= True)

#Find date range of sprint races
first_sprint_date = sprint_results_dated_sorted_df.iloc[0, len(sprint_results_dated_sorted_df.columns) - 1]
#print("Earliest sprint date: " + first_sprint_date)

last_sprint_date = sprint_results_dated_sorted_df.iloc[len(sprint_results_dated_sorted_df.index) - 1, len(sprint_results_dated_sorted_df.columns) - 1]
#print("Latest sprint date: " + last_sprint_date)

########## Trim using date ranges ##########

# Create date trimmed races csv
races_cleaned_df = races_sorted_df[(races_sorted_df['date'] >= "2011-03-27") & (races_sorted_df['date'] <= "2024-06-30")]
#print(races_trimmed_df.iloc[0, races_trimmed_df.columns.get_loc('date')])
#print(races_trimmed_df.iloc[len(races_trimmed_df.index) - 1, races_trimmed_df.columns.get_loc('date')])
races_cleaned_df.to_csv('Data/cleaned_data/races_cleaned.csv', index=False, header=True)

# Create date trimmed seasons csv 
seasons_df = pd.read_csv(archive_dir / "seasons.csv")
seasons_sorted_df = seasons_df.sort_values(by = "year", ascending= True)
seasons_cleaned_df = seasons_sorted_df[(seasons_sorted_df['year'] >= 2011) & (seasons_sorted_df['year'] <= 2024)]
seasons_cleaned_df.to_csv('Data/cleaned_data/seasons_cleaned.csv', index=False, header=True)

# Create date trimmed circuits csv
circuits_df = pd.read_csv(archive_dir / "circuits.csv")
races_cleaned_circuit_joined_df = pd.merge(races_cleaned_df, circuits_df, on='circuitId', how='left')
unique_circuits = pd.unique(races_cleaned_circuit_joined_df['circuitRef'])
circuits_cleaned_df = circuits_df[circuits_df['circuitRef'].isin(unique_circuits)]
circuits_cleaned_df.to_csv('Data/cleaned_data/circuits_cleaned.csv', index=False, header=True)

# Create date trimmed lap times csv
lap_times_df = pd.read_csv(archive_dir / "lap_times.csv")
lap_times_cleaned_df = lap_times_df[lap_times_df['raceId'].isin(races_cleaned_df['raceId'])]
lap_times_cleaned_df.to_csv('Data/cleaned_data/lap_times_cleaned.csv', index=False, header=True)

# Create date trimmed results csv
results_df = pd.read_csv(archive_dir / "results.csv")
results_cleaned_df = results_df[results_df['raceId'].isin(races_cleaned_df['raceId'])]
results_cleaned_df = results_cleaned_df.rename(columns={"time":"race_time"})
results_cleaned_df.to_csv('Data/cleaned_data/results_cleaned.csv', index=False, header= True)

# Create date trimmed drivers csv
drivers_df = pd.read_csv(archive_dir / "drivers.csv")
drivers_cleaned_df = drivers_df[drivers_df['driverId'].isin(results_cleaned_df['driverId'])]
drivers_cleaned_df.to_csv('Data/cleaned_data/drivers_cleaned.csv', index=False, header=True)

# Create date trimmed driver standings csv
driver_standings_df = pd.read_csv(archive_dir / "driver_standings.csv")
driver_standings_cleaned_df = driver_standings_df[driver_standings_df['raceId'].isin(races_cleaned_df['raceId'])]
driver_standings_cleaned_df.to_csv('Data/cleaned_data/driver_standings_cleaned.csv', index=False, header=True)

# Save pit stops cleaned df
pit_stops_df.to_csv('Data/cleaned_data/pit_stops_cleaned.csv', index=False, header=True)

# Create date trimmed qualifying csv
qualifying_df = pd.read_csv(archive_dir / "qualifying.csv")
qualifying_cleaned_df = qualifying_df[qualifying_df['raceId'].isin(races_cleaned_df['raceId'])]
qualifying_cleaned_df.to_csv('Data/cleaned_data/qualifying_cleaned.csv')

########## Create tables for analysis ########## 

# Create master df
master_df = pit_stops_df.drop(columns=['duration'])
master_df = pd.merge(master_df, races_cleaned_circuit_joined_df[['date', 'round','circuitRef', 'raceId']], on='raceId', how='left')

drivers_cleaned_df['full_name'] = drivers_cleaned_df['forename'] + " " + drivers_cleaned_df['surname']
master_df = pd.merge(master_df, drivers_cleaned_df[['driverId', 'full_name']], on='driverId', how='left')

master_df = pd.merge(master_df, results_cleaned_df[['driverId', 'raceId', 'grid', 'position', 'race_time']], on=['driverId', 'raceId'], how='left')

master_df.to_csv('Data/merged_data/master_pit_stops.csv', index=False, header= True)

# Create aggregated df

aggregated_pit_stops_df = master_df.groupby(['raceId','driverId', 'circuitRef', 'full_name', 'position', 'grid', 'race_time']).agg({'milliseconds': ['min','max','mean']}).reset_index()
aggregated_pit_stops_df.columns=["_".join(col).strip() for col in aggregated_pit_stops_df.columns.to_flat_index()]
aggregated_pit_stops_df = aggregated_pit_stops_df.rename(columns={'milliseconds_min': 'shortest_pit_stop_milliseconds', 'milliseconds_max': 'longest_pit_stop_milliseconds', 'milliseconds_mean': 'mean_pit_stop_milliseconds'})
aggregated_pit_stops_df = aggregated_pit_stops_df.replace(r'\\N', 0, regex=True)

aggregated_pit_stops_df.to_csv('Data/merged_data/aggregated_pit_stops.csv', index=False, header=True)

########## EDA ##########

# Correlation

pit_time_position_df = aggregated_pit_stops_df.copy()
pit_time_position_df["mean_pit_stop_milliseconds"] = pd.to_numeric(pit_time_position_df["mean_pit_stop_milliseconds"], errors="coerce")
pit_time_position_df["position_"] = pd.to_numeric(pit_time_position_df["position_"], errors="coerce")
pit_time_position_df = pit_time_position_df.dropna(subset=["mean_pit_stop_milliseconds", "position_"])

pit_time_position_correlation = pit_time_position_df["mean_pit_stop_milliseconds"].corr(pit_time_position_df["position_"])

# Create graphs

plt.figure(figsize = (6,4))
sns.regplot(data = pit_time_position_df, x = "mean_pit_stop_milliseconds", y = "position_", scatter_kws={"color":"blue"}, line_kws={"color": "red"})
plt.title(f"Correlation graph (r = {pit_time_position_correlation:.2f})")
plt.xlabel("Mean Pit Stop Time")
plt.ylabel("Finishing Position")
plt.grid(True)
plt.show()

########## Completion message ##########
print("Completed successfully")

