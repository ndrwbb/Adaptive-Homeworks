export default function Loader({ label = "Loading workspace..." }) {
  return (
    <div className="loader-card">
      <div className="loader-card__spinner" />
      <p>{label}</p>
    </div>
  );
}
