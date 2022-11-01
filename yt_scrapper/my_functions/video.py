
import pandas as pd
from .funcs import convert_duration_to_seconds


def extract_videos_data(service,
                        videos_id: list) -> pd.DataFrame:
    """
    Args:
        service: YouTube API service instance
        videos_id: list of videos ID's

    Returns:
        Pandas dataframe

    Retrieve YouTube videos statistics and creates data frame
    """

    videos_data = []  # Use to hold videos info

    for batch_range in range(0, len(videos_id), 50):
        # Creates videos batches of 50
        videos_batch = videos_id[batch_range:batch_range + 50]

        response = service.videos().list(
            id=videos_batch,
            part='contentDetails,snippet,statistics',
            maxResults=50
        ).execute()

        items = response['items']  # Holds videos data from response

        for item in items:
            title = item['snippet']['title']
            date = item['snippet']['publishedAt'][:10]
            views = item['statistics']['viewCount']

            vid_id = item['id']
            video_url = f'https://www.youtube.com/watch?v={vid_id}'

            duration = item['contentDetails']['duration']
            duration = convert_duration_to_seconds(duration)

            try:
                likes = item['statistics']['likeCount']
            except KeyError:
                item['statistics']['likeCount'] = '0'
                likes = item['statistics']['likeCount']

            try:
                dislikes = item['statistics']['dislikeCount']
            except KeyError:
                item['statistics']['dislikeCount'] = '0'
                dislikes = item['statistics']['dislikeCount']

            try:
                comments = item['statistics']['commentCount']
            except KeyError:
                item['statistics']['commentCount'] = '0'
                comments = item['statistics']['commentCount']

            videos_data.append({
                'title': title,
                'date': date,
                'views': views,
                'URL': video_url,
                'duration': duration,
                'likes': likes,
                'dislikes': dislikes,
                'comments': comments
            })

    print(f'Total videos data extracted: {len(videos_data)}')

    return pd.DataFrame(videos_data)

