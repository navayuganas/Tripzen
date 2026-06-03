const sidebar       = document.getElementById('sidebar');
const toggleBtn     = document.getElementById('toggleBtn');
const newChatBtn    = document.getElementById('newChatBtn');
const searchInput   = document.getElementById('searchInput');
const searchResults = document.getElementById('searchResults');
const searchList    = document.getElementById('searchList');
const defaultContent= document.getElementById('defaultContent');
const chatbox       = document.getElementById('chatbox');
const msgInput      = document.getElementById('msgInput');
const sendBtn       = document.getElementById('sendBtn');


let currentUserId   = localStorage.getItem('user_id');    // logged in user
let currentSessionId= localStorage.getItem('session_id'); // current chat session

window.addEventListener('load', async () => {
    if (!currentUserId) {
        // no user logged in — show default message
        addMessageToUI('bot', 'Hello! Please register or login to start chatting.');
        return;
    }

    // update profile in sidebar
    updateProfile();

    // load previous sessions in sidebar
    await loadSessions();

    // if existing session — load its messages
    if (currentSessionId) {
        await loadMessages(currentSessionId);
    } else {
        addMessageToUI('bot', 'Hello! How can I help you today?');
    }
});

async function loadSessions() {
    const sessions = await getSessions(currentUserId);
    const recentList = document.getElementById('recentList');
    recentList.innerHTML = '';

    sessions.forEach(session => {
        const item = document.createElement('div');
        item.className = 'chat-item';
        item.innerHTML = `<i class="ti ti-message"></i><span>${session.title}</span>`;

        item.addEventListener('click', async () => {
            // switch to this session
            currentSessionId = session.id;
            localStorage.setItem('session_id', session.id);
            chatbox.innerHTML = '';
            await loadMessages(session.id);

            document.querySelectorAll('.chat-item')
                    .forEach(i => i.classList.remove('active'));
            item.classList.add('active');
        });

        recentList.appendChild(item);
    });
}

async function loadMessages(session_id) {
    const messages = await getMessages(session_id);
    chatbox.innerHTML = '';

    messages.forEach(msg => {
        addMessageToUI(msg.sender, msg.message);
    });

    chatbox.scrollTop = chatbox.scrollHeight;
}

function addMessageToUI(sender, text) {
    const div = document.createElement('div');
    div.className = `message ${sender === 'user' ? 'user' : ''}`;
    div.textContent = text;
    chatbox.appendChild(div);
    chatbox.scrollTop = chatbox.scrollHeight;
}

async function handleSendMessage() {
    const text = msgInput.value.trim();
    if (!text) return;

    // clear input
    msgInput.value = '';
    msgInput.style.height = 'auto';

    // show user message in UI
    addMessageToUI('user', text);

    // if no user logged in
    if (!currentUserId) {
        addMessageToUI('bot', 'Please login first to chat.');
        return;
    }

    // if no session — create one
    if (!currentSessionId) {
        const session = await createSession(currentUserId, text.slice(0, 50));
        currentSessionId = session.session_id;
        localStorage.setItem('session_id', currentSessionId);
        await loadSessions();
    }

    // save user message to backend
    await sendMessage(currentSessionId, 'user', text);

    // show typing indicator
    const typing = document.createElement('div');
    typing.className = 'message';
    typing.textContent = 'Bot is typing...';
    typing.id = 'typing';
    chatbox.appendChild(typing);
    chatbox.scrollTop = chatbox.scrollHeight;

    // TODO: replace this with real AI response later
    setTimeout(async () => {
        const botReply = 'Hello';

        // remove typing indicator
        document.getElementById('typing')?.remove();

        // show bot reply in UI
        addMessageToUI('bot', botReply);

        // save bot reply to backend
        await sendMessage(currentSessionId, 'bot', botReply);
    }, 1000);
}

newChatBtn.addEventListener('click', async () => {
    currentSessionId = null;
    localStorage.removeItem('session_id');
    chatbox.innerHTML = '';
    addMessageToUI('bot', 'New chat started! How can I help you?');
    msgInput.focus();
});

sendBtn.addEventListener('click', handleSendMessage);

msgInput.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSendMessage();
    }
});

msgInput.addEventListener('input', () => {
    msgInput.style.height = 'auto';
    msgInput.style.height = Math.min(msgInput.scrollHeight, 120) + 'px';
});

toggleBtn.addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');
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

    const allItems = document.querySelectorAll('#recentList .chat-item span');
    const matches  = [...allItems].filter(s => s.textContent.toLowerCase().includes(q));

    searchList.innerHTML = matches.length
        ? matches.map(s => `<div class="chat-item"><i class="ti ti-message"></i><span>${s.textContent}</span></div>`).join('')
        : '<div class="no-results">No chats found</div>';
});

document.querySelectorAll('.sidebar-section').forEach(section => {
    section.querySelector('.collapsible').addEventListener('click', () => {
        section.classList.toggle('closed');
    });
});

function updateProfile() {
    const name  = localStorage.getItem('full_name') || 'Your Name';
    const email = localStorage.getItem('email') || 'you@example.com';

    document.querySelector('.profile-name').textContent  = name;
    document.querySelector('.profile-email').textContent = email;
}