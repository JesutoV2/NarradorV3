// extension/offscreen.js - Control completo de audio
let audioEl = null;

function ensureAudio() {
  if (!audioEl) {
    audioEl = document.getElementById("snw-audio");
    if (!audioEl) {
      audioEl = document.createElement("audio");
      audioEl.id = "snw-audio";
      document.body.appendChild(audioEl);
    }
    audioEl.autoplay = true;
    audioEl.controls = false;
    
    // ========== SOLUCIÓN 3: Listeners de eventos ==========
    audioEl.addEventListener('play', () => {
      console.log("[OFFSCREEN] Audio: play");
      notifyStateChange('playing');
    });
    
    audioEl.addEventListener('pause', () => {
      console.log("[OFFSCREEN] Audio: pause");
      notifyStateChange('paused');
    });
    
    audioEl.addEventListener('ended', () => {
      console.log("[OFFSCREEN] Audio: ended - notificando");
      // Pequeño delay para asegurar que el estado se procese
      setTimeout(() => {
        notifyStateChange('ended');
      }, 100);
    });
    
    audioEl.addEventListener('error', (e) => {
      console.error("[OFFSCREEN] Audio error:", e);
      notifyStateChange('error');
    });
  }
  return audioEl;
}

// Notificar cambios de estado al service worker
function notifyStateChange(state) {
  try {
    chrome.runtime.sendMessage({
      target: 'service_worker',
      cmd: 'audio_state_changed',
      state: state
    });
  } catch (e) {
    console.error("[OFFSCREEN] Failed to notify state change:", e);
  }
}

async function play(url) {
  const a = ensureAudio();
  try {
    a.src = url;
    await a.play();
    // El evento 'play' notificará automáticamente
  } catch (e) {
    console.error("[OFFSCREEN] Play error:", e);
    notifyStateChange('error');
  }
}

async function pause() {
  const a = ensureAudio();
  try {
    a.pause();
    // El evento 'pause' notificará automáticamente
  } catch (e) {
    console.error("[OFFSCREEN] Pause error:", e);
  }
}

async function resume() {
  const a = ensureAudio();
  try {
    await a.play();
    // El evento 'play' notificará automáticamente
  } catch (e) {
    console.error("[OFFSCREEN] Resume error:", e);
  }
}

function stop() {
  const a = ensureAudio();
  try {
    a.pause();
    a.removeAttribute("src");
    a.load();
    notifyStateChange('stopped');
  } catch (e) {
    console.error("[OFFSCREEN] Stop error:", e);
  }
}

function getState() {
  const a = ensureAudio();
  if (!a.src || a.src === '') {
    return 'idle';
  }
  if (a.paused) {
    if (a.ended) {
      return 'ended';
    }
    return 'paused';
  }
  return 'playing';
}

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (!msg || msg.target !== "offscreen") return;
  
  (async () => {
    try {
      if (msg.cmd === "play") {
        await play(msg.url);
        sendResponse({ ok: true, state: 'playing' });
      } else if (msg.cmd === "pause") {
        await pause();
        sendResponse({ ok: true, state: 'paused' });
      } else if (msg.cmd === "resume") {
        await resume();
        sendResponse({ ok: true, state: 'playing' });
      } else if (msg.cmd === "stop") {
        stop();
        sendResponse({ ok: true, state: 'stopped' });
      } else if (msg.cmd === "get_state") {
        const state = getState();
        sendResponse({ ok: true, state: state });
      } else {
        sendResponse({ ok: false, error: 'unknown_command' });
      }
    } catch (e) {
      console.error("[OFFSCREEN] Command error:", e);
      sendResponse({ ok: false, error: e.message });
    }
  })();
  
  return true; // Async response
});