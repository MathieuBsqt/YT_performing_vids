import matplotlib.pyplot as plt
import mplcursors as mplcursors
import pandas as pd


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


def plot_df(df, channel_name):
    # create plot x, y
    plt.figure(figsize=(12, 8))

    # create a scatter plot (points)
    scatter = plt.scatter(df['Video_Age'], df['Views_per_day'], s=15, alpha=0.7)

    plt.xlabel('Age de la video')
    plt.ylabel('Number of Views / days')
    plt.title('YouTube Video Performance - Views per Day Exponentiated vs. Views')

    # Connect mplcursors to the scatter plot
    cursor = mplcursors.cursor(hover=True)
    cursor.connect("add", lambda sel: hover_callback(sel, df))

    # Save the hover information to a CSV file
    hover_data = pd.DataFrame({
        'Title': df['Title'],
        'Video_URL': df['Video_URL'].apply(lambda url: url.split("=")[-1]),  # Extract ID from URL
        'Views': df['Views'],
        'Video_Age': df['Video_Age'],
        'Views_per_day': df['Views_per_day']
    })
    filename = f'output/{channel_name}_graph_info.csv'
    hover_data.to_csv(filename, index=False)

    # Show the plot
    plt.show()

    return hover_data, filename
