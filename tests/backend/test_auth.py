# Authentication tests for the AI Agent System
# This file contains tests for the authentication endpoints and logic

# Test cases:
# - test_user_signup(): Tests user registration endpoint
# - test_user_login(): Tests login and JWT token generation
# - test_invalid_credentials(): Tests login with wrong credentials
# - test_token_refresh(): Tests JWT token refresh functionality
# - test_password_hashing(): Tests password hashing and verification
# - test_get_current_user(): Tests the current user dependency
# - test_change_password(): Tests password change functionality

# Fixtures:
# - test_client(): Returns a FastAPI TestClient
# - test_user(): Creates a test user for authentication tests
# - authorized_client(): Returns a TestClient with auth headers 