import csv
import logging
from google.cloud import resourcemanager_v3
from google.cloud import run_v2
from google.cloud import functions_v1
from google.api_core.exceptions import GoogleAPIError

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def get_accessible_projects():
    """Returns a list of active project IDs the authenticated user can access."""
    logging.info("Fetching accessible projects...")
    client = resourcemanager_v3.ProjectsClient()
    projects = []
    
    try:
        # Searching without a query returns all projects the user has roles/viewer on
        request = resourcemanager_v3.SearchProjectsRequest()
        page_result = client.search_projects(request=request)
        for project in page_result:
            if project.state != resourcemanager_v3.Project.State.ACTIVE:
                continue

            project_id = project.project_id or ""
            if project_id.startswith("sys-"):
                continue

            projects.append(project_id)
    except Exception as e:
        logging.error(f"Failed to fetch projects. Ensure you are authenticated: {e}")
        
    logging.info(f"Found {len(projects)} accessible active projects.")
    return projects

def get_cloud_run_services(project_id):
    """Fetches all Cloud Run services for a given project across all locations."""
    services_data = []
    client = run_v2.ServicesClient()
    # The '-' wildcard tells the API to search across all GCP regions
    parent = f"projects/{project_id}/locations/-" 
    
    try:
        request = run_v2.ListServicesRequest(parent=parent)
        page_result = client.list_services(request=request)
        for service in page_result:
            services_data.append({
                'Project_ID': project_id,
                'Type': 'Cloud Run',
                'Name': service.name.split('/')[-1],
                'URL': service.uri
            })
    except GoogleAPIError:
        # Silently skip if the Cloud Run API is not enabled in this project
        pass 
    except Exception as e:
        logging.debug(f"Unexpected error checking Cloud Run in {project_id}: {e}")
        
    return services_data

def get_cloud_functions(project_id):
    """Fetches all Cloud Functions for a given project across all locations."""
    functions_data = []
    client = functions_v1.CloudFunctionsServiceClient()
    parent = f"projects/{project_id}/locations/-"
    
    try:
        request = functions_v1.ListFunctionsRequest(parent=parent)
        page_result = client.list_functions(request=request)
        for function in page_result:
            functions_data.append({
                'Project_ID': project_id,
                'Type': 'Cloud Function',
                'Name': function.name.split('/')[-1],
                'URL': function.https_trigger.url if function.https_trigger else 'No HTTP Trigger'
            })
    except GoogleAPIError:
        # Silently skip if the Cloud Functions API is not enabled
        pass
    except Exception as e:
        logging.debug(f"Unexpected error checking Cloud Functions in {project_id}: {e}")
        
    return functions_data

def main():
    projects = get_accessible_projects()
    if not projects:
        logging.error("No projects found. Exiting.")
        return

    all_endpoints = []
    
    for project_id in projects:
        logging.info(f"Scanning project: {project_id}...")
        
        run_services = get_cloud_run_services(project_id)
        if run_services:
            all_endpoints.extend(run_services)
            
        functions = get_cloud_functions(project_id)
        if functions:
            all_endpoints.extend(functions)

    # Write results to CSV
    output_file = 'gcp_endpoints_inventory.csv'
    if all_endpoints:
        keys = all_endpoints[0].keys()
        with open(output_file, 'w', newline='', encoding='utf-8') as output_csv:
            dict_writer = csv.DictWriter(output_csv, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(all_endpoints)
        logging.info(f"Scan complete! Successfully wrote {len(all_endpoints)} endpoints to {output_file}.")
    else:
        logging.info("Scan complete. No Cloud Run services or HTTP Cloud Functions found.")

if __name__ == "__main__":
    main()