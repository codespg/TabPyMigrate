'''
    config.py

    This file can contain configuration settings, constants, or any other
    variables that are required across different modules or parts of your application.
    Below are defined variables in TabPyMigrate

'''
# Download & Publish
ACTION=""
DOWNLOAD = True
PUBLISH = True

# Tag name for selectig the objects to download
TAG_NAME = ''

# Filesystem for Downloading and Publishing Tableau Objects
FILESYSTEM_PATH = ''

# Tableau Server Source connection settings - Source will be used for download
SOURCE_SERVER_ADDRESS = ''
SOURCE_SITE_ID = None
SOURCE_USERNAME = 'SRC'
SOURCE_PASSWORD = ''
SOURCE_IS_PERSONAL_ACCESS_TOKEN = False  # Give True if using Personal access token

# Tableau Server Target connection settings - Target will be used for publish
TARGET_SERVER_ADDDRESS = ''
TARGET_SITE_ID = None
TARGET_USERNAME = ''
TARGET_PASSWORD = ''
TARGET_IS_PERSONAL_ACCESS_TOKEN = False  # Give True if using Personal access token
