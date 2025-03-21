# Personal Website

A full-featured personal website with blog functionality, user authentication, and admin panel.

## Features

- **Public Frontend**: Responsive design with blog, about, and contact pages
- **User Authentication**: Login, registration, and role-based access control
- **Blog System**: Create, edit, and publish articles with categories and tags
- **Comments System**: User comments with moderation
- **Admin Panel**: Manage users, content, and website settings
- **Contributor Panel**: Allow users to contribute content
- **REST API**: Endpoints for frontend JavaScript interaction

## Project Structure

```
personal_website/
│
├── backend/                    # Python backend code
│   ├── app.py                  # Main application entry point
│   ├── config.py               # Configuration settings
│   ├── requirements.txt        # Python dependencies
│   ├── database/               # Database models and schema
│   ├── authentication/         # Authentication logic
│   ├── routes/                 # Route handlers
│   └── utils/                  # Helper functions
│
├── frontend/
│   ├── static/                 # Static assets (CSS, JS, images)
│   └── templates/              # HTML templates
│
├── tests/                      # Testing directory
│
├── .gitignore                  # Git ignore file
├── README.md                   # Project documentation
└── docker-compose.yml          # Docker setup for development/deployment
```

## Technology Stack

- **Backend**: Python, Flask, SQLAlchemy
- **Frontend**: HTML, CSS, JavaScript
- **Database**: PostgreSQL
- **Authentication**: JWT, Session-based
- **Containerization**: Docker, Docker Compose

## Getting Started

### Prerequisites

- Python 3.11+
- Docker and Docker Compose (optional)
- PostgreSQL (if not using Docker)

### Installation

#### Using Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/personal_website.git
   cd personal_website
   ```

2. Create a `.env` file with environment variables:
   ```
   SECRET_KEY=your-secret-key
   JWT_SECRET_KEY=your-jwt-secret-key
   ```

3. Build and start the containers:
   ```bash
   docker-compose up -d
   ```

4. Initialize the database:
   ```bash
   docker-compose exec web flask init-db
   ```

5. Create an admin user:
   ```bash
   docker-compose exec web flask create-admin
   ```

6. Access the website at `http://localhost:5000`

#### Manual Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/personal_website.git
   cd personal_website
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```

4. Set environment variables:
   ```bash
   export FLASK_APP=backend/app.py
   export FLASK_ENV=development
   export SECRET_KEY=your-secret-key
   export JWT_SECRET_KEY=your-jwt-secret-key
   export DATABASE_URL=postgresql://username:password@localhost:5432/personal_website
   ```

5. Initialize the database:
   ```bash
   flask init-db
   ```

6. Create an admin user:
   ```bash
   flask create-admin
   ```

7. Run the application:
   ```bash
   flask run
   ```

8. Access the website at `http://localhost:5000`

## User Roles

- **Viewer**: Can read articles and post comments
- **Contributor**: Can create and manage their own articles
- **Admin**: Full access to all features and management functions

## Development

### Database Migrations

When making changes to the database models:

```bash
# Generate a migration
flask db migrate -m "Migration message"

# Apply the migration
flask db upgrade
```

### Testing

Run tests with pytest:

```bash
pytest
```

### Code Style

Format code with Black:

```bash
black backend/
```

## Deployment

For production deployment, configure the following:

1. Uncomment the Nginx and Certbot services in `docker-compose.yml`
2. Create proper SSL certificates using Let's Encrypt
3. Set secure values for all environment variables
4. Configure proper database backups
5. Set `FLASK_ENV=production`

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Flask web framework
- SQLAlchemy ORM
- Bootstrap for responsive design
- Font Awesome for icons