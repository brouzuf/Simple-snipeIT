# Simple Snipe-IT Asset Management Helper

This Django application provides a simplified interface for common asset management tasks using the Snipe-IT API.

## Features

*   **User Asset Viewing:** View assets assigned to a user by searching for their employee number. This view displays assets across all categories, with an option to filter by a specific category.
*   **Asset Assignment:** Assign assets to users by asset tag. Users select an asset category from all available 'asset' type categories in Snipe-IT, and the system validates that the assigned asset belongs to the selected category.
*   **Asset Unassignment:** Unassign assets from users by asset tag or (previously) by asset ID (direct asset ID unassignment link might be deprecated or less prominent).
*   **Admin Configuration for Featured Categories:** Administrators can select a list of 'Featured Categories'. These categories are then used by the 'Featured Asset List Page'.
*   **Featured Asset List Page:** A dedicated page (`/assets/featured/`) displays assets belonging only to the admin-selected 'Featured Categories'. It shows the assigned user (if any), category, and other asset properties that are configurable via `simpleSnipeIT/settings.py`.
*   **Restricted Admin Access:** Application administration features (like configuring featured categories) are restricted to users belonging to a specific Snipe-IT group.

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
    *   `SECRET_KEY`: A strong, unique secret key for Django. (Generate one if not present in `.env.example`)

5.  **Apply Database Migrations:**
    ```bash
    python manage.py migrate
    ```
    This will set up the database, including the `AssetCategoryConfiguration` table used for storing the list of featured categories.

6.  **Run the Development Server:**
    ```bash
    python manage.py runserver
    ```
    The application will typically be available at `http://127.0.0.1:8000/`.

## Additional Configuration

### Featured Asset List Display (in `simpleSnipeIT/settings.py`)

The "Featured Asset List Page" can be customized to display specific asset properties. This is configured via the `NEW_ASSET_LIST_DISPLAY_PROPERTIES` setting in `simpleSnipeIT/settings.py`.

This setting is a Python list of dictionaries. Each dictionary defines a column for the list:
*   `'label'`: The text that will appear as the column header.
*   `'path'`: A dot-separated string representing the path to the desired value within the Snipe-IT asset data structure (as returned by the API).

Example:
```python
NEW_ASSET_LIST_DISPLAY_PROPERTIES = [
    {'label': 'Asset Name', 'path': 'name'},
    {'label': 'Asset Tag', 'path': 'asset_tag'},
    {'label': 'Serial', 'path': 'serial'},
    {'label': 'Model', 'path': 'model.name'},
    {'label': 'Status', 'path': 'status_label.name'},
    # You can add more custom fields:
    # {'label': 'Purchase Date', 'path': 'purchase_date.formatted'},
    # {'label': 'Warranty', 'path': 'warranty_expires.formatted'},
    # {'label': 'Location', 'path': 'location.name'},
]
```
The "Assigned To" and "Category" columns are displayed by default before these configured properties.

## Authentication and Authorization

*   **User Authentication:** User "login" is based on validating the `SNIPEIT_API_TOKEN` (provided in `.env`) against the Snipe-IT API (`/users/me` endpoint). A successful validation sets an authenticated flag in the user's session.
*   **Admin Privileges:** Specific views, such as "Configure Featured Categories" (`/configure_categories/`), require admin privileges.
    *   Admin status is determined by checking if the authenticated user (associated with the application's `SNIPEIT_API_TOKEN`) is a member of the Snipe-IT user group whose ID is specified in the `SNIPEIT_ADMIN_GROUP_ID` environment variable.
    *   The admin status flag (`is_admin`) is stored in the session upon successful login if the user meets the criteria.
*   **Logout:** The "Logout" functionality clears relevant session data, including authentication and admin status flags, effectively revoking access to protected views and admin features.

```
