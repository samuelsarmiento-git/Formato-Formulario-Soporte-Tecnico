import random
from datetime import datetime
from flask import Flask, render_template, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# Configuración
MI_CORREO = "samueldavidsarmientorodriguez@gmail.com"
MI_PASSWORD = "gigueecaskiobyto" 

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/enviar', methods=['POST'])
def enviar():
    try:
        datos = request.form
        ticket_id = f"BQ-PG-{random.randint(100000, 999999)}"
        ahora = datetime.now().strftime("%d/%m/%Y %I:%M %p")
        
        # Datos capturados
        nombre = datos.get('nombre')
        correo_usuario = datos.get('correo')
        servicios = request.form.getlist('servicios')
        servicios_html = "".join([f"<li>{s}</li>" for s in servicios])

        # --- DISEÑO DE TABLA PARA EL CORREO ---
        estilo_tabla = "border: 1px solid #e2e8f0; border-collapse: collapse; width: 100%; margin-bottom: 20px;"
        estilo_th = "background-color: #1e3a8a; color: white; padding: 10px; text-align: left; text-transform: uppercase; font-size: 12px;"
        estilo_td = "padding: 10px; border: 1px solid #e2e8f0; font-size: 14px; color: #334155;"

        cuerpo_html = f"""
        <div style="font-family: sans-serif; max-width: 700px; margin: auto; border: 1px solid #eee; padding: 20px;">
            <h2 style="color: #1e3a8a; text-align: center;">ORDEN DE SERVICIO: {ticket_id}</h2>
            <p style="text-align: center; color: #64748b;">Generada el: {ahora}</p>
            
            <table style="{estilo_tabla}">
                <tr><th colspan="2" style="{estilo_th}">Información del Solicitante</th></tr>
                <tr><td style="{estilo_td}"><b>Nombre:</b></td><td style="{estilo_td}">{nombre}</td></tr>
                <tr><td style="{estilo_td}"><b>Área:</b></td><td style="{estilo_td}">{datos.get('area')}</td></tr>
                <tr><td style="{estilo_td}"><b>Teléfono:</b></td><td style="{estilo_td}">{datos.get('telefono')}</td></tr>
                <tr><td style="{estilo_td}"><b>Email:</b></td><td style="{estilo_td}">{correo_usuario}</td></tr>
            </table>

            <table style="{estilo_tabla}">
                <tr><th colspan="2" style="{estilo_th}">Especificaciones del Equipo</th></tr>
                <tr><td style="{estilo_td}"><b>Tipo:</b></td><td style="{estilo_td}">{datos.get('tipo_maquina')}</td></tr>
                <tr><td style="{estilo_td}"><b>Marca/Modelo:</b></td><td style="{estilo_td}">{datos.get('marca')} - {datos.get('serie')}</td></tr>
                <tr><td style="{estilo_td}"><b>Hardware:</b></td><td style="{estilo_td}">RAM: {datos.get('ram')} | Disco: {datos.get('almacenamiento')}</td></tr>
                <tr><td style="{estilo_td}"><b>Serial:</b></td><td style="{estilo_td}">{datos.get('serial')}</td></tr>
            </table>

            <div style="background: #f8fafc; padding: 15px; border: 1px solid #e2e8f0; border-radius: 8px;">
                <h4 style="color: #1e3a8a; margin-top: 0;">INCIDENCIAS Y SERVICIOS:</h4>
                <ul style="color: #334155;">{servicios_html}</ul>
                <hr style="border: 0; border-top: 1px solid #cbd5e1;">
                <p><b>Observaciones:</b> {datos.get('observaciones')}</p>
            </div>
        </div>
        """

        # Enviar correos
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(MI_CORREO, MI_PASSWORD)

        # 1. Correo para Ti
        msg_admin = MIMEMultipart()
        msg_admin['Subject'] = f"NUEVA SOLICITUD [{ticket_id}] - {nombre}"
        msg_admin['From'] = MI_CORREO
        msg_admin['To'] = MI_CORREO
        msg_admin.attach(MIMEText(cuerpo_html, 'html'))
        server.send_message(msg_admin)

        # 2. Copia para el Usuario (OJO: Aquí se le envía al cliente)
        msg_user = MIMEMultipart()
        msg_user['Subject'] = f"Copia de tu Orden de Servicio - {ticket_id}"
        msg_user['From'] = MI_CORREO
        msg_user['To'] = correo_usuario
        msg_user.attach(MIMEText(cuerpo_html, 'html'))
        server.send_message(msg_user)

        server.quit()
        return jsonify({"status": "success", "ticket": ticket_id, "fecha": ahora})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)