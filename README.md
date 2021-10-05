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

- To extract channel videos:

  - Retrieve playlist id using `upload_response()`

  - Retrieve Videos details using `get_playlist_items()`
  - Extract video details using `get_videos_data()`

  - Create csv file using `create_csv()`

- To extract channels using search query
  - Retrieve channels id's using `get_channel_ids()`

  - Filter channels based on videos and subs using `filter_channels()`


  - Filter active channels using `filter_active_channels()`


  - Extract each channel data using `extract_channel_data()`


  - Create a .csv file using `create_csv()`


## Code Reference

### YouTube()

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `API_KEY` | string | **Required**. Your API key |

### upload_response()

| Parameter    | Type | Description               |
| :----------- | :--- | :------------------------ |
| `channel_id` | str  | YouTube Channel ID        |

| Return      | Type | Description               |
| :---------- | :--- | :------------------------ |
| playlist ID | str  | Playlist ID of all videos |

### get_playlist_items()

| Parameter     | Type | Description               |
| :------------ | :--- | :------------------------ |
| `playlist ID` | str  | Playlist ID of videos     |

| Return      | Type | Description                    |
| :---------- | :--- | :----------------------------- |
| Videos Info | list | List of all videos information |

### get_videos_data()

| Parameter     | Type | Description               |
| :------------ | :--- | :------------------------ |
| `data` | list  | Data retrieved from `get_playlist_items()` |

| Return      | Type | Description                    |
| :---------- | :--- | :----------------------------- |
| DataFrame | pd.DataFrame | Returns pandas dataframe |

### get_channel_ids()

| Parameter     | Type | Description               |
| :------------ | :--- | :------------------------ |
| query     |    str  | Search query to be request |
| no_of_channels | int  | Default: 300, No of channels to scrape|

| Return      | Type | Description                    |
| :---------- | :--- | :----------------------------- |
|  | list | List containing channel ids |

### filter_channels()

| Parameter     | Type | Description               |
| :------------ | :--- | :------------------------ |
| `channels_ids`| list | List containing channels id's |
| `sub_min` | int  | Minimum no. channel subscribers   |
| `sub_ma` | int  | Maximum no. channel subscribers   |
| `min_vid_count` | int  | Minimum no. videos on channel   |


| Return      | Type | Description                    |
| :---------- | :--- | :----------------------------- |
|  | list | List containing filtered channels |

### filter_active_channels()

| Parameter     | Type | Description               |
| :------------ | :--- | :------------------------ |
| `data`     |    list  | list containing channels info |
| `activity` | int  | Recent activity made by channel in days|

| Return      | Type | Description                    |
| :---------- | :--- | :----------------------------- |
|  | list | List containing active channels |

### extract_channel_data()

| Parameter     | Type | Description               |
| :------------ | :--- | :------------------------ |
| `data` | list  | List containing channels data|

| Return      | Type | Description                    |
| :---------- | :--- | :----------------------------- |
|  | DataFrame | Pandas DataFrame |

### convert_duration_to_seconds()

| Parameter  | Type | Description                                        |
| :--------- | :--- | :------------------------------------------------- |
| `duration` | str  | duration in format '\*00**_H_**00**_M_**00**\*S**' |

| Return  | Type | Description               |
| :------ | :--- | :------------------------ |
| seconds | int  | Video duration in seconds |

### create_csv()

| Parameter   | Type | Description                               |
| :---------- | :--- | :---------------------------------------- |
| `data`      | DataFrame | Pandas DataFrame |
| `file_name` | str  | Name by which file is to be saved|





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
