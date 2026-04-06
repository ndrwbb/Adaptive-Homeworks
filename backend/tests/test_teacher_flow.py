from backend.tests.base import BackendTestCase


class TeacherFlowTests(BackendTestCase):
    def test_teacher_can_create_task(self):
        headers = self.auth_headers("teacher@example.com", "demo123")

        response = self.client.post(
            "/teacher/tasks",
            json={
                "title": "Quadratic equation",
                "body": "Solve x^2 - 5x + 6 = 0",
                "difficulty": 3,
                "topic": "algebra",
                "answer_key": "2,3",
            },
            headers=headers,
        )

        self.assertEqual(response.status_code, 201, response.text)
        self.assertEqual(response.json()["title"], "Quadratic equation")

    def test_teacher_can_view_student_progress(self):
        headers = self.auth_headers("teacher@example.com", "demo123")

        response = self.client.get("/teacher/students", headers=headers)

        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertGreaterEqual(len(payload), 1)
        self.assertEqual(payload[0]["role"], "student")
