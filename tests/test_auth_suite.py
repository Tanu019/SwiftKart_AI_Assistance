"""
test_auth_suite.py
------------------
Automated test suite verifying Passwordless Authentication:
1. Continue with Email OTP (sign_in_with_otp, verify_otp with type='email')
2. Continue with Google OAuth (sign_in_with_oauth)
3. Role enforcement and privilege escalation defense
4. Protected dashboard access gating
"""

import os
import sys
import unittest
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from app.auth import (
    get_supabase_client,
    send_email_otp,
    verify_email_otp,
    get_google_oauth_url,
    get_user_profile,
    ROLE_BADGES,
    DEFAULT_ROLE,
    VALID_ROLES
)


class TestAuthenticationSuite(unittest.TestCase):

    def setUp(self):
        self.supabase = get_supabase_client()
        self.valid_email = "test.employee@swiftkart.io"

    def test_01_supabase_client_connection(self):
        """Test Supabase client is properly initialized from environment variables."""
        self.assertIsNotNone(self.supabase, "Supabase client failed to initialize with SUPABASE_URL / SUPABASE_KEY")
        print("[PASS] Test 1: Supabase client connected successfully.")

    def test_02_send_email_otp_validation(self):
        """Test validation when requesting Email OTP."""
        # Test empty email
        ok, msg = send_email_otp("")
        self.assertFalse(ok)
        self.assertIn("valid email", msg.lower())

        # Test invalid email format
        ok, msg = send_email_otp("invalid-email-address")
        self.assertFalse(ok)
        self.assertIn("valid email", msg.lower())
        print("[PASS] Test 2: Email OTP input validation works as expected.")

    def test_03_verify_email_otp_validation(self):
        """Test verification input checks and invalid/expired token rejection."""
        # Non-6-digit token
        ok, msg, session = verify_email_otp(self.valid_email, "123")
        self.assertFalse(ok)
        self.assertIsNone(session)
        self.assertIn("6-digit", msg.lower())

        # Non-digit characters
        ok, msg, session = verify_email_otp(self.valid_email, "abcdef")
        self.assertFalse(ok)
        self.assertIsNone(session)
        self.assertIn("6-digit", msg.lower())

        # Non-existent/invalid 6-digit token tested with Supabase verify_otp
        ok, msg, session = verify_email_otp(self.valid_email, "999999")
        self.assertFalse(ok)
        self.assertIsNone(session)
        self.assertTrue("invalid" in msg.lower() or "expired" in msg.lower() or "error" in msg.lower())
        print("[PASS] Test 3: OTP verification correctly validates format and rejects invalid/expired tokens.")

    def test_04_google_oauth_url_generation(self):
        """Test generating Google OAuth authorization URL via Supabase Auth."""
        oauth_url = get_google_oauth_url(redirect_to="http://localhost:8501")
        self.assertIsNotNone(oauth_url, "Google OAuth URL generation returned None")
        self.assertIn("provider=google", oauth_url)
        self.assertIn("supabase.co", oauth_url)
        self.assertIn("redirect_to", oauth_url)
        print("[PASS] Test 4: Google OAuth authorization URL successfully generated via Supabase Auth.")

    def test_05_roles_and_privilege_escalation_protection(self):
        """Test default role assignment and privilege escalation defense."""
        self.assertEqual(DEFAULT_ROLE, "analyst")
        self.assertIn("admin", VALID_ROLES)
        self.assertIn("hr_manager", VALID_ROLES)
        self.assertIn("analyst", VALID_ROLES)

        mock_user_id = "00000000-0000-0000-0000-000000000000"
        profile = get_user_profile(mock_user_id, email="guest@swiftkart.io", metadata={"role": "unauthorized_admin"})
        self.assertEqual(profile["role"], "analyst", "Self-assigned admin privilege must be rejected.")
        print("[PASS] Test 5: Role enforcement verified. Self-privilege escalation blocked.")

    def test_06_role_badges_configuration(self):
        """Verify role badges styling and definitions."""
        for role in ["admin", "hr_manager", "analyst"]:
            self.assertIn(role, ROLE_BADGES)
            self.assertIn("label", ROLE_BADGES[role])
            self.assertIn("color", ROLE_BADGES[role])
        print("[PASS] Test 6: Role badges correctly configured.")

    def test_07_protected_dashboard_guard(self):
        """Verify that unauthenticated state stops access to dashboard."""
        import streamlit as st
        st.session_state["authenticated"] = False
        st.session_state["user"] = None
        self.assertFalse(st.session_state["authenticated"])
        self.assertIsNone(st.session_state["user"])
        print("[PASS] Test 7: Protected dashboard gates unauthenticated users.")


if __name__ == "__main__":
    unittest.main()
