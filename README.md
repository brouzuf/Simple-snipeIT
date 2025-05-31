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

*   **System Authentication:** The application uses a global `SNIPEIT_API_TOKEN` (set in the `.env` file) for its general operations that require API access. The "Login" page (`/admin_login/`) primarily serves to validate this global token against the Snipe-IT API (e.g., by fetching `/users/me`). A successful validation establishes a basic authenticated session for the application (`request.session['snipeit_authenticated'] = True`). This initial system login explicitly sets admin privileges to false (`request.session['is_admin'] = False`).

*   **Determining Admin Privileges:**
    *   Admin status (`request.session['is_admin']`) for the current browser session is determined *after* system authentication, specifically when a user's details are viewed via the employee number lookup (typically on the main page, leading to the `user_asset_view`).
    *   When an employee's record is successfully fetched, the application checks if that specific employee is a member of the Snipe-IT user group whose ID is defined in the `SNIPEIT_ADMIN_GROUP_ID` environment variable.
    *   If the looked-up employee belongs to this designated admin group, the `request.session['is_admin']` flag is set to `True`. Information about the employee who triggered admin rights is stored in `request.session['admin_granting_employee_info']`.
    *   If the looked-up employee is not in the admin group, or if the employee lookup fails, `request.session['is_admin']` is set to `False`, and any stored `admin_granting_employee_info` is cleared.

*   **Accessing Admin Areas:** Admin-only sections, such as the "Configure Featured Categories" page (`/configure_categories/`), are protected by a decorator that checks if `request.session.get('is_admin')` is `True`. Access is granted only if an admin employee has been successfully looked up in the current session.

*   **Logout:** The "Logout" functionality (`/logout/`) clears all relevant session data, including `snipeit_authenticated`, `is_admin`, and `admin_granting_employee_info`. This effectively revokes both system authentication and any admin privileges for the browser session, requiring a new "Login" and subsequent admin employee lookup to regain admin access.

```
