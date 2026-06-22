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

// ─────────────────────────────────────────
// State
// ─────────────────────────────────────────
let currentUserId    = localStorage.getItem('user_id');
let currentSessionId = localStorage.getItem('session_id');

// ─────────────────────────────────────────
// On page load
// ─────────────────────────────────────────
window.addEventListener('load', async () => {
    if (!currentUserId) {
        addMessageToUI('bot', 'Hello! Please register or login to start chatting.');
        return;
    }

    updateProfile();
    await loadSessions();

    if (currentSessionId) {
        await loadMessages(currentSessionId);
    } else {
        addMessageToUI('bot', 'Hello! How can I help you today?');
    }
});

async function loadSessions() {
    try {
        const sessions = await getSessions(currentUserId);
        const recentList = document.getElementById('recentList');
        recentList.innerHTML = '';

        sessions.forEach(session => {
            const item = document.createElement('div');
            item.className = 'chat-item';
            item.innerHTML = `<i class="ti ti-message"></i><span>${session.title}</span>`;

            item.addEventListener('click', async () => {
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
    } catch (error) {
        console.error('Error loading sessions:', error);
    }
}

// ─────────────────────────────────────────
// Load messages for a session
// ─────────────────────────────────────────
async function loadMessages(session_id) {
    try {
        const messages = await getMessages(session_id);
        chatbox.innerHTML = '';

        messages.forEach(msg => {
            addMessageToUI(msg.sender, msg.message);
        });

        chatbox.scrollTop = chatbox.scrollHeight;
    } catch (error) {
        console.error('Error loading messages:', error);
    }
}
  
function formatItinerary(text) {
    text = text.replace(/(ITINERARY:|DESTINATION:|DURATION:|BUDGET:|TRAVELERS:|TRIP_TYPE:|SUMMARY:|DAY \d+[^:]*:|HOTEL:|TRANSPORT:|COST:|DESCRIPTION:|ACTIVITIES:)/g,
        '<br><strong>$1</strong>');
    text = text.replace(/ - /g, '<br>• ');
    return `<div class="itinerary-response">${text}</div>`;
}

// ─────────────────────────────────────────
// Add message bubble to UI
// ─────────────────────────────────────────
function addMessageToUI(sender, text) {
    // guard against null/undefined messages
    if (!text) return;
    text = String(text);

    const div = document.createElement('div');
    div.className = `message ${sender === 'user' ? 'user' : ''}`;

    if (sender === 'bot' && text.includes('PDF_URL:')) {
        // handle PDF_URL: format
        const parts  = text.split('PDF_URL:');
        const before = parts[0].trim();
        const pdfUrl = parts[1].trim();

        if (before) {
            div.textContent = before;
            chatbox.appendChild(div);
        }

        const pdfBtn       = document.createElement('a');
        pdfBtn.href        = pdfUrl;
        pdfBtn.target      = '_blank';
        pdfBtn.textContent = '📄 Download Itinerary PDF';
        pdfBtn.className   = 'pdf-btn';
        chatbox.appendChild(pdfBtn);

    } else if (sender === 'bot' && text.includes('](http')) {
        // handle markdown link format: [text](url)
        const parts = text.split(/(\[.*?\]\(.*?\))/g);
        parts.forEach(part => {
            const linkMatch = part.match(/\[(.*?)\]\((.*?)\)/);
            if (linkMatch) {
                const a       = document.createElement('a');
                a.href        = linkMatch[2];
                a.target      = '_blank';
                a.textContent = linkMatch[1];
                a.className   = 'pdf-btn';
                chatbox.appendChild(a);
            } else if (part.trim()) {
                const span       = document.createElement('span');
                span.textContent = part;
                span.className   = `message ${sender === 'user' ? 'user' : ''}`;
                chatbox.appendChild(span);
            }
        });

   } else {
    if (sender === 'bot') {
        div.innerHTML = formatItinerary(text);
    } else {
        div.textContent = text;
    }
    chatbox.appendChild(div);
}

    chatbox.scrollTop = chatbox.scrollHeight;
}
// ─────────────────────────────────────────
// Send message
// ─────────────────────────────────────────
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
        try {
            const session = await createSession(currentUserId, text.slice(0, 50));
            currentSessionId = session.session_id;
            localStorage.setItem('session_id', currentSessionId);
            await loadSessions();
        } catch (error) {
            console.error('Error creating session:', error);
            addMessageToUI('bot', 'Failed to create session. Please try again.');
            return;
        }
    }

    // show typing indicator
    const typing = document.createElement('div');
    typing.className = 'message';
    typing.textContent = 'Bot is typing...';
    typing.id = 'typing';
    chatbox.appendChild(typing);
    chatbox.scrollTop = chatbox.scrollHeight;

    try {
        const data = await sendMessage(currentSessionId, 'user', text);

        // remove typing indicator
        document.getElementById('typing')?.remove();

        // show Gemini reply in UI
        if (data.bot_reply) {
            addMessageToUI('bot', data.bot_reply);
        } else {
            addMessageToUI('bot', 'Something went wrong. Please try again.');
        }

    } catch (error) {
        document.getElementById('typing')?.remove();
        addMessageToUI('bot', 'Something went wrong. Please try again.');
        console.error('Error sending message:', error);
    }
}

// ─────────────────────────────────────────
// New chat button
// ─────────────────────────────────────────
newChatBtn.addEventListener('click', async () => {
    currentSessionId = null;
    localStorage.removeItem('session_id');
    chatbox.innerHTML = '';
    addMessageToUI('bot', 'New chat started! How can I help you?');
    msgInput.focus();
});

// ─────────────────────────────────────────
// Send button and Enter key
// ─────────────────────────────────────────
sendBtn.addEventListener('click', handleSendMessage);

msgInput.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSendMessage();
    }
});

// ─────────────────────────────────────────
// Auto resize textarea
// ─────────────────────────────────────────
msgInput.addEventListener('input', () => {
    msgInput.style.height = 'auto';
    msgInput.style.height = Math.min(msgInput.scrollHeight, 120) + 'px';
});

// ─────────────────────────────────────────
// Sidebar toggle
// ─────────────────────────────────────────
toggleBtn.addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');
});

// ─────────────────────────────────────────
// Search
// ─────────────────────────────────────────
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

// ─────────────────────────────────────────
// Collapsible sidebar sections
// ─────────────────────────────────────────
document.querySelectorAll('.sidebar-section').forEach(section => {
    section.querySelector('.collapsible').addEventListener('click', () => {
        section.classList.toggle('closed');
    });
});

// ─────────────────────────────────────────
// Update profile in sidebar
// ─────────────────────────────────────────
function updateProfile() {
    const name  = localStorage.getItem('full_name') || 'Your Name';
    const email = localStorage.getItem('email') || 'you@example.com';

    document.querySelector('.profile-name').textContent  = name;
    document.querySelector('.profile-email').textContent = email;
}