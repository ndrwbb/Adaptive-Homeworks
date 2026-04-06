export default function Progress() {
  return (
    <div className="bg-white p-6 rounded-xl shadow mt-6">
      <h1 className="text-2xl font-semibold">Ваш прогресс</h1>
      <p className="mt-2 text-gray-600">
        Сейчас это шаблон. Позже будет GET /progress/me.
      </p>

      <div className="mt-6 grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Stat title="Уровень" value="2" />
        <Stat title="Попытки" value="10" />
        <Stat title="Правильно" value="6" />
      </div>

      <div className="mt-6 bg-gray-50 p-4 rounded-lg">
        <div className="text-sm text-gray-700">Точность</div>
        <div className="mt-2 w-full h-3 bg-gray-200 rounded-full overflow-hidden">
          <div className="h-3 bg-black w-[60%]" />
        </div>
        <div className="mt-2 text-sm text-gray-600">60%</div>
      </div>
    </div>
  );
}

function Stat({ title, value }) {
  return (
    <div className="bg-gray-50 p-4 rounded-lg text-center">
      <div className="text-sm text-gray-500">{title}</div>
      <div className="text-xl font-bold">{value}</div>
    </div>
  );
}