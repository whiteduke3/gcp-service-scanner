# GCP Endpoint Scanner

When dealing with security audits or penetration tests, you are often given a list of vulnerable endpoint URLs (like `*.a.run.app` or `*.cloudfunctions.net`) without knowing which Google Cloud Projects they belong to. 

Without Organization-level Cloud Asset Viewer permissions, it is impossible to search Google Cloud top-down. This script solves that problem by taking a bottom-up approach. It iterates through every GCP project your user account has access to, checks all regions for Cloud Run services and Cloud Functions, and outputs a mapping of URLs to their respective Project IDs.



## Prerequisites

1. **Python 3.9–3.13** installed (3.12 recommended).  
   Note: Python 3.14 may currently fail with some Google Cloud dependencies (protobuf/upb).
2. **Google Cloud SDK (`gcloud`)** installed and authenticated.
3. You must have at least `roles/viewer` access to the projects you wish to scan. The script will only discover services in projects your account can see.

## Installation

1. Clone this repository:
   ```bash
   git clone <your-gitlab-repo-url>
   cd gcp-endpoint-scanner
   ```
2. Setup environment
   python3.12 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   gcloud auth application-default login
3. Run script
   python gcp_service_scanner.py
