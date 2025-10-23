/**
 * Chat WebSocket functionality
 */

let chatSocket = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;
const RECONNECT_DELAY = 3000;

/**
 * Initialize chat WebSocket connection
 */
function initializeChat(bookingId, currentUserId, currentUserName) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/chat/${bookingId}/`;
    
    console.log('Connecting to WebSocket:', wsUrl);
    
    try {
        chatSocket = new WebSocket(wsUrl);
        
        chatSocket.onopen = function(e) {
            console.log('WebSocket connection established');
            updateConnectionStatus('connected');
            reconnectAttempts = 0;
            scrollToBottom();
        };
        
        chatSocket.onmessage = function(e) {
            const data = JSON.parse(e.data);
            console.log('Message received:', data);
            
            // Add message to chat
            addMessageToChat(data, currentUserId);
            
            // Scroll to bottom
            scrollToBottom();
            
            // Play notification sound if message is from other user
            if (data.sender_id !== currentUserId) {
                playNotificationSound();
            }
        };
        
        chatSocket.onerror = function(e) {
            console.error('WebSocket error:', e);
            updateConnectionStatus('disconnected');
        };
        
        chatSocket.onclose = function(e) {
            console.log('WebSocket connection closed');
            updateConnectionStatus('disconnected');
            
            // Attempt to reconnect
            if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
                reconnectAttempts++;
                console.log(`Attempting to reconnect (${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})...`);
                updateConnectionStatus('connecting');
                setTimeout(() => {
                    initializeChat(bookingId, currentUserId, currentUserName);
                }, RECONNECT_DELAY);
            } else {
                console.error('Max reconnection attempts reached');
                showReconnectButton();
            }
        };
        
    } catch (error) {
        console.error('Error creating WebSocket:', error);
        updateConnectionStatus('disconnected');
    }
    
    // Setup form submission
    setupChatForm(currentUserId, currentUserName);
    
    // Scroll to bottom on load
    scrollToBottom();
}

/**
 * Setup chat form submission
 */
function setupChatForm(currentUserId, currentUserName) {
    const chatForm = document.getElementById('chatForm');
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    
    if (!chatForm || !messageInput || !sendButton) {
        console.error('Chat form elements not found');
        return;
    }
    
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const message = messageInput.value.trim();
        
        if (!message) {
            return;
        }
        
        if (!chatSocket || chatSocket.readyState !== WebSocket.OPEN) {
            alert('Connection lost. Please refresh the page.');
            return;
        }
        
        // Send message via WebSocket
        chatSocket.send(JSON.stringify({
            'message': message
        }));
        
        // Clear input
        messageInput.value = '';
        messageInput.focus();
    });
    
    // Enable/disable send button based on connection status
    messageInput.addEventListener('input', function() {
        sendButton.disabled = !messageInput.value.trim() || !chatSocket || chatSocket.readyState !== WebSocket.OPEN;
    });
}

/**
 * Add message to chat UI
 */
function addMessageToChat(data, currentUserId) {
    const chatMessages = document.getElementById('chatMessages');
    
    if (!chatMessages) {
        console.error('Chat messages container not found');
        return;
    }
    
    // Remove "no messages" placeholder if it exists
    const noMessages = chatMessages.querySelector('.no-messages');
    if (noMessages) {
        noMessages.remove();
    }
    
    // Create message element
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${data.sender_id === currentUserId ? 'message-sent' : 'message-received'}`;
    messageDiv.setAttribute('data-message-id', data.message_id);
    
    const timestamp = new Date(data.timestamp).toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
    
    messageDiv.innerHTML = `
        <div class="message-content">
            <div class="message-header">
                <strong>${escapeHtml(data.sender_name)}</strong>
                <small class="text-muted ms-2">${timestamp}</small>
            </div>
            <div class="message-text">${escapeHtml(data.message)}</div>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
}

/**
 * Update connection status indicator
 */
function updateConnectionStatus(status) {
    const statusElement = document.getElementById('connectionStatus');
    const sendButton = document.getElementById('sendButton');
    const messageInput = document.getElementById('messageInput');
    
    if (!statusElement) return;
    
    statusElement.className = 'badge';
    
    switch (status) {
        case 'connected':
            statusElement.classList.add('bg-success', 'connected');
            statusElement.innerHTML = '<i class="fa fa-check-circle me-1"></i> Connected';
            if (sendButton) sendButton.disabled = false;
            if (messageInput) messageInput.disabled = false;
            break;
        case 'connecting':
            statusElement.classList.add('bg-warning', 'connecting');
            statusElement.innerHTML = '<i class="fa fa-circle-notch fa-spin me-1"></i> Connecting...';
            if (sendButton) sendButton.disabled = true;
            if (messageInput) messageInput.disabled = true;
            break;
        case 'disconnected':
            statusElement.classList.add('bg-danger', 'disconnected');
            statusElement.innerHTML = '<i class="fa fa-times-circle me-1"></i> Disconnected';
            if (sendButton) sendButton.disabled = true;
            if (messageInput) messageInput.disabled = true;
            break;
    }
}

/**
 * Scroll chat to bottom
 */
function scrollToBottom() {
    const chatMessages = document.getElementById('chatMessages');
    if (chatMessages) {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

/**
 * Show reconnect button
 */
function showReconnectButton() {
    const statusElement = document.getElementById('connectionStatus');
    if (statusElement) {
        statusElement.innerHTML = '<i class="fa fa-exclamation-triangle me-1"></i> Connection lost. <a href="#" onclick="location.reload(); return false;">Refresh page</a>';
    }
}

/**
 * Play notification sound (optional)
 */
function playNotificationSound() {
    // You can add a notification sound here if needed
    // const audio = new Audio('/static/sounds/notification.mp3');
    // audio.play().catch(e => console.log('Could not play sound:', e));
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}

/**
 * Close WebSocket connection when leaving page
 */
window.addEventListener('beforeunload', function() {
    if (chatSocket) {
        chatSocket.close();
    }
});

