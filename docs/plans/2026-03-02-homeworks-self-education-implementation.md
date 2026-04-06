# Homeworks And Self-Education Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Introduce separate homework and self-education learning modes, add teacher homework creation and assignment flows, and make the student dashboard resilient to partial API failures.

**Architecture:** The backend keeps `Task` as the reusable practice bank and adds a homework domain layer with assignments and per-item submissions. The frontend restructures student navigation around explicit learning modes and treats dashboard sections as independently loadable blocks so failures in recommendation or homework APIs do not stall the entire page.

**Tech Stack:** FastAPI, SQLAlchemy, SQLite, React, Vite, React Router, Axios

---

### Task 1: Add failing backend tests for homework flows

**Files:**
- Create: `backend/tests/test_homeworks.py`
- Modify: `backend/tests/base.py`

**Step 1: Write the failing test**

```python
def test_teacher_can_create_homework_with_assignees(self):
    response = self.client.post("/teacher/homeworks", json=payload, headers=teacher_headers)
    self.assertEqual(response.status_code, 201)
```

**Step 2: Run test to verify it fails**

Run: `PYTHONPATH=backend /Users/andreybobua/PycharmProjects/EdTech/venv/bin/python -m unittest backend.tests.test_homeworks -v`
Expected: FAIL because homework routes and models do not exist yet.

**Step 3: Write minimal implementation**

```python
@router.post("/homeworks")
def create_homework(...):
    ...
```

**Step 4: Run test to verify it passes**

Run: `PYTHONPATH=backend /Users/andreybobua/PycharmProjects/EdTech/venv/bin/python -m unittest backend.tests.test_homeworks -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/tests
git commit -m "test: add homework backend flows"
```

### Task 2: Implement homework backend domain and routes

**Files:**
- Create: `backend/app/models/homework.py`
- Create: `backend/app/models/homework_item.py`
- Create: `backend/app/models/homework_assignment.py`
- Create: `backend/app/models/homework_submission.py`
- Create: `backend/app/schemas/homework.py`
- Create: `backend/app/api/routes/homeworks.py`
- Modify: `backend/app/models/__init__.py`
- Modify: `backend/app/schemas/__init__.py`
- Modify: `backend/app/api/routes/__init__.py`
- Modify: `backend/app/main.py`
- Modify: `backend/seed.py`

**Step 1: Write the failing test**

```python
def test_student_sees_assigned_homeworks(self):
    response = self.client.get("/homeworks/my", headers=student_headers)
    self.assertEqual(response.status_code, 200)
    self.assertGreaterEqual(len(response.json()), 1)
```

**Step 2: Run test to verify it fails**

Run: `PYTHONPATH=backend /Users/andreybobua/PycharmProjects/EdTech/venv/bin/python -m unittest backend.tests.test_homeworks -v`
Expected: FAIL because the route does not exist.

**Step 3: Write minimal implementation**

```python
class Homework(Base):
    __tablename__ = "homeworks"
```

**Step 4: Run test to verify it passes**

Run: `PYTHONPATH=backend /Users/andreybobua/PycharmProjects/EdTech/venv/bin/python -m unittest discover -s backend/tests -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/app backend/seed.py
git commit -m "feat: add homework backend domain"
```

### Task 3: Restructure student data loading and dashboard resilience

**Files:**
- Modify: `frontend/src/context/AppContext.jsx`
- Create: `frontend/src/lib/dashboard.js`
- Modify: `frontend/src/pages/StudentDashboard.jsx`

**Step 1: Write the failing test**

```js
test("builds dashboard state when recommendation is missing", () => {
  const state = buildStudentDashboardState({ progress, homeworkSummary, recommendation: null });
  assert.equal(state.sections.recommendation.status, "empty");
});
```

**Step 2: Run test to verify it fails**

Run: `node --test frontend/src/lib/dashboard.test.js`
Expected: FAIL because helper does not exist.

