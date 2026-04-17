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

    def test_teacher_can_filter_update_and_archive_task(self):
        headers = self.auth_headers("teacher@example.com", "demo123")
        create_response = self.client.post(
            "/teacher/tasks",
            json={
                "title": "Geometry drill",
                "body": "Find the area of a square with side 4.",
                "difficulty": 2,
                "topic": "geometry",
                "answer_key": "16",
                "solution": "4 * 4 = 16",
            },
            headers=headers,
        )
        self.assertEqual(create_response.status_code, 201, create_response.text)
        task_id = create_response.json()["id"]

        filter_response = self.client.get("/teacher/tasks?topic=geometry&difficulty=2", headers=headers)
        self.assertEqual(filter_response.status_code, 200, filter_response.text)
        self.assertTrue(any(task["id"] == task_id for task in filter_response.json()))

        update_response = self.client.patch(
            f"/teacher/tasks/{task_id}",
            json={"title": "Updated geometry drill", "difficulty": 3},
            headers=headers,
        )
        self.assertEqual(update_response.status_code, 200, update_response.text)
        self.assertEqual(update_response.json()["title"], "Updated geometry drill")
        self.assertEqual(update_response.json()["difficulty"], 3)

        delete_response = self.client.delete(f"/teacher/tasks/{task_id}", headers=headers)
        self.assertEqual(delete_response.status_code, 200, delete_response.text)

        list_response = self.client.get("/teacher/tasks?include_archived=true", headers=headers)
        self.assertEqual(list_response.status_code, 200, list_response.text)

    def test_student_cannot_create_teacher_task(self):
        headers = self.auth_headers("student@example.com", "demo123")

        response = self.client.post(
            "/teacher/tasks",
            json={
                "title": "Forbidden task",
                "body": "Students should not create this.",
                "difficulty": 1,
                "topic": "security",
                "answer_key": "no",
            },
            headers=headers,
        )

        self.assertEqual(response.status_code, 403, response.text)

    def test_teacher_can_view_student_progress(self):
        headers = self.auth_headers("teacher@example.com", "demo123")

        response = self.client.get("/teacher/students", headers=headers)

        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertGreaterEqual(len(payload), 1)
        self.assertEqual(payload[0]["role"], "student")
