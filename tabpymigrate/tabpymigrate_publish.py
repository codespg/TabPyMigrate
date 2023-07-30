"""
TabPyMigrate Publish Script

This script helps in publishing objects (flows, datasources, and workbooks) from the local file system to Tableau Server.
Objects are published to their respective projects based on the information provided in CSV files (flows.csv, datasources.csv,
and workbooks.csv). The publishing process is tracked, and details are stored in corresponding CSV files (flows_publish.csv,
datasources_publish.csv, and workbooks_publish.csv).

Requirements:
- Python 3.x
- tableauserverclient library (install using 'pip install tableauserverclient')

Usage:
1. Modify the server_address, username, password, filesystem_path, site_id, and is_personal_access_token
   variables in the 'tabpymigrate_publish' function to suit your Tableau Server environment and requirements.
2. Run the script to initiate the publishing process.
"""
import csv
import os
import tableauserverclient as TSC
from mapping import update_flow_mapping, update_workbook_mapping


# Function to get Tableau Server and Authentication
def gettableauauth(server_address, username=None, password=None,
                   site_id=None, is_personal_access_token=False):
    """
    Create Tableau Server and authentication objects.

    Args:
        server_url (str): The URL of the Tableau Server.
        username (str): Tableau Server username. Not required if using Personal Access Token.
        password (str): Tableau Server password. Not required if using Personal Access Token.
        tag_name (str): The tag name to filter objects during download.
        site_id (str): ID of the Tableau site. Not required if using Personal Access Token.
        is_personal_access_token (bool): Flag indicating whether Personal Access Token is being used.

    Returns:
        Tuple[TSC.Server, TSC.Auth]: The Tableau Server and authentication objects.
    """
    server = TSC.Server(server_address, use_server_version=True, http_options={'verify': False})

    if is_personal_access_token:
        tableau_auth = TSC.PersonalAccessTokenAuth(username, password, site_id)
    else:
        tableau_auth = TSC.TableauAuth(username, password, site_id)

    return server, tableau_auth


# Common Parameters and function for download
def read_download_csv(csv_filename):
    """
    Read the CSV file containing object metadata for download (flows.csv, datasources.csv, workbooks.csv).

    Args:
        csv_filename (str): The filename of the CSV to be read.

    Returns:
        csv.DictReader: A CSV reader object containing object metadata.
    """    
    if os.path.isfile(csv_filename) is True:
        csvfile = open(csv_filename, 'r', newline='')
        return csv.DictReader(csvfile)
    else:
        print("CSV File not found:" + str(csv_filename))
        return []


def write_publish_csv(csv_filename):
    """
    Create a CSV writer for storing details of the publishing process.

    Args:
        csv_filename (str): The filename of the CSV to be created.

    Returns:
        csv.DictWriter: A CSV writer object.
    """
    fieldnames = ['Sno', 'Type', 'ProjectName', 'Name', 'Show_Tabs', 'Hidden_Views', 'Path', 'Response', 'Details']
    csvfile = open(csv_filename, 'w', newline='')
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    return writer


def publish_flow(server, flow, project_id, filepath):
    """
    Publish a flow to Tableau Server.

    Args:
        server (TSC.Server): The Tableau Server object.
        project_id (str): The ID of the project to which the flow will be published.
        filepath (str): The local file path of the flow to be published.

    Returns:
        TSC.FlowItem: The published flow object.
    """
    new_flow = TSC.FlowItem(project_id=project_id, name=flow['Name'])
    overwrite_true = TSC.Server.PublishMode.Overwrite
    flow = server.flows.publish(new_flow, filepath, overwrite_true)
    return flow


def publish_datasource(server, datasource, project_id, filepath):
    """
    Publish a Datasource to Tableau Server.

    Args:
        server (TSC.Server): The Tableau Server object.
        project_id (str): The ID of the project to which the flow will be published.
        filepath (str): The local file path of the flow to be published.

    Returns:
        TSC.DatasourceItem: The published flow object.
    """
    new_ds = TSC.DatasourceItem(project_id=project_id, name=datasource['Name'])
    overwrite_true = TSC.Server.PublishMode.Overwrite
    datasource = server.datasources.publish(new_ds, filepath, overwrite_true)
    return datasource