**Step 3: Write minimal implementation**

```js
export function buildStudentDashboardState(...) {
  ...
}
```

**Step 4: Run test to verify it passes**

Run: `node --test frontend/src/lib/dashboard.test.js`
Expected: PASS

**Step 5: Commit**

```bash
git add frontend/src/context frontend/src/lib frontend/src/pages/StudentDashboard.jsx
git commit -m "feat: make student dashboard resilient"
```

### Task 4: Add student Homeworks and Self-Education pages

**Files:**
- Create: `frontend/src/pages/HomeworksPage.jsx`
- Create: `frontend/src/pages/HomeworkDetailPage.jsx`
- Create: `frontend/src/pages/SelfEducationPage.jsx`
- Create: `frontend/src/lib/homeworks.js`
- Create: `frontend/src/lib/homeworks.test.js`
- Modify: `frontend/src/App.jsx`
- Modify: `frontend/src/components/Layout.jsx`
- Modify: `frontend/src/api/client.js`
- Modify: `frontend/src/api/demoData.js`
- Modify: `frontend/src/index.css`

**Step 1: Write the failing test**

```js
test("computes homework card status after deadline", () => {
  const status = getHomeworkCardStatus(homework, assignment);
  assert.equal(status.label, "Closed");
});
```

**Step 2: Run test to verify it fails**

Run: `node --test frontend/src/lib/homeworks.test.js`
Expected: FAIL because status helper does not exist.

**Step 3: Write minimal implementation**

```js
export function getHomeworkCardStatus(homework, assignment) {
  ...
}
```

**Step 4: Run test to verify it passes**

Run: `node --test frontend/src/lib/homeworks.test.js`
Expected: PASS

**Step 5: Commit**

```bash
git add frontend/src
git commit -m "feat: add student homework and self-education flows"
```

### Task 5: Add teacher Homeworks workspace with New Homework flow

**Files:**
- Create: `frontend/src/pages/TeacherHomeworksPage.jsx`
- Create: `frontend/src/pages/TeacherHomeworkDetailPage.jsx`
- Modify: `frontend/src/pages/TeacherDashboard.jsx`
- Modify: `frontend/src/components/Layout.jsx`
- Modify: `frontend/src/context/AppContext.jsx`
- Modify: `frontend/src/index.css`

**Step 1: Write the failing test**

```js
test("builds teacher homework summary cards", () => {
  const cards = buildTeacherHomeworkCards(homeworks, students);
  assert.equal(cards[0].assigneeCount, 2);
});
```

**Step 2: Run test to verify it fails**

Run: `node --test frontend/src/lib/homeworks.test.js`
Expected: FAIL because teacher card helper does not exist.

**Step 3: Write minimal implementation**

```js
export function buildTeacherHomeworkCards(homeworks, students) {
  ...
}
```

**Step 4: Run test to verify it passes**

Run: `node --test frontend/src/lib/homeworks.test.js`
Expected: PASS

**Step 5: Commit**

```bash
git add frontend/src
git commit -m "feat: add teacher homework creation flow"
```

### Task 6: Verify integrated build

**Files:**
- Modify: `README.md`

**Step 1: Write the failing test**

```text
Manual verification checklist:
- student toolbar shows Homeworks and Self-Education
- teacher toolbar shows Homeworks and New Homework flow
- backend tests pass
- frontend build passes
```

**Step 2: Run test to verify it fails**

Run: `npm run build`
Expected: FAIL until routes and context align.

**Step 3: Write minimal implementation**

```text
Document the updated run flow in README.md.
```

**Step 4: Run test to verify it passes**

Run: `PYTHONPATH=backend /Users/andreybobua/PycharmProjects/EdTech/venv/bin/python -m unittest discover -s backend/tests -v && cd frontend && npm run build`
Expected: PASS

**Step 5: Commit**

```bash
git add README.md
git commit -m "docs: update run flow for homework mode"
```
