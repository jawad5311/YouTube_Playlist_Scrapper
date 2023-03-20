# YouTube Video Scrapper API

Scrap YouTube Channels by search query and also scrape channel videos and return data in .csv file


## Features

- Extract channel videos
- Extract channel data
- Object Oriented Code
- Descriptive Code



## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

`API_KEY`


## Roadmap

- Add API_KEY to .env file

- Create instance of YouTube class

- Then call the related function with appropriate parameter


## Code Reference

### YouTube()

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `API_KEY` | string | **Required**. Your API key |


### extract_channel_videos()

| Parameter     | Type | Description               |
| :------------ | :--- | :------------------------ |
| `channel_id` | str  | Channel ID     |

| Return      | Type | Description                    |
| :---------- | :--- | :----------------------------- |
| CSV file   | file | .csv file with all videos of the channel |


### extract_videos_from_playlist()

| Parameter     | Type | Description               |
| :------------ | :--- | :------------------------ |
| `youtube_playlist` | str  | link of the youtube playlist |

| Return      | Type | Description                    |
| :---------- | :--- | :----------------------------- |
| CSV file | file | .csv file with all the videos in the playlist |


### extract_channels_by_keyword()

| Parameter     | Type | Description               |
| :------------ | :--- | :------------------------ |
| search_query  | str  | Search query to be request |

| Return      | Type | Description                    |
| :---------- | :--- | :----------------------------- |
| | CSV file | file | .csv file with all the channels |


### extract_videos_by_keyword()

| Parameter     | Type | Description               |
| :------------ | :--- | :------------------------ |
| `search_query`| str | Search query to be requested |

| Return      | Type | Description                    |
| :---------- | :--- | :----------------------------- |
| | CSV file | file | .csv file with all the videos |




## Lessons Learned

- Use of YouTube API
- Errors Exception handling
- Processing of data in batches
- Extracting data from .json
- Time handling using datetime
- Use of Regex
- Pandas DataFrame


## Tech Stack

**Client:** Python, Jupyter Notebook

**Server:** YouTube API


## Authors

- [@jawad5311](https://github.com/jawad5311)
