// ==============================================================================
// LecturaAI Studio - Professional Frontend Controller
// ==============================================================================

const STATE = {
  lectureTitle: "Convolutional Neural Networks: Deep Visual Perception",
  voiceProfile: "en-US-ChristopherNeural",
  theme: "dark_modern",
  burnSubtitles: true,
  kenBurns: false,
  activeSlideIndex: 0,
  slides: [
    {
      index: 1,
      title: "Biological Foundations of CNNs",
      bullet_points: [
        "Hubel & Wiesel: Receptive fields in mammalian visual cortex",
        "Hierarchical processing: From edge detectors to semantic entities",
        "Spatial invariance and parameter reduction vs dense MLPs"
      ],
      code_snippet: "import torch\nimport torch.nn as nn\n\n# 2D Convolution with 16 filters\nlayer = nn.Conv2d(in_channels=3, out_channels=16, kernel_size=3, padding=1)",
      spoken_script: "Welcome to our lecture on Convolutional Neural Networks. In this opening section, we examine the biological motivation behind spatial filtering and discover how hierarchical convolutions overcome the parameter explosion of traditional dense layers."
    },
    {
      index: 2,
      title: "Convolution Operations & Feature Maps",
      bullet_points: [
        "Kernel cross-correlation sliding across spatial dimensions",
        "Stride (S) and Zero-Padding (P) determine output resolution",
        "Feature maps capture translation-invariant local patterns"
      ],
      code_snippet: "# Spatial output dimension formula\n# Output = floor((Input - Kernel + 2*Pad) / Stride) + 1",
      spoken_script: "As the kernel moves across our input image, it performs localized dot products. Stride controls downsampling speed, while zero-padding preserves border information, producing activation feature maps."
    },
    {
      index: 3,
      title: "Downsampling: Max & Average Pooling",
      bullet_points: [
        "Max Pooling: Extracts prominent activation features",
        "Average Pooling: Aggregates global spatial contextual averages",
        "Decreases memory footprint and mitigates overfitting"
      ],
      code_snippet: "pool = nn.MaxPool2d(kernel_size=2, stride=2)",
      spoken_script: "Following convolutional feature extraction, pooling layers progressively compress the spatial volume. Max pooling selects the strongest signal in each window, providing spatial robustness and computational efficiency."
    },
    {
      index: 4,
      title: "Modern Horizons: ResNets to Vision Transformers",
      bullet_points: [
        "Residual skip connections: Solving vanishing gradients in deep nets",
        "Self-attention mechanisms: Global receptive fields in ViTs",
        "Next Session: Hands-on fine-tuning with PyTorch & Hugging Face"
      ],
      code_snippet: "# Residual Connection\nx_out = f(x) + x",
      spoken_script: "In modern production architectures, residual skip connections enable the training of models with hundreds of layers. In our next workshop, we will contrast CNNs against modern Vision Transformers. Thank you."
    }
  ],
  voices: [],
  themes: {},
  activeJobId: null,
  pollInterval: null,
  currentAudio: null
};

// --- Application Initialization ---
document.addEventListener("DOMContentLoaded", async () => {
  setupTabs();
  setupInspectorTabs();
  await loadVoices();
  await loadThemes();
  renderFilmstrip();
  updateInspectorForActiveSlide();
  drawSlidePreview();
  setupEventListeners();
  setupKeyboardNav();
  setupModals();
  loadRecentLectures();
});

// --- Tab Navigation ---
function setupTabs() {
  const tabs = document.querySelectorAll(".tab-btn");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach(tc => tc.classList.remove("active"));

      tab.classList.add("active");
      const targetId = tab.getAttribute("data-tab");
      const targetEl = document.getElementById(targetId);
      if (targetEl) targetEl.classList.add("active");

      if (targetId === "studio-tab") {
        setTimeout(drawSlidePreview, 40);
      }
    });
  });
}

function switchTab(tabId) {
  const targetBtn = document.querySelector(`.tab-btn[data-tab="${tabId}"]`);
  if (targetBtn) targetBtn.click();
}

// --- Inspector Tab Navigation ---
function setupInspectorTabs() {
  const inspBtns = document.querySelectorAll(".inspector-tab-btn");
  inspBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      inspBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const mode = btn.getAttribute("data-insp");

      document.getElementById("inspectorContentSection").style.display = mode === "content" ? "block" : "none";
      document.getElementById("inspectorCodeSection").style.display = mode === "code" ? "block" : "none";
      document.getElementById("inspectorNarrationSection").style.display = mode === "narration" ? "block" : "none";
    });
  });
}

// --- Sample Deck Loader ---
async function loadSampleDeck(deckKey) {
  try {
    showToast(`Loading "${deckKey}" lecture deck...`, "info");
    const res = await fetch("/api/sample-decks");
    if (!res.ok) throw new Error("Could not fetch sample decks");
    const decks = await res.json();
    const selected = decks[deckKey];
    if (!selected) return;

    STATE.lectureTitle = selected.lecture_title;
    STATE.voiceProfile = selected.voice_profile;
    STATE.theme = selected.theme;
    STATE.slides = selected.slides;
    STATE.activeSlideIndex = 0;

    document.getElementById("lectureTitleInput").value = STATE.lectureTitle;
    document.getElementById("voiceSelect").value = STATE.voiceProfile;
    document.getElementById("themeSelect").value = STATE.theme;
    updateQuickThemeDots();

    renderFilmstrip();
    updateInspectorForActiveSlide();
    drawSlidePreview();
    renderVoiceCards();
    switchTab("studio-tab");

    showToast(`Loaded "${selected.lecture_title}"!`, "success");
  } catch (err) {
    showToast("Error loading sample deck: " + err.message, "error");
  }
}

