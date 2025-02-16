from app import app, db
from flask_migrate import Migrate
from flask_script import Manager

# Initialize the manager
manager = Manager(app)
migrate = Migrate(app, db)  # Initialize Migrate

# Add the migration commands to the manager
manager.add_command('db', migrate)

if __name__ == '__main__':
    manager.run()