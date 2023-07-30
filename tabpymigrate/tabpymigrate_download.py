"""
This will help in downloading Tagged Objects from Tableau server
"""

import csv
import os
import tableauserverclient as TSC
# requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


# Function to get Tableau Server and Authentication
def getTableauAuth(server_url, username=None, password=None, tag_name=None,
                   site_id=None, is_personal_access_token=False):

    server = TSC.Server(server_url, use_server_version=True,
                        http_options={'verify': False})

    if is_personal_access_token:
        tableau_auth = TSC.PersonalAccessTokenAuth(username, password, site_id)
    else:
        tableau_auth = TSC.TableauAuth(username, password, site_id)

    return server, tableau_auth


# Common Parameters and function for download
def write_download_csv(csv_filename):
    fieldnames = ['Sno', 'Type', 'ProjectName', 'Name', 'Path', 'Show_Tabs', 'Views', 'Response', 'Details']
    csvfile = open(csv_filename, 'w', newline='')
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    return writer


# Download flows by tagname
def download_flows(server, filesystem_path, tag_name, response_details=[]):
    # Setup download path and CSV output
    flows_path = os.path.join(filesystem_path, 'flow')
    csvwriter = write_download_csv(os.path.join(filesystem_path, 'flows.csv'))

    count = 0
    for flow in TSC.Pager(server.flows):
        if tag_name in flow.tags:
            if flow.project_name is None:
                response = "Error"
                details = f"Could not retrieve project name for Flow '{flow.name}'. Skipping download."
                filepath = ''
            else:
                # Create the download path if it doesn't exist
                download_path = os.path.join(flows_path, flow.project_name)
                os.makedirs(download_path, exist_ok=True)

                # Download the flow
                try:
                    filepath = server.flows.download(flow.id, filepath=download_path)
                    response = "Success"
                    details = f"Flow '{flow.name}' downloaded successfully in '{filepath}'!"
                except Exception as e:
                    response = "Error"
                    details = "Error in download:" + str(e)

            count += 1
            flow_details = {'Sno': count,
                            'Type': 'Flow',
                            'Name': flow.name,
                            'ProjectName': flow.project_name,
                            'Path': filepath,
                            'Response': response,
                            'Details': details}
            csvwriter.writerow(flow_details)
            print("flow", flow_details, response)
            response_details.append(flow_details)
    return response_details


# Download datasource by tagname
def download_datasources(server, filesystem_path, tag_name, response_details=[]):
    # Setup download path and CSV output
    datasources_path = os.path.join(filesystem_path, 'datasource')
    csvwriter = write_download_csv(os.path.join(filesystem_path, 'datasources.csv'))

    count = 0
    for datasource in TSC.Pager(server.datasources):
        if tag_name in datasource.tags:
            if datasource.project_name is None:
                response = "Error"
                details = f"Could not retrieve project name for Datasource '{datasource.name}'. Skipping download."
                filepath = ''
            else:
                # Create the download path if it doesn't exist
                download_path = os.path.join(datasources_path, datasource.project_name)
                os.makedirs(download_path, exist_ok=True)

                # Download the Datasource
                try:
                    filepath = server.datasources.download(datasource.id, filepath=download_path)
                    response = "Success"
                    details = f"Datasource '{datasource.name}' downloaded successfully in '{filepath}'!"
                except Exception as e:
                    print(datasource)
                    print(str(e))
                    response = "Error"
                    details = "Error in download:" + str(e)

            count += 1
            datasource_details = {'Sno': count,
                                  'Type': 'Datasource',
                                  'Name': datasource.name,
                                  'ProjectName': datasource.project_name,
                                  'Path': filepath,
                                  'Response': response,
                                  'Details': details}
            csvwriter.writerow(datasource_details)
            response_details.append(datasource_details)
    return response_details


# Download workbook by tagname
def download_workbooks(server, filesystem_path, tag_name, response_details=[]):
    # Setup download path and CSV output
    workbooks_path = os.path.join(filesystem_path, 'workbook')
    csvwriter = write_download_csv(os.path.join(filesystem_path, 'workbooks.csv'))

    count = 0
    for workbook in TSC.Pager(server.workbooks):
        if tag_name in workbook.tags:
            if workbook.project_name is None:
                response = "Error"
                details = f"Could not retrieve project name for Workbook '{workbook.name}'. Skipping download."
                filepath = ''
            else:
                # Create the download path if it doesn't exist
                download_path = os.path.join(workbooks_path, workbook.project_name)
                os.makedirs(download_path, exist_ok=True)

                # Download the workbook
                try:
                    filepath = server.workbooks.download(workbook.id, filepath=download_path)
                    response = "Success"
                    details = f"Workbook '{workbook.name}' downloaded successfully in '{filepath}'!"
                except Exception as e:
                    response = "Error"
                    details = "Error in download:" + str(e)
            server.workbooks.populate_views(workbook)
            print(workbook.views)
            print(workbook.hidden_views)
            view_list = [view.name for view in workbook.views]
            for view in workbook.views:
                print(view.content_url)
                print(view.name)
                print(dir(view))
            count += 1
            workbook_details = {'Sno': count,
                                'Type': 'Workbook',
                                'Name': workbook.name,
                                'ProjectName': workbook.project_name,
                                'Show_Tabs': workbook.show_tabs,
                                'Views': view_list,
                                'Path': filepath,
                                'Response': response,
                                'Details': details}
            csvwriter.writerow(workbook_details)
            response_details.append(workbook_details)
    return response_details


def tabpymigrate_download(server_address='', username=None, password=None, filesystem_path=None, tag_name=None, site_id=None, is_personal_access_token=False):
    response_details = []
    try:
        # Create server and tableau_auth object
        server, tableau_auth = getTableauAuth(server_address, username=username, password=password, tag_name=None, site_id=site_id, is_personal_access_token=is_personal_access_token)

        # Authenticate to Tableau Server
        tableau_auth = TSC.TableauAuth(username, password, site_id=site_id)
        with server.auth.sign_in(tableau_auth):
            print("starting")
            # download objects from server to the filesystem for given tag_name
            response_details = download_flows(server, filesystem_path, tag_name, response_details)
            response_details = download_datasources(server, filesystem_path, tag_name, response_details)
            response_details = download_workbooks(server, filesystem_path, tag_name, response_details)

        print(response_details)
        return 0, response_details
    except Exception as e:
        response_details = "Error in TabPyMigrate Export Execution:" + str(e)
        print(response_details)
        return 1, response_details


if __name__ == '__main__':

    # Filesystem and Tag name
    filesystem_path = ''
    tag_name = ''

    # Tableau Server connection settings
    server_url = ''
    site_id = None
    username = ''
    password = ''
    is_personal_access_token = False

    # Call download function
    tabpymigrate_download(server_url=server_url,
                          site_id=site_id,
                          username=username,
                          password=password,
                          is_personal_access_token=is_personal_access_token,
                          tag_name=tag_name,
                          filesystem_path=filesystem_path
                          )
