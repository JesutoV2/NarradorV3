// extension/content.js (MV3) - UI con estados completos
(() => {
  const BACKEND = "http://127.0.0.1:8000";

  if (window.__snw_injected) return;
  window.__snw_injected = true;

  // ========== Estado con posición persistente ==========
  let state = {
    current: 'idle',
    runId: null,
    clickable: true,
    position: null  // {left, top} o null si usa posición default
  };

  // Cargar posición guardada al inicio
  (async function loadPosition() {
    try {
      const storageKey = `snw_btn_position_${window.location.hostname}`;
      const result = await chrome.storage.local.get(storageKey);
      if (result[storageKey]) {
        state.position = result[storageKey];
        console.log("[CONTENT] Posición cargada:", state.position);
      }
    } catch (e) {
      console.warn("[CONTENT] No se pudo cargar posición:", e);
    }
  })();

  // ========== Configuración de botón por estado ==========
  const STATE_CONFIG = {
    idle: {
      label: "Narrar",
      bg: "#0ea5e9",
      color: "#ffffff",
      clickable: true
    },
    processing: {
      label: "Procesando…",
      bg: "#f59e0b",
      color: "#000000",
      clickable: false
    },
    playing: {
      label: "Pausar",
      bg: "#10b981",
      color: "#ffffff",
      clickable: true
    },
    paused: {
      label: "Reproducir",
      bg: "#64748b",
      color: "#ffffff",
      clickable: true
    },
    error: {
      label: "Error",
      bg: "#ef4444",
      color: "#ffffff",
      clickable: false
    }
  };

  function setState(newState) {
    console.log(`[CONTENT] Estado: ${state.current} → ${newState}`);
    state.current = newState;
    updateButton();
  }

  function updateButton() {
    const btn = ensureBtn();
    const config = STATE_CONFIG[state.current] || STATE_CONFIG.idle;
    
    btn.textContent = config.label;
    state.clickable = config.clickable;
    
    // ========== FIX: Usar setProperty con 'important' ==========
    btn.style.setProperty('background', config.bg, 'important');
    btn.style.setProperty('color', config.color, 'important');
    
    if (config.clickable) {
      btn.style.cursor = "pointer";
      btn.style.opacity = "1";
    } else {
      btn.style.cursor = "not-allowed";
      btn.style.opacity = "0.7";
    }
    
    console.log(`[CONTENT] Botón actualizado: ${config.label} (${config.bg})`);
  }

  function ensureBtn() {
    let b = document.getElementById("snw-btn");
    if (!b) {
      b = document.createElement("button");
      b.id = "snw-btn";
      b.className = "snw-btn";
      b.textContent = "Narrar";
      
      // Estilos base (sin box-shadow)
      Object.assign(b.style, {
        position: "fixed",
        right: "12px",
        bottom: "12px",
        padding: "10px 14px",
        zIndex: "2147483646",
        borderRadius: "999px",
        border: "none",
        color: "#fff",
        background: "#0ea5e9",
        fontFamily: "system-ui, sans-serif",
        fontSize: "14px",
        fontWeight: "600",
        cursor: "pointer",
        userSelect: "none",
        transition: "opacity 0.2s ease"
      });
      
      // ========== DRAG & DROP ==========
      let isDragging = false;
      let dragStartX, dragStartY;
      let buttonStartX, buttonStartY;
      let hasMoved = false;
      
      b.addEventListener("mousedown", (e) => {
        // Solo iniciar drag con botón izquierdo
        if (e.button !== 0) return;
        
        isDragging = true;
        hasMoved = false;
        
        // Guardar posiciones iniciales
        const rect = b.getBoundingClientRect();
        dragStartX = e.clientX;
        dragStartY = e.clientY;
        buttonStartX = rect.left;
        buttonStartY = rect.top;
        
        // Cambiar a absolute para drag
        b.style.right = "auto";
        b.style.bottom = "auto";
        b.style.left = buttonStartX + "px";
        b.style.top = buttonStartY + "px";
        
        e.preventDefault();
      });
      
      document.addEventListener("mousemove", (e) => {
        if (!isDragging) return;
        
        const deltaX = e.clientX - dragStartX;
        const deltaY = e.clientY - dragStartY;
        
        // Si se movió más de 5px, considerarlo drag (no click)
        if (Math.abs(deltaX) > 5 || Math.abs(deltaY) > 5) {
          hasMoved = true;
        }
        
        // Calcular nueva posición
        let newX = buttonStartX + deltaX;
        let newY = buttonStartY + deltaY;
        
        // Limitar a viewport
        const maxX = window.innerWidth - b.offsetWidth;
        const maxY = window.innerHeight - b.offsetHeight;
        
        newX = Math.max(0, Math.min(newX, maxX));
        newY = Math.max(0, Math.min(newY, maxY));
        
        b.style.left = newX + "px";
        b.style.top = newY + "px";
      });
      
      document.addEventListener("mouseup", (e) => {
        if (!isDragging) return;
        isDragging = false;
        
        // Si NO se movió, es un click normal
        if (!hasMoved) {
          // Restaurar posición fixed
          b.style.position = "fixed";
          b.style.right = "12px";
          b.style.bottom = "12px";
          b.style.left = "auto";
          b.style.top = "auto";
          
          // Ejecutar click handler
          onClick();
        }
        // Si SÍ se movió, dejar en posición absolute donde quedó
      });
      
      document.documentElement.appendChild(b);
    }
    return b;
  }

  async function onClick() {
    if (!state.clickable) return;
    
    const currentState = state.current;
    
    // ========== FSM (Finite State Machine) ==========
    if (currentState === 'idle') {
      await handleStart();
    } else if (currentState === 'playing') {
      await handlePause();
    } else if (currentState === 'paused') {
      await handleResume();
    }
    // 'processing' y 'error' no son clicables
  }

  async function handleStart() {
    try {
      setState('processing');
      
      const html = document.documentElement ? 
        document.documentElement.outerHTML : 
        document.body.outerHTML;
      
      const payload = { html, url: location.href };
      
      const res = await fetch(`${BACKEND}/speak`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      
      let data = null;
      try { data = await res.json(); } catch (_) {}
      
      if (!res.ok) {
        const detail = data?.detail || data?.message || `HTTP ${res.status}`;
        throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
      }
      
      const runId = data?.run_id;
      if (!runId) throw new Error("Respuesta inválida del backend (sin run_id).");
      
      state.runId = runId;
      
      await sendToSW({
        cmd: 'play',
        run_id: runId,
        stream_url: `${BACKEND}/stream/${runId}`
      });
      
      // El estado cambiará a 'playing' cuando offscreen notifique
      // Timeout de seguridad por si no llega la notificación
      setTimeout(() => {
        if (state.current === 'processing') {
          setState('playing');
        }
      }, 1000);
      
    } catch (e) {
      console.error("[CONTENT] Start error:", e);
      showError();
    }
  }

  async function handlePause() {
    try {
      await sendToSW({ cmd: 'pause' });
      // El estado cambiará a 'paused' cuando offscreen notifique
    } catch (e) {
      console.error("[CONTENT] Pause error:", e);
    }
  }

  async function handleResume() {
    try {
      await sendToSW({ cmd: 'resume' });
      // El estado cambiará a 'playing' cuando offscreen notifique
    } catch (e) {
      console.error("[CONTENT] Resume error:", e);
    }
  }

  async function handleStop() {
    try {
      await sendToSW({ cmd: 'stop' });
      state.runId = null;
      setState('idle');
    } catch (e) {
      console.error("[CONTENT] Stop error:", e);
      setState('idle'); // Forzar idle incluso si falla
    }
  }

  function showError() {
    setState('error');
    setTimeout(() => {
      setState('idle');
      state.runId = null;
    }, 3000);
  }

  function sendToSW(msg) {
    return new Promise((resolve) => {
      try {
        chrome.runtime.sendMessage(msg, (resp) => resolve(resp));
      } catch (e) {
        console.error("[CONTENT] sendMessage error:", e);
        resolve(null);
      }
    });
  }

  // ========== Listener de cambios de estado desde service worker ==========
  chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    if (msg.cmd === 'audio_state_update') {
      console.log("[CONTENT] ✅ Recibido audio_state_update:", msg.state);
      
      if (msg.state === 'playing') {
        setState('playing');
      } else if (msg.state === 'paused') {
        setState('paused');
      } else if (msg.state === 'ended') {
        console.log("[CONTENT] ✅ Audio terminó, limpiando...");
        handleStop();
      } else if (msg.state === 'error') {
        showError();
      }
      
      sendResponse({ ok: true });
      return true;
    }
  });

  // Cleanup al cerrar página
  window.addEventListener("pagehide", () => {
    try {
      if (state.runId) {
        chrome.runtime.sendMessage({ cmd: "stop" });
      }
    } catch (e) {
      console.error("[CONTENT] Pagehide error:", e);
    }
  });

  ensureBtn();
  updateButton();
})();