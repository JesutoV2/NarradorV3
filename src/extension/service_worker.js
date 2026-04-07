// extension/service_worker.js (MV3) - Coordinador de estados
const BACKEND = "http://127.0.0.1:8000";
let currentRunId = null;
let currentTabId = null;

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  (async () => {
    try {
      // ========== Mensajes desde content.js ==========
      if (msg.cmd === "play") {
        // Cleanup anterior si existe
        if (currentRunId) {
          try {
            await fetch(`${BACKEND}/cleanup/${currentRunId}`, { method: "POST" });
          } catch (e) {
            console.warn("[SW] Cleanup failed:", e);
          }
        }
        
        await ensureOffscreen();
        currentRunId = msg.run_id || null;
        currentTabId = sender.tab?.id || null;
        
        await postToOffscreen({ cmd: "play", url: msg.stream_url });
        sendResponse({ ok: true });
      }
      
      else if (msg.cmd === "pause") {
        await ensureOffscreen();
        await postToOffscreen({ cmd: "pause" });
        sendResponse({ ok: true });
      }
      
      else if (msg.cmd === "resume") {
        await ensureOffscreen();
        await postToOffscreen({ cmd: "resume" });
        sendResponse({ ok: true });
      }
      
      else if (msg.cmd === "stop") {
        try {
          await ensureOffscreen();
          await postToOffscreen({ cmd: "stop" });
        } catch (e) {
          console.warn("[SW] Stop offscreen failed:", e);
        }
        
        if (currentRunId) {
          try {
            await fetch(`${BACKEND}/cleanup/${currentRunId}`, { method: "POST" });
          } catch (e) {
            console.warn("[SW] Cleanup failed:", e);
          }
        }
        
        currentRunId = null;
        currentTabId = null;
        sendResponse({ ok: true });
      }
      
      else if (msg.cmd === "get_state") {
        await ensureOffscreen();
        const result = await postToOffscreen({ cmd: "get_state" });
        sendResponse({ ok: true, state: result?.state || 'idle' });
      }
      
      // ========== Mensajes desde offscreen.js ==========
      else if (msg.target === 'service_worker' && msg.cmd === 'audio_state_changed') {
        // Audio cambió de estado, notificar al content script
        console.log("[SW] Audio state changed:", msg.state);
        
        if (currentTabId) {
          try {
            await chrome.tabs.sendMessage(currentTabId, {
              cmd: 'audio_state_update',
              state: msg.state,
              run_id: currentRunId
            });
          } catch (e) {
            console.warn("[SW] Failed to notify tab:", e);
          }
        }
        
        // Si terminó, hacer cleanup
        if (msg.state === 'ended' && currentRunId) {
          try {
            await fetch(`${BACKEND}/cleanup/${currentRunId}`, { method: "POST" });
          } catch (e) {
            console.warn("[SW] Cleanup on end failed:", e);
          }
          currentRunId = null;
        }
        
        sendResponse({ ok: true });
      }
      
      else {
        sendResponse({ ok: false, reason: "unknown-cmd" });
      }
    } catch (e) {
      console.error("[SW] Error:", e);
      sendResponse({ ok: false, reason: String(e) });
    }
  })();
  
  return true; // Async response
});

async function ensureOffscreen() {
  const has = await chrome.offscreen.hasDocument();
  if (!has) {
    await chrome.offscreen.createDocument({
      url: "offscreen.html",
      reasons: [chrome.offscreen.Reason.AUDIO_PLAYBACK],
      justification: "Reproducir audio TTS sin afectar CSP",
    });
  }
}

function postToOffscreen(message) {
  return chrome.runtime.sendMessage({ target: "offscreen", ...message });
}