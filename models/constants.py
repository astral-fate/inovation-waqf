# Constants for the application

# User roles
ROLES = {
    'ADMIN': 'admin',
    'FUNDER': 'funder',
    'PROJECT_OWNER': 'project_owner'
}

# Project status types
PROJECT_STATUS = {
    'DRAFT': 'draft',
    'PENDING': 'pending',  # Added for backward compatibility
    'PENDING_REVIEW': 'pending',
    'REJECTED': 'rejected',
    'FUNDING': 'funding',
    'FUNDED': 'funded',
    'IN_PROGRESS': 'in_progress',
    'COMPLETED': 'completed'
}
