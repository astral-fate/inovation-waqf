from app import create_app, db
from models.constants import ROLES, PROJECT_STATUS
from models.user import User
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta, timezone
import os

app = create_app()

# Add context processors for template filters
@app.template_filter('format_currency')
def format_currency(value):
    """Format a number as currency in Saudi Riyals"""
    if value is None:
        return "٠ ريال"
    
    # Convert value to float if it's a string
    if isinstance(value, str):
        try:
            value = float(value.replace(',', ''))
        except ValueError:
            return f"{value} ريال"  # Return as is if conversion fails
    
    # Format with thousands separator
    formatted = f"{value:,.0f}"
    
    # Convert to Arabic numerals
    arabic_numerals = {
        '0': '٠', '1': '١', '2': '٣', '4': '٤',
        '5': '٥', '6': '٦', '7': '٧', '8': '٨', '9': '٩',
        ',': '٬'
    }
    
    for english, arabic in arabic_numerals.items():
        formatted = formatted.replace(english, arabic)
    
    return f"{formatted} ريال"

@app.template_filter('format_percentage')
def format_percentage(value):
    """Format a number as a percentage in Arabic numerals"""
    if value is None:
        return "٠٪"
    
    # Round to 1 decimal place
    formatted = f"{value:.1f}"
    
    # Convert to Arabic numerals
    arabic_numerals = {
        '0': '٠', '1': '١', '2': '٣', '4': '٤',
        '5': '٥', '6': '٦', '7': '٧', '8': '٨', '9': '٩',
        '.': '٫'
    }
    
    for english, arabic in arabic_numerals.items():
        formatted = formatted.replace(english, arabic)
    
    return f"{formatted}٪"

@app.template_filter('format_days')
def format_days(days):
    """Format days in Arabic text"""
    if days <= 0:
        return "منتهي"
    
    # Convert to Arabic numerals
    arabic_numerals = {
        '0': '٠', '1': '١', '2': '٣', '4': '٤',
        '5': '٥', '6': '٦', '7': '٧', '8': '٨', '9': '٩'
    }
    
    formatted = str(days)
    for english, arabic in arabic_numerals.items():
        formatted = formatted.replace(english, arabic)
    
    return f"{formatted} يوم"

@app.template_filter('nl2br')
def nl2br(text):
    """Convert newlines to <br> tags"""
    if not text:
        return ""
    return text.replace('\n', '<br>')

@app.context_processor
def inject_now():
    # Use timezone-aware datetime instead of deprecated utcnow()
    return {'now': datetime.now(timezone.utc)}

def create_default_admin():
    """Create a default admin user if none exists"""
    with app.app_context():
        # First, create all tables if they don't exist
        db.create_all()
        
        # Check if any admin user exists
        admin = User.query.filter_by(user_type=ROLES['ADMIN']).first()
        if not admin:
            print("Creating default admin account...")
            admin = User(
                full_name='Admin User',
                email='admin@waqf-innovation.sa',
                password=generate_password_hash('admin123', method='pbkdf2:sha256'),
                user_type=ROLES['ADMIN'],
                created_at=datetime.now(timezone.utc)
            )
            db.session.add(admin)
            db.session.commit()
            print("Default admin account created.")
            print("Login with:")
            print("Email: admin@waqf-innovation.sa")
            print("Password: admin123")
        else:
            # Update admin password for testing
            admin.password = generate_password_hash('admin123', method='pbkdf2:sha256')
            db.session.commit()
            print("Admin password reset to 'admin123' for testing")

def reset_database():
    """Reset the database - USE WITH CAUTION"""
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        print("Creating all tables...")
        db.create_all()
        print("Database reset complete.")

if __name__ == '__main__':
    # First reset the database to ensure schema is up to date
    reset_database()
    
    # Then create default admin account
    create_default_admin()
    
    # Run the app
    app.run(debug=True)