// --- Voice & Theme Data Loaders ---
async function loadVoices() {
  try {
    const res = await fetch("/api/voices");
    STATE.voices = await res.json();

    const select = document.getElementById("voiceSelect");
    if (select) {
      select.innerHTML = "";
      STATE.voices.forEach(v => {
        const opt = document.createElement("option");
        opt.value = v.id;
        opt.textContent = `${v.name} (${v.gender})`;
        if (v.id === STATE.voiceProfile) opt.selected = true;
        select.appendChild(opt);
      });
    }

    renderVoiceCards();
  } catch (err) {
    console.error("Failed to load voices:", err);
  }
}

function renderVoiceCards() {
  const container = document.getElementById("voiceCardsGrid");
  if (!container) return;
  container.innerHTML = "";

  const flags = {
    "en-US": "🇺🇸",
    "en-GB": "🇬🇧",
    "en-IN": "🇮🇳"
  };

  STATE.voices.forEach(v => {
    const card = document.createElement("div");
    card.className = `voice-card ${v.id === STATE.voiceProfile ? "selected" : ""}`;
    const flag = flags[v.locale] || "🌐";

    card.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
        <span style="font-size: 1.4rem;">${flag}</span>
        <span class="telemetry-tag">${v.gender}</span>
      </div>
      <h3 style="font-size: 0.98rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.2rem;">${v.name}</h3>
      <p style="font-size: 0.78rem; color: var(--text-muted); margin-bottom: 0.85rem;">Locale: ${v.locale} • Neural HD</p>
      <div style="display: flex; gap: 0.5rem;">
        <button class="btn btn-secondary btn-sm" onclick="event.stopPropagation(); playVoicePreview('${v.id}')">
          🔊 Sample
        </button>
      </div>
    `;

    card.addEventListener("click", () => {
      STATE.voiceProfile = v.id;
      const select = document.getElementById("voiceSelect");
      if (select) select.value = v.id;
      renderVoiceCards();
      showToast(`Selected voice: ${v.name}`, "info");
    });

    container.appendChild(card);
  });
}

async function loadThemes() {
  try {
    const res = await fetch("/api/themes");
    STATE.themes = await res.json();
    const select = document.getElementById("themeSelect");
    if (select) {
      select.innerHTML = "";
      for (const [key, val] of Object.entries(STATE.themes)) {
        const opt = document.createElement("option");
        opt.value = key;
        opt.textContent = val.name;
        if (key === STATE.theme) opt.selected = true;
        select.appendChild(opt);
      }
    }
    updateQuickThemeDots();
  } catch (err) {
    console.error("Failed to load themes:", err);
  }
}

function updateQuickThemeDots() {
  const dots = document.querySelectorAll(".theme-pill-dot");
  dots.forEach(d => {
    if (d.getAttribute("data-theme") === STATE.theme) {
      d.classList.add("active");
    } else {
      d.classList.remove("active");
    }
  });
}

function setQuickTheme(themeKey) {
  STATE.theme = themeKey;
  const select = document.getElementById("themeSelect");
  if (select) select.value = themeKey;
  updateQuickThemeDots();
  drawSlidePreview();
  showToast(`Switched theme to ${STATE.themes[themeKey]?.name || themeKey}`, "info");
}

// --- Filmstrip & Slide Timeline ---
function renderFilmstrip() {
  const list = document.getElementById("filmstripList");
  if (!list) return;
  list.innerHTML = "";

  document.getElementById("slideCounterBadge").textContent = `${STATE.slides.length} Slides`;
  document.getElementById("stageSlideIndicator").textContent = `Slide ${STATE.activeSlideIndex + 1} of ${STATE.slides.length}`;

  STATE.slides.forEach((slide, idx) => {
    const item = document.createElement("div");
    item.className = `filmstrip-item ${idx === STATE.activeSlideIndex ? "active" : ""}`;
    item.draggable = true;

    const snippet = slide.spoken_script || slide.bullet_points.join(" ") || "No narration defined";

    item.innerHTML = `
      <div class="filmstrip-top">
        <span class="slide-number-pill">#${idx + 1}</span>
        <div class="filmstrip-controls" onclick="event.stopPropagation()">
          <button class="icon-btn" onclick="moveSlideOrder(${idx}, -1)" title="Move slide up" ${idx === 0 ? "disabled style='opacity:0.3;'" : ""}>▲</button>
          <button class="icon-btn" onclick="moveSlideOrder(${idx}, 1)" title="Move slide down" ${idx === STATE.slides.length - 1 ? "disabled style='opacity:0.3;'" : ""}>▼</button>
        </div>
      </div>
      <div class="filmstrip-title">${escapeHtml(slide.title || "Untitled Slide")}</div>
      <div class="filmstrip-snippet">${escapeHtml(snippet)}</div>
    `;

    item.addEventListener("click", () => {
      STATE.activeSlideIndex = idx;
      renderFilmstrip();
      updateInspectorForActiveSlide();
      drawSlidePreview();
    });

    list.appendChild(item);
  });
}

function moveSlideOrder(idx, delta) {
  const targetIdx = idx + delta;
  if (targetIdx < 0 || targetIdx >= STATE.slides.length) return;

  const item = STATE.slides.splice(idx, 1)[0];
  STATE.slides.splice(targetIdx, 0, item);

  if (STATE.activeSlideIndex === idx) {
    STATE.activeSlideIndex = targetIdx;
  } else if (STATE.activeSlideIndex === targetIdx) {
    STATE.activeSlideIndex = idx;
  }

  // Update slide index numbers
  STATE.slides.forEach((s, i) => s.index = i + 1);

  renderFilmstrip();
  drawSlidePreview();
}

// --- Slide Inspector Controller ---
function updateInspectorForActiveSlide() {
  const slide = STATE.slides[STATE.activeSlideIndex];
  if (!slide) return;

  document.getElementById("slideTitleInput").value = slide.title || "";
  document.getElementById("slideBulletsInput").value = (slide.bullet_points || []).join("\n");
  document.getElementById("slideCodeInput").value = slide.code_snippet || "";
  document.getElementById("slideScriptInput").value = slide.spoken_script || "";

  updateTeleprompterStats();
}

function updateTeleprompterStats() {
  const slide = STATE.slides[STATE.activeSlideIndex];
  if (!slide) return;

  const text = slide.spoken_script || "";
  const words = text.trim() ? text.trim().split(/\s+/).length : 0;
  // Standard educational speaking cadence: ~145 words per minute
  const estSec = Math.max(2, Math.round((words / 145) * 60));

  const wordEl = document.getElementById("teleprompterWordCount");
  const timeEl = document.getElementById("teleprompterEstTime");

  if (wordEl) wordEl.textContent = `${words} words`;
  if (timeEl) timeEl.textContent = `~${estSec}s narration`;
}

// --- Slide Management Operations ---
function duplicateCurrentSlide() {
  const current = STATE.slides[STATE.activeSlideIndex];
  if (!current) return;

  const copy = JSON.parse(JSON.stringify(current));
  copy.title = `${current.title} (Copy)`;
  copy.index = STATE.slides.length + 1;

  STATE.slides.splice(STATE.activeSlideIndex + 1, 0, copy);
  STATE.activeSlideIndex += 1;

  // Re-index
  STATE.slides.forEach((s, i) => s.index = i + 1);

  renderFilmstrip();
  updateInspectorForActiveSlide();
  drawSlidePreview();
  showToast("Slide duplicated successfully", "success");
}

function deleteCurrentSlide() {
  if (STATE.slides.length <= 1) {
    showToast("A lecture requires at least one slide!", "error");
    return;
  }

  STATE.slides.splice(STATE.activeSlideIndex, 1);
  if (STATE.activeSlideIndex >= STATE.slides.length) {
    STATE.activeSlideIndex = STATE.slides.length - 1;
  }

  // Re-index
  STATE.slides.forEach((s, i) => s.index = i + 1);

  renderFilmstrip();
  updateInspectorForActiveSlide();
  drawSlidePreview();
  showToast("Slide removed from lecture", "info");
}

function addSlide() {
  const newIdx = STATE.slides.length + 1;
  const newSlide = {
    index: newIdx,
    title: `Key Concept ${newIdx}`,
    bullet_points: [
      "Primary theoretical principle",
      "Empirical evidence and validation",
      "System design consideration"
    ],
    code_snippet: "",
    spoken_script: `In this section, we examine key concept ${newIdx} in detail, focusing on implementation patterns and performance tradeoffs.`
  };

  STATE.slides.push(newSlide);
  STATE.activeSlideIndex = STATE.slides.length - 1;

  renderFilmstrip();
  updateInspectorForActiveSlide();
  drawSlidePreview();
  showToast(`Slide ${newIdx} added`, "success");
}

function navigateSlide(delta) {
  const target = STATE.activeSlideIndex + delta;
  if (target >= 0 && target < STATE.slides.length) {
    STATE.activeSlideIndex = target;
    renderFilmstrip();
    updateInspectorForActiveSlide();
    drawSlidePreview();
  }
}

// --- AI Script Polisher / Enhancer ---
function enhanceCurrentScript() {
  const slide = STATE.slides[STATE.activeSlideIndex];
  if (!slide) return;

  const title = slide.title || "this topic";
  const bullets = slide.bullet_points.join(". ");

  const intros = [
    `Now, let's turn our attention to ${title}.`,
    `Moving forward to an essential milestone, ${title}.`,
    `To build upon our foundational principles, let us analyze ${title}.`
  ];
  const conclusions = [
    `Notice how these elements synthesize to deliver robust performance in practice.`,
    `Understanding this interaction is critical before evaluating advanced architectures.`,
    `Keep these structural dynamics in mind as we proceed to the subsequent slide.`
  ];

  const intro = intros[Math.floor(Math.random() * intros.length)];
  const outro = conclusions[Math.floor(Math.random() * conclusions.length)];

  const enhanced = `${intro} Specifically, ${bullets}. ${outro}`;
  slide.spoken_script = enhanced;

  document.getElementById("slideScriptInput").value = enhanced;
  updateTeleprompterStats();
  renderFilmstrip();
  showToast("Script enhanced with academic pedagogical cadence!", "success");
}

// --- Live Audio Narration Preview ---
async function testCurrentSlideSpeech() {
  const slide = STATE.slides[STATE.activeSlideIndex];
  if (!slide) return;

  const text = slide.spoken_script || "No spoken narration written for this slide.";
  const btn = document.getElementById("btnTestSlideSpeech");
  const eq = document.getElementById("voiceEqualizer");

  btn.disabled = true;
  btn.textContent = "🔊 Synthesizing...";
  if (eq) eq.classList.add("animating");

  try {
    const formData = new FormData();
    formData.append("voice", STATE.voiceProfile);
    formData.append("text", text);

    const res = await fetch("/api/preview-voice", { method: "POST", body: formData });
    if (!res.ok) throw new Error("TTS synthesis failed");
    const data = await res.json();

    if (STATE.currentAudio) {
      STATE.currentAudio.pause();
    }

    const audio = new Audio(data.audio_url);
    STATE.currentAudio = audio;

    audio.onended = () => {
      if (eq) eq.classList.remove("animating");
      btn.disabled = false;
      btn.textContent = "🔊 Test Voice on This Slide";
    };

    audio.onerror = () => {
      if (eq) eq.classList.remove("animating");
      btn.disabled = false;
      btn.textContent = "🔊 Test Voice on This Slide";
    };

    await audio.play();
    showToast("Playing live voice narration sample...", "info");
  } catch (err) {
    if (eq) eq.classList.remove("animating");
    btn.disabled = false;
    btn.textContent = "🔊 Test Voice on This Slide";
    showToast("Voice preview error: " + err.message, "error");
  }
}

async function playVoicePreview(voiceId) {
  try {
    const formData = new FormData();
    formData.append("voice", voiceId);
    formData.append("text", "Welcome to LecturaAI Studio. This is how your video lecture narration will sound with natural intonation.");

    const res = await fetch("/api/preview-voice", { method: "POST", body: formData });
    if (!res.ok) throw new Error("Could not synthesize voice sample");
    const data = await res.json();

    if (STATE.currentAudio) STATE.currentAudio.pause();
    const audio = new Audio(data.audio_url);
    STATE.currentAudio = audio;
    await audio.play();

    showToast(`Playing voice sample for ${voiceId}`, "info");
  } catch (err) {
    showToast("Voice sample failed: " + err.message, "error");
  }
}

// --- 1080p Canvas Slide Renderer ---
function drawSlidePreview() {
  const canvas = document.getElementById("slideCanvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const slide = STATE.slides[STATE.activeSlideIndex];
  if (!slide) return;

  const theme = STATE.themes[STATE.theme] || {
    bg_color: "#0F172A",
    card_bg: "#1E293B",
    accent_color: "#38BDF8",
    title_color: "#F8FAFC",
    text_color: "#CBD5E1",
    code_bg: "#0B1120",
    code_text: "#38BDF8",
    footer_color: "#64748B"
  };

  const W = 1920;
  const H = 1080;
  canvas.width = W;
  canvas.height = H;

  // Background Fill
  ctx.fillStyle = theme.bg_color;
  ctx.fillRect(0, 0, W, H);

  // Subtle Background Radial Glow
  const grad = ctx.createRadialGradient(W / 2, 0, 50, W / 2, H / 2, 1100);
  grad.addColorStop(0, hexToRgba(theme.accent_color, 0.12));
  grad.addColorStop(1, "transparent");
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, W, H);

  // Top Neon Accent Bar
  ctx.fillStyle = theme.accent_color;
  ctx.fillRect(0, 0, W, 10);

  // Main Card Container
  const pad = 80;
  ctx.fillStyle = theme.card_bg;
  ctx.strokeStyle = hexToRgba(theme.accent_color, 0.4);
  ctx.lineWidth = 1.5;
  ctx.beginPath();
  ctx.roundRect(pad, 60, W - pad * 2, H - 130, 24);
  ctx.fill();
  ctx.stroke();

  // Slide Title
  ctx.fillStyle = theme.title_color;
  ctx.font = "bold 54px Outfit, Inter, Arial, sans-serif";
  ctx.fillText(slide.title || "Untitled Slide", pad + 60, 160);

  // Accent Line Under Title
  ctx.fillStyle = theme.accent_color;
  ctx.fillRect(pad + 60, 195, 240, 5);

  // Content & Code Split Calculation
  const hasCode = Boolean(slide.code_snippet && slide.code_snippet.trim());
  ctx.fillStyle = theme.text_color;
  ctx.font = "34px Inter, Arial, sans-serif";

  let y = 280;
  const bullets = slide.bullet_points || [];
  bullets.slice(0, 5).forEach(bullet => {
    // Bullet Dot Indicator
    ctx.fillStyle = theme.accent_color;
    ctx.beginPath();
    ctx.arc(pad + 72, y - 10, 8, 0, Math.PI * 2);
    ctx.fill();

    // Bullet Text
    ctx.fillStyle = theme.text_color;
    const maxChars = hasCode ? 38 : 64;
    const lines = wrapText(bullet, maxChars);
    lines.forEach(l => {
      ctx.fillText(l, pad + 105, y);
      y += 46;
    });
    y += 24;
  });

  // Code Snippet Box (If Present)
  if (hasCode) {
    const codeX = W / 2 + 20;
    const codeY = 240;
    const codeW = W - pad - 60 - codeX;
    const codeH = H - 380;

    // Code container background
    ctx.fillStyle = theme.code_bg;
    ctx.strokeStyle = hexToRgba(theme.accent_color, 0.5);
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.roundRect(codeX, codeY, codeW, codeH, 14);
    ctx.fill();
    ctx.stroke();

    // Code Header Bar
    ctx.fillStyle = hexToRgba(theme.card_bg, 0.95);
    ctx.fillRect(codeX, codeY, codeW, 42);
    ctx.fillStyle = theme.accent_color;
    ctx.font = "bold 18px 'JetBrains Mono', monospace";
    ctx.fillText("Code Implementation", codeX + 20, codeY + 28);

    // Code lines
    ctx.fillStyle = theme.code_text;
    ctx.font = "22px 'JetBrains Mono', monospace";
    const clines = slide.code_snippet.split("\n").slice(0, 12);
    let cy = codeY + 76;
    clines.forEach(cl => {
      ctx.fillText(cl.substring(0, 48), codeX + 24, cy);
      cy += 32;
    });
  }

  // Footer Metadata
  ctx.fillStyle = theme.footer_color;
  ctx.font = "22px Inter, Arial, sans-serif";
  ctx.fillText(`${STATE.lectureTitle}  |  Slide ${STATE.activeSlideIndex + 1} of ${STATE.slides.length}`, pad + 60, H - 100);

  ctx.fillStyle = theme.accent_color;
  ctx.fillText("LecturaAI Studio 1080p", W - pad - 320, H - 100);
}

function wrapText(text, maxChars) {
  const words = text.split(" ");
  const lines = [];
  let curr = [];
  let len = 0;
  for (const w of words) {
    if (len + w.length + 1 <= maxChars) {
      curr.push(w);
      len += w.length + 1;
    } else {
      if (curr.length) lines.push(curr.join(" "));
      curr = [w];
      len = w.length;
    }
  }
  if (curr.length) lines.push(curr.join(" "));
  return lines;
}

function hexToRgba(hex, alpha) {
  const clean = hex.replace("#", "");
  const r = parseInt(clean.substring(0, 2), 16);
  const g = parseInt(clean.substring(2, 4), 16);
  const b = parseInt(clean.substring(4, 6), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

// Download Slide as PNG
function downloadSlideCanvasPNG() {
  const canvas = document.getElementById("slideCanvas");
  if (!canvas) return;
  const link = document.createElement("a");
  link.download = `slide_${STATE.activeSlideIndex + 1}_1080p.png`;
  link.href = canvas.toDataURL("image/png");
  link.click();
  showToast("Slide 1080p PNG downloaded!", "success");
}

function toggleCanvasFullscreen() {
  const container = document.querySelector(".slide-canvas-container");
  if (!document.fullscreenElement) {
    container.requestFullscreen().catch(err => {
      showToast("Fullscreen error: " + err.message, "error");
    });
  } else {
    document.exitFullscreen();
  }
}

// --- Event Listeners Setup ---
function setupEventListeners() {
  // Lecture title input
  document.getElementById("lectureTitleInput").value = STATE.lectureTitle;
  document.getElementById("lectureTitleInput").addEventListener("input", (e) => {
    STATE.lectureTitle = e.target.value;
    drawSlidePreview();
  });

  // Slide Inspector Real-time Inputs
  document.getElementById("slideTitleInput").addEventListener("input", (e) => {
    if (STATE.slides[STATE.activeSlideIndex]) {
      STATE.slides[STATE.activeSlideIndex].title = e.target.value;
      renderFilmstrip();
      drawSlidePreview();
    }
  });

  document.getElementById("slideBulletsInput").addEventListener("input", (e) => {
    if (STATE.slides[STATE.activeSlideIndex]) {
      const bullets = e.target.value.split("\n").map(s => s.trim()).filter(s => s.length > 0);
      STATE.slides[STATE.activeSlideIndex].bullet_points = bullets;
      drawSlidePreview();
    }
  });

  document.getElementById("slideCodeInput").addEventListener("input", (e) => {
    if (STATE.slides[STATE.activeSlideIndex]) {
      STATE.slides[STATE.activeSlideIndex].code_snippet = e.target.value;
      drawSlidePreview();
    }
  });

  document.getElementById("slideScriptInput").addEventListener("input", (e) => {
    if (STATE.slides[STATE.activeSlideIndex]) {
      STATE.slides[STATE.activeSlideIndex].spoken_script = e.target.value;
      updateTeleprompterStats();
      renderFilmstrip();
    }
  });

  // Add Slide button
  document.getElementById("btnAddSlide").addEventListener("click", addSlide);

  // Inspector Action Buttons
  document.getElementById("btnTestSlideSpeech").addEventListener("click", testCurrentSlideSpeech);
  document.getElementById("btnEnhanceScript").addEventListener("click", enhanceCurrentScript);

  // Voice select dropdown
  document.getElementById("voiceSelect").addEventListener("change", (e) => {
    STATE.voiceProfile = e.target.value;
    renderVoiceCards();
  });

  // Theme select dropdown
  document.getElementById("themeSelect").addEventListener("change", (e) => {
    STATE.theme = e.target.value;
    updateQuickThemeDots();
    drawSlidePreview();
  });

  // Subtitles & Ken Burns toggles
  document.getElementById("switchSubtitles").addEventListener("change", (e) => {
    STATE.burnSubtitles = e.target.checked;
  });
  document.getElementById("switchKenBurns").addEventListener("change", (e) => {
    STATE.kenBurns = e.target.checked;
  });

  // Generate from Topic
  document.getElementById("btnGenerateTopic").addEventListener("click", handleTopicGeneration);

  // Hero Omnibox Interactions
  const heroInput = document.getElementById("heroTopicInput");
  const heroSubmit = document.getElementById("btnHeroSubmit");

  if (heroInput && heroSubmit) {
    heroSubmit.addEventListener("click", () => {
      const topic = heroInput.value.trim();
      if (!topic) {
        showToast("Please enter a lecture topic in the omnibox!", "info");
        heroInput.focus();
        return;
      }
      document.getElementById("topicInput").value = topic;
      handleTopicGeneration();
      scrollToSection("studioSection");
    });

    heroInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        heroSubmit.click();
      }
    });
  }

  // Hero File Upload Button (+)
  const btnHeroUpload = document.getElementById("btnHeroUpload");
  const heroFileInput = document.getElementById("heroFileInput");
  if (btnHeroUpload && heroFileInput) {
    btnHeroUpload.addEventListener("click", () => heroFileInput.click());
    heroFileInput.addEventListener("change", (e) => {
      if (e.target.files.length) {
        handleFileUpload(e.target.files[0]);
        scrollToSection("studioSection");
      }
    });
  }

  // Hero Voice Preview Button (mic)
  const btnHeroVoicePreview = document.getElementById("btnHeroVoicePreview");
  if (btnHeroVoicePreview) {
    btnHeroVoicePreview.addEventListener("click", () => {
      playVoicePreview(STATE.voiceProfile);
    });
  }

  // Hero Model Selector Pill
  const btnSelectVoiceModel = document.getElementById("btnSelectVoiceModel");
  if (btnSelectVoiceModel) {
    btnSelectVoiceModel.addEventListener("click", cycleNextVoiceProfile);
  }

  // Document Dropzone & File Input
  setupDropzone();

  // Start Full Render Button
  document.getElementById("btnStartRender").addEventListener("click", startLectureRender);
}

