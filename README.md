
# YouTube Video Scrapper API

Scrap YouTube Channel all videos and return data in .csv file


## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

`API_KEY`

  
## Code Reference

### `YouTube()`

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `API_KEY` | `string` | **Required**. Your API key |

### `construct_service()`

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `None`      |  | No parameter required |

### `upload_response()`

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `service` |  | Instance of YouTube Class |
| `channel_id` | str | YouTube Channel ID |

| Return | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| playlist ID | str | Playlist ID of all videos |

### `get_playlist_items()`

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `service` |  | Instance of YouTube Class |
| `playlist ID` | str | Playlist ID of videos |

| Return | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| Videos Info | list | List of all videos information |

### `convert_duration_to_seconds()`

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `duration` | str | duration in format '*00***H***00***M***00***S**' |

| Return | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| seconds | int | Video duration in seconds |


### `create_csv()`

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `data` | list | data received from `get_playlist_items()` | 
| `file_name` | str | name of the file to be saved with |




  
## Roadmap

- Add API_KEY to .env file

- Create instance of YouTube class

- Create connection with API using `Construct_service()`

- Retrieve playlist id using `upload_response()`

- Retrieve Videos details using `get_playlist_items()`

- Create csv file using `create_csv()`
  
## Features

- Descriptive Code
- OOP Code

  
## Lessons Learned

- Use of YouTube API 
- KeyError Exception handling
- Create batches of data
- Using regex to convert time format
- Pandas DataFrame
  
## Tech Stack

**Client:** Python, Pandas

**Server:** YouTube API

  
## Authors

- [@jawad5311](https://github.com/jawad5311)

  