const portraits = {
  normal:   "/static/assets/normal.png",
  thinking: "/static/assets/berpikir.png",
  confused: "/static/assets/bingung.png",
  angry:    "/static/assets/marah.png",
  happy:    "/static/assets/senang.png",
};

const elPortrait = document.getElementById("portrait");
const elMoodTag  = document.getElementById("moodTag");
const elText     = document.getElementById("text");
const elInput    = document.getElementById("input");
const btnSend    = document.getElementById("btnSend");

const btnHistory = document.getElementById("btnHistory");
const historyDialog = document.getElementById("historyDialog");
const historyBody = document.getElementById("historyBody");
const btnClear = document.getElementById("btnClear");

let isTyping = false;
let skipTyping = false;

function setMood(mood){
  const mapLabel = {
    normal:"NORMAL",
    thinking:"BERPIKIR",
    confused:"BINGUNG",
    angry:"MARAH",
    happy:"SENANG",
  };
  elPortrait.src = portraits[mood] ?? portraits.normal;
  elMoodTag.textContent = mapLabel[mood] ?? "NORMAL";
}

function sleep(ms){ return new Promise(r => setTimeout(r, ms)); }

async function typeText(text, { charDelay=14 } = {}){
  isTyping = true;
  skipTyping = false;
  elText.textContent = "";

  for (let i = 0; i < text.length; i++){
    if (skipTyping){
      elText.textContent = text;
      break;
    }
    elText.textContent += text[i];
    await sleep(charDelay);
  }

  isTyping = false;
}

function preloadPortraits(){
  Object.values(portraits).forEach((src) => {
    const img = new Image();
    img.src = src;
  });
}

function scrollHistoryToBottom(){
  historyBody.scrollTop = historyBody.scrollHeight;
}

function addHistoryBubble(role, label, text){
  const wrap = document.createElement("div");
  wrap.className = `bubble ${role}`;

  const meta = document.createElement("div");
  meta.className = "bubble__meta";
  meta.textContent = label;

  const body = document.createElement("div");
  body.textContent = text;

  wrap.appendChild(meta);
  wrap.appendChild(body);
  historyBody.appendChild(wrap);
  scrollHistoryToBottom();
}

async function askBackend(message){
  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message })
  });
  return res.json();
}

async function send(){
  const q = elInput.value.trim();
  if (!q) return;

  addHistoryBubble("user", "User", q);
  elInput.value = "";
  elInput.focus();

  // tampilkan thinking sebentar
  setMood("thinking");
  elText.textContent = "…";
  await sleep(180);

  let data;
  try{
    data = await askBackend(q);
  }catch(e){
    setMood("confused");
    await typeText("Server error / tidak bisa terhubung ke backend.", { charDelay: 12 });
    addHistoryBubble("bot", "Q-Bot • confused", "Server error / tidak bisa terhubung ke backend.");
    return;
  }

  const reply = String(data.reply ?? "Maaf, saya tidak mengerti.");
  const mood = String(data.mood ?? "normal");

  setMood(mood);
  await typeText(reply, { charDelay: 14 });
  addHistoryBubble("bot", `Q-Bot • ${mood}`, reply);
}

btnSend.addEventListener("click", send);
elInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") send();
});

elText.addEventListener("click", () => { skipTyping = true; });

btnHistory.addEventListener("click", () => historyDialog.showModal());
btnClear.addEventListener("click", () => { historyBody.innerHTML = ""; });

preloadPortraits();
setMood("normal");
typeText("Q-Bot siap. Tanya fisika kuantum apa saja…", { charDelay: 14 });
addHistoryBubble("bot", "Q-Bot • normal", "Q-Bot siap. Tanya fisika kuantum apa saja…");
