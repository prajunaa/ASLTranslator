// ========== SIGN → TEXT (Flask backend) ==========
const signOut = document.getElementById("sign-output");

async function updateSignOutput() {
  try {
    const res = await fetch("http://localhost:5000/get_words", { cache: "no-store" });
    if (!res.ok) throw new Error(res.status + " " + res.statusText);
    const data = await res.json();
    signOut.value = data.text || "";
  } catch (err) {
    console.warn("GET /get_words failed:", err.message);
  }
}
setInterval(updateSignOutput, 1000);

// Copy + Clear for sign text
document.getElementById("btn-copy-sign").addEventListener("click", async () => {
  const v = signOut.value.trim();
  if (v) await navigator.clipboard.writeText(v);
});
document.getElementById("btn-clear-sign").addEventListener("click", async () => {
  signOut.value = "";
  try { await fetch("http://localhost:5000/clear_words", { method: "POST" }); }
  catch (e) { console.warn("POST /clear_words failed:", e.message); }
});


// ========== SPEECH → TEXT (English only) ==========
const micStatus = document.getElementById("mic-status");
const btnMic = document.getElementById("btn-mic");
const btnMicStop = document.getElementById("btn-mic-stop");
const speechOut = document.getElementById("speech-output");

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let rec = null;
let listening = false;

if (!SpeechRecognition) {
  micStatus.textContent = "mic: not supported in this browser";
  btnMic.disabled = true;
  btnMicStop.disabled = true;
  console.warn("Web Speech API not available. Use Chrome on desktop.");
} else {
  function createRecognizer() {
    const r = new SpeechRecognition();
    r.lang = "en-US";      // English only
    r.continuous = true;
    r.interimResults = true;

    r.onresult = (e) => {
      const transcript = Array.from(e.results).map(res => res[0]?.transcript || "").join("");
      speechOut.value = transcript;
    };

    r.onerror = (e) => {
      console.error("SpeechRecognition error:", e.error);
      micStatus.textContent = "mic: error (" + e.error + ")";
      listening = false;
      btnMic.disabled = false;
      btnMicStop.disabled = true;
    };

    r.onend = () => {
      listening = false;
      micStatus.textContent = "mic: off";
      btnMic.disabled = false;
      btnMicStop.disabled = true;
    };

    return r;
  }

  btnMic.addEventListener("click", () => {
    if (listening) return;
    try {
      rec = createRecognizer();
      rec.start();
      listening = true;
      micStatus.textContent = "mic: on (English)";
      btnMic.disabled = true;
      btnMicStop.disabled = false;
    } catch (e) {
      console.warn("rec.start() failed:", e);
    }
  });

  btnMicStop.addEventListener("click", () => {
    if (!rec) return;
    try { rec.stop(); } catch (e) { console.warn("rec.stop() failed:", e); }
    rec = null;
  });
}

// Copy + Clear for speech output
document.getElementById("btn-copy-speech").addEventListener("click", async () => {
  const v = speechOut.value.trim();
  if (v) await navigator.clipboard.writeText(v);
});
document.getElementById("btn-clear-speech").addEventListener("click", () => {
  speechOut.value = "";
  micStatus.textContent = "mic: off";
  if (rec) { try { rec.stop(); } catch {} rec = null; }
  btnMic.disabled = false;
  btnMicStop.disabled = true;
  listening = false;
});
