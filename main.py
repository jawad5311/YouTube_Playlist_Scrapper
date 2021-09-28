from Google import Create_Service
from googleapiclient.discovery import build

import os
import dotenv


dotenv.load_dotenv()


# Creating YouTube class to communicate with YouTube API
class YouTube:
    def __init__(self, secret_file, key, scopes: list = None):
        self.secret_file = secret_file
        self.key = key
        self.scopes = scopes

    def construct_service(self):
        """
            Responsible for creating service instance from 'google.Create_Service'
        """
        API_SERVICE = 'youtube'
        API_VERSION = 'v3'
        service = Create_Service(self.secret_file, API_SERVICE, API_VERSION, self.scopes)
        return service

    def construct_service_2(self):
        """
        Creates service object from build method
        """

        API_SERVICE = 'youtube'
        API_VERSION = 'v3'
        service = build(
            API_SERVICE,
            API_VERSION,
            developerKey=self.key
        )
        return service

    @staticmethod
    def upload_response(service, channel_id: str) -> str:
        """
        Send request to retrieve uploaded videos response as playlist ID.

            Parameters:
                service: Instance of Create_Service()
                    service object created using construct_service()
                channel_id: str
                    Channel's id required for request
            Returns:
                str: playlist_id
        """
        request = service.channels().list(
            part='contentDetails',
            id=channel_id
        )

        response = request.execute()  # Send request and receive response

        # Extract playlist_id from the received response

        pass

