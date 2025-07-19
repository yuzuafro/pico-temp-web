let isConnected = false;
let intervalId = null;

const ctx = document.getElementById("chart").getContext("2d");
const chart = new Chart(ctx, {
  type: "line",
  data: {
    labels: [],
    datasets: [{
      label: "温度 (℃)",
      data: [],
      borderColor: "tomato",
      backgroundColor: "rgba(255, 99, 132, 0.2)"
    }]
  },
  options: {
    responsive: true,
    scales: {
      y: {
        suggestedMin: 15,
        suggestedMax: 40,
        title: { display: true, text: "温度 (℃)" }
      },
      x: {
        title: { display: true, text: "時刻" }
      }
    }
  }
});

function startPolling() {
  if (intervalId === null) {
    update();
    intervalId = setInterval(update, 5000);
  }
}

function stopPolling() {
  if (intervalId !== null) {
    clearInterval(intervalId);
    intervalId = null;
  }
}

function update() {
  if (!isConnected) return;

  fetch("/temperature")
    .then(res => res.json())
    .then(data => {
      if (data.temperature !== undefined) {
        const now = new Date().toLocaleTimeString();
        document.getElementById("latest").textContent = `最新の温度: ${data.temperature.toFixed(2)} °C`;
        chart.data.labels.push(now);
        chart.data.datasets[0].data.push(data.temperature);
        if (chart.data.labels.length > 20) {
          chart.data.labels.shift();
          chart.data.datasets[0].data.shift();
        }
        chart.update();
      }

      // 接続状態が false なら停止
      if (data.connected === false) {
        isConnected = false;
        document.getElementById("status").innerHTML = `<span style="color:red">切断中</span>`;
        stopPolling();
      }
    })
    .catch(() => {
      isConnected = false;
      document.getElementById("status").innerHTML = `<span style="color:red">切断中</span>`;
      stopPolling();
    });
}

function connectBLE() {
  fetch("/connect", { method: "POST" })
    .then(res => res.json())
    .then(data => {
      isConnected = data.connected === true;
      if (isConnected) {
        document.getElementById("status").innerHTML = `<span style="color:green">接続中</span>`;
        waitForTemperature();  // 🔽 最初の温度が来るまで待機
      }
      alert(data.message || "接続開始");
    });
}

function waitForTemperature(retries = 10) {
  if (retries <= 0) return;

  fetch("/temperature")
    .then(res => res.json())
    .then(data => {
      if (data.temperature !== undefined) {
        document.getElementById("latest").textContent = `最新の温度: ${data.temperature.toFixed(2)} °C`;
        startPolling(); // ✨ ここで初めて開始
      } else {
        setTimeout(() => waitForTemperature(retries - 1), 1000);
      }
    })
    .catch(() => {
      setTimeout(() => waitForTemperature(retries - 1), 1000);
    });
}

function disconnect() {
  fetch("/disconnect", { method: "POST" })
    .then(res => res.json())
    .then(data => {
      isConnected = false;
      stopPolling();
      document.getElementById("status").innerHTML = `<span style="color:red">切断中</span>`;
      alert(data.message || data.error);
    });
}