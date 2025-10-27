// ======================
// ASL Translator Frontend
// ======================

// --- SIGN-TO-TEXT SECTION ---
// refs outputs
const signOut = document.getElementById("sign-output");

// live update from Python backend
async function updateSignOutput() {
  try {
    const res = await fetch("http://localhost:5000/get_words");
    const data = await res.json();
    signOut.value = data.text || "";
  } catch (err) {
    console.warn("Fetch error:", err);
  }
}

// poll every 1 second
setInterval(updateSignOutput, 1000);

// copy / clear buttons for sign text
document.getElementById("btn-copy-sign").addEventListener("click", async () => {
  const val = signOut.value.trim();
  if (val) {
    await navigator.clipboard.writeText(val);
    alert("Copied detected text to clipboard!");
  }
});

document.getElementById("btn-clear-sign").addEventListener("click", async () => {
  signOut.value = "";
  try {
    await fetch("http://localhost:5000/clear_words", { method: "POST" });
    console.log("Backend word_list cleared.");
  } catch (err) {
    console.warn("Failed to clear backend word list:", err);
  }
});


// --- SPEECH-TO-TEXT PANEL (UI helper only; your ML/STT can wire into #speech-output) ---
const micStatus = document.getElementById("mic-status");
const btnMic = document.getElementById("btn-mic");
const btnMicStop = document.getElementById("btn-mic-stop");
const speechOut = document.getElementById("speech-output");
const langSel = document.getElementById("lang");

let micStream = null;
let listening = false;

// request mic permission and toggle ui, but do not transcribe automatically
btnMic.addEventListener("click", async () => {
  try {
    micStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    listening = true;
    micStatus.textContent = "mic: on";
    console.log("Microphone listening started...");
  } catch (e) {
    alert("Microphone error: " + e.message);
  }
});

// stop mic
btnMicStop.addEventListener("click", () => {
  if (micStream) {
    micStream.getTracks().forEach((t) => t.stop());
    micStream = null;
  }
  listening = false;
  micStatus.textContent = "mic: off";
  console.log("Microphone stopped.");
});

// copy / clear for speech output
document.getElementById("btn-copy-speech").addEventListener("click", async () => {
  const val = speechOut.value.trim();
  if (val) await navigator.clipboard.writeText(val);
});
document.getElementById("btn-clear-speech").addEventListener("click", () => {
  speechOut.value = "";
});
