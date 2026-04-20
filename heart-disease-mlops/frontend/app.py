import gradio as gr
import requests
import time

API_URL = "https://heart-api-y63c.onrender.com/predict"

# ─────────────────────────────────────────────
#  TEMA GRADIO — neutro, funciona en light/dark
# ─────────────────────────────────────────────
theme = gr.themes.Base(
    font=gr.themes.GoogleFont("DM Sans"),
    font_mono=gr.themes.GoogleFont("DM Mono"),
).set(


    # Botón primario
    button_primary_background_fill="*neutral_900",
    button_primary_background_fill_hover="*neutral_700",
    button_primary_text_color="white",
    button_primary_border_color="transparent",

    # Botón secundario
    button_secondary_background_fill="*neutral_100",
    button_secondary_text_color="*neutral_800",
    button_secondary_border_color="*neutral_200",
)

# ─────────────────────────────────────────────
#  CSS MÍNIMO — solo lo que Gradio no controla
# ─────────────────────────────────────────────
css = """
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Serif+Display&display=swap');

.gradio-container { max-width: 860px !important; margin: 0 auto !important; padding: 48px 32px !important; }

/* Header */
#app-header { text-align: center; margin-bottom: 36px; padding: 0; }
#app-header h1 {
    font-family: 'DM Serif Display', serif;
    font-size: 2.2rem;
    font-weight: 400;
    letter-spacing: -0.3px;
    margin: 0 0 8px 0;
    line-height: 1.2;
}
#app-header p { font-size: 0.95rem; opacity: 0.6; margin: 0; font-weight: 300; }

/* Banner */
#cold-start-banner {
    border-radius: 12px;
    padding: 13px 18px;
    margin-bottom: 20px;
    font-size: 0.84rem;
    line-height: 1.5;
    border: 1px solid;
    opacity: 0.85;
}

/* Separador de sección */
.section-label {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    opacity: 0.45;
    margin-bottom: 4px;
}

/* Botón predecir */
#btn-predict { margin-top: 8px; }
#btn-predict button { font-size: 0.9rem; letter-spacing: 0.06em; padding: 14px !important; }

/* Output card */
#result-box { margin-top: 4px; }
.result-card {
    border-radius: 14px;
    padding: 26px 28px;
    border: 1.5px solid;
}
.result-card .label {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.result-card .title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.5rem;
    font-weight: 400;
    margin-bottom: 12px;
    line-height: 1.2;
}
.result-card .pill {
    display: inline-block;
    border-radius: 100px;
    padding: 5px 16px;
    font-size: 0.86rem;
    font-weight: 500;
    margin-bottom: 14px;
}
.result-card .note {
    font-size: 0.82rem;
    line-height: 1.6;
    opacity: 0.75;
    margin: 0;
}

/* Waiting card */
.waiting-card {
    border-radius: 14px;
    padding: 26px 28px;
    border: 1.5px solid;
    display: flex;
    flex-direction: column;
    gap: 10px;
}
.waiting-card .wlabel {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    opacity: 0.55;
}
.waiting-card .wtitle {
    font-family: 'DM Serif Display', serif;
    font-size: 1.4rem;
    font-weight: 400;
}
.waiting-card .wbar-bg {
    height: 4px;
    border-radius: 2px;
    overflow: hidden;
    opacity: 0.3;
}
.waiting-card .wbar-fill {
    height: 100%;
    border-radius: 2px;
    animation: load 45s linear forwards;
}
@keyframes load { from { width: 0% } to { width: 100% } }
.waiting-card .wnote { font-size: 0.82rem; opacity: 0.6; margin: 0; }

footer { display: none !important; }
.app-footer { text-align: center; margin-top: 48px; font-size: 0.72rem; opacity: 0.35; }
"""


