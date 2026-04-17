from backend.tests.base import BackendTestCase
from app.models.learner_topic_state import LearnerTopicState
from app.models.task import Task


class StudentFlowTests(BackendTestCase):
    def test_recommendation_returns_task_for_student(self):
        headers = self.auth_headers("student@example.com", "demo123")

        response = self.client.get("/tasks/recommendation", headers=headers)

        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertIn("difficulty", payload)
        self.assertIn("title", payload)
        self.assertNotIn("answer_key", payload)

    def test_student_submission_updates_skill_score(self):
        headers = self.auth_headers("student@example.com", "demo123")
        task_response = self.client.get("/tasks/recommendation", headers=headers)
        task_id = task_response.json()["id"]
        with self.SessionLocal() as db:
            answer_key = db.query(Task).filter(Task.id == task_id).first().answer_key

        response = self.client.post(
            "/submissions",
            json={"task_id": task_id, "answer": answer_key},
            headers=headers,
        )

        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertGreater(payload["new_skill_score"], 50)
        self.assertTrue(payload["is_correct"])
        self.assertEqual(payload["attempt_number"], 1)

        with self.SessionLocal() as db:
            topic_state = (
                db.query(LearnerTopicState)
                .filter(LearnerTopicState.user_id.isnot(None), LearnerTopicState.topic == task_response.json()["topic"])
                .first()
            )
            self.assertIsNotNone(topic_state)
            self.assertEqual(topic_state.attempts_count, 1)
            self.assertEqual(topic_state.correct_count, 1)

    def test_student_progress_includes_recent_history(self):
        headers = self.auth_headers("student@example.com", "demo123")
        self.client.get("/tasks/recommendation", headers=headers)

        response = self.client.get("/progress/me", headers=headers)

        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertIn("skill_score", payload)
        self.assertIn("accuracy", payload)
        self.assertIn("recent_submissions", payload)

    def test_teacher_cannot_use_student_recommendation_endpoint(self):
        headers = self.auth_headers("teacher@example.com", "demo123")

        response = self.client.get("/tasks/recommendation", headers=headers)

        self.assertEqual(response.status_code, 403, response.text)