function scrollToSection(id) {
  const el = document.getElementById(id);
  if (el) el.scrollIntoView({ behavior: "smooth" });
}

function cycleNextVoiceProfile() {
  if (!STATE.voices.length) return;
  const currIdx = STATE.voices.findIndex(v => v.id === STATE.voiceProfile);
  const nextIdx = (currIdx + 1) % STATE.voices.length;
  STATE.voiceProfile = STATE.voices[nextIdx].id;

  const select = document.getElementById("voiceSelect");
  if (select) select.value = STATE.voiceProfile;

  const label = document.getElementById("selectedVoiceLabel");
  if (label) label.textContent = STATE.voices[nextIdx].name.split("(")[0].trim() + " Neural";

  renderVoiceCards();
  showToast(`Voice model: ${STATE.voices[nextIdx].name}`, "info");
}

// --- Topic Generation ---
async function handleTopicGeneration() {
  const topic = document.getElementById("topicInput").value.trim();
  if (!topic) {
    showToast("Please enter a lecture topic!", "error");
    return;
  }

  const numSlides = parseInt(document.getElementById("topicNumSlides").value) || 4;
  const audience = document.getElementById("topicAudience").value;
  const apiKey = document.getElementById("topicApiKey").value.trim();
  const provider = document.getElementById("topicProvider").value;

  const btn = document.getElementById("btnGenerateTopic");
  btn.disabled = true;
  btn.textContent = "✨ Generating Curriculum...";

  try {
    const res = await fetch("/api/generate-from-topic", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        topic,
        num_slides: numSlides,
        audience_level: audience,
        llm_provider: provider,
        api_key: apiKey || null
      })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Curriculum generation failed");

    STATE.lectureTitle = data.lecture_title;
    STATE.slides = data.slides;
    STATE.activeSlideIndex = 0;

    document.getElementById("lectureTitleInput").value = STATE.lectureTitle;
    renderFilmstrip();
    updateInspectorForActiveSlide();
    drawSlidePreview();
    switchTab("studio-tab");

    showToast(`Curriculum generated for "${topic}"!`, "success");
  } catch (err) {
    showToast("Generation error: " + err.message, "error");
  } finally {
    btn.disabled = false;
    btn.textContent = "✨ Generate Curriculum & Narration";
  }
}

