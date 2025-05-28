from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from unittest.mock import patch, MagicMock
import requests

class UserAuthTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        self.asset_list_url = reverse('asset_list')
        self.logout_url = reverse('logout')
        self.index_url = reverse('index')

        # Store original API settings to restore them if necessary, though mocks should handle this
        self.original_api_url = settings.SNIPEIT_API_URL
        self.original_api_token = settings.SNIPEIT_API_TOKEN

    def tearDown(self):
        # Restore original settings if they were changed directly (though not typical with mocks)
        settings.SNIPEIT_API_URL = self.original_api_url
        settings.SNIPEIT_API_TOKEN = self.original_api_token

    @patch('userCheckIO.views.requests.get')
    def test_login_successful(self, mock_requests_get):
        # Mock a successful API response for the /users?limit=1 check
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'success', 'messages': 'User details'} # Example data
        mock_requests_get.return_value = mock_response

        response = self.client.post(self.login_url)
        
        self.assertTrue(self.client.session.get('snipeit_authenticated'))
        self.assertEqual(self.client.session.get('snipeit_api_token'), settings.SNIPEIT_API_TOKEN)
        # Modified assertRedirects to not fetch the redirect response, avoiding a second API call
        self.assertRedirects(response, self.asset_list_url, fetch_redirect_response=False)
        mock_requests_get.assert_called_once_with(
            f"{settings.SNIPEIT_API_URL.rstrip('/')}/users?limit=1",
            headers={
                "Authorization": f"Bearer {settings.SNIPEIT_API_TOKEN}",
                "Accept": "application/json",
            },
            timeout=10
        )

    @patch('userCheckIO.views.requests.get')
    def test_login_failed_api_error(self, mock_requests_get):
        # Mock an API error response
        mock_response = MagicMock()
        mock_response.status_code = 401 # Unauthorized
        mock_response.text = "Invalid token"
        mock_requests_get.return_value = mock_response

        response = self.client.post(self.login_url)
        
        self.assertFalse(self.client.session.get('snipeit_authenticated'))
        self.assertEqual(response.status_code, 200) # Should re-render login page
        self.assertContains(response, "Snipe-IT API authentication failed")

    @patch('userCheckIO.views.requests.get')
    def test_login_failed_connection_error(self, mock_requests_get):
        # Mock a connection error
        mock_requests_get.side_effect = requests.exceptions.RequestException("Connection timed out")

        response = self.client.post(self.login_url)
        
        self.assertFalse(self.client.session.get('snipeit_authenticated'))
        self.assertEqual(response.status_code, 200) # Should re-render login page
        self.assertContains(response, "Error connecting to Snipe-IT API")

    @patch('userCheckIO.views.requests.get') # Mock for asset fetching
    def test_asset_list_authenticated(self, mock_asset_get):
        # Mock a successful asset fetch
        mock_asset_response = MagicMock()
        mock_asset_response.status_code = 200
        mock_asset_response.json.return_value = {"total":1,"rows":[{"id":1,"name":"Test Asset","asset_tag":"12345","model":{"name":"Test Model"}}]}
        mock_asset_get.return_value = mock_asset_response
        
        # Manually log in the user by setting session
        session = self.client.session
        session['snipeit_authenticated'] = True
        session['snipeit_api_token'] = settings.SNIPEIT_API_TOKEN # Ensure token is in session if view uses it
        session.save()

        response = self.client.get(self.asset_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Asset") # Check if asset data is in template

    def test_asset_list_unauthenticated(self):
        response = self.client.get(self.asset_list_url)
        self.assertRedirects(response, f"{self.login_url}?next={self.asset_list_url}")

    def test_logout(self):
        # Manually log in the user
        session = self.client.session
        session['snipeit_authenticated'] = True
        session['snipeit_api_token'] = "testtoken"
        session.save()

        response = self.client.get(self.logout_url)
        
        self.assertFalse(self.client.session.get('snipeit_authenticated'))
        self.assertIsNone(self.client.session.get('snipeit_api_token'))
        self.assertRedirects(response, self.index_url)

    @patch('userCheckIO.views.requests.get') # Mock for asset fetching
    def test_index_page_authenticated(self, mock_asset_get):
        session = self.client.session
        session['snipeit_authenticated'] = True
        session.save()
        response = self.client.get(self.index_url)
        self.assertContains(response, "View Assets")
        self.assertContains(response, "Logout")
        self.assertNotContains(response, "Login")

    def test_index_page_unauthenticated(self):
        response = self.client.get(self.index_url)
        self.assertNotContains(response, "View Assets")
        self.assertNotContains(response, "Logout")
        self.assertContains(response, "Login")
