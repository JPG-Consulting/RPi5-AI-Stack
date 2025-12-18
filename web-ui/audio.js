function supportsOpusMSE() {
  return typeof MediaSource !== "undefined" &&
    MediaSource.isTypeSupported('audio/ogg; codecs="opus"');
}

export class StreamingAudioPlayer {
  constructor(audioEl) {
    this.audioEl = audioEl;
    this.abortController = null;
    this.mediaSource = null;
    this.sourceBuffer = null;
    this.queue = [];
    this.ended = false;
    this.playing = false;
  }

  stop() {
    try { this.abortController?.abort(); } catch {}
    this.abortController = null;

    try {
      this.audioEl.pause();
      this.audioEl.removeAttribute("src");
      this.audioEl.load();
      this.audioEl.classList.add("hidden");
    } catch {}

    this.queue = [];
    this.mediaSource = null;
    this.sourceBuffer = null;
    this.ended = false;
    this.playing = false;
  }

  async playOpusStream(url, body) {
    if (!supportsOpusMSE()) throw new Error("OPUS/OGG MediaSource not supported.");

    this.stop();
    this.abortController = new AbortController();

    this.mediaSource = new MediaSource();
    this.audioEl.src = URL.createObjectURL(this.mediaSource);
    this.audioEl.classList.remove("hidden");

    await new Promise((resolve, reject) => {
      this.mediaSource.addEventListener("sourceopen", () => resolve(), { once: true });
      this.mediaSource.addEventListener("error", () => reject(new Error("MediaSource error")), { once: true });
    });

    this.sourceBuffer = this.mediaSource.addSourceBuffer('audio/ogg; codecs="opus"');
    this.sourceBuffer.mode = "sequence";

    const pump = () => {
      if (!this.sourceBuffer || this.sourceBuffer.updating) return;
      const chunk = this.queue.shift();
      if (!chunk) {
        if (this.ended && this.mediaSource?.readyState === "open") {
          try { this.mediaSource.endOfStream(); } catch {}
        }
        return;
      }
      try { this.sourceBuffer.appendBuffer(chunk); } catch {}
    };

    this.sourceBuffer.addEventListener("updateend", pump);

    const resp = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: this.abortController.signal
    });
    if (!resp.ok) throw new Error(`TTS failed: ${resp.status}`);

    const reader = resp.body.getReader();

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      if (value && value.byteLength) {
        const copy = value.buffer.slice(value.byteOffset, value.byteOffset + value.byteLength);
        this.queue.push(copy);
        pump();
        if (!this.playing) {
          this.playing = true;
          try { await this.audioEl.play(); } catch {}
        }
      }
    }

    this.ended = true;
    pump();
  }
}
