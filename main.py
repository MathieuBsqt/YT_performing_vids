import googleapiclient.discovery
from secrets import API_KEY, CHANNEL_ID
import requests
from datetime import datetime
from graphs import plot_df
from samples_classification import classify_samples
import pandas as pd


def create_client(api_key):
    """
    https://developers.google.com/youtube/v3/docs/channels/list
    """
    # Initialize the YouTube Data API client
    yt_client = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
    return yt_client


def get_channel_data(yt_client, channel_ID=None):
    """
    Retrieve global info about a YT channel from its ID
    """

    channel_request = yt_client.channels().list(part="snippet,contentDetails,statistics", id=channel_ID)

    channel_response = channel_request.execute()
    # Extract relevant information

    if channel_response["items"]:
        channel_data = channel_response["items"][0]["snippet"]
        channel_name = channel_data["title"]

        channel_statistics = channel_response["items"][0]["statistics"]
        nb_subscribers = channel_statistics["subscriberCount"]
        nb_views = channel_statistics["viewCount"]
        playlist_ID = channel_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        nb_videos = channel_statistics["videoCount"]
        # Once we have the playlist id of the channel, we can get the user videos
        # Fetch videos from the channel
        #videos_request = youtube.playlistItems().list(
        #    part="snippet,contentDetails",
        #    playlistId=channel_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"],
        #    maxResults=10  # You can adjust the number of videos to fetch
        #)
        #videos_response = videos_request.execute()

        # Extract video information
        #for video_item in videos_response["items"]:
        #    video_snippet = video_item["snippet"]
            #print("\nVideo Title:", video_snippet["title"])
            #print("Video Description:", video_snippet["description"])
            #print("Video Thumbnail:", video_snippet["thumbnails"]["default"]["url"])
            #print("Video Views:", video_snippet["publishedAt"])

    return channel_name, nb_subscribers, nb_views, playlist_ID, nb_videos


def get_yt_videos_ids(yt_client, playlist_ID):
    print("\n Retrieving user videos from Playlist ID ... \n")

    # Send request
    request = yt_client.playlistItems().list(
        part="contentDetails",
        playlistId=playlist_ID,
        maxResults=50, # limited to 50 per request
    )
    response = request.execute()

    video_IDs = []

    # Videos are displayed on several pages. If we don't get all the videos on the first page, the request
    # will contain a "nextPageToken" that we will try to get. If it doesn't exist, it means we got all the user videos.

    # try to get variable
    next_page_token = response.get("nextPageToken")

    while next_page_token:
        for item in response["items"]:
            video_IDs.append(item["contentDetails"]["videoId"])

        if "nextPageToken" in response:
            next_page_token = response["nextPageToken"]
            request = yt_client.playlistItems().list(
                part="contentDetails",
                playlistId=playlist_ID,
                maxResults=50,
                pageToken=next_page_token,
            )
            response = request.execute()
        else:
            break

    return video_IDs


def get_video_details(yt_client, video_ids):
    all_video_stats = []

    for ids in chunks(video_ids, 50):
        ids_str = ",".join(ids)
        request = yt_client.videos().list(
            part="snippet,statistics",
            id=ids_str
        )
        response = request.execute()

        all_video_stats.extend(video_stats_from_response(response))

    # Export the information in a dataframe
    df = pd.DataFrame(all_video_stats)
    print("Verify number of videos: ", len(df))
    return df

def video_stats_from_response(response):
    """
    Extract relevant information for each video of the Playlist (title, published_date, nb_views, ...)
    :param response:
    :return:
    """
    for video in response["items"]:
        video_stats = dict(Title=video["snippet"]["title"],
                           Video_URL="youtube.com/watch?v="+video["id"],
                           Published_date=video["snippet"]["publishedAt"],
                           Description=video["snippet"]["description"],
                           # If video doesn't contain tags, it will throw an error so we use get method
                           Tags=video["snippet"].get("tags", []),
                           # same here for thumbnail, maxres not always available
                           Thumbnail_URL=video["snippet"]["thumbnails"].get("maxres", {}).get("url", video["snippet"]["thumbnails"].get("standard", {}).get("url", "")),
                           Views=video["statistics"].get("viewCount", 0),
                           Likes=video["statistics"].get("likeCount", 0),
                           Comments=video["statistics"].get("commentCount", 0))
        yield video_stats

def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def verify_entered_yt_channel_id(channel_ID=None):
    if channel_ID is None:
        raise ValueError("channel_id_or_username must be provided")

    if channel_ID:
        channel_url = f'https://www.youtube.com/channel/{channel_ID}'
        response = requests.head(channel_url)
        # Try to reach channel
        if response.status_code == 200:
            return True
        else:
            return False


def add_views_per_day(df):
    """
    From the basic dataframe and videos information, we create 2 new columns that will contain the
    video age (today's date - published date)
    Views per days since this video age date
    """

    # Convert the Published_date string column to datetime objects
    df['Published_date'] = pd.to_datetime(df['Published_date']).dt.date

    current_date = datetime.now().date()

    df['Video_Age'] = (current_date - df['Published_date']).dt.days

    df['Views'] = df['Views'].astype(int)

    df['Views_per_day'] = df['Views'] / df['Video_Age']

    # Trier les vidéos par taux de vues par jour (Views_per_day) en ordre décroissant
    df_sorted = df.sort_values(by='Views_per_day', ascending=False)

    return df_sorted


if __name__ == "__main__":
    # Specify Channel ID

    RERUN_API = True
    filename = None

    if RERUN_API:
        # channel_ID = CHANNEL_ID
        channel_ID_or_handle = input("Enter Channel YouTube ID: ")

        does_channel_exist = verify_entered_yt_channel_id(channel_ID_or_handle)

        if does_channel_exist:
            yt_client = create_client(API_KEY)

            # Get Channel Data & the ID of the user's upload playlist
            channel_name, nb_subscribers, nb_views, playlist_ID, nb_videos = get_channel_data(yt_client, channel_ID_or_handle)
            print("Channel: ", channel_name)
            print("Subscriber Count: ", nb_subscribers)
            print("View Count: ", nb_views)
            print("*** Playlist ID ***:", playlist_ID)
            print("Number of videos", nb_videos)

            # Extract the video IDs from the user's upload Playlist
            video_IDs_list = get_yt_videos_ids(yt_client, playlist_ID)

            # Get information of all videos (upload_date, nb_views, ...)
            all_video_stats_df = get_video_details(yt_client, video_IDs_list)

            # Get Video Age & Views per day
            sorted_df_by_views_per_day = add_views_per_day(all_video_stats_df)

            sorted_df_by_views_per_day.to_csv("test.csv")
            # Plot sorted DF with over & save it
            hover_data, filename = plot_df(sorted_df_by_views_per_day, channel_name)

    if filename is not None:
        # Classify samples & export it as csv & save graph
        classify_samples(filename)







