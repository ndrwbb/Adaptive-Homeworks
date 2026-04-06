import { useState, useTransition } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import { useAppContext } from "../context/AppContext";

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { loading, login } = useAppContext();
  const [form, setForm] = useState({ email: "student@example.com", password: "demo123" });
  const [error, setError] = useState("");
  const [, startTransition] = useTransition();

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");

    try {
      const nextSession = await login(form);
      const fallbackPath = nextSession.user.role === "teacher" ? "/teacher" : "/student";
      startTransition(() => {
        navigate(location.state?.from || fallbackPath);
      });
    } catch {
      setError("Login failed. Check the demo credentials or backend availability.");
    }
  }

  return (
    <section className="auth-layout">
      <div className="hero-card hero-card--compact">
        <span className="eyebrow">Role-based access</span>
        <h1>Sign in to continue the demo flow.</h1>
        <p>
          Login works against the live API when available and automatically falls back to the seeded
          demo profile when the backend is offline.
        </p>
      </div>

      <form className="form-card" onSubmit={handleSubmit}>
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

        {error ? <p className="form-error">{error}</p> : null}

        <button type="submit" className="primary-button" disabled={loading.auth}>
          {loading.auth ? "Signing in..." : "Sign in"}
        </button>

        <p className="form-note">
          Need a new profile? <Link to="/register">Create an account</Link>
        </p>
      </form>
    </section>
  );
}
