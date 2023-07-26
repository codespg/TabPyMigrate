'''
    TabPyMigrate

    Tabpymigrate.py gets all input from config.py and execute download and publish for tableau server.
'''
from datetime import datetime
from tabpymigrate_download import tabpymigrate_download
from tabpymigrate_publish import tabpymigrate_publish
import os
import shutil
import csv
import config


def tabpymigrate():
    print("Starting the Download....")
    # Call download function
    tabpymigrate_download(server_url=config.SOURCE_SERVER_URL,
                          site_id=config.SOURCE_SITE_ID,
                          username=config.SOURCE_USERNAME,
                          password=config.SOURCE_PASSWORD,
                          is_personal_access_token=config.SOURCE_IS_PERSONAL_ACCESS_TOKEN,
                          tag_name=config.TAG_NAME,
                          filesystem_path=config.FILESYSTEM_PATH
                          )
    print("Completed the Download....")

    print("Starting the Publish....")
    # Execute Publish function
    tabpymigrate_publish(server_address=config.TARGET_SERVER_URL,
                         site_id=config.TARGET_SITE_ID,
                         username=config.TARGET_USERNAME,
                         password=config.TARGET_PASSWORD,
                         is_personal_access_token=config.TARGET_IS_PERSONAL_ACCESS_TOKEN,
                         filesystem_path=config.FILESYSTEM_PATH)
    print("Completed the Download....")

if __name__ == "__main__":
    tabpymigrate()
