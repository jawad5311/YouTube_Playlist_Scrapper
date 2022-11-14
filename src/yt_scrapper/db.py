

import os
import dotenv

import mysql.connector as connector


dotenv.load_dotenv()

# db_user = os.environ.get('DB_USER')
# db_pass = os.environ.get('DB_PASS')


class Competitor:
    def __init__(self, db_user, db_password):
        self.conn = self.create_connection(db_user, db_password)
        pass

    @staticmethod
    def create_connection(user, password):
        """
        Create connection with database using username and password
        Returns:
                database connection object
        """
        conn = connector.connect(
            host='localhost',
            user=user,
            password=password
        )
        return conn
