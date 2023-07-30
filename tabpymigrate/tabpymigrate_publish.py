"""
This will help in publishing Objects from filesystem to Tableau server
"""
import csv
import os
import tableauserverclient as TSC


def getTableauAuth(server_address, username=None, password=None, tag_name=None, site_id=None, is_personal_access_token=False):
    server = TSC.Server(server_address, use_server_version=True,
                        http_options={'verify': False})

    if is_personal_access_token:
        tableau_auth = TSC.PersonalAccessTokenAuth(username, password, site_id)
    else:
        tableau_auth = TSC.TableauAuth(username, password, site_id)

    return server, tableau_auth


# Common Parameters and function for download
def read_download_csv(csv_filename):
    if os.path.isfile(csv_filename) is True:
        csvfile = open(csv_filename, 'r', newline='')
        return csv.DictReader(csvfile)
    else:
        print("CSV File not found:" + str(csv_filename))
        return []


def write_publish_csv(csv_filename):
    fieldnames = ['Sno', 'Type', 'ProjectName', 'Name', 'Show_Tabs', 'Hidden_Views', 'Path', 'Response', 'Details']
    csvfile = open(csv_filename, 'w', newline='')
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    return writer


def publish_flow(server, project_id, filepath):
    new_flow = TSC.FlowItem(project_id=project_id)
    overwrite_true = TSC.Server.PublishMode.Overwrite
    flow = server.flows.publish(new_flow, filepath, overwrite_true)
    return flow


def publish_datasource(server, project_id, filepath):
    new_ds = TSC.DatasourceItem(project_id=project_id)
    overwrite_true = TSC.Server.PublishMode.Overwrite
    datasource = server.datasources.publish(new_ds, filepath, overwrite_true)
    return datasource


def publish_workbook(server, project_id, filepath, show_tabs=True, hidden_views=[]):
    new_wb = TSC.WorkbookItem(project_id=project_id, show_tabs=show_tabs)
    overwrite_true = TSC.Server.PublishMode.Overwrite
    workbook = server.workbooks.publish(new_wb, filepath, overwrite_true,
                                        skip_connection_check=True,
                                        hidden_views=hidden_views)
    return workbook


def publish_flows(server, filesystem_path, project_list, response_details=[]):
    # Setup download path and CSV output
    csvreader = read_download_csv(os.path.join(filesystem_path, 'flows.csv'))
    csvwriter = write_publish_csv(os.path.join(filesystem_path, 'flows_publish.csv'))

    # Create temp path if not exist
    temp_path = os.path.join(filesystem_path, '_temp')
    os.makedirs(temp_path, exist_ok=True)

    for flow in csvreader:
        print(flow)
        project_name = flow['ProjectName']
        project_id = project_list.get(project_name)
        if project_id is not None:
            try:
                flowFile = flow['Path']
                published_flow = publish_flow(server, project_id, flowFile)
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
                published_datasource = publish_datasource(server, project_id, filePath)
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
        print("show_tabs", show_tabs)
        display_views = workbook['Views']
        hidden_views = []
        if project_id is not None:
            try:
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
        server, tableau_auth = getTableauAuth(server_address, username=username, password=password, tag_name=None, site_id=site_id, is_personal_access_token=is_personal_access_token)

        with server.auth.sign_in(tableau_auth):
            project_list = get_project_list(server)
            print("starting publish")
            # publish objects to server from filesystem/metadata csv
            response_details = publish_flows(server, filesystem_path, project_list, response_details)
            response_details = publish_datasources(server, filesystem_path, project_list, response_details)
            response_details = publish_workbooks(server, filesystem_path, project_list, response_details, username=username, password=password)

        print(response_details)
        return 0, response_details
    except Exception as e:
        response_details = "Error in TabPyMigrate Publish Execution:" + str(e)
        print(response_details)
        return 1, response_details


if __name__ == '__main__':
    # Provide fileystem path where files are downloaded
    filesystem_path = ''

    # Tableau Server connection settings
    server_address = ''
    site_id = None
    username = ''
    password = ''
    is_personal_access_token = False

    # Execute Publish function
    tabpymigrate_publish(server_address=server_address,
                         site_id=site_id,
                         username=username,
                         password=password,
                         is_personal_access_token=is_personal_access_token,
                         filesystem_path=filesystem_path)
