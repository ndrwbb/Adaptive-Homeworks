import { useState, useTransition } from "react";
import { useNavigate } from "react-router-dom";

import { useAppContext } from "../context/AppContext";

const initialForm = {
  full_name: "",
  email: "",
  password: "",
  role: "student",
};

export default function Register() {
  const navigate = useNavigate();
  const { loading, register } = useAppContext();
  const [form, setForm] = useState(initialForm);
  const [error, setError] = useState("");
  const [, startTransition] = useTransition();

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");

    try {
      const nextSession = await register(form);
      startTransition(() => {
        navigate(nextSession.user.role === "teacher" ? "/teacher" : "/student");
      });
    } catch {
      setError("Registration failed. Try one of the demo accounts or check the backend.");
    }
  }

  return (
    <section className="auth-layout">
      <div className="hero-card hero-card--compact">
        <span className="eyebrow">Checkpoint ~60%</span>
        <h1>Create your workspace</h1>
        <p>
          Register as a student or teacher. If the backend is offline, the app still opens a demo-ready
          flow for presentation.
        </p>
      </div>

      <form className="form-card" onSubmit={handleSubmit}>
        <div className="field-grid">
          <label className="field">
            <span>Full name</span>
            <input
              value={form.full_name}
              onChange={(event) => setForm((current) => ({ ...current, full_name: event.target.value }))}
              placeholder="Andrey Bobua"
              required
            />
          </label>

          <label className="field">
            <span>Email</span>
            <input
              type="email"
              value={form.email}
              onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))}
              placeholder="student@example.com"
              required
            />
          </label>
        </div>

        <div className="field-grid">
          <label className="field">
            <span>Password</span>
            <input
              type="password"
              value={form.password}
              onChange={(event) => setForm((current) => ({ ...current, password: event.target.value }))}
              placeholder="demo123"
              required
            />
          </label>

          <label className="field">
            <span>Role</span>
            <select
              value={form.role}
              onChange={(event) => setForm((current) => ({ ...current, role: event.target.value }))}
            >
              <option value="student">Student</option>
              <option value="teacher">Teacher</option>
            </select>
          </label>
        </div>

        {error ? <p className="form-error">{error}</p> : null}

        <button type="submit" className="primary-button" disabled={loading.auth}>
          {loading.auth ? "Creating..." : "Create account"}
        </button>
      </form>
    </section>
  );
}