def publish_workbook(server, project_id, filepath, show_tabs=True, hidden_views=[]):
    """
    Publish a Workbook to Tableau Server.

    Args:
        server (TSC.Server): The Tableau Server object.
        project_id (str): The ID of the project to which the flow will be published.
        filepath (str): The local file path of the flow to be published.

    Returns:
        TSC.WorkookItem: The published flow object.
    """
    new_wb = TSC.WorkbookItem(project_id=project_id, show_tabs=show_tabs)
    overwrite_true = TSC.Server.PublishMode.Overwrite
    workbook = server.workbooks.publish(new_wb, filepath, overwrite_true,
                                        skip_connection_check=True,
                                        hidden_views=hidden_views)
    return workbook


def publish_flows(server, filesystem_path, project_list, response_details=[]):
    """
    Publish flows to Tableau Server based on metadata from flows.csv.

    Args:
        server (TSC.Server): The Tableau Server object.
        filesystem_path (str): The path to the file system containing object metadata CSVs and objects to publish.
        project_list (dict): A dictionary containing project names as keys and project IDs as values.
        response_details (list, optional): A list to store details of the publishing response. Default is an empty list.

    Returns:
        list: A list containing dictionaries with details of the publishing response for each flow.
    """
    # Setup download path and CSV output
    csvreader = read_download_csv(os.path.join(filesystem_path, 'flows.csv'))
    csvwriter = write_publish_csv(os.path.join(filesystem_path, 'flows_publish.csv'))

    for flow in csvreader:
        print(flow)
        project_name = flow['ProjectName']
        project_id = project_list.get(project_name)
        if project_id is not None:
            try:
                flowFile = flow['Path']
                updated_flowFile, details = update_flow_mapping(flow, server.server_address,
                                                                project_list, filesystem_path)
                published_flow = publish_flow(server, flow, project_id, updated_flowFile)
                response = "Success"
                details = "Flow has been successfully published:"
                details += str(published_flow.webpage_url)
            except Exception as e:
                response = "Error"
                details = str(e)

        else:
            response = "Error"
            details = "Project not found in server:" + str(project_name)

        flow_details = {'Sno': flow['Sno'],
                        'Type': 'Flow',
                        'Name': flow['Name'],
                        'ProjectName': project_name,
                        'Path': flow['Path'],
                        'Response': response,
                        'Details': details}
        csvwriter.writerow(flow_details)
        response_details.append(flow_details)
    return response_details



def publish_datasources(server, filesystem_path, project_list, response_details=[]):
    """
    Publish Datasources to Tableau Server based on metadata from flows.csv.

    Args:
        server (TSC.Server): The Tableau Server object.
        filesystem_path (str): The path to the file system containing object metadata CSVs and objects to publish.
        project_list (dict): A dictionary containing project names as keys and project IDs as values.
        response_details (list, optional): A list to store details of the publishing response. Default is an empty list.

    Returns:
        list: A list containing dictionaries with details of the publishing response for each flow.
    """    
    # Setup download path and CSV output
    csvreader = read_download_csv(os.path.join(filesystem_path, 'datasources.csv'))
    csvwriter = write_publish_csv(os.path.join(filesystem_path, 'datasources_publish.csv'))

    for datasource in csvreader:
        print(datasource)
        project_name = datasource['ProjectName']
        project_id = project_list.get(project_name)
        filePath = datasource['Path']
        if project_id is not None:
            try:
                published_datasource = publish_datasource(server, datasource, project_id, filePath)
                response = "Success"
                details = "Datasource has been successfully published:"
                details += str(published_datasource.webpage_url)
            except Exception as e:
                response = "Error"
                details = str(e)

        else:
            response = "Error"
            details = "Project not found in server:" + str(project_name)

        datasource_details = {'Sno': datasource['Sno'],
                              'Type': 'Datasource',
                              'Name': datasource['Name'],
                              'ProjectName': project_name,
                              'Path': filePath,
                              'Response': response,
                              'Details': details}
        csvwriter.writerow(datasource_details)
        response_details.append(datasource_details)
    return response_details


