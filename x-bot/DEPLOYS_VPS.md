# Guía de Despliegue en VPS (Linux)

Para que tu bot de X (Twitter) funcione 24/7 en un VPS, lo ideal es configurarlo como un **servicio de systemd**. Esto hará que se inicie solo al arrancar el servidor y se reinicie automáticamente si falla.

## 1. Preparar el VPS

Asegúrate de tener Python instalado y clona/copia tu proyecto en el VPS. Ejemplo de ruta: `/home/usuario/x-bot`.

```bash
# Instalar dependencias si no las tienes (Ubuntu/Debian)
sudo apt update && sudo apt install python3-pip python3-venv -y

# Crear entorno virtual e instalar requerimientos
cd /home/usuario/x-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 2. Configurar el Servicio systemd

Crea un archivo de configuración para el servicio:

```bash
sudo nano /etc/systemd/system/x-bot-scheduler.service
```

Pega el siguiente contenido (ajustando las rutas a las tuyas):

```ini
[Unit]
Description=X (Twitter) Bot Scheduler
After=network.target

[Service]
# Cambia 'usuario' por tu nombre de usuario en el VPS
User=usuario
WorkingDirectory=/home/usuario/x-bot
# Ruta completa al binario de Python en tu entorno virtual
ExecStart=/home/usuario/x-bot/venv/bin/python scheduler.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 3. Activar el Servicio

Ejecuta estos comandos para iniciar el bot:

```bash
# Recargar systemd para que reconozca el nuevo servicio
sudo systemctl daemon-reload

# Habilitar para que empiece al arrancar el VPS
sudo systemctl enable x-bot-scheduler

# Iniciar el servicio ahora mismo
sudo systemctl start x-bot-scheduler

# Comprobar el estado
sudo systemctl status x-bot-scheduler
```

## 4. Ver los Logs en Tiempo Real

Puedes ver lo que está haciendo el bot (si está enviando tweets o si hay errores) con este comando:

```bash
journalctl -u x-bot-scheduler -f
# O revisando el archivo que crea el script:
tail -f /home/usuario/x-bot/scheduler.log
```

---

### Notas Adicionales:
- **Zona Horaria:** Asegúrate de que tu VPS tenga la zona horaria correcta (`timedatectl set-timezone Europe/Madrid`) para que los tweets salgan a la hora que esperas.
- **Configuración (`schedule.json`):** Puedes editar el archivo `schedule.json` en cualquier momento y reiniciar el servicio (`sudo systemctl restart x-bot-scheduler`) para aplicar los cambios.