function setTopicIdea(ideaText) {
  const input = document.getElementById("topicInput");
  input.value = ideaText;
  showToast(`Topic selected: "${ideaText}"`, "info");
}

// --- Dropzone & File Upload ---
function setupDropzone() {
  const dropzone = document.getElementById("fileDropzone");
  const fileInput = document.getElementById("docFileInput");

  dropzone.addEventListener("click", () => fileInput.click());
  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.style.borderColor = "var(--accent-cyan)";
    dropzone.style.background = "rgba(56, 189, 248, 0.08)";
  });
  dropzone.addEventListener("dragleave", () => {
    dropzone.style.borderColor = "rgba(56, 189, 248, 0.35)";
    dropzone.style.background = "rgba(14, 22, 38, 0.4)";
  });
  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.style.borderColor = "rgba(56, 189, 248, 0.35)";
    dropzone.style.background = "rgba(14, 22, 38, 0.4)";
    if (e.dataTransfer.files.length) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  });
  fileInput.addEventListener("change", (e) => {
    if (e.target.files.length) {
      handleFileUpload(e.target.files[0]);
    }
  });
}

async function handleFileUpload(file) {
  const formData = new FormData();
  formData.append("file", file);

  const dropText = document.getElementById("dropzoneText");
  dropText.textContent = `Parsing "${file.name}"...`;

  try {
    const res = await fetch("/api/upload-document", { method: "POST", body: formData });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Upload failed");

    STATE.lectureTitle = data.lecture_title;
    STATE.slides = data.slides;
    STATE.activeSlideIndex = 0;

    document.getElementById("lectureTitleInput").value = STATE.lectureTitle;
    renderFilmstrip();
    updateInspectorForActiveSlide();
    drawSlidePreview();
    switchTab("studio-tab");

    showToast(`Successfully extracted ${STATE.slides.length} slides from "${file.name}"!`, "success");
  } catch (err) {
    showToast("Error parsing file: " + err.message, "error");
  } finally {
    dropText.textContent = "Drop PDF, PowerPoint (.pptx), or Notes (.txt / .md) here";
  }
}

