# Models package
from app import db
from models.constants import ROLES, PROJECT_STATUS

# Import models after constants to avoid circular imports
from models.user import User
from models.project import Project
from models.funding import Funding
from models.watchlist import WatchlistItem as Watchlist
from models.project_update import ProjectUpdate
from models.notification import Notification
from models.milestone import Milestone

# Make sure to export db and constants
__all__ = ['db', 'User', 'Project', 'Funding', 'Watchlist', 'ProjectUpdate', 
           'Notification', 'Milestone', 'ROLES', 'PROJECT_STATUS']
