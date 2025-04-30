let socket = null;

document.getElementById('start-btn').onclick = async () => {
    const location = document.getElementById('location-select').value;
    const res = await fetch(`/start/${location}`, { method: 'POST' });
    const data = await res.json();
    if (data.status === 'started') {
        log('[Simulación] Iniciada');
        document.getElementById('start-btn').disabled = true;
        document.getElementById('stop-btn').disabled = false;
        connectWebSocket();
    } else if (data.status === 'already_running') {
        log('[Simulación] Ya está en ejecución');
    } else {
        log(`[Error] ${data.message || 'Error desconocido'}`);
    }
};

document.getElementById('stop-btn').onclick = async () => {
    const res = await fetch('/stop', { method: 'POST' });
    const data = await res.json();
    if (data.status === 'stopped') {
        log('[Simulación] Detenida');
        document.getElementById('start-btn').disabled = false;
        document.getElementById('stop-btn').disabled = true;
        if (socket) {
            socket.close();
            socket = null;
        }
    } else {
        log('[Simulación] No estaba en ejecución');
    }
};

function connectWebSocket() {
    if (socket) {
        socket.close();
    }
    const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
    socket = new WebSocket(`${protocol}//${location.host}/ws`);

    socket.onopen = () => log('[WebSocket] Conectado');
    socket.onclose = () => log('[WebSocket] Desconectado');
    socket.onerror = (e) => log('[WebSocket] Error: ' + e.message);

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        updateTelemetry(data);
        updateMap(data);
        logData(data);
    };
}

function updateTelemetry(data) {
    const container = document.getElementById('telemetry');
    container.innerHTML = `
        <p><b>Ubicación:</b> ${data.location}</p>
        <p><b>Coordenadas:</b> ${data.latitude.toFixed(6)}, ${data.longitude.toFixed(6)}</p>
        <p><b>Altitud:</b> ${data.altitude.toFixed(1)} m / Máx: ${data.max_altitude} m</p>
        <p><b>Velocidad:</b> ${data.speed.toFixed(2)} m/s</p>
        <p><b>Batería:</b> ${data.battery.toFixed(1)}%</p>
        <p><b>Estado:</b> ${data.status}</p>
    `;
}

const canvas = document.getElementById('drone-map');
const ctx = canvas.getContext('2d');
let basePos = null;

function updateMap(data) {
    if (!basePos) basePos = [data.latitude, data.longitude];

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Área de patrulla
    ctx.strokeStyle = 'green';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(200, 200, 100, 0, 2 * Math.PI);
    ctx.stroke();

    // Base
    ctx.fillStyle = 'red';
    ctx.beginPath();
    ctx.arc(195, 195, 5, 0, 2 * Math.PI);
    ctx.fill();

    // Dron
    const scale = 1000;
    const deltaLat = (data.latitude - basePos[0]) * 111000;
    const deltaLon = (data.longitude - basePos[1]) * 111000 * Math.cos(basePos[0] * Math.PI / 180);
    const x = 200 + (deltaLon / scale) * 200;
    const y = 200 - (deltaLat / scale) * 200;

    ctx.fillStyle = 'blue';
    ctx.beginPath();
    ctx.arc(x, y, 5, 0, 2 * Math.PI);
    ctx.fill();
}

function logData(data) {
    const logArea = document.getElementById('log');
    const timeStr = new Date(data.timestamp * 1000).toLocaleTimeString();
    logArea.value += `[${timeStr}] Lat:${data.latitude.toFixed(6)} Lon:${data.longitude.toFixed(6)} Alt:${data.altitude.toFixed(1)}m Speed:${data.speed.toFixed(2)}m/s Battery:${data.battery.toFixed(1)}% Status:${data.status}\n`;
    logArea.scrollTop = logArea.scrollHeight;
}

function log(msg) {
    const logArea = document.getElementById('log');
    logArea.value += msg + '\n';
    logArea.scrollTop = logArea.scrollHeight;
}
