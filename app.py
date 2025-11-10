#Modules
import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView

#Template
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
  .sidebar { width: 280px; background: var(--panel); padding: 16px; display: flex; flex-direction: column; gap: 16px; transition: all .3s ease; }
  .sidebar.hidden { width: 0; padding: 0; overflow: hidden; }
  .brand { font-size: 20px; font-weight: 600; color: var(--accent); text-align: center; margin-bottom: 10px; }
  .btn { background: #21262d; border: none; border-radius: 6px; padding: 8px 10px; color: var(--muted); cursor: pointer; transition: .2s; text-align: left; }
  .btn:hover { background: #30363d; color: var(--text); }
  .btn.primary { background: var(--accent); color: white; }
  .conv-item { background: #1c2128; padding: 8px; border-radius: 6px; margin-bottom: 6px; cursor: pointer; transition: .2s; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
  .conv-item:hover { background: #262b33; }

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
</style>
</head>
<body>
<div class='app'>
  <div class='sidebar hidden' id='sidebar'>
    <div class='brand'>Tiny-AI</div>
    <button class='btn primary' id='newBtn'>[N] New Chat</button>
    <button class='btn' id='clearBtn'>[D] Clear All Memory</button>
    <div id='convs'></div>
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
<script>
const el = id => document.getElementById(id);
const sidebar = el('sidebar');
const messages = el('messages');
const input = el('input');
const promptInput = el('promptInput');

// Load memory from localStorage
let memory = JSON.parse(localStorage.getItem('purr_memory') || '[]');
let prompt = localStorage.getItem('purr_prompt') || '';
promptInput.value = prompt;

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

function typeEffect(el, text, i = 0) {
  if (i < text.length) {
    el.textContent += text.charAt(i);
    setTimeout(() => typeEffect(el, text, i + 1), 20);
  }
}

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
    // Include memory context (last 10 messages)
    const context = memory.slice(-10).map(m => `${m.role}: ${m.content}`).join('\n');
    const resp = await fetch('https://text.pollinations.ai/' + encodeURIComponent(prompt + '\n' + context + '\nUser: ' + text));
    const txt = await resp.text();
    typeEffect(elMsg, txt);
    a.content = txt;
    localStorage.setItem('purr_memory', JSON.stringify(memory));
  } catch (e) {
    a.content = '⚠️ Error: ' + e.message;
  }
}

document.getElementById('sendBtn').onclick = send;
input.addEventListener('keydown', e => { if (e.key === 'Enter') send(); });

document.getElementById('toggleBtn').onclick = () => sidebar.classList.toggle('hidden');
document.getElementById('clearBtn').onclick = () => { memory = []; localStorage.removeItem('purr_memory'); render(); };
document.getElementById('newBtn').onclick = () => { memory = []; render(); };

promptInput.addEventListener('change', e => {
  prompt = e.target.value;
  localStorage.setItem('purr_prompt', prompt);
});

render();
</script>
</body>
</html>
"""

#main fuctiom
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