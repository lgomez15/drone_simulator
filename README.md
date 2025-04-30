# Drone Simulator Web
# Drone Simulator Web
# Drone Simulator Web

```markdown
# Drone Simulator Web

Una aplicación web interactiva que simula el comportamiento de drones en diferentes ubicaciones. Utiliza FastAPI, WebSocket y archivos estáticos (HTML/JS/CSS) para mostrar en tiempo real la simulación. Incluye un script para probar el WebSocket desde consola.

---

## 📁 Estructura del Proyecto

```
drone_simulator_web/
├── app/
│   ├── __init__.py
│   ├── main.py              # API principal y lógica de WebSocket
│   └── simulator.py         # Lógica de simulación de drones
├── static/
│   ├── index.html           # Interfaz web
│   ├── script.js            # Script JS para WebSocket
│   └── style.css            # Estilos
├── tester.py                # Script para probar la API WebSocket desde terminal
└── requirements.txt         # Dependencias del proyecto
```

---

## 🚀 Requisitos

- Python 3.9+
- pip
- Un servidor Linux (como Ubuntu en un VPS)
- (Opcional) `screen`, `tmux` o `systemd` para mantener el servidor corriendo

---

## 🔧 Instalación

1. **Clona o sube el proyecto a tu servidor**
   ```bash
   git clone https://tu-repo/drone_simulator_web.git
   cd drone_simulator_web
   ```

2. **Crea un entorno virtual (opcional pero recomendado)**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instala las dependencias**
   ```bash
   pip install -r requirements.txt
   ```

---

## ▶️ Ejecutar el servidor

Puedes ejecutar el servidor directamente con:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Para mantenerlo funcionando en segundo plano incluso después de cerrar sesión:

```bash
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > log.txt 2>&1 &
```

También puedes usar `screen` o configurar un servicio con `systemd`.

---

## 🌐 Acceder a la interfaz web

Abre tu navegador y visita:

```
http://TU_IP_DEL_VPS:8000/static/index.html
```

---

## 🧪 Probar el WebSocket desde terminal

Este proyecto incluye un cliente de prueba `tester.py` que se conecta al WebSocket:

### Ejecutar el tester

```bash
python3 tester.py
```

Asegúrate de que el servidor esté corriendo antes de lanzar el tester.

---

## ⚙️ API

### `POST /start/{location}`

Inicia la simulación para una ubicación.

- Ejemplo: `POST /start/paris`

### `POST /stop`

Detiene la simulación.

### `WebSocket /ws`

Canal WebSocket donde se transmiten los datos de simulación cada segundo.

---

## 🛠 Dependencias principales

- FastAPI
- Uvicorn
- Numpy
- Haversine
- Websockets (para el tester)

Instala websockets para ejecutar `tester.py`:

```bash
pip install websockets
```

---

## 📌 Notas

- Asegúrate de que el puerto 8000 esté abierto en tu VPS.
- Puedes usar Nginx como proxy inverso para servir la app en el puerto 80/443 (opcional).

---

## 📤 Futuras mejoras

- Agregar autenticación para los clientes WebSocket.
- Añadir interfaz gráfica para seleccionar ubicación desde el frontend.
- Soporte HTTPS usando Let's Encrypt + Nginx.

---

## 👨‍💻 Autor

Osprean Software Development Team

```

---

