import { useEffect } from "react";

export default function Toast({ toast, onDismiss }) {
  useEffect(() => {
    if (!toast) {
      return undefined;
    }

    const timer = window.setTimeout(onDismiss, 3200);
    return () => window.clearTimeout(timer);
  }, [onDismiss, toast]);

  if (!toast) {
    return null;
  }

  return (
    <div className={`toast toast--${toast.tone || "info"}`}>
      <strong>{toast.tone === "success" ? "Done" : toast.tone === "warning" ? "Notice" : "Info"}</strong>
      <span>{toast.message}</span>
      <button type="button" onClick={onDismiss} className="toast__close">
        Close
      </button>
    </div>
  );
}
