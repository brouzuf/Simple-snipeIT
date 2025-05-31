# Simple Snipe-IT Asset Management Helper

This Django application provides a simplified interface for common asset management tasks using the Snipe-IT API.

## Features

*   **User Asset Viewing:** View assets assigned to a user by searching for their employee number.
*   **Asset Assignment:** Assign assets to users by asset tag.
*   **Asset Unassignment:** Unassign assets from users by asset tag or asset ID.
*   **Admin-Controlled Category Assignment:**
    *   Administrators can configure how asset categories are handled during assignment.
    *   **Select Mode:** Users choose an asset category from a dropdown, and the assigned asset must belong to that category.
    *   **Fixed Mode:** Administrators can predefine a specific list of asset categories allowed for assignment.
*   **Restricted Admin Access:** Application administration features are restricted to users belonging to a specific Snipe-IT group.

## Setup Instructions

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Create and Activate a Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    This project uses Poetry for dependency management.
    ```bash
    pip install poetry
    poetry install
    ```
    If you prefer to use `requirements.txt` (though `poetry.lock` is the primary source of truth):
    ```bash
    # Ensure pip is up to date
    pip install --upgrade pip
    # Export from Poetry (do this once if requirements.txt is outdated)
    # poetry export -f requirements.txt --output requirements.txt --without-hashes
    # Then install
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    Copy the example environment file:
    ```bash
    cp .env.example .env
    ```
    Edit the `.env` file and provide the necessary values:
    *   `SNIPEIT_API_URL`: The URL to your Snipe-IT API (e.g., `https://your-snipeit-instance.com/api/v1`).
    *   `SNIPEIT_API_TOKEN`: Your Snipe-IT API token.
    *   `SNIPEIT_ADMIN_GROUP_ID`: The ID of the Snipe-IT user group that should have admin privileges in this application.
    *   `DJANGO_DEBUG`: Set to `True` for development, `False` for production.
    *   `SECRET_KEY`: A strong, unique secret key for Django.

5.  **Apply Database Migrations:**
    ```bash
    python manage.py migrate
    ```

6.  **Run the Development Server:**
    ```bash
    python manage.py runserver
    ```
    The application will typically be available at `http://127.0.0.1:8000/`.
