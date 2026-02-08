const video = document.getElementById("videoStream");
const videoSelect = document.getElementById("videoSelect");
const vehicleFilter = document.getElementById("vehicleFilter");
const challanInfo = document.getElementById("challanInfo");
const platesDiv = document.getElementById("plates");

let latestData = [];

async function loadVideos() {
  const res = await fetch("http://127.0.0.1:8000/get_videos");
  const data = await res.json();

  data.videos.forEach(v => {
    const o = document.createElement("option");
    o.value = v;
    o.textContent = v;
    videoSelect.appendChild(o);
  });

  setVideo(data.videos[0]);
}

async function setVideo(v) {
  await fetch(`http://127.0.0.1:8000/set_video?video=${encodeURIComponent(v)}`);
  video.src = `http://127.0.0.1:8000/video_feed?${Date.now()}`;
}

videoSelect.onchange = () => setVideo(videoSelect.value);

async function updateUI() {
  const res = await fetch("http://127.0.0.1:8000/metadata");
  latestData = await res.json();

  const type = vehicleFilter.value;
  const filtered = type ? latestData.filter(d => d.label === type) : latestData;

  platesDiv.innerHTML = "";
  challanInfo.innerHTML = "No challan detected";

  filtered.forEach(d => {
    if (d.license_plate) {
      platesDiv.innerHTML += `<p>${d.license_plate}</p>`;

      if (d.challan.status !== "No Pending Challan") {
        challanInfo.innerHTML = `
          <p><b>Status:</b> ${d.challan.status}</p>
          <p><b>Amount:</b> ₹${d.challan.amount || "-"}</p>
          <p><b>Violation:</b> ${d.challan.violation || "-"}</p>
        `;
      }
    }
  });
}

vehicleFilter.onchange = updateUI;
setInterval(updateUI, 1000);
loadVideos();
