const chat      = document.getElementById('chat');
const form      = document.getElementById('form');
const input     = document.getElementById('prompt');
const sidebar   = document.getElementById('sidebar');
const overlay   = document.getElementById('overlay');
const hamburger = document.getElementById('hamburger');
let thread_id   = null;

// ── Sidebar toggle ───────────────────────────────────────────────
function openSidebar() {
  sidebar.classList.add('open');
  overlay.classList.add('show');
}
function closeSidebar() {
  sidebar.classList.remove('open');
  overlay.classList.remove('show');
}
hamburger.addEventListener('click', openSidebar);
overlay.addEventListener('click', closeSidebar);

// ── Auto‑resize textarea ─────────────────────────────────────────
input.addEventListener('input', () => {
  input.style.height = 'auto';
  input.style.height = input.scrollHeight + 'px';
});

// ── Add a chat bubble ────────────────────────────────────────────
function addBubble(text, cls) {
  const div      = document.createElement('div');
  div.className  = `bubble ${cls}`;
  div.innerHTML  = marked.parse(text);
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
  return div;
}

// ── Welcome message on load ─────────────────────────────────────
window.addEventListener('load', () => {
  addBubble("Hello! 👋 I'm LawBot, your AI Criminal & Immigration Advisor. How can I help you today?", 'bot');
  input.focus();
});

// ── Form submit ─────────────────────────────────────────────────
form.addEventListener('submit', async e => {
  e.preventDefault();
  const msg = input.value.trim();
  if (!msg) return;

  addBubble(msg, 'user');          // user bubble
  const thinking = addBubble('Thinking...', 'bot thinking');
  input.value = '';
  input.style.height = 'auto';
  input.disabled = true;
  closeSidebar();                  // close nav if open

  try {
    const res = await fetch('https://lawbot-api.onrender.com/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg, thread_id })
    });
    const data = await res.json();
    thread_id = data.thread_id;

    // replace thinking with real answer
    thinking.classList.remove('thinking');
    thinking.innerHTML = marked.parse(data.answer);
  } catch (err) {
    thinking.classList.remove('thinking');
    thinking.innerHTML = '⚠️ Error connecting. Please try again.';
    console.error(err);
  } finally {
    input.disabled = false;
    input.focus();
  }
});