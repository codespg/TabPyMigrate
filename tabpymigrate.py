'''
    TabPyMigrate

    Tabpymigrate.py gets input from commandline or config.py and execute download and publish to tableau server.
'''
import argparse
import sys
import config
from tabpymigrate_download import tabpymigrate_download
from tabpymigrate_publish import tabpymigrate_publish


def execute(action=config.ACTION,
            tag_name=config.TAG_NAME,
            filesystem_path=config.FILESYSTEM_PATH,
            source_server_address=config.SOURCE_SERVER_ADDRESS,
            source_site_id=config.SOURCE_SITE_ID,
            source_username=config.SOURCE_USERNAME,
            source_password=config.SOURCE_PASSWORD,
            source_is_personal_access_token=config.SOURCE_IS_PERSONAL_ACCESS_TOKEN,
            target_server_address=config.TARGET_SERVER_ADDDRESS,
            target_site_id=config.TARGET_SITE_ID,
            target_username=config.TARGET_USERNAME,
            target_password=config.TARGET_PASSWORD,
            target_is_personal_access_token=config.TARGET_IS_PERSONAL_ACCESS_TOKEN
            ):
    '''
    TabPyMigrate Execute function to call download and publish
    '''

    if action.upper() not in ["DOWNLOAD", "PUBLISH","DOWNLOAD_AND_PUBLISH"]:
        print("Invalid Action given...")
        sys.exit()

    if action.upper() in ["DOWNLOAD", "DOWNLOAD_AND_PUBLISH"]:
        print("Starting the Download....")
        # Call download function
        tabpymigrate_download(server_address=source_server_address,
                              site_id=source_site_id,
                              username=source_username,
                              password=source_password,
                              is_personal_access_token=source_is_personal_access_token,
                              tag_name=tag_name,
                              filesystem_path=filesystem_path
                              )
        print("Completed the Download....")

    if action.upper() in ["PUBLISH", "DOWNLOAD_AND_PUBLISH"]:
        print("Starting the Publish....")
        # Execute Publish function
        tabpymigrate_publish(server_address=target_server_address,
                             site_id=target_site_id,
                             username=target_username,
                             password=target_password,
                             is_personal_access_token=target_is_personal_access_token,
                             filesystem_path=filesystem_path)
        print("Completed the Download....")


def tabpymigrate():
    '''
    TabPyMigrate function will parse argument and call execution
    '''
    # Create an argument parser
    parser = argparse.ArgumentParser(description="TabPyMigrate helps on Tableau content download and publish")

    # Add all the arguments
    parser.add_argument("-action", help="Action for Tabmigrate", choices=['DOWNLOAD', 'PUBLISH', 'DOWNLOAD_AND_PUBLISH'])
    parser.add_argument("-tag_name", help="Tag name for downloading tagged objects.")
    parser.add_argument("-filesystem_path", help="Filesystem path for download and publish")
    parser.add_argument("-source_server_address", help="Source Tableau server address.")
    parser.add_argument("-source_site_id", help="Source Tableau server Site name, Default to None", default=None)
    parser.add_argument("-source_username", help="Source Tableau server username for authentication.")
    parser.add_argument("-source_password", help="Source Tableau server password for authentication.")
    parser.add_argument("-source_is_personal_access_token", help="Source Tableau server authentication via personal access token? - Default False.", choices=["TRUE", "FALSE"])
    parser.add_argument("-target_server_address", help="Target Tableau server address.")
    parser.add_argument("-target_site_id", help="Target Tableau server Site name, Default to None", default=None)
    parser.add_argument("-target_username", help="Target Tableau server username for authentication.")
    parser.add_argument("-target_password", help="Target Tableau server password for authentication.")
    parser.add_argument("-target_is_personal_access_token", help="Target Tableau server authentication via personal access token? - Default False.", choices=["TRUE", "FALSE"])
    args = parser.parse_args()

    # Check if username and password are provided as arguments
    action = args.action if args.action is not None else config.ACTION
    tag_name = args.tag_name if args.tag_name is not None else config.TAG_NAME
    filesystem_path = args.filesystem_path if args.filesystem_path is not None else config.FILESYSTEM_PATH
    source_server_address = args.source_server_address if args.source_server_address is not None else config.SOURCE_SERVER_ADDRESS
    source_site_id = args.source_site_id if args.source_site_id is not None else config.SOURCE_SITE_ID
    source_username = args.source_username if args.source_username is not None else config.SOURCE_USERNAME
    source_password = args.source_password if args.source_password is not None else config.SOURCE_PASSWORD
    source_is_personal_access_token = True if ((args.source_is_personal_access_token is not None and args.source_is_personal_access_token == "TRUE")
                                               or (args.source_is_personal_access_token is None and config.SOURCE_IS_PERSONAL_ACCESS_TOKEN)) else False
    target_server_address = args.target_server_address if args.target_server_address is not None else config.TARGET_SERVER_ADDDRESS
    target_site_id = args.target_site_id if args.target_site_id is not None else config.TARGET_SITE_ID
    target_username = args.target_username if args.target_username is not None else config.TARGET_USERNAME
    target_password = args.target_password if args.target_password is not None else config.TARGET_PASSWORD
    target_is_personal_access_token = True if ((args.target_is_personal_access_token is not None and args.target_is_personal_access_token == "TRUE")
                                                or (args.target_is_personal_access_token is None and config.TARGET_IS_PERSONAL_ACCESS_TOKEN)) else False

    print(args)
    execute(action=action,
            tag_name=tag_name,
            filesystem_path=filesystem_path,
            source_server_address=source_server_address,
            source_site_id=source_site_id,
            source_username=source_username,
            source_password=source_password,
            source_is_personal_access_token=source_is_personal_access_token,
            target_server_address=target_server_address,
            target_site_id=target_site_id,
            target_username=target_username,
            target_password=target_password,
            target_is_personal_access_token=target_is_personal_access_token
            )


if __name__ == "__main__":
    tabpymigrate()