def publish_workbooks(server, filesystem_path, project_list, response_details=[], username=None, password=None):
    """
    Publish workbooks to Tableau Server based on metadata from flows.csv.

    Args:
        server (TSC.Server): The Tableau Server object.
        filesystem_path (str): The path to the file system containing object metadata CSVs and objects to publish.
        project_list (dict): A dictionary containing project names as keys and project IDs as values.
        response_details (list, optional): A list to store details of the publishing response. Default is an empty list.

    Returns:
        list: A list containing dictionaries with details of the publishing response for each flow.
    """
    # Setup download path and CSV output
    csvreader = read_download_csv(os.path.join(filesystem_path, 'workbooks.csv'))
    csvwriter = write_publish_csv(os.path.join(filesystem_path, 'workbooks_publish.csv'))

    for workbook in csvreader:
        print(workbook)
        project_name = workbook['ProjectName']
        project_id = project_list.get(project_name)
        filePath = workbook['Path']
        show_tabs = workbook['Show_Tabs']
        show_tabs = False if show_tabs.lower() == 'false' else True
        display_views = workbook['Views']
        hidden_views = []
        if project_id is not None:
            try:
                filePathUpd = update_workbook_mapping(filePath,
                                                      server.server_address)
                published_workbook = publish_workbook(server, project_id, filePath, show_tabs=show_tabs, hidden_views=hidden_views)
                server.workbooks.populate_views(published_workbook)
                for view in published_workbook.views:
                    if view.name not in display_views:
                        hidden_views.append(view.name)
                if len(hidden_views) > 0:
                    print("hidden_views-publishing", hidden_views)
                    published_workbook = publish_workbook(server, project_id, filePath, show_tabs=show_tabs, hidden_views=hidden_views)
                response = "Success"
                details = "Workbook has been successfully published:"
                details += str(published_workbook.webpage_url)
            except Exception as e:
                response = "Error"
                details = str(e)

        else:
            response = "Error"
            details = "Project not found in server:" + str(project_name)

        workbook_details = {'Sno': workbook['Sno'],
                            'Type': 'Workbook',
                            'Name': workbook['Name'],
                            'ProjectName': project_name,
                            'Path': filePath,
                            'Show_Tabs': show_tabs,
                            'Hidden_Views': hidden_views,
                            'Response': response,
                            'Details': details}
        csvwriter.writerow(workbook_details)
        response_details.append(workbook_details)
    return response_details


def get_project_list(server):
    project_list = {}
    for project in TSC.Pager(server.projects):
        if project_list.get(project.name) is None:
            project_list[project.name] = project.id
        else:
            print("duplicate", project.name, project_list.get(project.name))
    return project_list


def tabpymigrate_publish(server_address, username=None, password=None, filesystem_path=None, site_id=None, is_personal_access_token=False):
    try:
        response_details = []
        # Create server and tableau_auth object
        server, tableau_auth = gettableauauth(server_address, username=username, password=password, site_id=site_id, is_personal_access_token=is_personal_access_token)

        with server.auth.sign_in(tableau_auth):
            project_list = get_project_list(server)
            print("Starting publish")
            # publish objects to server from filesystem/metadata csv
            response_details = publish_flows(server, filesystem_path, project_list, response_details)
            response_details = publish_datasources(server, filesystem_path, project_list, response_details)
            response_details = publish_workbooks(server, filesystem_path, project_list, response_details, username=username, password=password)

        print(response_details)
        return "Success", response_details
    except Exception as e:
        response_details = "Error in TabPyMigrate Publish Execution:" + str(e)
        print(response_details)
        return "Error", response_details

