from backend.tests.base import BackendTestCase


class HomeworkFlowTests(BackendTestCase):
    def test_teacher_can_create_homework_with_assignees(self):
        headers = self.auth_headers("teacher@example.com", "demo123")

        response = self.client.post(
            "/teacher/homeworks",
            json={
                "title": "Algebra Homework 1",
                "subject": "Mathematics",
                "description": "Practice equations and one explanation task.",
                "deadline": "2099-03-05T18:00:00",
                "assignee_ids": [1],
                "items": [
                    {
                        "title": "Equation drill",
                        "prompt": "Solve x + 5 = 12",
                        "item_type": "test",
                        "difficulty": 1,
                        "max_points": 5,
                        "answer_key": "7",
                    },
                    {
                        "title": "Explain method",
                        "prompt": "Explain how you isolated x.",
                        "item_type": "manual",
                        "difficulty": 1,
                        "max_points": 5,
                        "answer_key": None,
                    },
                ],
            },
            headers=headers,
        )

        self.assertEqual(response.status_code, 201, response.text)
        payload = response.json()
        self.assertEqual(payload["title"], "Algebra Homework 1")
        self.assertEqual(len(payload["items"]), 2)
        self.assertEqual(payload["assignment_count"], 1)

    def test_student_sees_assigned_homeworks(self):
        headers = self.auth_headers("student@example.com", "demo123")

        response = self.client.get("/homeworks/my", headers=headers)

        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertGreaterEqual(len(payload), 1)
        self.assertIn("teacher_name", payload[0])
        self.assertIn("status", payload[0])

    def test_student_can_submit_test_homework_item(self):
        headers = self.auth_headers("student@example.com", "demo123")
        assignments = self.client.get("/homeworks/my", headers=headers).json()
        assignment_id = assignments[0]["assignment_id"]
        detail = self.client.get(f"/homeworks/my/{assignment_id}", headers=headers).json()
        test_item = next(item for item in detail["items"] if item["item_type"] == "test")

        response = self.client.post(
            f"/homeworks/my/{assignment_id}/submit-item",
            json={"item_id": test_item["id"], "answer": test_item["answer_key"]},
            headers=headers,
        )

        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertTrue(payload["is_correct"])
        self.assertGreater(payload["awarded_points"], 0)
