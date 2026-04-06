# NATIONAL RESEARCH UNIVERSITY HIGHER SCHOOL OF ECONOMICS
## Faculty of Computer Science
### Bachelor’s Programme “Data Science and Business Analytics”

**Software Project Progress Report on the Topic:**  
**Web Application for Adaptive Homework Assignment and Student Progress Analysis Using Artificial Intelligence**

**Submitted by the Students:**  
group #БПАД233, 3rd year of study  
Bobua Andrey Borisovich  
Smirnova Anastasiya Denisovna

**Approved by the Project Supervisor:**  
Ovchinnikov Vsevolod Aleksandrovich  
Teacher, Faculty of Computer Science, HSE University

**Moscow 2026**

---

## Contents

1. Abstract  
2. Keywords  
3. Introduction  
4. Current Implementation Status (Checkpoint ~60%)  
5. Demonstration Workflow  
6. Plan of Further Work  

---

## Abstract

This report describes the current progress of the project devoted to the development of an intelligent web-based educational system for adaptive homework assignment and student progress analysis. The application combines software engineering principles with baseline adaptive logic in order to personalize the educational experience and provide role-specific tools for both learners and instructors.

At the current stage of development, the system has progressed beyond a backend-only prototype and reached an integrated checkpoint of approximately 60% completion. A substantial backend part has been implemented using FastAPI and SQLAlchemy. It includes user registration and authentication, role-based access control for students and teachers, a relational data model for users, reusable tasks, homeworks, homework items, submissions, and learner states, as well as API endpoints for homework management, self-education recommendation, submission processing, and progress tracking. The adaptive logic is currently based on a rule-driven learner skill score that is updated according to submission correctness and task difficulty.

In parallel with the backend, a frontend MVP has been developed. The client application provides separate interface flows for students and teachers, including dashboards, assigned homework management, self-education practice, progress visualization, teacher homework composition, task banking, and student analytics. The frontend is integrated with the backend API and additionally supports a deterministic fallback mode for demonstration purposes when some backend services are unavailable.

Thus, the current version of the project already demonstrates the core business workflow of the target system: authentication, teacher homework creation, homework assignment, self-education task selection, answer submission, learner state update, and progress monitoring. Advanced machine learning-based personalization, richer analytics, and final evaluation remain planned for the next phase.

### Аннотация

Данный отчёт описывает текущее состояние проекта по разработке интеллектуальной веб-платформы для адаптивного назначения домашних заданий и анализа прогресса студента. Система сочетает принципы программной инженерии и базовую адаптивную логику, позволяя персонализировать образовательный процесс и предоставлять отдельные сценарии работы для студентов и преподавателей.

На текущем этапе проект вышел за рамки исключительно серверного прототипа и достиг интегрированного состояния, соответствующего примерно 60% готовности. Реализована значительная часть backend-системы на базе FastAPI и SQLAlchemy, включающая регистрацию и аутентификацию пользователей, разграничение ролей student и teacher, реляционную модель данных для пользователей, заданий, отправок решений и состояния обучающегося, а также API-эндпоинты для рекомендаций заданий, обработки ответов и отслеживания прогресса. Адаптивная логика на текущем этапе основана на rule-based модели `skill_score`, которая обновляется с учётом сложности задания и корректности ответа.

Параллельно была разработана frontend MVP-версия приложения. Клиентская часть включает отдельные интерфейсы для студентов и преподавателей: дашборды, список назначенных домашних заданий, режим self-education, визуализацию прогресса, конструктор домашних заданий для teacher и просмотр аналитики по студентам. Frontend интегрирован с backend API и дополнительно поддерживает демонстрационный fallback-режим, позволяющий сохранить работоспособный сценарий показа даже при частичной недоступности сервера.

Таким образом, текущая версия проекта уже демонстрирует основной пользовательский цикл системы: вход в систему, создание и назначение домашнего задания, выполнение homework или self-education, отправку ответа, обновление состояния обучающегося и просмотр прогресса. Реализация более сложной ML-персонализации, расширенной аналитики и итоговой экспериментальной оценки запланирована на следующий этап.

---

## Keywords

- Adaptive learning
- Educational data mining
- Web-based educational systems
- Personalized homework assignment
- Student progress analytics
- Role-based educational interfaces

---

## 1. Introduction

The rapid development of educational technologies has intensified the need for systems capable of adapting educational content to individual learner characteristics. Traditional platforms frequently provide static assignments and limited personalization, which reduces their effectiveness for students with heterogeneous preparation levels and different learning trajectories.

The objective of the present project is to develop a modular web application that supports automated personalization of homework tasks and tracking of learning progress. The system is intended to combine a robust software architecture with adaptive logic that can later be extended by machine learning models.

At the current stage, the project focuses on establishing a stable software foundation: backend services for core educational workflows and a frontend MVP that makes these workflows accessible through a demonstrable user interface. This stage is essential because it forms the integration layer on top of which more advanced learner modeling and personalization methods can be implemented later.

---

## 2. Current Implementation Status (Checkpoint ~60%)

At the current checkpoint, the project has reached an integrated MVP phase. The implemented functionality already covers the main user scenarios and demonstrates a coherent interaction between backend services and frontend components.

### 2.1 Backend Architecture

The backend is implemented with the FastAPI framework and uses a modular project structure separating API routes, configuration, database access, ORM models, and data schemas. SQLite is used as the development database, while the configuration design allows migration to another DBMS if required in the future.

The backend exposes documented RESTful endpoints via OpenAPI (Swagger). This ensures both interactive testing and a clean contract for frontend integration.

### 2.2 Authentication and Role-Based Access Control

The system supports two roles: `student` and `teacher`. Registration and login are implemented with JWT-based authentication. Passwords are stored in hashed form. Protected routes are restricted according to the current user role.

