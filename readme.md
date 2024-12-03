# Flask CRUD Application

A modern CRUD (Create, Read, Update, Delete) application built with Flask, HTMX, Tailwind CSS, and SQLite. This application demonstrates real-time data manipulation with a clean, responsive interface.

## Features

- ✨ Create, Read, Update, and Delete operations for managing people records
- 🔍 Real-time search functionality
- 📄 Pagination with dynamic loading
- 🎯 HTMX for seamless, JavaScript-free interactions
- 💾 SQLite database for data persistence
- 🎨 Tailwind CSS for modern styling

## Requirements

- Python 3.9 or higher
- Poetry for dependency management

## Dependencies

- Flask - Web framework
- Pydantic - Data validation
- Python-dotenv - Environment variable management
- Flask-CORS - Cross-Origin Resource Sharing support
- Watchdog - File system monitoring

## Installation

1. Clone the repository:

```bash
git clone [repository-url]
cd crud_app_01
```

2. Install dependencies using Poetry:

```bash
poetry install
```

3. Set up environment variables:
   Create a `.env` file in the root directory with:

```
FLASK_SECRET_KEY=your_secret_key_here
```

4. Initialize the database:

```bash
flask init-db
```

## Running the Application

1. Start the Flask server:

```bash
poetry run python app.py
```

2. Access the application at `http://localhost:5000`

## API Endpoints

- `GET /` - Main page with people listing
- `GET /load_more` - Load additional records (pagination)
- `POST /create` - Create a new person record
- `GET/POST /edit/<id>` - Edit existing person record
- `DELETE /delete/<id>` - Delete a person record
- `GET /search` - Search through people records

## Data Model

Person:

- `id`: Integer (Primary Key)
- `name`: String
- `age`: Integer

## Features in Detail

### Real-time Search

- Dynamic search functionality that updates results as you type
- Searches across both name and age fields

### Pagination

- Loads records in configurable page sizes
- Dynamic "Load More" functionality
- Automatic detection of end of records

### Modal Forms

- Clean modal interfaces for create and edit operations
- Form validation on both client and server side

### Responsive Design

- Mobile-friendly interface
- Clean, modern UI with Tailwind CSS

## Development

The application uses Poetry for dependency management. To add new dependencies:

```bash
poetry add package_name
```

For development dependencies:

```bash
poetry add --dev package_name
```
