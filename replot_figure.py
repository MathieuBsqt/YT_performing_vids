import matplotlib.pyplot as plt
import pandas as pd
import mplcursors

# Load the hover information from the CSV file
filename = input("Enter name to the .csv file you want to plot: ")
df = pd.read_csv("output/"+filename)

# Create a scatter plot
plt.figure(figsize=(12, 8))
scatter = plt.scatter(df['Video_Age'], df['Views_per_day'], s=15, alpha=0.7)

# Create a function to handle hover events
def hover_callback(sel, df):
    index = sel.target.index
    title = df.iloc[index]['Title']
    video_id = df.iloc[index]['Video_URL'].split("=")[-1]  # Extract ID from URL
    views = df.iloc[index]['Views']
    video_age = df.iloc[index]['Video_Age']
    views_per_day = df.iloc[index]['Views_per_day']

    text = f'Title: {title}\nVideo ID: {video_id}\nViews: {views}\nVideo Age: {video_age}\nViews per Day: {views_per_day}'

    sel.annotation.set_text(text)

# Connect mplcursors to the scatter plot
cursor = mplcursors.cursor(hover=True)
cursor.connect("add", lambda sel: hover_callback(sel, df))

# Show the plot
plt.show()
