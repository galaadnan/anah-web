
const MOOD_IMAGES = {
  "سعيد": "images/Habby.png",
  "لا بأس": "images/Ok.png",
  "غاضب": "images/Angry.png",
  "حزين": "images/Sad.png",
  "قلق": "images/worried.png",
  "متعب": "images/Tired.png",
  "غير محدد": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='64' height='64'><text x='50%' y='50%' font-size='40' text-anchor='middle' dominant-baseline='middle'>❔</text></svg>"
};



function renderDashboard(days) {
  const { totalScores, historyList, totalWords } = loadAnalyzedData(days);

  // Chart
  const ctx = document.getElementById("moodChart");
  if (ctx) {
    const labels = Object.keys(totalScores);
    const data = labels.map(mood =>
      totalWords > 0 ? Math.round((totalScores[mood] / totalWords) * 100) : 0
    );
    const bgColors = labels.map(l => {
      if (l === "غاضب") return "#ff6b6b";
      if (l === "سعيد") return "#1dd1a1";
      if (l === "حزين") return "#54a0ff";
      if (l === "قلق")  return "#ff9f43";
      if (l === "متعب") return "#feca57";
      return "#ccabd8";
    });

    if (chartInstance) chartInstance.destroy();
    chartInstance = new Chart(ctx, {
      type: "bar",
      data: {
        labels,
        datasets: [{
          label: "النسبة المئوية للكلمات",
          data,
          backgroundColor: bgColors,
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (tooltipItem) => tooltipItem.parsed.y + "%"
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            max: 100,
            ticks: {
              callback: (value) => value + "%"
            }
          }
        }
      }
    });
  }

  // Top Moods
  const topEl = document.getElementById("topMoods");
  if (topEl) {
    topEl.innerHTML = "";
    const sorted = Object.entries(totalScores)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3);
    const total = Object.values(totalScores).reduce((a, b) => a + b, 0);

    if (!sorted.length) {
      topEl.innerHTML = `<p class="an-subtext">لا توجد بيانات.</p>`;
    } else {
      sorted.forEach(([m, s]) => {
        const pct = Math.round((s / total) * 100);
        const img = MOOD_IMAGES[m] || MOOD_IMAGES["غير محدد"];
        topEl.innerHTML += `
          <div class="an-metric">
            <div class="an-metric-label">
              <img src="${img}" class="mood-icon" style="width:30px"> <span>${m}</span>
            </div>
            <span class="an-metric-value">${pct}%</span>
          </div>`;
      });
    }
  }

  // List
  const listEl = document.getElementById("moodList");
  if (listEl) {
    listEl.innerHTML = "";
    historyList.reverse().forEach(item => {
      const img = MOOD_IMAGES[item.dominant] || MOOD_IMAGES["غير محدد"];
      listEl.innerHTML += `
        <div class="an-mood-row">
          <div style="display:flex;align-items:center;gap:10px">
            <img src="${img}" class="mood-icon" style="width:36px"> <strong>${item.dominant}</strong>
          </div>
          <span class="an-tag">${item.date}</span>
        </div>`;
    });
    if (!historyList.length) {
      listEl.innerHTML = `<p class="an-subtext" style="padding:10px">فارغ.</p>`;
    }
  }
}

document.addEventListener("DOMContentLoaded", () => {
  renderDashboard(7);
  document.querySelectorAll(".an-chip").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".an-chip").forEach(b => b.classList.remove("is-active"));
      btn.classList.add("is-active");
      renderDashboard(parseInt(btn.dataset.range));
      const lbl = document.getElementById("analysisRange");
      if (lbl) lbl.textContent = btn.textContent;
    });
  });
});