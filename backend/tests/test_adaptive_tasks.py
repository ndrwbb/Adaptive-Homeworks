"""
Tests for the adaptive task endpoints (fake-data layer).

These tests exercise:
  - GET /tasks/next
  - GET /tasks/all
  - GET /tasks/{task_id}
  - POST /tasks/{task_id}/answer
  - GET /stats/{user_id}
"""

from backend.tests.base import BackendTestCase
from app.services.adaptive import USER_ANSWERS, USER_STATE


class AdaptiveTaskTests(BackendTestCase):
    def setUp(self):
        super().setUp()
        # Reset in-memory adaptive state between tests
        USER_STATE.clear()
        USER_ANSWERS.clear()

    # ── GET /tasks/next ─────────────────────────────────────────

    def test_get_next_task_returns_200(self):
        response = self.client.get("/tasks/next?user_id=test_user")
        self.assertEqual(response.status_code, 200)

    def test_get_next_task_has_no_answer_field(self):
        response = self.client.get("/tasks/next?user_id=test_user")
        data = response.json()
        self.assertNotIn("answer", data)
        self.assertNotIn("solution", data)

    def test_get_next_task_with_topic(self):
        response = self.client.get("/tasks/next?user_id=test_user&topic=fractions")
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["topic"], "fractions")

    def test_get_next_task_unknown_topic_returns_404(self):
        response = self.client.get("/tasks/next?user_id=test_user&topic=quantum_physics")
        self.assertEqual(response.status_code, 404)

    # ── GET /tasks/all ──────────────────────────────────────────

    def test_get_all_tasks_returns_list(self):
        response = self.client.get("/tasks/all")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 15)

    def test_get_all_tasks_hides_answers(self):
        response = self.client.get("/tasks/all")
        for task in response.json():
            self.assertNotIn("answer", task)
            self.assertNotIn("solution", task)

    # ── GET /tasks/{task_id} ────────────────────────────────────

    def test_get_single_task(self):
        response = self.client.get("/tasks/1")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], 1)
        self.assertNotIn("answer", data)

    def test_get_single_task_not_found(self):
        response = self.client.get("/tasks/9999")
        self.assertEqual(response.status_code, 404)

    # ── POST /tasks/{task_id}/answer ────────────────────────────

    def test_submit_correct_answer(self):
        response = self.client.post(
            "/tasks/1/answer",
            json_body={"user_id": "test_user", "answer": "105"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["is_correct"])
        self.assertEqual(data["correct_answer"], "105")
        self.assertIn("solution", data)
        # difficulty should increase from 1 to 2
        self.assertEqual(data["next_difficulty"], 2)

    def test_submit_wrong_answer(self):
        response = self.client.post(
            "/tasks/1/answer",
            json_body={"user_id": "test_user", "answer": "999"},
        )
        data = response.json()
        self.assertFalse(data["is_correct"])
        # difficulty stays at minimum 1
        self.assertEqual(data["next_difficulty"], 1)

    def test_submit_answer_updates_state(self):
        """After two correct answers, difficulty should be 3."""
        self.client.post("/tasks/1/answer", json_body={"user_id": "u1", "answer": "105"})
        self.client.post("/tasks/2/answer", json_body={"user_id": "u1", "answer": "400"})

        response = self.client.get("/stats/u1")
        data = response.json()
        self.assertEqual(data["current_difficulty"], 3)
        self.assertEqual(data["total_answers"], 2)
        self.assertEqual(data["correct_answers"], 2)

    def test_submit_answer_task_not_found(self):
        response = self.client.post(
            "/tasks/9999/answer",
            json_body={"user_id": "test_user", "answer": "42"},
        )
        self.assertEqual(response.status_code, 404)

    # ── GET /stats/{user_id} ────────────────────────────────────

    def test_stats_empty_user(self):
        response = self.client.get("/stats/brand_new_user")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total_answers"], 0)
        self.assertEqual(data["accuracy"], 0.0)
        self.assertEqual(data["weak_topics"], [])

    def test_stats_with_weak_topics(self):
        # Submit two wrong answers in fractions
        self.client.post("/tasks/4/answer", json_body={"user_id": "u2", "answer": "wrong"})
        self.client.post("/tasks/5/answer", json_body={"user_id": "u2", "answer": "wrong"})
        # Submit one correct answer in arithmetic
        self.client.post("/tasks/1/answer", json_body={"user_id": "u2", "answer": "105"})

        response = self.client.get("/stats/u2")
        data = response.json()
        self.assertEqual(data["total_answers"], 3)
        self.assertIn("fractions", data["weak_topics"])
