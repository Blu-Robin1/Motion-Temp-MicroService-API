/* UPDATE THESE VALUES TO MATCH YOUR SETUP */

const PROCESSING_STATS_API_URL = "/processing/stats";
const ANALYZER_API_URL = {
    stats: "/analyzer/stats",
    motion: "/analyzer/motiontemp/motion",    
    temperature: "/analyzer/motiontemp/temperature"
};
const STATUS_URL = "/health/status"; // Matches localhost/health/status

async function updateHealthDashboard() {
  try {
    const response = await fetch(STATUS_URL);
    const data = await response.json();

    console.log("HEALTH DATA:", data);

    const normalize = (status) =>
      status?.toLowerCase() === "up" ? "Up" : "Down";

    document.getElementById("receiver-status").textContent =
      normalize(data.Receiver);

    document.getElementById("storage-status").textContent =
      normalize(data.Storage);

    document.getElementById("processing-status").textContent =
      normalize(data.Processing);

    document.getElementById("analyzer-status").textContent =
      normalize(data.Analyzer);

    document.getElementById("receiver-status").className =
      normalize(data.Receiver) === "Up" ? "status-up" : "status-down";

    document.getElementById("storage-status").className =
      normalize(data.Storage) === "Up" ? "status-up" : "status-down";

    document.getElementById("processing-status").className =
      normalize(data.Processing) === "Up" ? "status-up" : "status-down";

    document.getElementById("analyzer-status").className =
      normalize(data.Analyzer) === "Up" ? "status-up" : "status-down";

    document.getElementById("last-update").textContent =
      `Last update: ${timeAgo(data.last_update)}`;

  } catch (error) {
    console.error("Error updating health dashboard:", error);
  }
}

// This function fetches and updates the general statistics
const makeReq = (url, cb) => {
    fetch(url)
        .then(res => res.json())
        .then((result) => {
            console.log("Received data: ", result)
            cb(result);
        }).catch((error) => {
            updateErrorMessages(error.message)
        })
}


const updateCodeDiv = (result, elemId) => document.getElementById(elemId).innerText = JSON.stringify(result)

const getLocaleDateStr = () => (new Date()).toLocaleString()

let motionIndex = 0;

const getStats = () => {
    document.getElementById("last-updated-value").innerText = getLocaleDateStr()
    
    makeReq(PROCESSING_STATS_API_URL, (result) => updateCodeDiv(result, "processing-stats"))
    makeReq(ANALYZER_API_URL.stats, (result) => updateCodeDiv(result, "analyzer-stats"))

    motionIndex++;

    makeReq(`${ANALYZER_API_URL.motion}?index=${motionIndex}`, (result) =>
        updateCodeDiv(result, "event-motion")
    )

    makeReq(`${ANALYZER_API_URL.temperature}?index=${motionIndex}`, (result) =>
        updateCodeDiv(result, "event-temperature")
    )
}

const updateErrorMessages = (message) => {
    const id = Date.now()
    console.log("Creation", id)
    msg = document.createElement("div")
    msg.id = `error-${id}`
    msg.innerHTML = `<p>Something happened at ${getLocaleDateStr()}!</p><code>${message}</code>`
    document.getElementById("messages").style.display = "block"
    document.getElementById("messages").prepend(msg)
    setTimeout(() => {
        const elem = document.getElementById(`error-${id}`)
        if (elem) { elem.remove() }
    }, 7000)
}

const timeAgo = (timestamp) => {
  const now = new Date();
  const past = new Date(timestamp);

  const diffMs = now - past;
  const diffSec = Math.floor(diffMs / 1000);

  if (diffSec < 60) return `${diffSec} seconds ago`;

  const diffMin = Math.floor(diffSec / 60);
  if (diffMin < 60) return `${diffMin} minutes ago`;

  const diffHr = Math.floor(diffMin / 60);
  if (diffHr < 24) return `${diffHr} hours ago`;

  const diffDays = Math.floor(diffHr / 24);
  return `${diffDays} days ago`;
};

const setup = () => {
    updateHealthDashboard();
    getStats();

    setInterval(() => {
        updateHealthDashboard();
        getStats();
    }, 4000);
};

document.addEventListener('DOMContentLoaded', setup);
