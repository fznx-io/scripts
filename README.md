# Scripts Collection

A collection of utility scripts for database and infrastructure management.

## indexing.py

MongoDB index management script with JIRA integration.

### Features
- Automated MongoDB index creation
- JIRA ticket tracking and status updates
- PostgreSQL integration for credential management
- Jenkins build linking
- Error handling with automatic JIRA notifications

### Requirements
- Python 3.x
- psycopg2
- pymongo
- jira

### Environment Variables
- `SERVICE` - Service identifier
- `ADMIN_PWD` - PostgreSQL admin password
- `DATABASE` - Target database name
- `COLLECTION` - MongoDB collection name
- `NEW_INDEX` - Index field to create
- `ISSUE_KEY` - JIRA issue key
- `JIRA_TOKEN` - JIRA API token
- `BUILD_URL` - Jenkins build URL

### Usage
Set required environment variables and run:
```bash
python indexing.py
```

The script will:
1. Connect to PostgreSQL to retrieve MongoDB credentials
2. Connect to target MongoDB database
3. Transition JIRA ticket to "In Progress"
4. Create specified index on collection
5. Update JIRA ticket with build status
