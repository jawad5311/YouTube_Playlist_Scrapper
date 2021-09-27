from Google import Create_Service


# Creating YouTube class to communicate with YouTube API
class YouTube:
    def __init__(self, secret_file, scopes: list = None):
        self.secret_file = secret_file
        self.scopes = scopes

    def construct_service(self):
        """
            Responsible for creating service instance from 'google.Create_Service'
        """
        API_SERVICE = 'youtube'
        API_VERSION = 'v3'
        service = Create_Service(self.secret_file, API_SERVICE, API_VERSION, self.scopes)
        return service
