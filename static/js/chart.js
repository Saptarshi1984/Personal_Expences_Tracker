document.addEventListener("DOMContentLoaded", () => {
  const canvas = document.getElementById("expenseChart");
  if (!canvas || typeof Chart === "undefined") return;

  const ctx = canvas.getContext("2d");
  const payload = window.expenseChartData || { labels: [], values: [] };
  const labels = payload.labels || [];
  const values = payload.values || [];

  const colors = [
    "rgba(75, 192, 192, 0.7)",
    "rgba(54, 162, 235, 0.7)",
    "rgba(255, 206, 86, 0.7)",
    "rgba(255, 99, 132, 0.7)",
    "rgba(153, 102, 255, 0.7)",
    "rgba(255, 159, 64, 0.7)",
  ];

  new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "Expenses (?)",
          data: values,
          backgroundColor: labels.map((_, idx) => colors[idx % colors.length]),
          borderRadius: 8,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: true },
      },
      scales: {
        y: { beginAtZero: true },
      },
    },
  });
});
