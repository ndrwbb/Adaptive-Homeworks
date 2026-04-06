from backend.tests.base import BackendTestCase


class AuthFlowTests(BackendTestCase):
    def test_student_registration_creates_initial_state(self):
        response = self.client.post(
            "/auth/register",
            json={
                "email": "new.student@example.com",
                "password": "secret123",
                "role": "student",
                "full_name": "New Student",
            },
        )

        self.assertEqual(response.status_code, 201, response.text)
        payload = response.json()
        self.assertEqual(payload["role"], "student")
        self.assertEqual(payload["email"], "new.student@example.com")

    def test_login_returns_access_token_and_user_payload(self):
        response = self.client.post(
            "/auth/login",
            data={"username": "student@example.com", "password": "demo123"},
        )

        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertIn("access_token", payload)
        self.assertEqual(payload["user"]["role"], "student")

