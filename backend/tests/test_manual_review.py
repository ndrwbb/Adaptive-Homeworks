from backend.tests.base import BackendTestCase


class ManualReviewTests(BackendTestCase):
    """Полный цикл ревью manual-задания: submit → pending → review → checked."""

    def _create_homework_with_manual_item(self, teacher_headers, assignee_id: int) -> dict:
        response = self.client.post(
            "/teacher/homeworks",
            json={
                "title": "Manual Review Test HW",
                "subject": "Literature",
                "description": "Homework with a manual item for review.",
                "deadline": "2099-12-31T23:59:59",
                "assignee_ids": [assignee_id],
                "items": [
                    {
                        "title": "Essay question",
                        "prompt": "Explain the main theme of the story.",
                        "item_type": "manual",
                        "difficulty": 2,
                        "max_points": 10,
                        "answer_key": None,
                    }
                ],
            },
            headers=teacher_headers,
        )
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()

    def test_teacher_sees_pending_reviews_after_student_submits(self):
        teacher_headers = self.auth_headers("teacher@example.com", "demo123")
        student_headers = self.auth_headers("student@example.com", "demo123")

        # Получаем id студента
        students = self.client.get("/teacher/students", headers=teacher_headers).json()
        student_id = students[0]["id"]

        hw = self._create_homework_with_manual_item(teacher_headers, student_id)
        homework_id = hw["homework_id"]

        # Студент находит своё задание и сдаёт manual-элемент
        assignments = self.client.get("/homeworks/my", headers=student_headers).json()
        assignment = next(a for a in assignments if a["homework_id"] == homework_id)
        detail = self.client.get(f"/homeworks/my/{assignment['assignment_id']}", headers=student_headers).json()
        manual_item = next(item for item in detail["items"] if item["item_type"] == "manual")

        submit_resp = self.client.post(
            f"/homeworks/my/{assignment['assignment_id']}/submit-item",
            json={"item_id": manual_item["id"], "answer": "The theme is about courage and perseverance."},
            headers=student_headers,
        )
        self.assertEqual(submit_resp.status_code, 200, submit_resp.text)
        self.assertEqual(submit_resp.json()["review_status"], "pending")

        # Учитель видит задание в pending-reviews
        pending_resp = self.client.get(f"/teacher/homeworks/{homework_id}/pending-reviews", headers=teacher_headers)
        self.assertEqual(pending_resp.status_code, 200, pending_resp.text)
        pending = pending_resp.json()
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0]["review_status"], "pending")
        self.assertIn("answer", pending[0])

    def test_teacher_can_review_and_award_points(self):
        teacher_headers = self.auth_headers("teacher@example.com", "demo123")
        student_headers = self.auth_headers("student@example.com", "demo123")

        students = self.client.get("/teacher/students", headers=teacher_headers).json()
        student_id = students[0]["id"]

        hw = self._create_homework_with_manual_item(teacher_headers, student_id)
        homework_id = hw["homework_id"]

        assignments = self.client.get("/homeworks/my", headers=student_headers).json()
        assignment = next(a for a in assignments if a["homework_id"] == homework_id)
        detail = self.client.get(f"/homeworks/my/{assignment['assignment_id']}", headers=student_headers).json()
        manual_item = next(item for item in detail["items"] if item["item_type"] == "manual")

        submit_resp = self.client.post(
            f"/homeworks/my/{assignment['assignment_id']}/submit-item",
            json={"item_id": manual_item["id"], "answer": "Great answer here."},
            headers=student_headers,
        )
        submission_id = submit_resp.json()["submission_id"]

        # Учитель ставит 8 из 10 баллов
        review_resp = self.client.post(
            f"/teacher/submissions/{submission_id}/review",
            json={"awarded_points": 8},
            headers=teacher_headers,
        )
        self.assertEqual(review_resp.status_code, 200, review_resp.text)
        payload = review_resp.json()
        self.assertEqual(payload["awarded_points"], 8)
        self.assertEqual(payload["review_status"], "reviewed")
        self.assertEqual(payload["assignment_status"], "checked")
        self.assertEqual(payload["assignment_final_score"], 8)

    def test_review_rejects_points_over_max(self):
        teacher_headers = self.auth_headers("teacher@example.com", "demo123")
        student_headers = self.auth_headers("student@example.com", "demo123")

        students = self.client.get("/teacher/students", headers=teacher_headers).json()
        student_id = students[0]["id"]

        hw = self._create_homework_with_manual_item(teacher_headers, student_id)
        homework_id = hw["homework_id"]

        assignments = self.client.get("/homeworks/my", headers=student_headers).json()
        assignment = next(a for a in assignments if a["homework_id"] == homework_id)
        detail = self.client.get(f"/homeworks/my/{assignment['assignment_id']}", headers=student_headers).json()
        manual_item = next(item for item in detail["items"] if item["item_type"] == "manual")

        submit_resp = self.client.post(
            f"/homeworks/my/{assignment['assignment_id']}/submit-item",
            json={"item_id": manual_item["id"], "answer": "Some answer."},
            headers=student_headers,
        )
        submission_id = submit_resp.json()["submission_id"]

        # Пытаемся поставить 999 баллов — должны получить 422
        over_resp = self.client.post(
            f"/teacher/submissions/{submission_id}/review",
            json={"awarded_points": 999},
            headers=teacher_headers,
        )
        self.assertEqual(over_resp.status_code, 422, over_resp.text)
