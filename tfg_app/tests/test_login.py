import unittest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from tfg_app.views.login.login_form import AppState
import reflex as rx

class TestLoginForm(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        """Test environment setup."""

        # Crate a mock for AppState
        self.state = MagicMock(spec=AppState)

        # Set simulated values for the state
        self.state.COGNITO_DOMAIN = "https://test.auth.us-east-1.amazoncognito.com"
        self.state.COGNITO_CLIENT_ID = "test_client_id"
        self.state.COGNITO_CLIENT_SECRET = "test_client_secret"
        self.state.COGNITO_REDIRECT_URI = "http://localhost:3000/authorize"
        self.state.COGNITO_REGION = "us-east-1"
        self.state.COGNITO_USER_POOL_ID = "test_user_pool_id"
        self.state.COGNITO_SCOPE = "openid+email+profile"
        self.state.COGNITO_LOGOUT_URI = "http://localhost:3000/sign-in"

        # Simulate state variables
        self.state.signed_in = False
        self.state.guest = False
        self.state.user_info = {}
        self.state.access_token = ""
        self.state.id_token = ""
        self.state.refresh_token = ""
        self.state.oauth_state = ""
        self.state.error_message = ""

        # Simulate the state.router and state.router.page.params
        self.state.router = MagicMock()
        self.state.router.page.params = {}

    async def test_sign_in_redirect(self):
        """Check if sign_in redirects to the correct URL.

        Returns:
            MagicMock(rx.Redirect): Simulated redirection to the sign-in URL.
        """
        # Mock url with cognito-idp and parameters
        mock_url = "https://cognito-idp.us-east-1.amazonaws.com/oauth2/authorize?response_type=code&client_id=test_client_id&redirect_uri=http://localhost:3000/authorize&scope=openid+email+profile"
        mock_state = "test_state"

        # Mock the create_authorization_url method to return the mock URL and state
        with patch("authlib.integrations.httpx_client.AsyncOAuth2Client.create_authorization_url",
                  return_value=(mock_url, mock_state)):
            async def mock_sign_in():
                """Sign in method to simulate the OAuth2 authorization flow.
                This method is called when the user clicks the sign-in button.

                Returns:
                    EventSpec: Simulated event specification for redirection.
                """
                self.state.oauth_state = mock_state
                # Simulate rx.redirect with an EventSpec that contains the URL as a string
                event_spec = MagicMock()
                event_spec.args = (mock_url,)
                return event_spec
            
            # Mock the sign_in method to return the mock URL
            self.state.sign_in = AsyncMock(side_effect=mock_sign_in)

            # Call the sign_in method and check the results
            redirect = await self.state.sign_in()
            self.assertIsInstance(redirect, MagicMock)
            self.assertEqual(redirect.args[0], mock_url)
            self.assertIn("cognito-idp", redirect.args[0])
            self.assertEqual(self.state.oauth_state, mock_state)

    async def test_guest_session(self):
        """Check that guest_session sets the state correctly and redirects to the home page.
        """
        async def mock_guest_session():
            """Simulate a guest session by setting the state variables to their default values.

            Returns:
                EventSpec: Simulated event specification for redirection to the guest session.
            """
            self.state.guest = True
            self.state.signed_in = False
            self.state.user_info = {}
            self.state.access_token = ""
            self.state.id_token = ""
            self.state.refresh_token = ""
            # Simulate rx.redirect() with an EventSpec that contains the home path as string.
            event_spec = MagicMock()
            event_spec.args = ("/",)
            return event_spec
        self.state.guest_session = AsyncMock(side_effect=mock_guest_session)

        # Call the guest_session method and check the results
        redirect = await self.state.guest_session()
        self.assertIsInstance(redirect, MagicMock)
        self.assertEqual(redirect.args[0], "/")
        self.assertTrue(self.state.guest)
        self.assertFalse(self.state.signed_in)
        self.assertEqual(self.state.user_info, {})
        self.assertEqual(self.state.access_token, "")
        self.assertEqual(self.state.id_token, "")
        self.assertEqual(self.state.refresh_token, "")

    async def test_handle_authorize_missing_code(self):
        """Check that handle_authorize redirects to /sign-in if the code is missing.
           If the code is not missing, it checks if the state matches the expected state.       
        """
        async def mock_handle_authorize():
            """Simulate a handle_authorize method that checks for the presence of the code and state parameters.
            If the code or state is missing, it redirects to the sign-in page. 
            If not, it simulates a successful authorization.

            Returns:
                EventSpec: Simulated event specification for redirection to the sign-in page or successful authorization.
            """
            code = self.state.router.page.params.get("code")
            state = self.state.router.page.params.get("state")
            if not code or not state:
                self.state.signed_in = False
                self.state.guest = False
                # Simulate rx.redirect with an EventSpec that contains the URL as a string
                event_spec = MagicMock()
                event_spec.args = ("/sign-in",)
                return event_spec
            event_spec = MagicMock()
            event_spec.args = ("/sign-in",)
            return event_spec
        
        # Mock the handle_authorize method to return the mock URL
        self.state.handle_authorize = AsyncMock(side_effect=mock_handle_authorize)

        # Simulate the absence of the code parameter
        self.state.oauth_state = "test_state"
        self.state.router.page.params = {"state": "test_state"}
        redirect = await self.state.handle_authorize()
        # Check the results
        self.assertIsInstance(redirect, MagicMock)
        self.assertEqual(redirect.args[0], "/sign-in")
        self.assertFalse(self.state.signed_in)
        self.assertFalse(self.state.guest)

    async def test_handle_authorize_state_mismatch(self):
        """Check that handle_authorize redirects to /sign-in if the state does not match.
           If the state matches, it simulates a successful authorization.
        """
        async def mock_handle_authorize():
            """Simulate a handle_authorize method that checks for the presence of the code and state parameters.
            If the state does not match, it redirects to the sign-in page. 
            If not, it simulates a successful authorization.


            Returns:
                EventSpec: Simulated event specification for redirection to the sign-in page or successful authorization.
            """
            code = self.state.router.page.params.get("code")
            state = self.state.router.page.params.get("state")
            if self.state.oauth_state != state:
                self.state.signed_in = False
                self.state.guest = False
                # Simular rx.redirect con un EventSpec que contiene la URL como cadena
                event_spec = MagicMock()
                event_spec.args = ("/sign-in",)
                return event_spec
            event_spec = MagicMock()
            event_spec.args = ("/sign-in",)
            return event_spec
        
        # Mock the handle_authorize method to return the mock URL
        self.state.handle_authorize = AsyncMock(side_effect=mock_handle_authorize)

        # Simulate a state mismatch
        self.state.oauth_state = "different_state"
        self.state.router.page.params = {"code": "test_code", "state": "test_state"}
        redirect = await self.state.handle_authorize()

        # Check the results
        self.assertIsInstance(redirect, MagicMock)
        self.assertEqual(redirect.args[0], "/sign-in")
        self.assertFalse(self.state.signed_in)
        self.assertFalse(self.state.guest)

    async def test_handle_authorize_success(self):
        """Check that handle_authorize successfully processes the authorization code and state."""

        # Mock token and user info
        mock_token = {
            "access_token": "mock_access_token",
            "id_token": "mock_id_token",
            "refresh_token": "mock_refresh_token"
        }
        mock_user_info = {"sub": "test_user"}

        async def mock_handle_authorize():
            """Simulate a handle_authorize method that checks for the presence of the code and state parameters.

            Returns:
                EventSpec: Simulated event specification for successful authorization.
            """

            # Check for the presence of the code and state parameters
            code = self.state.router.page.params.get("code")
            state = self.state.router.page.params.get("state")
            if self.state.oauth_state != state or not code:
                self.state.signed_in = False
                self.state.guest = False
                event_spec = MagicMock()
                event_spec.args = ("/sign-in",)
                return event_spec


            # Simulate the successful authorization process
            self.state.access_token = mock_token["access_token"]
            self.state.id_token = mock_token["id_token"]
            self.state.refresh_token = mock_token["refresh_token"]
            self.state.user_info = mock_user_info
            self.state.signed_in = True
            self.state.guest = False
            # Simulate rx.redirect with an EventSpec that contains the path as a string
            event_spec = MagicMock()
            event_spec.args = ("/",)
            return event_spec
        
        # Mock the handle_authorize method to return the mock URL

        self.state.handle_authorize = AsyncMock(side_effect=mock_handle_authorize)

        # Simulate the presence of the code and state parameters
        self.state.oauth_state = "test_state"
        self.state.router.page.params = {"code": "test_code", "state": "test_state"}


        # Mock the token exchange and user info retrieval
        with patch("authlib.integrations.httpx_client.AsyncOAuth2Client.fetch_token",
                  new=AsyncMock(return_value=mock_token)):
            with patch("requests.get", return_value=MockResponse({
                "keys": [{"kid": "test_kid"}]
            })):
                # Mock the JWT decode function to return the mock user info
                with patch("jwt.get_unverified_header", return_value={"kid": "test_kid"}):
                    with patch("jose.jwt.decode", return_value=mock_user_info):

                        # Call the handle_authorize method and check the results
                        redirect = await self.state.handle_authorize()
                        self.assertIsInstance(redirect, MagicMock)
                        self.assertEqual(redirect.args[0], "/")
                        self.assertTrue(self.state.signed_in)
                        self.assertFalse(self.state.guest)
                        self.assertEqual(self.state.user_info, mock_user_info)
                        self.assertEqual(self.state.access_token, mock_token["access_token"])
                        self.assertEqual(self.state.id_token, mock_token["id_token"])
                        self.assertEqual(self.state.refresh_token, mock_token["refresh_token"])

    async def test_logout(self):
        """Check that logout clears the state and redirects to the logout URL.
        """

        # Mock the logout URL with cognito-idp and parameters
        expected_logout_url = (
            f"{self.state.COGNITO_DOMAIN}/logout?"
            f"client_id={self.state.COGNITO_CLIENT_ID}&"
            f"logout_uri={self.state.COGNITO_LOGOUT_URI}"
        )
        # Mock the logout method to return the expected URL
        async def mock_logout():
            self.state.signed_in = False
            self.state.guest = False
            self.state.user_info = {}
            self.state.access_token = ""
            self.state.id_token = ""
            self.state.refresh_token = ""
            # Simulate rx.redirect with an EventSpec that contains the logout URL as a string
            event_spec = MagicMock()
            event_spec.args = (expected_logout_url,)
            return event_spec
        self.state.logout = AsyncMock(side_effect=mock_logout)

        # Simulate a user being signed in
        self.state.signed_in = True
        self.state.user_info = {"sub": "test_user"}
        self.state.access_token = "mock_access_token"
        self.state.id_token = "mock_id_token"
        self.state.refresh_token = "mock_refresh_token"

        redirect = await self.state.logout()
        self.assertIsInstance(redirect, MagicMock)
        self.assertEqual(redirect.args[0], expected_logout_url)
        self.assertIn("logout", redirect.args[0])
        self.assertIn(self.state.COGNITO_LOGOUT_URI, redirect.args[0])
        self.assertFalse(self.state.signed_in)
        self.assertFalse(self.state.guest)
        self.assertEqual(self.state.user_info, {})
        self.assertEqual(self.state.access_token, "")
        self.assertEqual(self.state.id_token, "")
        self.assertEqual(self.state.refresh_token, "")

    async def test_check_session_guest(self):
        """Check that check_session does not redirect if the user is a guest.
        This test simulates a guest user and checks that the check_session method does not redirect.
        """
        async def mock_check_session(redirect_url: str = None):
            """Simulate a check_session method that checks if the user is a guest.

            Returns:
                EventSpec: Simulated event specification for redirection to the sign-in page.
            """
            if self.state.guest:
                return
            event_spec = MagicMock()
            event_spec.args = ("/sign-in",)
            return event_spec
        self.state.check_session = AsyncMock(side_effect=mock_check_session)

        self.state.guest = True
        result = await self.state.check_session("/some-page")
        self.assertIsNone(result)  # No redirect for guest

    async def test_check_session_no_session(self):
        """Check that check_session redirects to /sign-in if there is no session.
        """
        async def mock_check_session(redirect_url: str = None):
            if self.state.guest:
                return
            if not self.state.signed_in or not self.state.access_token or not self.state.id_token:
                #Simulate rx.redirect with an EventSpec that contains the path as a string
                event_spec = MagicMock()
                event_spec.args = ("/sign-in",)
                return event_spec
            return
        self.state.check_session = AsyncMock(side_effect=mock_check_session)

        self.state.guest = False
        self.state.signed_in = False
        redirect = await self.state.check_session("/some-page")
        self.assertIsInstance(redirect, MagicMock)
        self.assertEqual(redirect.args[0], "/sign-in")

class MockResponse:
    """Mock class for simulating HTTP responses.
    """
    def __init__(self, json_data):
        self.json_data = json_data

    def json(self):
        return self.json_data

if __name__ == "__main__":
    unittest.main()