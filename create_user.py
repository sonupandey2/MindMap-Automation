"""
CLI script to create a user account for MindMap from the backend.
Usage: python create_user.py <username> <password>
username: admin and password: admin
"""

import sys
from app import create_app
from models import db
from models.user import User

def main():
    if len(sys.argv) != 3:
        print("Usage: python create_user.py <username> <password>")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]

    app = create_app()
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"Error: User '{username}' already exists.")
            sys.exit(1)

        # Create new user
        new_user = User(username=username)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()
        
        print(f"Success: User '{username}' created successfully!")

if __name__ == '__main__':
    main()
