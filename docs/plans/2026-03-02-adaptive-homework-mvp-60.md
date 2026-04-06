# Adaptive Homework MVP 60% Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a substantial backend plus a demonstrable frontend MVP for the adaptive homework system and update the academic documentation to reflect an integrated ~60% completion checkpoint.

**Architecture:** The backend remains a modular FastAPI service with SQLAlchemy models, JWT-based role-aware flows, and seeded demo data. The frontend becomes a role-aware React SPA that prefers live API data but falls back to deterministic demo data so the main student and teacher scenarios remain demonstrable even if some backend behavior is still incomplete.

**Tech Stack:** FastAPI, SQLAlchemy, Pydantic, SQLite, React, Vite, React Router, Axios

---

### Task 1: Establish backend test harness and domain skeleton

**Files:**
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_health.py`
- Create: `backend/app/core/config.py`
- Create: `backend/app/db/base.py`
- Create: `backend/app/db/session.py`
- Create: `backend/app/api/__init__.py`
- Create: `backend/app/api/routes/__init__.py`
- Modify: `backend/app/main.py`

**Step 1: Write the failing test**

```python
def test_health_endpoint_returns_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_health.py -v`
Expected: FAIL because the test package and client fixture do not exist yet.

**Step 3: Write minimal implementation**

```python
app = FastAPI(title="Adaptive Homework API")

@app.get("/health")
def health():
    return {"status": "ok"}
```

**Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_health.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/tests backend/app backend/app/main.py
git commit -m "test: add backend harness and health check"
```

### Task 2: Implement authentication and role-aware user model

**Files:**
- Create: `backend/app/core/security.py`
- Create: `backend/app/api/deps.py`
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/models/user.py`
- Create: `backend/app/models/learner_state.py`
- Create: `backend/app/schemas/__init__.py`
- Create: `backend/app/schemas/auth.py`
- Create: `backend/app/api/routes/auth.py`
- Create: `backend/tests/test_auth.py`
- Modify: `backend/app/main.py`

**Step 1: Write the failing test**

```python
def test_student_registration_creates_initial_state(client, db_session):
    response = client.post(
        "/auth/register",
        json={"email": "student@example.com", "password": "secret123", "role": "student"},
    )

    assert response.status_code == 201
    assert response.json()["role"] == "student"
```

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_auth.py::test_student_registration_creates_initial_state -v`
Expected: FAIL with missing route or model errors.

**Step 3: Write minimal implementation**

```python
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50))
```

**Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_auth.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/app backend/tests/test_auth.py
git commit -m "feat: add auth flow and user roles"
```

### Task 3: Add task management, recommendation, submissions, and progress

**Files:**
- Create: `backend/app/models/task.py`
- Create: `backend/app/models/submission.py`
- Create: `backend/app/schemas/task.py`
- Create: `backend/app/schemas/submission.py`
- Create: `backend/app/schemas/progress.py`
- Create: `backend/app/api/routes/tasks.py`
- Create: `backend/app/api/routes/submissions.py`
- Create: `backend/app/api/routes/progress.py`
- Create: `backend/app/api/routes/teacher.py`
- Create: `backend/tests/test_student_flow.py`
- Create: `backend/tests/test_teacher_flow.py`
- Modify: `backend/app/main.py`

**Step 1: Write the failing test**

```python
def test_student_submission_updates_skill_score(authenticated_student_client, seeded_task):
    response = authenticated_student_client.post(
        "/submissions",
        json={"task_id": seeded_task["id"], "answer": seeded_task["answer_key"]},
    )

    assert response.status_code == 200
    assert response.json()["new_skill_score"] > 50
```

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_student_flow.py::test_student_submission_updates_skill_score -v`
Expected: FAIL because tasks, submissions, and progress logic are not implemented yet.

**Step 3: Write minimal implementation**

```python
base = 5 * task.difficulty
delta = base if is_correct else -base
state.skill_score = max(0, min(100, state.skill_score + delta))
```

**Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_student_flow.py backend/tests/test_teacher_flow.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/app backend/tests
git commit -m "feat: add adaptive homework flows"
```

### Task 4: Seed demo data and expose a demo-ready backend

**Files:**
- Create: `backend/seed.py`
- Create: `backend/.env.example`
- Modify: `backend/.env`
- Modify: `backend/requirements.txt`
- Create: `backend/tests/test_seed.py`

**Step 1: Write the failing test**

```python
def test_seed_creates_demo_tasks(db_session):
    run_seed(db_session)
    assert db_session.query(Task).count() >= 6
```

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_seed.py -v`
Expected: FAIL because seeding helper does not exist.

**Step 3: Write minimal implementation**

```python
db.add_all([
    Task(title="Linear equation", body="Solve 2x + 3 = 11", difficulty=1, topic="algebra", answer_key="4"),
])
```

**Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_seed.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/seed.py backend/.env.example backend/requirements.txt backend/tests/test_seed.py
git commit -m "feat: add demo seed data"
```

### Task 5: Build shared frontend app shell, routing, and API/demo data layer

**Files:**
- Create: `frontend/src/api/client.js`
- Create: `frontend/src/api/demoData.js`
- Create: `frontend/src/context/AppContext.jsx`
- Create: `frontend/src/components/Layout.jsx`
- Create: `frontend/src/components/ProtectedRoute.jsx`
- Create: `frontend/src/components/RoleRoute.jsx`
- Create: `frontend/src/components/Loader.jsx`
- Create: `frontend/src/components/Toast.jsx`
- Modify: `frontend/src/App.jsx`
- Modify: `frontend/src/main.jsx`
- Modify: `frontend/src/index.css`
- Create: `frontend/src/App.test.jsx`

**Step 1: Write the failing test**

```jsx
it("redirects unauthenticated users away from student pages", async () => {
  render(<App />)
  await user.click(screen.getByText(/student dashboard/i))
  expect(screen.getByText(/login/i)).toBeInTheDocument()
})
```

**Step 2: Run test to verify it fails**

Run: `npm test -- App.test.jsx`
Expected: FAIL because the app shell and guards are not implemented.

**Step 3: Write minimal implementation**

```jsx
<Route
  path="/student"
  element={
    <ProtectedRoute>
      <StudentDashboard />
    </ProtectedRoute>
  }
/>
```

**Step 4: Run test to verify it passes**

Run: `npm test -- App.test.jsx`
Expected: PASS

**Step 5: Commit**

```bash
git add frontend/src
git commit -m "feat: add frontend app shell and routing"
```

### Task 6: Implement student-facing frontend flows

**Files:**
- Create: `frontend/src/pages/Register.jsx`
- Create: `frontend/src/pages/StudentDashboard.jsx`
- Create: `frontend/src/pages/TaskWorkspace.jsx`
- Create: `frontend/src/pages/ProgressPage.jsx`
- Modify: `frontend/src/pages/Login.jsx`
- Modify: `frontend/src/pages/Home.jsx`
- Modify: `frontend/src/index.css`

**Step 1: Write the failing test**

```jsx
it("shows recommended task and submission feedback for students", async () => {
  renderWithStudentSession(<TaskWorkspace />)
  expect(await screen.findByText(/recommended task/i)).toBeInTheDocument()
})
```

**Step 2: Run test to verify it fails**

Run: `npm test -- TaskWorkspace`
Expected: FAIL because the student pages do not exist yet.

**Step 3: Write minimal implementation**

```jsx
const { task, submitAnswer } = useAppContext()
```

**Step 4: Run test to verify it passes**

Run: `npm test -- TaskWorkspace`
Expected: PASS

**Step 5: Commit**

```bash
git add frontend/src/pages frontend/src/index.css
git commit -m "feat: add student dashboard and task flow"
```

### Task 7: Implement teacher-facing frontend flows

**Files:**
- Create: `frontend/src/pages/TeacherDashboard.jsx`
- Create: `frontend/src/pages/TaskManager.jsx`
- Create: `frontend/src/pages/StudentAnalytics.jsx`
- Modify: `frontend/src/index.css`
- Create: `frontend/src/pages/TeacherDashboard.test.jsx`

**Step 1: Write the failing test**

```jsx
it("lets teachers review student progress cards", async () => {
  renderWithTeacherSession(<TeacherDashboard />)
  expect(await screen.findByText(/student overview/i)).toBeInTheDocument()
})
```

**Step 2: Run test to verify it fails**

Run: `npm test -- TeacherDashboard`
Expected: FAIL because the teacher pages do not exist yet.

**Step 3: Write minimal implementation**

```jsx
<section className="panel-grid">
  {students.map((student) => (
    <StudentCard key={student.id} student={student} />
  ))}
</section>
```

**Step 4: Run test to verify it passes**

Run: `npm test -- TeacherDashboard`
Expected: PASS

**Step 5: Commit**

```bash
git add frontend/src/pages frontend/src/index.css
git commit -m "feat: add teacher workspace"
```

### Task 8: Update academic documentation for the 60% checkpoint

**Files:**
- Create: `docs/report/Adaptive_Homework_60_percent_report.md`
- Create: `docs/report/assets/`
- Modify: `README.md`

**Step 1: Write the failing test**

```text
Manual verification checklist:
- The report has abstract, current implementation status, workflow, and further work sections.
- The report matches the implemented repository state.
```

**Step 2: Run test to verify it fails**

Run: `rg -n "60%|frontend MVP|integration" docs/report/Adaptive_Homework_60_percent_report.md`
Expected: FAIL because the report file does not exist yet.

**Step 3: Write minimal implementation**

```markdown
## Current Implementation Status (Checkpoint ~60%)

The system now includes a substantial backend part together with an integrated frontend MVP.
```

**Step 4: Run test to verify it passes**

Run: `rg -n "60%|frontend MVP|integration" docs/report/Adaptive_Homework_60_percent_report.md`
Expected: PASS

**Step 5: Commit**

```bash
git add docs/report README.md
git commit -m "docs: add 60 percent project report"
```

### Task 9: Verify end-to-end runnability

**Files:**
- Modify: `README.md`

**Step 1: Write the failing test**

```text
Manual verification checklist:
- backend starts with uvicorn
- frontend builds with vite
- main student and teacher demo paths work
```

**Step 2: Run test to verify it fails**

Run: `python -m uvicorn app.main:app --reload`
Expected: FAIL until dependencies, imports, and configuration are correct.

**Step 3: Write minimal implementation**

```text
Document exact backend and frontend run commands in README.md.
```

**Step 4: Run test to verify it passes**

Run: `pytest && npm run build`
Expected: PASS

**Step 5: Commit**

```bash
git add README.md
git commit -m "docs: add run and verification steps"
```
