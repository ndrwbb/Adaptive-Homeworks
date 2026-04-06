from backend.tests.base import BackendTestCase


class StudentFlowTests(BackendTestCase):
    def test_recommendation_returns_task_for_student(self):
        headers = self.auth_headers("student@example.com", "demo123")

        response = self.client.get("/tasks/recommendation", headers=headers)

        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertIn("difficulty", payload)
        self.assertIn("title", payload)

    def test_student_submission_updates_skill_score(self):
        headers = self.auth_headers("student@example.com", "demo123")
        task_response = self.client.get("/tasks/recommendation", headers=headers)
        task_id = task_response.json()["id"]
        answer_key = task_response.json()["answer_key"]

        response = self.client.post(
            "/submissions",
            json={"task_id": task_id, "answer": answer_key},
            headers=headers,
        )

        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertGreater(payload["new_skill_score"], 50)
        self.assertTrue(payload["is_correct"])

    def test_student_progress_includes_recent_history(self):
        headers = self.auth_headers("student@example.com", "demo123")
        self.client.get("/tasks/recommendation", headers=headers)

        response = self.client.get("/progress/me", headers=headers)

        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertIn("skill_score", payload)
        self.assertIn("accuracy", payload)
        self.assertIn("recent_submissions", payload)