# ─────────────────────────────────────────────
#  LÓGICA DE PREDICCIÓN (CON REINTENTOS)
# ─────────────────────────────────────────────
def predict(age, sex, chest_pain_type, resting_bp, cholesterol,
            fasting_bs, resting_ecg, max_hr, exercise_angina,
            oldpeak, st_slope, progress=gr.Progress()):

    sex_map        = {"Masculino": 1, "Femenino": 0}
    chest_pain_map = {"ASY (Asintomático)": 3, "NAP": 2, "ATA": 1, "TA": 4}
    ecg_map        = {"Normal": 0, "ST": 1, "LVH": 2}
    angina_map     = {"No": 0, "Sí": 1}
    slope_map      = {"Up": 1, "Flat": 2, "Down": 3}

    features = [
        age, sex_map[sex], chest_pain_map[chest_pain_type],
        resting_bp, cholesterol, fasting_bs,
        ecg_map[resting_ecg], max_hr, angina_map[exercise_angina],
        oldpeak, slope_map[st_slope],
    ]

    # Configuración de reintentos
    MAX_RETRIES = 3
    RETRY_DELAYS = [5, 10, 15]  # segundos de espera entre intentos

    # Mostrar estado de espera inicial
    waiting_html = """
    <div class="waiting-card" style="border-color: currentColor;">
        <div class="wlabel">Procesando</div>
        <div class="wtitle" id="waiting-title">Conectando con el servidor…</div>
        <div class="wbar-bg" style="background: currentColor;">
            <div class="wbar-fill" style="background: currentColor;"></div>
        </div>
        <p class="wnote" id="waiting-note">
            Si el servidor estuvo inactivo, puede tardar hasta 45 segundos en responder.
            Por favor espera, no recargues la página.
        </p>
    </div>
    """

    # Función para actualizar el mensaje de espera (usando progress de Gradio)
    def update_waiting(attempt):
        progress(0.1 + (attempt * 0.1), desc=f"Intento {attempt + 1}/{MAX_RETRIES + 1} - Despertando servidor...")

    progress(0.1, desc="Verificando conexión...")
    time.sleep(0.5)

    last_error = None

    for attempt in range(MAX_RETRIES + 1):
        try:
            update_waiting(attempt)
            
            # Timeout progresivo: más tiempo en cada intento
            timeout = 60 if attempt == 0 else 90
            
            t0 = time.time()
            response = requests.post(
                API_URL,
                json={"features": features},
                timeout=timeout,
                headers={"Connection": "close"}  # Evitar keep-alive que puede causar problemas
            )
            response.raise_for_status()
            elapsed = time.time() - t0

            result = response.json()
            prob = result["heart_disease_probability"]
            prediction = result["prediction"]

            progress(0.9, desc="Procesando resultado...")
            cold = f" (el servidor tardó {elapsed:.0f}s en arrancar)" if elapsed > 10 else ""

            if prediction == 1:
                return f"""
                <div class="result-card" style="
                    background: rgba(220,38,38,0.07);
                    border-color: rgba(220,38,38,0.25);
                ">
                    <div class="label" style="color:#dc2626;">Resultado del análisis{cold}</div>
                    <div class="title" style="color:#991b1b;">Alto riesgo de enfermedad cardíaca</div>
                    <div class="pill" style="background:rgba(220,38,38,0.12);color:#991b1b;">
                        Probabilidad: {prob:.1%}
                    </div>
                    <p class="note">
                        Se recomienda consultar con un especialista en cardiología
                        para una evaluación clínica completa.
                    </p>
                </div>"""
            else:
                return f"""
                <div class="result-card" style="
                    background: rgba(22,163,74,0.07);
                    border-color: rgba(22,163,74,0.25);
                ">
                    <div class="label" style="color:#16a34a;">Resultado del análisis{cold}</div>
                    <div class="title" style="color:#166534;">Bajo riesgo de enfermedad cardíaca</div>
                    <div class="pill" style="background:rgba(22,163,74,0.12);color:#166534;">
                        Probabilidad: {prob:.1%}
                    </div>
                    <p class="note">
                        Los indicadores analizados no sugieren riesgo elevado.
                        Continúe con controles periódicos de rutina.
                    </p>
                </div>"""

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            last_error = e
            if attempt < MAX_RETRIES:
                delay = RETRY_DELAYS[attempt]
                progress(0.2 + (attempt * 0.15), desc=f"Servidor no disponible. Reintentando en {delay}s...")
                time.sleep(delay)
            else:
                # Último intento fallido
                progress(1.0, desc="Error de conexión")
                return """
                <div class="result-card" style="background:rgba(220,38,38,0.07);border-color:rgba(220,38,38,0.25);">
                    <div class="label" style="color:#dc2626;">Error de conexión</div>
                    <div class="title" style="color:#991b1b;">No se pudo conectar tras varios intentos</div>
                    <p class="note">
                        El servidor está tardando más de lo habitual en despertar.
                        Por favor, espera 1-2 minutos y vuelve a intentarlo.
                    </p>
                </div>"""

        except requests.exceptions.HTTPError as e:
            # Error HTTP (ej. 502 Bad Gateway durante el arranque)
            last_error = e
            if attempt < MAX_RETRIES and response.status_code in [502, 503, 504]:
                delay = RETRY_DELAYS[attempt]
                progress(0.2 + (attempt * 0.15), desc=f"Servidor arrancando (HTTP {response.status_code}). Reintentando en {delay}s...")
                time.sleep(delay)
            else:
                progress(1.0, desc="Error del servidor")
                return f"""
                <div class="result-card" style="background:rgba(220,38,38,0.07);border-color:rgba(220,38,38,0.25);">
                    <div class="label" style="color:#dc2626;">Error del servidor</div>
                    <div class="title" style="color:#991b1b;">HTTP {response.status_code}</div>
                    <p class="note">
                        El servidor respondió con un error. Intenta de nuevo en unos segundos.
                    </p>
                </div>"""

        except Exception as e:
            progress(1.0, desc="Error inesperado")
            return f"""
            <div class="result-card" style="background:rgba(220,38,38,0.07);border-color:rgba(220,38,38,0.25);">
                <div class="label" style="color:#dc2626;">Error inesperado</div>
                <div class="title" style="color:#991b1b;">Algo salió mal</div>
                <p class="note" style="font-family:monospace;">{str(e)}</p>
            </div>"""

    # Si salimos del bucle sin retornar (no debería ocurrir)
    return """
    <div class="result-card" style="background:rgba(220,38,38,0.07);border-color:rgba(220,38,38,0.25);">
        <div class="label" style="color:#dc2626;">Error desconocido</div>
        <div class="title" style="color:#991b1b;">No se pudo completar la predicción</div>
        <p class="note">Por favor, recarga la página e inténtalo de nuevo.</p>
    </div>"""
    
