const chat    = document.getElementById('chat');
const form    = document.getElementById('form');
const input   = document.getElementById('prompt');
let thread_id = null;

// Auto‑resize textarea
input.addEventListener('input', () => {
  input.style.height = 'auto';
  input.style.height = input.scrollHeight + 'px';
});

// Add a chat bubble
function addBubble(text, cls) {
  const div      = document.createElement('div');
  div.className  = `bubble ${cls}`;
  div.innerHTML  = marked.parse(text);
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
  return div;
}

form.addEventListener('submit', async e => {
  e.preventDefault();
  const msg = input.value.trim();
  if (!msg) return;

  // User bubble
  addBubble(msg, 'user');

  // Thinking bubble placeholder
  const thinking = addBubble('Thinking...', 'bot thinking');

  input.value = '';
  input.style.height = 'auto';
  input.disabled = true;

  try {
    const res = await fetch('https://lawbot-api.onrender.com/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg, thread_id })
    });
    const data = await res.json();
    thread_id = data.thread_id;

    // Replace "Thinking..." with real answer
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

// Initial focus
window.onload = () => input.focus();
