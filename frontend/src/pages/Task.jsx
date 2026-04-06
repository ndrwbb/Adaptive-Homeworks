import { useState } from "react";

export default function Task() {
  const [answer, setAnswer] = useState("");

  function handleSubmit() {
    alert("Ответ отправлен (демо). Позже подключим POST /submissions.");
  }

  return (
    <div className="page">
      <div className="card">
        <h1 className="h1">Текущее задание</h1>
        <p className="p">Сейчас это шаблон. Позже подключим реальный эндпоинт рекомендаций.</p>

        <div style={{ marginTop: 18 }} className="box">
          <div style={{ fontWeight: 700 }}>Задание</div>
          <div style={{ marginTop: 8 }}>Найдите x: 2x + 3 = 11</div>
        </div>

        <div style={{ marginTop: 18 }}>
          <div className="label">Ваш ответ</div>
          <input
            className="input"
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            placeholder="Например: 4"
          />
        </div>

        <div style={{ marginTop: 14 }} className="grid">
          <button className="btn" onClick={handleSubmit}>Отправить</button>
          <button className="btn btn-secondary" onClick={() => setAnswer("")}>
            Очистить
          </button>
        </div>
      </div>
    </div>
  );
}