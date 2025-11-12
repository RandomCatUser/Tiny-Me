# Modules
import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView

# Template
HTML = r"""
<!doctype html>
<html lang='en'>
<head>
<meta charset='utf-8'>
<meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Tiny-AI with Memory</title>
<style>
  :root {
    --bg: #0d1117;
    --panel: #161b22;
    --accent: #7c3aed;
    --text: #e6edf3;
    --muted: #8b949e;
    --border: #21262d;
  }
  * { box-sizing: border-box; font-family: Inter, system-ui, sans-serif; }
  body, html { margin: 0; padding: 0; height: 100%; background: var(--bg); color: var(--text); }
  .app { display: flex; height: 100%; overflow: hidden; }

  /* Sidebar */
  .sidebar { width: 280px; background: var(--panel); padding: 16px; display: flex; flex-direction: column; justify-content: space-between; transition: all .3s ease; }
  .sidebar.hidden { width: 0; padding: 0; overflow: hidden; }
  .top-side { display: flex; flex-direction: column; gap: 16px; }
  .bottom-side { display: flex; flex-direction: column; align-items: center; gap: 10px; }
  .brand { font-size: 20px; font-weight: 600; color: var(--accent); text-align: center; margin-bottom: 10px; }
  .btn { background: #21262d; border: none; border-radius: 6px; padding: 8px 10px; color: var(--muted); cursor: pointer; transition: .2s; text-align: left; }
  .btn:hover { background: #30363d; color: var(--text); }
  .btn.primary { background: var(--accent); color: white; }
  .conv-item { background: #1c2128; padding: 8px; border-radius: 6px; margin-bottom: 6px; cursor: pointer; transition: .2s; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
  .conv-item:hover { background: #262b33; }
  .icon-btn { font-size: 22px; color: var(--muted); cursor: pointer; transition: .2s; }
  .icon-btn:hover { color: var(--accent); }

  /* Main */
  .main { flex: 1; display: flex; flex-direction: column; }
  .topbar { display: flex; align-items: center; justify-content: space-between; background: var(--panel); padding: 10px 16px; border-bottom: 1px solid var(--border); }
  .toggle { font-size: 22px; cursor: pointer; color: var(--muted); }
  .prompt-box { display: flex; align-items: center; gap: 10px; }
  .prompt-input { flex: 1; background: #0d1117; color: var(--text); border: 1px solid var(--border); border-radius: 8px; padding: 8px; }
  .messages { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 12px; scroll-behavior: smooth; }
  .msg { max-width: 75%; padding: 12px 16px; border-radius: 12px; line-height: 1.4; white-space: pre-wrap; word-wrap: break-word; animation: fadeIn .3s ease; }
  .msg.user { align-self: flex-end; background: #238636; color: white; }
  .msg.assistant { align-self: flex-start; background: #1c2128; color: var(--text); }
  @keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
  .composer { display: flex; gap: 10px; padding: 16px; background: var(--panel); border-top: 1px solid var(--border); }
  .input { flex: 1; background: #0d1117; color: var(--text); border: 1px solid var(--border); padding: 10px; border-radius: 8px; }

  /* Popup */
  .popup-bg { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,.6); display: flex; align-items: center; justify-content: center; z-index: 100; }
  .popup { background: var(--panel); padding: 20px; border-radius: 10px; width: 400px; max-height: 80vh; overflow-y: auto; }
  .popup h2 { margin-top: 0; text-align: center; color: var(--accent); }
  .popup button { width: 100%; margin-top: 10px; }
</style>
</head>
<body>
<div class='app'>
  <div class='sidebar hidden' id='sidebar'>
    <div class='top-side'>
      <div class='brand'>Tiny-AI</div>
      <button class='btn primary' id='newBtn'>[N] New Chat</button>
      <button class='btn' id='historyBtn'>[H] Chat History</button>
      <button class='btn' id='clearBtn'>[D] Clear All Memory</button>
      <div id='convs'></div>
    </div>
    <div class='bottom-side'>
      <span class='icon-btn' id='settingsBtn'>⚙️</span>
    </div>
  </div>

  <div class='main'>
    <div class='topbar'>
      <span class='toggle' id='toggleBtn'>☰</span>
      <div class='prompt-box'>
        <input id='promptInput' class='prompt-input' placeholder='Enter system prompt...'>
      </div>
    </div>
    <div class='messages' id='messages'></div>
    <div class='composer'>
      <input id='input' class='input' placeholder='Type a message...'>
      <button class='btn primary' id='sendBtn'>Send</button>
    </div>
  </div>
</div>

<!-- Popup -->
<div id='popupContainer' style='display:none'></div>

<script>
const el = id => document.getElementById(id);
const sidebar = el('sidebar');
const messages = el('messages');
const input = el('input');
const promptInput = el('promptInput');
const popupContainer = el('popupContainer');

// Load memory
let memory = JSON.parse(localStorage.getItem('purr_memory') || '[]');
let history = JSON.parse(localStorage.getItem('purr_history') || '[]');
let prompt = localStorage.getItem('purr_prompt') || '';
let personalMemory = localStorage.getItem('purr_personal') || '';
promptInput.value = prompt;

// --- Render messages ---
function render() {
  messages.innerHTML = '';
  memory.forEach(m => {
    const d = document.createElement('div');
    d.className = 'msg ' + m.role;
    d.textContent = m.content;
    messages.appendChild(d);
  });
  messages.scrollTop = messages.scrollHeight;
  localStorage.setItem('purr_memory', JSON.stringify(memory));
}

// --- Typewriter effect ---
function typeEffect(el, text, i = 0) {
  if (i < text.length) {
    el.textContent += text.charAt(i);
    setTimeout(() => typeEffect(el, text, i + 1), 20);
  }
}

// --- Send message ---
async function send() {
  const text = input.value.trim();
  if (!text) return;
  memory.push({ role: 'user', content: text });
  render();
  input.value = '';

  const a = { role: 'assistant', content: '' };
  memory.push(a);
  render();
  const elMsg = messages.lastElementChild;

  try {
    const context = memory.slice(-10).map(m => `${m.role}: ${m.content}`).join('\\n');
    const fullPrompt = prompt + "\\nPersonal Memory: " + personalMemory + "\\n" + context + "\\nUser: " + text;
    const resp = await fetch('https://text.pollinations.ai/' + encodeURIComponent(fullPrompt));
    const txt = await resp.text();
    typeEffect(elMsg, txt);
    a.content = txt;
    localStorage.setItem('purr_memory', JSON.stringify(memory));
  } catch (e) {
    a.content = '⚠️ Error: ' + e.message;
  }
  render();
}

// --- Popup system ---
function showPopup(title, contentHTML) {
  popupContainer.innerHTML = `
    <div class='popup-bg' onclick='hidePopup(event)'>
      <div class='popup' onclick='event.stopPropagation()'>
        <h2>${title}</h2>
        ${contentHTML}
      </div>
    </div>`;
  popupContainer.style.display = 'flex';
}
function hidePopup(e) {
  if (e) e.stopPropagation();
  popupContainer.style.display = 'none';
}

// --- Buttons ---
el('sendBtn').onclick = send;
input.addEventListener('keydown', e => { if (e.key === 'Enter') send(); });
el('toggleBtn').onclick = () => sidebar.classList.toggle('hidden');
el('clearBtn').onclick = () => { memory = []; localStorage.removeItem('purr_memory'); render(); };
el('newBtn').onclick = () => { 
  if (memory.length) history.push(memory);
  localStorage.setItem('purr_history', JSON.stringify(history));
  memory = []; render();
};
promptInput.addEventListener('change', e => {
  prompt = e.target.value;
  localStorage.setItem('purr_prompt', prompt);
});

// --- History ---
el('historyBtn').onclick = () => {
  let html = '';
  if (history.length === 0) html = '<p>No chat history saved.</p>';
  else {
    html = history.map((conv, i) => `
      <button class='btn' onclick='loadHistory(${i})'>Chat ${i + 1} (${conv.length} msgs)</button>
    `).join('');
  }
  showPopup('Chat History', html + "<button class='btn primary' onclick='clearHistory()'>Clear All</button>");
};

function loadHistory(i) {
  memory = history[i];
  render();
  hidePopup();
}

function clearHistory() {
  history = [];
  localStorage.removeItem('purr_history');
  hidePopup();
}

// --- Settings ---
el('settingsBtn').onclick = () => {
  const html = `
    <label>Personal Memory</label>
    <textarea id='personalMem' style='width:100%;height:100px;background:#0d1117;color:white;border:1px solid var(--border);border-radius:8px;padding:8px;'>${personalMemory}</textarea>
    <button class='btn primary' onclick='savePersonal()'>Save</button>
  `;
  showPopup('Settings', html);
};

function savePersonal() {
  const val = document.getElementById('personalMem').value;
  personalMemory = val;
  localStorage.setItem('purr_personal', val);
  hidePopup();
}

render();
</script>
</body>
</html>
"""

# Main function
def main():
    app = QApplication(sys.argv)
    win = QMainWindow()
    win.setWindowTitle('Tiny AI')
    view = QWebEngineView()
    view.setHtml(HTML, QUrl('http://localhost/'))
    win.setCentralWidget(view)
    win.resize(950, 720)
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