// --- Keyboard Navigation ---
function setupKeyboardNav() {
  document.addEventListener("keydown", (e) => {
    // Only trigger if not actively typing inside an input or textarea
    if (["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement.tagName)) return;

    if (e.key === "ArrowLeft") {
      navigateSlide(-1);
    } else if (e.key === "ArrowRight") {
      navigateSlide(1);
    }
  });
}

// --- Production Video Render Pipeline ---
async function startLectureRender() {
  const btn = document.getElementById("btnStartRender");
  btn.disabled = true;
  btn.textContent = "⚙️ Dispatching Video Pipeline...";

  switchTab("render-tab");
  updatePipelineStepper(1);

  const payload = {
    lecture_title: STATE.lectureTitle,
    voice_profile: STATE.voiceProfile,
    theme: STATE.theme,
    burn_subtitles: STATE.burnSubtitles,
    ken_burns_effect: STATE.kenBurns,
    slides: STATE.slides
  };

  try {
    const res = await fetch("/api/lectures/create", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to start render");

    STATE.activeJobId = data.job_id;
    addLog(`Pipeline task initialized. Job ID: ${data.job_id}`);
    showToast("Render job dispatched to FFmpeg compositor!", "info");
    startPollingJob(data.job_id);
  } catch (err) {
    showToast("Render Error: " + err.message, "error");
    btn.disabled = false;
    btn.textContent = "🎬 Render Full Video Lecture";
  }
}

function startPollingJob(jobId) {
  if (STATE.pollInterval) clearInterval(STATE.pollInterval);

  const progressBar = document.getElementById("progressBarFill");
  const progressText = document.getElementById("progressPercentage");
  const currentStep = document.getElementById("currentStepText");

  STATE.pollInterval = setInterval(async () => {
    try {
      const res = await fetch(`/api/lectures/${jobId}/status`);
      const status = await res.json();

      progressBar.style.width = `${status.progress}%`;
      progressText.textContent = `${status.progress}%`;
      currentStep.textContent = status.current_step;

      // Update Stepper Nodes dynamically based on progress
      if (status.progress < 25) {
        updatePipelineStepper(1);
      } else if (status.progress < 50) {
        updatePipelineStepper(2);
      } else if (status.progress < 75) {
        updatePipelineStepper(3);
      } else if (status.progress < 100) {
        updatePipelineStepper(4);
      }

      addLog(`[${status.status.toUpperCase()}] ${status.current_step}`);

      if (status.status === "completed") {
        clearInterval(STATE.pollInterval);
        updatePipelineStepper(5);

        document.getElementById("btnStartRender").disabled = false;
        document.getElementById("btnStartRender").textContent = "🎬 Render Full Video Lecture";

        showVideoDeliverables(status);
        loadRecentLectures();
        triggerConfetti();
        showToast("Video Lecture rendered successfully!", "success");
      } else if (status.status === "failed") {
        clearInterval(STATE.pollInterval);
        document.getElementById("btnStartRender").disabled = false;
        document.getElementById("btnStartRender").textContent = "🎬 Render Full Video Lecture";
        showToast("Lecture render failed: " + status.error_message, "error");
      }
    } catch (e) {
      console.error("Polling error:", e);
    }
  }, 1200);
}

function updatePipelineStepper(activeStep) {
  for (let i = 1; i <= 5; i++) {
    const node = document.getElementById(`stepNode${i}`);
    if (!node) continue;
    if (i < activeStep) {
      node.className = "step-node completed";
      node.querySelector(".step-icon").textContent = "✓";
    } else if (i === activeStep) {
      node.className = "step-node active";
      node.querySelector(".step-icon").textContent = `${i}`;
    } else {
      node.className = "step-node";
      node.querySelector(".step-icon").textContent = `${i}`;
    }
  }
}

function addLog(msg) {
  const logBox = document.getElementById("statusLogBox");
  if (!logBox) return;
  const time = new Date().toLocaleTimeString();
  logBox.innerHTML += `<div>[${time}] ${escapeHtml(msg)}</div>`;
  logBox.scrollTop = logBox.scrollHeight;
}

function clearStatusLog() {
  const logBox = document.getElementById("statusLogBox");
  if (logBox) logBox.innerHTML = "<div>[LOG CLEARED] Ready.</div>";
}

function showVideoDeliverables(status) {
  const container = document.getElementById("videoResultContainer");
  container.style.display = "block";

  const video = document.getElementById("finalVideoPlayer");
  video.src = status.video_url;

  const existingTrack = video.querySelector("track");
  if (existingTrack) existingTrack.remove();

  if (status.vtt_url) {
    const track = document.createElement("track");
    track.kind = "subtitles";
    track.label = "English";
    track.srclang = "en";
    track.src = status.vtt_url;
    track.default = true;
    video.appendChild(track);
  }

  video.load();

  document.getElementById("btnDownloadVideo").href = status.video_url;
  document.getElementById("btnDownloadSrt").href = status.srt_url;
  document.getElementById("btnDownloadVtt").href = status.vtt_url;

  // Scroll smoothly to video deliverable
  container.scrollIntoView({ behavior: "smooth" });
}

function copyVideoShareLink() {
  const video = document.getElementById("finalVideoPlayer");
  if (!video || !video.src) return;
  navigator.clipboard.writeText(video.src).then(() => {
    showToast("Direct video link copied to clipboard!", "success");
  });
}

async function loadRecentLectures() {
  try {
    const res = await fetch("/api/lectures/recent");
    const list = await res.json();
    const container = document.getElementById("recentLecturesList");
    if (!container) return;

    if (list.length === 0) {
      container.innerHTML = "<p style='color: var(--text-muted); font-size: 0.85rem;'>No recent lectures rendered yet.</p>";
      return;
    }

    container.innerHTML = "";
    list.forEach(item => {
      const el = document.createElement("div");
      el.style.cssText = "display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 1rem; border-bottom: 1px solid var(--border-subtle); font-size: 0.85rem; background: var(--bg-surface); margin-bottom: 0.5rem; border-radius: var(--radius-xs);";
      el.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.75rem;">
          <span style="font-size: 1.2rem;">🎬</span>
          <div>
            <span style="color: var(--accent-cyan); font-weight: 700;">${item.job_id.substring(0, 8)}...</span>
            <span style="color: var(--text-muted); margin-left: 0.5rem; font-size: 0.78rem;">${item.modified} (${item.size_mb} MB)</span>
          </div>
        </div>
        <div style="display: flex; gap: 0.5rem;">
          <a href="${item.video_url}" target="_blank" class="btn btn-secondary btn-sm" download>⬇️ Download MP4</a>
        </div>
      `;
      container.appendChild(el);
    });
  } catch (e) {
    console.error("Failed to load recent lectures:", e);
  }
}

// --- Modals Controller ---
function setupModals() {
  const btnDeploy = document.getElementById("btnOpenDeployModal");
  if (btnDeploy) btnDeploy.addEventListener("click", () => openModal("deployModal"));

  const btnTech = document.getElementById("btnOpenTechModal");
  if (btnTech) btnTech.addEventListener("click", () => openModal("techModal"));
}

function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.classList.add("open");
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.classList.remove("open");
}

// Close modal on backdrop click
document.addEventListener("click", (e) => {
  if (e.target.classList.contains("modal-backdrop")) {
    e.target.classList.remove("open");
  }
});

// --- Toast Notifications ---
function showToast(message, type = "info") {
  const container = document.getElementById("toastContainer");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = "toast";

  const icons = {
    info: "💡",
    success: "✅",
    error: "⚠️"
  };

  toast.innerHTML = `<span>${icons[type] || "ℹ️"}</span><span>${escapeHtml(message)}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(10px)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// --- Confetti Particle System ---
function triggerConfetti() {
  const canvas = document.getElementById("confettiCanvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;

  const count = 120;
  const particles = [];
  const colors = ["#38bdf8", "#6366f1", "#a855f7", "#10b981", "#f59e0b", "#f43f5e"];

  for (let i = 0; i < count; i++) {
    particles.push({
      x: window.innerWidth / 2,
      y: window.innerHeight / 2,
      vx: (Math.random() - 0.5) * 18,
      vy: (Math.random() - 0.5) * 18 - 4,
      size: Math.random() * 8 + 4,
      color: colors[Math.floor(Math.random() * colors.length)],
      alpha: 1,
      decay: Math.random() * 0.015 + 0.008
    });
  }

  function frame() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    let active = 0;

    particles.forEach(p => {
      p.x += p.vx;
      p.y += p.vy;
      p.vy += 0.35; // gravity
      p.alpha -= p.decay;

      if (p.alpha > 0) {
        active++;
        ctx.fillStyle = p.color;
        ctx.globalAlpha = p.alpha;
        ctx.fillRect(p.x, p.y, p.size, p.size);
      }
    });

    if (active > 0) {
      requestAnimationFrame(frame);
    } else {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
  }

  requestAnimationFrame(frame);
}

function escapeHtml(str) {
  if (!str) return "";
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
