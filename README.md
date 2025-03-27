# Breaking Point MCP Agent CMS

A Content Management System for the Breaking Point MCP Agent to store test configurations, results, reports, and media files.

## Features

- Manage test environments and devices under test (DUTs)
- Create and run test configurations
- Store and analyze test results
- Generate and download reports
- Upload and view media files (videos, screenshots, etc.)
- RESTful API for automation
- Web interface for user interaction

## Architecture

The CMS consists of the following components:

- **API**: RESTful API for interacting with the CMS
- **Database**: SQLAlchemy ORM for storing structured data
- **Storage**: Interface for storing files (local or S3-compatible)
- **Web Interface**: Flask-based web interface for user interaction

## Installation

### Prerequisites

- Python 3.7 or higher
- Pip package manager
- Breaking Point MCP Agent

### Setup

1. Clone the repository:

```bash
git clone https://github.com/example/BP_MCP_Agent_CMS.git
cd BP_MCP_Agent_CMS
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure the environment:

Copy the `.env.example` file to `.env` and edit it with your configuration:

```bash
cp .env.example .env
# Edit .env with your settings
```

5. Initialize the database and run migrations:

```bash
./scripts/init_and_migrate.sh
```

6. Create a storage directory:

```bash
mkdir -p storage_files
```

## Usage

### Running the CMS

Start the CMS server:

```bash
flask run
```

The server will start at http://localhost:5000 by default.

### API Endpoints

The CMS provides the following API endpoints:

- `/api/environments` - Manage test environments
- `/api/devices` - Manage devices under test
- `/api/test-configs` - Manage test configurations
- `/api/test-runs` - Manage test runs
- `/api/reports` - Manage reports
- `/api/media` - Manage media files
- `/api/users` - Manage users
- `/api/auth` - Authentication

### Web Interface

The CMS provides a web interface at http://localhost:5000 with the following pages:

- Dashboard - Overview of recent test runs
- Test Configurations - Manage test configurations
- Test Runs - View test runs and results
- Reports - Generate and view reports
- Media Gallery - View and upload media files
- Environments - Manage test environments
- Devices - Manage devices under test
- Users - Manage users

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
├── tests/                    # Tests for the CMS
├── config/                   # Configuration
├── app.py                    # Main application entry point
├── requirements.txt          # Python dependencies
└── .env                      # Environment variables
```

### Running Tests

Run the tests with pytest:

```bash
pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