Students are allowed to browse assigned homeworks, submit homework answers, request self-education recommendations, and view their own progress. Teachers are allowed to create reusable tasks, compose homeworks from multiple items, assign them to students, inspect student summaries, and access detailed progress data for selected learners.

### 2.3 Data Model and Core Entities

The current data model includes the following key entities:

- `User`, which stores role, credentials, and basic profile information;
- `Task`, which stores reusable self-education content, topic, difficulty level, and optional answer key;
- `Homework`, which stores teacher-created homework metadata and deadline information;
- `HomeworkItem`, which stores individual exercises included into a homework;
- `HomeworkAssignment`, which links a homework to one or more students;
- `Submission`, which records student answers, correctness, score delta, and submission time;
- `HomeworkSubmission`, which records student answers inside homework items and their review state;
- `LearnerState`, which stores the current adaptive skill score of a student.

These entities provide the necessary structural foundation for recommendation, evaluation, and analytics.

### 2.4 Adaptive Recommendation Mechanism

The current recommendation mechanism is used in the `Self-Education` mode and is based on a baseline learner model represented by a `skill_score` value in the interval from 0 to 100. This score is mapped to one of several task difficulty bands. The recommendation endpoint selects a task whose difficulty corresponds to the learner’s current proficiency level, while optional filters such as subject or difficulty can further constrain the selection.

Although the current implementation is rule-based rather than ML-driven, it already demonstrates the fundamental adaptive behavior required by the project and provides a meaningful basis for later extension.

### 2.5 Submission Processing and Skill Update

When a student submits an answer in the self-education mode, the system evaluates correctness automatically if the corresponding task contains an answer key. For homework items, the system supports both auto-graded test exercises and manually reviewed exercises. This allows the current MVP to reflect two realistic educational scenarios: teacher-assigned homeworks and student-driven self-practice.

After evaluation, the learner’s skill score is updated in accordance with correctness and task difficulty. Correct answers increase the score, while incorrect answers reduce it within bounded limits. Every submission is stored in the database, forming a persistent interaction history.

### 2.6 Progress Tracking and Teacher Analytics

The backend provides endpoints for retrieving student progress metrics, including:

- current skill score;
- total number of attempts;
- number of correct answers;
- accuracy;
- recent submission history.

In addition, teacher-facing endpoints expose summaries for multiple students and detailed analytics for a selected learner, which makes the system more suitable for instructor monitoring scenarios.

### 2.7 Frontend MVP

The frontend MVP is implemented as a React single-page application. It contains separate flows for students and teachers and is built around the following pages:

- landing page with project overview and demo access;
- login and registration screens;
- student dashboard;
- assigned homeworks page;
- homework detail page;
- self-education workspace;
- progress analytics page;
- teacher dashboard;
- homework management page with `New Homework` flow;
- task bank;
- student analytics page.

The frontend supports role-based navigation, guarded routes, and stateful interactions. It prefers live backend data whenever the API is available and falls back to deterministic demonstration data when necessary. This approach ensures that the main project scenarios remain demonstrable even if some backend services are temporarily incomplete or unavailable.

### 2.8 Integrated State of the Project

The current state of the project may therefore be characterized as follows:

- the backend is already substantial and operational for the main business flows;
- the frontend MVP is implemented and visually separates student and teacher scenarios;
- backend and frontend integration has been completed at the MVP level;
- adaptive logic is present in a baseline form;
- advanced personalization and final evaluation remain future work.

---

## 3. Demonstration Workflow

The current implementation supports the following end-to-end workflow:

1. A user registers or logs into the system as either a student or a teacher.
2. A teacher opens the homework management workspace, creates a new homework, fills it with exercises, and assigns it to one or more students.
3. A student opens the dashboard and chooses either the `Homeworks` mode or the `Self-Education` mode.
4. In the homework flow, the student opens an assigned homework, submits answers, and sees whether the work is auto-graded or moved to review.
5. In the self-education flow, the system returns a practice task selected according to the learner’s current `skill_score` and the chosen filters.
6. The backend validates the answer, records the submission, and updates the learner state.
7. Updated progress data becomes visible on the student progress page, while the teacher can inspect individual learner analytics.

This workflow demonstrates that the current system already functions as an integrated educational MVP rather than a disconnected prototype of isolated components.

---

## 4. Plan of Further Work

Although the project has reached a meaningful implementation milestone, several important directions remain for the final stage.

### 4.1 Advanced Personalization and Machine Learning

The baseline recommendation mechanism should be extended with more sophisticated learner modeling methods. Possible next steps include performance-history-aware recommendation, topic-sensitive adaptation, or integration of machine learning approaches such as knowledge tracing or proficiency prediction.

### 4.2 Extended Analytics

The analytics module should be expanded to include richer teacher reports, temporal trends, more detailed submission history, and clearer visual representations of learner dynamics. These additions would improve both interpretability and practical utility for educational settings.

### 4.3 Testing and System Hardening

Further work is also needed in the area of automated testing, validation of edge cases, and overall production hardening. This includes broader coverage of frontend behavior, backend validation scenarios, and integration checks across the full system.

### 4.4 Final Evaluation and Report Preparation

At the final project stage, the system should undergo integrated testing and qualitative assessment. The outcomes of these experiments, together with the finalized implementation and architectural analysis, will be incorporated into the final project report.

---

## 5. Conclusion

The project has successfully progressed from a backend-oriented prototype to an integrated MVP with both substantial server-side functionality and a demonstrable frontend interface. The core adaptive workflow is now implemented at the system level, and the repository already reflects a coherent software product that can be demonstrated, analyzed, and further extended.

This makes the current state of the project consistent with an intermediate checkpoint of approximately 60% completion and provides a solid foundation for the final stage of development.
