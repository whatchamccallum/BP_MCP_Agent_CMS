# Breaking Point MCP Agent Content Management System

## Introduction

The Breaking Point MCP Agent CMS is a comprehensive content management system designed to work alongside the Breaking Point MCP Agent. It provides a centralized platform for storing, organizing, and managing all the data related to Breaking Point test environments, configurations, runs, results, reports, and media files.

## Key Features

- **Environment Management**: Store and organize test environment configurations
- **Device Management**: Manage devices under test (DUTs) with secure credential storage
- **Test Configuration Management**: Create, store, and version test configurations
- **Test Run Management**: Track all test runs with detailed status and results
- **Report Generation**: Generate various types of reports (standard, executive, detailed, compliance)
- **Media Storage**: Upload and organize media files (videos, screenshots) related to tests
- **User Management**: Control access with role-based permissions
- **RESTful API**: Programmatically interact with all CMS features
- **Web Interface**: User-friendly web interface for all operations
- **Integration with BP Agent**: Seamless interaction with the Breaking Point MCP Agent

## System Architecture

The CMS is built with a modular architecture that separates data persistence, storage management, and presentation:

### Database Layer

Uses SQLAlchemy ORM to support multiple database backends with models for:
- Environments
- Devices
- Test Configurations
- Test Runs
- Test Results
- Reports
- Media Files
- Users

### Storage Layer

Flexible storage interface with implementations for:
- Local File Storage: Simple storage on the local file system
- S3-Compatible Storage: Scalable storage using S3 or compatible services

### API Layer

RESTful API endpoints for all operations:
- CRUD operations for all data models
- Authentication and authorization
- File uploads and downloads
- Integration with Breaking Point MCP Agent

### Web Interface

User-friendly web interface built with:
- Flask templates
- Bootstrap for responsive design
- Chart.js for data visualization
- JavaScript for interactive elements

### Integration Layer

Integration with the Breaking Point MCP Agent for:
- Running tests
- Retrieving results
- Generating reports
- Creating charts

## Getting Started

### Installation

1. Clone the repository:
```bash
git clone https://github.com/example/BP_MCP_Agent_CMS.git
cd BP_MCP_Agent_CMS
```

2. Set up a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables in `.env`:
```
FLASK_ENV=development
FLASK_APP=app.py
SECRET_KEY=your-secret-key
DATABASE_URI=sqlite:///bp_mcp_agent_cms.db
STORAGE_TYPE=local
STORAGE_BASE_DIR=./storage_files
BP_MCP_AGENT_HOST=localhost
BP_MCP_AGENT_PORT=5000
```

5. Initialize the database:
```bash
python init_db.py
```

6. Run the application:
```bash
flask run
```

### Default Login

- Username: `admin`
- Password: `admin`

**Important**: Change the default password after first login.

## Usage

### Web Interface

Access the web interface at `http://localhost:5000` and use the navigation menu to:
- View the dashboard with recent activity and statistics
- Manage environments and devices
- Create and run test configurations
- View test runs and results
- Generate and download reports
- Upload and view media files
- Manage users (admin only)

### API

The RESTful API is available at `http://localhost:5000/api` with endpoints for:
- `/api/environments`: Manage test environments
- `/api/devices`: Manage devices under test
- `/api/test-configs`: Manage test configurations
- `/api/test-runs`: Manage test runs
- `/api/reports`: Manage reports
- `/api/media`: Manage media files
- `/api/users`: Manage users
- `/api/auth`: Authentication

## Integration with Breaking Point MCP Agent

The CMS integrates with the Breaking Point MCP Agent to:
1. Run tests configured in the CMS
2. Retrieve test results
3. Generate reports based on test results
4. Create visualizations of test data

The integration is handled by the `integration/bp_agent.py` module, which provides a client for the Breaking Point MCP Agent API.

## Customization

### Adding New Report Types

1. Create a new report generator in `api/report_generators/`
2. Update the `report.py` route to support the new report type
3. Add the new report type to the web interface

### Adding New Storage Backends

1. Implement the `StorageInterface` in a new module
2. Update the `storage/__init__.py` factory to support the new backend
3. Add configuration options to `config/__init__.py`

## Security Considerations

- All passwords are hashed using `pbkdf2_sha256`
- JWT authentication for API access
- Role-based access control for sensitive operations
- Secure file handling to prevent path traversal attacks
- CSRF protection for web forms
- Input validation for all API endpoints

## Development

### Directory Structure

```
BP_MCP_Agent_CMS/
├── api/                      # REST API for CMS
│   ├── routes/               # API route handlers
│   ├── models/               # Database models
│   └── controllers/          # Business logic
├── database/                 # Database configuration and migrations
│   └── migrations/           # Database schema migrations
├── storage/                  # File storage management
│   ├── local.py              # Local file storage implementation
│   ├── s3.py                 # S3-compatible storage implementation
│   └── storage.py            # Storage interface
├── web/                      # Web interface
│   ├── static/               # Static assets (CSS, JS, images)
│   ├── templates/            # HTML templates
│   └── views/                # Web route handlers
├── integration/              # Integration with BP MCP Agent
├── tests/                    # Tests for the CMS
├── config/                   # Configuration
└── app.py                    # Main application entry point
```

### Extending the CMS

The modular architecture makes it easy to extend the CMS:
- Add new models to `api/models/`
- Add new API routes to `api/routes/`
- Add new web views to `web/views/`
- Add new templates to `web/templates/`
- Add new integrations to `integration/`

## License

This project is licensed under the MIT License - see the LICENSE file for details.
