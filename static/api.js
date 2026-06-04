const BASE_URL = 'http://127.0.0.1:5000';

async function registerUser(full_name, email, phone, password) {
    const response = await fetch(`${BASE_URL}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ full_name, email, phone, password })
    });
    return await response.json();
}

async function loginUser(email, password) {
    const response = await fetch(`${BASE_URL}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    });
    return await response.json();
}

async function createSession(user_id, title) {
    const response = await fetch(`${BASE_URL}/sessions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id, title })
    });
    return await response.json();
}

async function getSessions(user_id) {
    const response = await fetch(`${BASE_URL}/sessions/${user_id}`);
    return await response.json();
}


async function sendMessage(session_id, sender, message) {
    const response = await fetch(`${BASE_URL}/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id, sender, message })
    });
    return await response.json();
}

async function getMessages(session_id) {
    const response = await fetch(`${BASE_URL}/messages/${session_id}`);
    return await response.json();

    async function chatWithAI(session_id, user_id, message) {
    const response = await fetch(`${BASE_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id, user_id, message })
    });
    return await response.json();
}
} 
async function chatWithAI(session_id, user_id, message) {
    const response = await fetch(`${BASE_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id, user_id, message })
    });
    return await response.json();
}