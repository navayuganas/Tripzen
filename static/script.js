const sidebar = document.getElementById('sidebar');
const toggleBtn = document.getElementById('toggleBtn');
const newChatBtn = document.getElementById('newChatBtn');
const searchInput = document.getElementById('searchInput');
const searchResults = document.getElementById('searchResults');
const searchList = document.getElementById('searchList');
const defaultContent = document.getElementById('defaultContent');
const chatbox = document.getElementById('chatbox');
const msgInput = document.getElementById('msgInput');
const sendBtn = document.getElementById('sendBtn');

const allChats = [
  'Hello! How can I help?', 'Recipe suggestions', 'Python help',
  'Plan my week', 'Email drafting', 'Paris 5-day trip',
  'Tokyo weekend plan', 'NYC food tour'
];

toggleBtn.addEventListener('click', () => {
  sidebar.classList.toggle('collapsed');
});

newChatBtn.addEventListener('click', () => {
  chatbox.innerHTML = '';
  const msg = document.createElement('div');
  msg.className = 'message';
  msg.textContent = 'New chat started! How can I help you?';
  chatbox.appendChild(msg);
  msgInput.focus();
});

searchInput.addEventListener('input', () => {
  const q = searchInput.value.trim().toLowerCase();
  if (!q) {
    searchResults.classList.remove('visible');
    defaultContent.style.display = '';
    return;
  }
  defaultContent.style.display = 'none';
  searchResults.classList.add('visible');
  const matches = allChats.filter(c => c.toLowerCase().includes(q));
  searchList.innerHTML = matches.length
    ? matches.map(c => `<div class="chat-item"><i class="ti ti-message"></i><span>${c}</span></div>`).join('')
    : '<div class="no-results">No chats found</div>';
});

document.querySelectorAll('.chat-item, .itinerary-item').forEach(item => {
  item.addEventListener('click', function () {
    document.querySelectorAll('.chat-item').forEach(i => i.classList.remove('active'));
    this.classList.add('active');
  });
});

function sendMessage() {
  const text = msgInput.value.trim();
  if (!text) return;

  const userMsg = document.createElement('div');
  userMsg.className = 'message user';
  userMsg.textContent = text;
  chatbox.appendChild(userMsg);

  msgInput.value = '';
  msgInput.style.height = 'auto';
  chatbox.scrollTop = chatbox.scrollHeight;
}

sendBtn.addEventListener('click', sendMessage);

msgInput.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

msgInput.addEventListener('input', () => {
  msgInput.style.height = 'auto';
  msgInput.style.height = Math.min(msgInput.scrollHeight, 120) + 'px';
});

const sections = document.querySelectorAll(".sidebar-section");
sections.forEach(section => {
    const header = section.querySelector(".collapsible");

    header.addEventListener("click", () => {
        section.classList.toggle("closed");
    });
});