# ─────────────────────────────────────────────
#  INTERFAZ
# ─────────────────────────────────────────────
with gr.Blocks(theme=theme, css=css, title="Predicción Cardíaca") as demo:

    # Header
    gr.HTML("""
    <div id="app-header">
        <h1>Predicción de Riesgo Cardíaco</h1>
        <p>Ingrese los datos clínicos del paciente para evaluar el riesgo mediante Machine Learning</p>
    </div>
    <div id="cold-start-banner" style="border-color: rgba(124,111,196,0.4); background: rgba(124,111,196,0.08); color: inherit;">
        <strong style="color:#7c6fc4;">Primera predicción más lenta</strong> —
        El servidor gratuito entra en reposo tras inactividad.
        La primera llamada puede tardar hasta 45 segundos, las siguientes son instantáneas.
    </div>
    """)

    # Formulario
    with gr.Row():
        # Columna izquierda — datos del paciente
        with gr.Column():
            gr.HTML('<div class="section-label">Datos del paciente</div>')
            age             = gr.Number(label="Edad", value=25, precision=0, minimum=1, maximum=120)
            sex             = gr.Radio(label="Sexo", choices=["Masculino", "Femenino"], value="Masculino")
            chest_pain_type = gr.Dropdown(
                label="Tipo de dolor torácico",
                choices=["ASY (Asintomático)", "NAP", "ATA", "TA"],
                value="ASY (Asintomático)",
            )
            resting_bp  = gr.Number(label="Presión arterial en reposo (mm Hg)", value=110, precision=0)
            cholesterol = gr.Number(label="Colesterol (mg/dl)", value=280, precision=0)

        # Columna derecha — indicadores clínicos
        with gr.Column():
            gr.HTML('<div class="section-label">Indicadores clínicos</div>')
            fasting_bs      = gr.Radio(label="Azúcar en ayunas > 120 mg/dl", choices=[0, 1], value=0)
            resting_ecg     = gr.Dropdown(
                label="ECG en reposo",
                choices=["Normal", "ST", "LVH"],
                value="Normal",
            )
            max_hr          = gr.Number(label="Frecuencia cardíaca máxima", value=120, precision=0)
            exercise_angina = gr.Radio(label="Angina inducida por ejercicio", choices=["No", "Sí"], value="No")
            oldpeak         = gr.Number(label="Depresión del ST (Oldpeak)", value=1.0, step=0.1)
            st_slope        = gr.Dropdown(
                label="Pendiente del segmento ST",
                choices=["Up", "Flat", "Down"],
                value="Flat",
            )

    # Botón
    btn = gr.Button("Predecir riesgo", variant="primary", elem_id="btn-predict")

    # Resultado
    result_html = gr.HTML(elem_id="result-box")

    btn.click(
        fn=predict,
        inputs=[age, sex, chest_pain_type, resting_bp, cholesterol,
                fasting_bs, resting_ecg, max_hr, exercise_angina, oldpeak, st_slope],
        outputs=result_html,
    )

    gr.HTML('<div class="app-footer">ML 2026-01 | Predictor de riesgo cardíaco · Desarrollado por Tiffany Mendoza y Nino Cabrera</div>')


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)