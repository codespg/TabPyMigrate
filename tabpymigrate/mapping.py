import json
import zipfile
import os
from tableaudocumentapi import Workbook


def parse_zipfile(filename):
    if zipfile.is_zipfile(filename):
        return zipfile.ZipFile(filename)
    return None

def get_flow_from_archive(zip_content):
    flow_file_name = 'flow'
    for filename in zip_content.namelist():
        if filename == flow_file_name:
            flow_file = zip_content.open(filename).read()
            return json.loads(flow_file)
    return None


def update_flow_mapping(flow, server_address=None, project_list={}, filesystem=None):
    # Open flow file in Zip file and flow_content
    flow_path = flow['Path']
    flow_extension = os.path.splitext(flow_path)[1].split('.')[-1]
    try:
        zip_content = parse_zipfile(flow_path)
        flow_content = get_flow_from_archive(zip_content)
    except Exception as error:
        response += f"\nError in opening flow file: {str(e)}"
        raise f"\nError in opening flow file: {str(e)}"         

    # Process and update serverUrl and projectLuid
    response = ""
    for node in flow_content['nodes']:
        if flow_content['nodes'][node].get('serverUrl') is not None:
            flow_content['nodes'][node]['serverUrl'] = server_address
            response += "serverUrl updated:" + str(flow_content['nodes'][node]['serverUrl'])
        if flow_content['nodes'][node].get('projectLuid') is not None:
            if flow_content['nodes'][node].get('projectName') is not None:
                projectName = flow_content['nodes'][node].get('projectName')
                newprojectLuid = project_list.get(projectName)
                if newprojectLuid is not None:
                    flow_content['nodes'][node]['projectLuid'] = newprojectLuid
                    response += "\nUpdated projectLuid:" + newprojectLuid
                else:
                    response += f"\nError: Target Project not found in server - {projectName}"
            else:
                response += f"\nError: projectLuid found but projectName not found - {projectName}"

    # Create project folder in temp directory and updated filename
    updated_filename = flow['Name'] + "." + flow_extension
    updated_filepath = os.path.join(filesystem, '_temp', flow['ProjectName'])
    os.makedirs(updated_filepath, exist_ok=True)
    updated_file = os.path.join(updated_filepath, updated_filename)

    # Read zip file contents and write to new file
    try:
        new_zipfile = zipfile.ZipFile(updated_file, 'w', zipfile.ZIP_DEFLATED)
        zip_content = parse_zipfile(flow_path)
        for filename in zip_content.namelist():
            if filename == 'flow':
                    new_zipfile.writestr('flow', json.dumps(flow_content))
            else:
                    file_content = zip_content.open(filename).read()
                    new_zipfile.writestr(filename, file_content)
        response += "\nUpdated flow file saved successfully:" + str(updated_file)
    except Exception as e:
            response += f"\nError in saving updated flow file: {str(e)}"
            raise f"\nError in saving updated flow file: {str(e)}"
    finally:
         new_zipfile.close()
         zip_content.close()

    return updated_file, response


def get_dbname_for_source_to_target():
     return


def update_workbook_mapping(workbookpath, server_address):
    sourceWB = Workbook(workbookpath)
    for datasource in sourceWB.datasources:
        for connection in datasource.connections:
            print(connection.server, connection.dbname, connection.username)
            connection.server = server_address
            #connection.dbname = get_dbname_for_source_to_target(
            #                                    connection.dbname,
            #                                    source_datasource,
            #                                    taget_datasource)

    sourceWB.save()
    return workbookpath

