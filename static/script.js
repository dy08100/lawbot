// Grab DOM elements
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

// ── On load: show welcome & handle initial URL query ────────────
window.addEventListener('load', () => {
  // Welcome
  addBubble(
    "Hello! 👋 I'm LawBot, your AI Criminal & Immigration Advisor. How can I help you today?",
    'bot'
  );
  input.focus();

  // Check for initial prompt in URL
  const params  = new URLSearchParams(window.location.search);
  const initial = params.get('initial');
  if (initial) {
    // Insert into textarea & resize
    input.value = initial;
    input.style.height = 'auto';
    input.style.height = input.scrollHeight + 'px';

    // Delay so the UI updates, then submit
    setTimeout(() => form.dispatchEvent(new Event('submit')), 300);
  }
});

// ── Handle form submission ───────────────────────────────────────
form.addEventListener('submit', async e => {
  e.preventDefault();
  const msg = input.value.trim();
  if (!msg) return;

  // Show user bubble
  addBubble(msg, 'user');
  // Show thinking placeholder
  const thinking = addBubble('Thinking...', 'bot thinking');

  // Reset input
  input.value = '';
  input.style.height = 'auto';
  input.disabled = true;
  closeSidebar();

  try {
    // Call your backend
    const res = await fetch('https://lawbot-api.onrender.com/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg, thread_id })
    });
    const data = await res.json();
    thread_id = data.thread_id;

    // Replace thinking with real answer
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