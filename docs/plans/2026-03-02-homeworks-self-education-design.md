# Homeworks And Self-Education Design

## Goal

Restructure the student experience around two explicit learning modes:

- assigned `Homeworks`
- voluntary `Self-Education`

At the same time, extend the teacher workflow so teachers can create a homework, fill it with items, assign students, and monitor the resulting status.

## Product Shape

### Student navigation

- `Dashboard`
- `Homeworks`
- `Self-Education`
- `Progress`

### Teacher navigation

- `Dashboard`
- `Homeworks`
- `Task Bank`
- `Students`

## Domain Model

The existing `Task` entity remains the reusable content bank for auto-graded practice. A new homework domain is added on top of it.

### Homework

- metadata for a teacher-created assignment
- fields: `title`, `subject`, `description`, `deadline`, `teacher_id`, `max_score`, `requires_manual_review`

### HomeworkItem

- one block inside a homework
- can be:
  - `task_ref`: references an existing task-bank task
  - `inline_test`: inline test-style prompt with answer key
  - `manual`: free-response item that requires teacher review

### HomeworkAssignment

- assignment of one homework to one student
- fields include `status`, `submitted_at`, `final_score`

### HomeworkSubmission

- answer for one item within an assignment
- stores `answer`, `is_correct`, `awarded_points`, `review_status`

## Key UI Flows

### Student Dashboard

The dashboard becomes an overview page instead of a task-only page. It highlights:

- active homeworks
- nearest deadline
- progress summary
- self-education entry point

The dashboard bug is addressed by decoupling initial sections:

- progress loads independently
- homework summary loads independently
- self-education preview loads independently

This prevents one failing API block from stalling the whole page.

### Homeworks Page

Students see a list of homework cards. Each card shows:

- homework title
- subject
- teacher name
- deadline
- progress preview
- status badge

Statuses include:

- `Not started`
- `In progress`
- `Submitted`
- `On review`
- `Checked`
- `Closed`

### Homework Detail

Shows:

- teacher
- description
- deadline
- item list
- item types
- current score/state

### Self-Education

This remains test-only for now. The student chooses:

- subject
- difficulty

Then enters the existing adaptive/self-practice flow.

### Teacher Homeworks

Teachers get a dedicated page with a visible `New Homework` button. Creation flow includes:

- title
- subject
- description
- deadline
- assignees
- items

For the first iteration, assignees are selected from a flat student list rather than groups.

## Backend Scope

Add student endpoints for:

- homework list
- homework detail
- item submission

Add teacher endpoints for:

- homework list
- homework creation
- homework detail

Keep the existing task recommendation flow for `Self-Education`.

## Intentional Deferrals

- group/class assignment
- file uploads
- full teacher review tooling for manual items
- advanced ML-based self-education logic
- full gradebook

## Verification

- backend tests cover homework creation, student homework retrieval, and item submission
- frontend build stays green
- student dashboard renders even when one API section falls back to demo mode
