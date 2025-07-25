console.log('sfd');
// const socket = new WebSocket('ws://127.0.0.1:8001/ws/notifications/');
const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
console.log(protocol,window.location.hostname);
console.log(`${protocol}://127.0.0.1:8002/ws/notifications/`);

const socket = new WebSocket(`${protocol}://127.0.0.1:8002/ws/notifications/`);


socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('on mesasge');

    console.log("🔔 Notification:", data);
    // Do something, update UI
};

socket.onopen = () => console.log("WebSocket connected");
socket.onclose = () => console.log("WebSocket disconnected");
