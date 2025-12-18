import { sseFromFetch } from "./stream.js";
import { StreamingAudioPlayer } from "./audio.js";

const chatEl = document.getElementById("chat");
const inputEl = document.getElementById("input");
const sendBtn = document.getElementById("sendBtn");
const stopBtn = document.getElementById("stopBtn");
const statusText = document.getElementById("statusText");
const ttsToggle = document.getElementById("ttsToggle");
const audioEl = document.getElementById("audio");

let conversationId = null;
let chatAbort = null;
let generating = false;

const audioPlayer = new StreamingAudioPlayer(audioEl);

function setStatus(s) { statusText.textContent = s; }

function addMessage(role, content) {
  const msg = document.createElement("div");
  msg.className = `msg ${role}`;
  msg.innerHTML = `<div class="role">${role}</div><div class="content"></div>`;
  msg.querySelector(".content").textContent = content || "";
  chatEl.appendChild(msg);
  chatEl.scrollTop = chatEl.scrollHeight;
  return msg.querySelector(".content");
}

function autosize() {
  inputEl.style.height = "auto";
  inputEl.style.height = Math.min(inputEl.scrollHeight, 220) + "px";
}

function stopAll() {
  try { chatAbort?.abort(); } catch {}
  chatAbort = null;
  audioPlayer.stop();
  generating = false;
  stopBtn.disabled = true;
  sendBtn.disabled = false;
  setStatus("Interrumpido");
}

inputEl.addEventListener("input", () => {
  autosize();
  if (generating || audioPlayer.playing) stopAll();
});

stopBtn.addEventListener("click", () => stopAll());

async function send() {
  const text = (inputEl.value || "").trim();
  if (!text || generating) return;

  generating = true;
  stopBtn.disabled = false;
  sendBtn.disabled = true;
  setStatus("Generando…");

  addMessage("user", text);
  inputEl.value = "";
  autosize();

  const assistantEl = addMessage("assistant", "");
  let full = "";

  chatAbort = new AbortController();

  const resp = await fetch("/v1/chat/completions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      conversation_id: conversationId,
      stream: true,
      messages: [{ role: "user", content: text }]
    }),
    signal: chatAbort.signal
  });

  const hdrConv = resp.headers.get("X-Conversation-Id");
  if (hdrConv) conversationId = hdrConv;

  if (!resp.ok) {
    assistantEl.textContent = `Error: ${resp.status}`;
    generating = false;
    stopBtn.disabled = true;
    sendBtn.disabled = false;
    setStatus("Error");
    return;
  }

  try {
    for await (const data of sseFromFetch(resp, { signal: chatAbort.signal })) {
      if (data === "[DONE]") break;
      let obj;
      try { obj = JSON.parse(data); } catch { continue; }
      const delta = obj?.choices?.[0]?.delta?.content ?? "";
      if (!delta) continue;
      full += delta;
      assistantEl.textContent = full;
      chatEl.scrollTop = chatEl.scrollHeight;
    }
  } catch (e) {
    if (e?.name === "AbortError") return;
    assistantEl.textContent = "Error leyendo stream";
  } finally {
    chatAbort = null;
    generating = false;
    stopBtn.disabled = true;
    sendBtn.disabled = false;
  }

  setStatus("Listo");

  if (ttsToggle.checked && full.trim()) {
    setStatus("Reproduciendo audio…");
    try {
      await audioPlayer.playOpusStream("/v1/audio/speech", {
        input: full,
        response_format: "opus"
      });
    } catch (e) {
      console.warn(e);
    } finally {
      setStatus("Listo");
    }
  }
}

sendBtn.addEventListener("click", () => send());
inputEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    send();
  }
});

autosize();
setStatus("Listo");
