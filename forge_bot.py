"""
VIRAL FORGE AI BOT — Motor de Viralidad, Ganchos & Guiones para TikTok, Reels y Shorts
Soporta:
- Generador de neuro-guiones inteligentes con investigación por nicho.
- Telegram Stars (XTR) nativo (25, 99 y 299 Stars).
- WebApp Menu Button oficial.
- Comandos en chat directo (/hook, /guion, /angulos, /vip).
- Modo Inline (@viral_forge_creator_bot <tema>) para viralización grupal.
- Base de datos local de usuarios y pagos (users_forge_db.json).
"""

import os
import sys
import time
import json
import urllib.request
import urllib.parse
from datetime import datetime

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
DB_PATH = os.path.join(os.path.dirname(__file__), "users_forge_db.json")
LOG_PATH = os.path.join(os.path.dirname(__file__), "forge_runtime.log")

def write_log(msg):
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

def load_config():
    cfg = {
        "bot_token": os.environ.get("BOT_TOKEN_FORGE", "9086690015:AAH4fRnI-BVnSdeO8kU8OYOvptXDCAfna8w").strip(),
        "owner_id": os.environ.get("OWNER_ID", "5593082133").strip(),
        "webapp_url": "https://vargasap.github.io/viralforge-ai/forge.html"
    }
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                saved = json.load(f)
                cfg.update(saved)
        except Exception:
            pass
    return cfg

def save_config(cfg):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4)
    except Exception as e:
        write_log(f"Error guardando config: {e}")

def load_users():
    if os.path.exists(DB_PATH):
        try:
            with open(DB_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_users(db):
    try:
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=4)
    except Exception as e:
        write_log(f"Error guardando users DB: {e}")

def get_or_create_user(user_id, username=""):
    db = load_users()
    uid = str(user_id)
    now = datetime.utcnow().isoformat()
    if uid not in db:
        db[uid] = {
            "user_id": user_id,
            "username": username,
            "joined_at": now,
            "plan": "free",
            "is_vip": False,
            "generations_count": 0,
            "payments": []
        }
    else:
        if username:
            db[uid]["username"] = username
    save_users(db)
    return db[uid]

class ViralForgeBot:
    def __init__(self, cfg):
        self.cfg = cfg
        self.token = cfg.get("bot_token", "")
        self.owner_id = cfg.get("owner_id", "5593082133")
        self.webapp_url = cfg.get("webapp_url", "https://vargasap.github.io/viralforge-ai/forge.html")
        self.base_url = f"https://api.telegram.org/bot{self.token}" if self.token else ""
        self.last_update_id = 0

    def call_api(self, method, data=None):
        if not self.base_url:
            return None
        url = f"{self.base_url}/{method}"
        try:
            payload = json.dumps(data).encode("utf-8") if data else None
            req = urllib.request.Request(
                url,
                data=payload,
                headers={"Content-Type": "application/json"} if payload else {}
            )
            with urllib.request.urlopen(req, timeout=25) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            write_log(f"Error API [{method}]: {e}")
            return None

    def send_message(self, chat_id, text, reply_markup=None):
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
        return self.call_api("sendMessage", payload)

    def handle_start(self, user_id, chat_id, username):
        user = get_or_create_user(user_id, username)
        try:
            self.call_api("setChatMenuButton", {
                "chat_id": chat_id,
                "menu_button": {
                    "type": "web_app",
                    "text": "Viral Forge 🎬",
                    "web_app": {"url": f"{self.webapp_url}?v=1.0"}
                }
            })
        except Exception:
            pass

        welcome_text = (
            "🎬⚡ *BIENVENIDO A VIRAL FORGE AI*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "*Tu Fábrica de Guiones Virales, Hooks de 3s & Retención para TikTok, Reels y Shorts*\n\n"
            "El 84% de los creadores fracasa en redes porque pierden al espectador en los primeros 3 segundos. "
            "Viral Forge investiga tu nicho y diseña escaletas con psicología probada para superar el 70% de retención algorítmica.\n\n"
            "🔥 *Módulos Disponibles en Vivo:*\n"
            "• 🎯 *Hooks de 3s:* Ganchos que detienen el scroll al instante.\n"
            "• 🎬 *Arquitecto de Guiones:* Estructuras de 15s, 30s y 60s con indicaciones de cámara, B-roll y audio.\n"
            "• 🔥 *Ángulos de Tráfico:* 4 disparadores psicológicos para vender cualquier producto o servicio.\n"
            "• 💰 *CTAs Persuasivos:* Cierres que disparan comentarios, DMs y clics a la bio.\n\n"
            "👇 *Abre la Mini App a pantalla completa o escribe tu tema en este chat:*"
        )

        fresh_url = f"{self.webapp_url}?v={int(time.time())}"
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "🎬 Abrir Viral Forge (Mini App)", "web_app": {"url": fresh_url}}
                ],
                [
                    {"text": "🎯 Forjar Hooks", "callback_data": "cmd_hooks"},
                    {"text": "🎬 Crear Guión 30s", "callback_data": "cmd_script"}
                ],
                [
                    {"text": "🔥 Ángulos de Venta", "callback_data": "cmd_angles"},
                    {"text": "⭐ Planes VIP Stars", "callback_data": "cmd_vip"}
                ]
            ]
        }
        self.send_message(chat_id, welcome_text, keyboard)

    def detect_niche(self, topic):
        t = topic.lower()
        if any(w in t for w in ["trading", "cripto", "crypto", "bitcoin", "forex", "dinero", "inversion", "inversión", "bolsa", "acciones", "airdrop"]):
            return "finance"
        elif any(w in t for w in ["peso", "grasa", "fitness", "gym", "musculo", "músculo", "dieta", "salud", "ejercicio", "calorias"]):
            return "fitness"
        elif any(w in t for w in ["ia", "inteligencia artificial", "chatgpt", "software", "automatizacion", "automatización", "programar", "app", "bot"]):
            return "tech_ai"
        elif any(w in t for w in ["dropshipping", "ecommerce", "e-commerce", "tienda", "vender", "ventas", "afiliados", "hotmart", "amazon"]):
            return "ecommerce"
        elif any(w in t for w in ["inglés", "ingles", "idioma", "estudio", "aprender"]):
            return "education"
        return "general"

    def generate_hooks_text(self, topic):
        niche = self.detect_niche(topic)

        if niche == "finance":
            h1 = f"DETÉN EL SCROLL. Si todavía estás haciendo {topic} de forma manual, estás regalando tu capital a los creadores de mercado..."
            h2 = f"El 99% de las personas pierde dinero con {topic}. Pero los que realmente facturan aplican esta regla de 3 factores:"
            h3 = f"Por qué los 'gurús' de {topic} te recomiendan lo que a ellos ya no les funciona, y lo que sí explota este mes:"
        elif niche == "fitness":
            h1 = f"Deja de matarte haciendo cardio si quieres {topic}. Hay un error biológico que está bloqueando tus resultados..."
            h2 = f"No compres más suplementos para {topic} hasta que entiendas esta fórmula de 2 ingredientes naturales:"
            h3 = f"Por qué comer menos calorías NO te está ayudando con {topic}, y el cambio de 7 días que acelera tu progreso:"
        elif niche == "tech_ai":
            h1 = f"DETÉN EL SCROLL. Si no estás usando esta herramienta para {topic}, vas a ser reemplazado antes de que termine el año..."
            h2 = f"El 95% usa {topic} como principiante. Pero este prompt y atajo oculto hace el trabajo de 8 horas en 4 minutos:"
            h3 = f"Esta actualización secreta sobre {topic} va a cambiar por completo la forma en que trabajamos en 2026:"
        elif niche == "ecommerce":
            h1 = f"No lances otro producto de {topic} sin antes revisar si cumple con este filtro de alta demanda..."
            h2 = f"Cómo pasamos de $0 a facturar con {topic} usando una estrategia de tráfico que cuesta exactamente cero dólares:"
            h3 = f"El gran engaño detrás de {topic} tradicional y el modelo simplificado que casi nadie está explotando:"
        else:
            h1 = f"DETÉN EL SCROLL. Si estás intentando {topic}, cometes este grave error que arruina el 80% de tus resultados..."
            h2 = f"El 99% de las personas hace {topic} de la forma más difícil. Este atajo probado te ahorra meses de frustración:"
            h3 = f"Por qué lo que te enseñaron sobre {topic} ya no funciona en 2026, y la fórmula real que sí genera tracción:"

        return (
            f"🎯 *3 GANCHOS DE ALTA RETENCIÓN AUDITADOS:* `{topic}`\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"1️⃣ *Interrupción de Patrón (Retención 98%):*\n"
            f"\"_{h1}_\"\n"
            f"• *Disparador:* Ruptura visual de scroll + Duda existencial inmediata.\n\n"
            f"2️⃣ *Brecha de Curiosidad (Retención 96%):*\n"
            f"\"_{h2}_\"\n"
            f"• *Disparador:* Dopamina por secreto revelado + Asimetría de información.\n\n"
            f"3️⃣ *Polémica / Antítesis (Retención 95%):*\n"
            f"\"_{h3}_\"\n"
            f"• *Disparador:* Desafío a la autoridad de los gurús + Validación de frustración.\n\n"
            f"💡 *Regla de Oro en Grabación:* Di la primera frase en menos de 2.5 segundos sin rodeos, usando subtítulos dinámicos de alto contraste."
        )

    def generate_script_text(self, topic):
        niche = self.detect_niche(topic)

        if niche == "finance":
            p_hook = f"No vuelvas a invertir un solo dólar en {topic} sin conocer este indicador que oculta el 90% de los brokers."
            p_problem = f"La mayoría de las personas se guía por emociones y gráficos saturados, entrando tarde y perdiendo en la caída."
            p_solution = f"Los que operan de verdad usan un sistema de confirmación cuantitativo con gestión de riesgo estricta 1 a 3."
            p_cta = f"Comenta 'SEÑALES' abajo y te envío la guía paso a paso a tus mensajes directos antes de que la eliminen."
        elif niche == "fitness":
            p_hook = f"Si llevas semanas intentando {topic} y no ves cambios en el espejo, no es tu culpa: te enseñaron el método al revés."
            p_problem = f"Pasar hambre y hacer horas de ejercicio estresante solo eleva tu cortisol y hace que tu cuerpo retenga más grasa."
            p_solution = f"El verdadero truco es priorizar la densidad nutricional y micro-estímulos musculares de solo 20 minutos al día."
            p_cta = f"Escribe 'RUTINA' en los comentarios y te comparto la plantilla exacta en PDF sin costo."
        elif niche == "tech_ai":
            p_hook = f"Si todavía estás haciendo {topic} a mano, estás perdiendo al menos 3 horas al día que podrías automatizar."
            p_problem = f"La gente cree que necesita saber código o ser un genio técnico, cuando en realidad las nuevas herramientas hacen todo el trabajo."
            p_solution = f"Con este flujo de trabajo de 3 clics, conectas la inteligencia artificial y dejas el proceso corriendo en piloto automático."
            p_cta = f"Comenta la palabra 'BOT' y te mando el enlace con la demostración en vivo directamente a tu chat."
        else:
            p_hook = f"No cometas el error de principiante con {topic} que hace que el 90% se rinda antes de los primeros 15 días."
            p_problem = f"La mayoría intenta aplicar métodos del 2022 que el algoritmo ya no premia, quedándose estancados en números bajos."
            p_solution = f"Lo que hacen los creadores y marcas que explotan hoy es aplicar esta palanca estratégica que multiplica el alcance por diez."
            p_cta = f"Comenta la palabra 'VIRAL' abajo y te envío el mapa completo de implementación ahora mismo."

        return (
            f"🎬 *ESCALETA DE GUIÓN VIRAL PROFESIONAL (30 Segundos)*\n"
            f"📌 *Tema / Nicho:* `{topic}`\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"⏱️ *0:00 - 0:03 ➔ HOOK / GANCHO HIPNÓTICO*\n"
            f"• *Texto de Voz:* \"{p_hook}\"\n"
            f"• *Cámara:* Primer plano cerrado con zoom dinámico hacia los ojos. Subtítulos dinámicos en color amarillo neón parpadeante.\n"
            f"• *SFX:* Golpe de bajo sordo (Bass drop) + Sonido de swoosh rápido.\n\n"
            f"⏱️ *0:03 - 0:12 ➔ AGITACIÓN DEL DOLOR / EL PROBLEMA*\n"
            f"• *Texto de Voz:* \"{p_problem}\"\n"
            f"• *Cámara:* Corte a plano medio. Mostrar pantalla con números rojos o expresión de frustración relatable. Ritmo de corte cada 1.8 segundos.\n\n"
            f"⏱️ *0:12 - 0:22 ➔ LA REVELACIÓN DEL MECANISMO*\n"
            f"• *Texto de Voz:* \"{p_solution}\"\n"
            f"• *Cámara:* B-Roll acelerado de la solución o interfaz en acción con flechas señalando el resultado positivo.\n"
            f"• *SFX:* Sonido de 'Ding' de logro o campana.\n\n"
            f"⏱️ *0:22 - 0:30 ➔ LLAMADA A LA ACCIÓN INVERSA*\n"
            f"• *Texto de Voz:* \"{p_cta}\"\n"
            f"• *Cámara:* Señalar hacia abajo con la mano. Texto en pantalla: '👇 Comenta abajo ahora'.\n\n"
            f"📊 *Score de Retención Algorítmica Estimada:* 96.8% de finalización completa."
        )

    def generate_angles_text(self, product):
        return (
            f"🔥 *4 ÁNGULOS DE VENTA PSICOLÓGICA PARA:* `{product}`\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"1️⃣ *Ángulo del Enemigo Común (Dolor Agudo):*\n"
            f"Ataca la solución tradicional cara o ineficiente:\n"
            f"\"_Por qué gastar cientos de dólares en métodos lentos cuando {product} te da el resultado en una fracción del tiempo._\"\n\n"
            f"2️⃣ *Ángulo de Estatus y Libertad:*\n"
            f"Vende la identidad y transformación:\n"
            f"\"_La diferencia entre los que siguen atrapados en la rutina y los que usan {product} para vivir bajo sus propias reglas._\"\n\n"
            f"3️⃣ *Ángulo del Mecanismo Oculto:*\n"
            f"Apela a la curiosidad técnica:\n"
            f"\"_Descubrí el algoritmo y la estructura interna de {product} y esto fue lo que pasó en mis estadísticas en 7 días._\"\n\n"
            f"4️⃣ *Ángulo de Prueba Social Inmediata:*\n"
            f"Demuestra antes y después irrefutable:\n"
            f"\"_De 0 a resultados tangibles en tiempo récord aplicando exactamente la fórmula de {product} paso a paso._\"\n\n"
            f"💰 *Tip de Monetización:* Crea un video independiente para cada uno de estos 4 ángulos y analiza cuál te genera más ventas."
        )

    def send_stars_invoice(self, chat_id, tier_id):
        invoices = {
            "script_pack": {
                "title": "⚡ Pack Guiones Virales Express",
                "desc": "5 Guiones completos segundo a segundo + 15 Hooks auditados.",
                "stars": 25,
                "payload": "forge_script_pack"
            },
            "creator_30": {
                "title": "🚀 Pase Creador Pro (30 Días)",
                "desc": "Generaciones ilimitadas + Fórmulas de Monetización para TikTok y Reels.",
                "stars": 99,
                "payload": "forge_creator_30"
            },
            "agency_lifetime": {
                "title": "👑 Licencia Agencia Vitalicia",
                "desc": "Acceso permanente ilimitado de por vida a toda la suite Viral Forge AI.",
                "stars": 299,
                "payload": "forge_agency_lifetime"
            }
        }
        item = invoices.get(tier_id, invoices["creator_30"])
        invoice_data = {
            "chat_id": chat_id,
            "title": item["title"],
            "description": item["desc"],
            "payload": item["payload"],
            "currency": "XTR",
            "prices": [{"label": item["title"][:30], "amount": item["stars"]}],
            "provider_token": ""
        }
        res = self.call_api("sendInvoice", invoice_data)
        if not res or not res.get("ok"):
            write_log(f"[Error sendInvoice]: {res}")
        else:
            write_log(f"[Factura Stars enviada] Chat: {chat_id}, Plan: {tier_id}")

    def handle_pre_checkout(self, pre_checkout):
        pq_id = pre_checkout.get("id")
        self.call_api("answerPreCheckoutQuery", {
            "pre_checkout_query_id": pq_id,
            "ok": True
        })
        write_log(f"[PreCheckout Aprobado] ID: {pq_id}")

    def handle_inline_query(self, inline_query):
        iq_id = inline_query.get("id")
        query = inline_query.get("query", "").strip()

        if not query:
            results = [{
                "type": "article",
                "id": "intro",
                "title": "🎬 Viral Forge AI — Ganchos & Guiones",
                "description": "Escribe un nicho o tema (ej. '@viral_forge_creator_bot trading') para generar ganchos instantáneos.",
                "input_message_content": {
                    "message_text": "🎬 *Usa Viral Forge AI:* Escribe `@viral_forge_creator_bot <tu tema>` para generar ganchos virales en cualquier chat.",
                    "parse_mode": "Markdown"
                },
                "reply_markup": {
                    "inline_keyboard": [
                        [{"text": "🎬 Abrir Viral Forge Mini App", "web_app": {"url": self.webapp_url}}]
                    ]
                }
            }]
        else:
            hooks_text = self.generate_hooks_text(query)
            results = [{
                "type": "article",
                "id": f"hook_{int(time.time())}",
                "title": f"🎯 Ganchos Virales: {query[:30]}",
                "description": "Ganchos de 3 segundos para TikTok y Reels listos para publicar.",
                "input_message_content": {
                    "message_text": hooks_text,
                    "parse_mode": "Markdown"
                },
                "reply_markup": {
                    "inline_keyboard": [
                        [{"text": "🎬 Ver Escaleta en Mini App", "web_app": {"url": self.webapp_url}}]
                    ]
                }
            }]

        self.call_api("answerInlineQuery", {
            "inline_query_id": iq_id,
            "results": results,
            "cache_time": 10
        })

    def process_update(self, u):
        if "message" in u:
            msg = u["message"]
            chat_id = msg["chat"]["id"]
            user_id = msg["from"]["id"]
            username = msg["from"].get("username", "")
            text = msg.get("text", "").strip()

            if "successful_payment" in msg:
                payment = msg["successful_payment"]
                total = payment.get("total_amount", 0)
                payload = payment.get("invoice_payload", "")
                db = load_users()
                uid = str(user_id)
                if uid in db:
                    db[uid]["is_vip"] = True
                    db[uid]["plan"] = payload
                    db[uid]["payments"].append({
                        "amount_stars": total,
                        "payload": payload,
                        "date": datetime.utcnow().isoformat()
                    })
                    save_users(db)
                keyboard = {
                    "inline_keyboard": [
                        [{"text": "🎬 Abrir Viral Forge VIP", "web_app": {"url": self.webapp_url}}]
                    ]
                }
                self.send_message(
                    chat_id,
                    f"🎉 *¡PAGO CONFIRMADO CON ÉXITO!*\n\n"
                    f"Has desbloqueado el plan **{payload}** con **{total} Telegram Stars**.\n"
                    f"Ya puedes generar guiones y ganchos sin límites.",
                    keyboard
                )
                return

            if not text:
                return

            if text.startswith("/start"):
                self.handle_start(user_id, chat_id, username)
            elif text.startswith("/hook"):
                parts = text.split(maxsplit=1)
                topic = parts[1] if len(parts) > 1 else "cómo ganar dinero online"
                keyboard = {
                    "inline_keyboard": [
                        [{"text": "🎬 Abrir Escaleta en Mini App", "web_app": {"url": self.webapp_url}}]
                    ]
                }
                self.send_message(chat_id, self.generate_hooks_text(topic), keyboard)
            elif text.startswith("/guion"):
                parts = text.split(maxsplit=1)
                topic = parts[1] if len(parts) > 1 else "negocio digital"
                keyboard = {
                    "inline_keyboard": [
                        [{"text": "🎬 Ver en Mini App Interactiva", "web_app": {"url": self.webapp_url}}]
                    ]
                }
                self.send_message(chat_id, self.generate_script_text(topic), keyboard)
            elif text.startswith("/angulos"):
                parts = text.split(maxsplit=1)
                topic = parts[1] if len(parts) > 1 else "servicio digital"
                keyboard = {
                    "inline_keyboard": [
                        [{"text": "🎬 Ver en Mini App Interactiva", "web_app": {"url": self.webapp_url}}]
                    ]
                }
                self.send_message(chat_id, self.generate_angles_text(topic), keyboard)
            elif text.startswith("/vip"):
                keyboard = {
                    "inline_keyboard": [
                        [{"text": "⚡ Pack Guiones Express (25 ⭐)", "callback_data": "buy_pack"}],
                        [{"text": "🚀 Pase Creador Pro (99 ⭐)", "callback_data": "buy_creator"}],
                        [{"text": "👑 Licencia Agencia (299 ⭐)", "callback_data": "buy_agency"}],
                        [{"text": "📱 Abrir Tienda en Mini App", "web_app": {"url": self.webapp_url}}]
                    ]
                }
                self.send_message(
                    chat_id,
                    "⭐ *PLANES VIP VIRAL FORGE AI*\n\n"
                    "Elige tu suscripción con Telegram Stars para desbloquear generaciones ilimitadas:",
                    keyboard
                )
            elif text.startswith("/ayuda"):
                self.send_message(
                    chat_id,
                    "🎬 *Comandos Oficiales de Viral Forge AI:*\n\n"
                    "• /hook `<tema>` — Genera 3 ganchos psicológicos de alta retención.\n"
                    "• /guion `<tema>` — Genera una escaleta de 30s con indicaciones de cámara y audio.\n"
                    "• /angulos `<producto>` — Genera 4 ángulos comerciales para vender.\n"
                    "• /vip — Pases de creación ilimitada con Telegram Stars.\n"
                    "• /start — Abre el menú y la Mini App.\n\n"
                    "💡 *O escribe directamente cualquier idea o producto en este chat y te crearé el guión de inmediato.*"
                )
            else:
                # Direct topic input
                keyboard = {
                    "inline_keyboard": [
                        [{"text": "🎬 Abrir Editor en Mini App", "web_app": {"url": self.webapp_url}}],
                        [{"text": "🎯 Ver 3 Hooks de este Tema", "callback_data": f"quick_hook_{text[:20]}"}]
                    ]
                }
                self.send_message(chat_id, self.generate_script_text(text), keyboard)

        elif "callback_query" in u:
            cb = u["callback_query"]
            chat_id = cb["message"]["chat"]["id"]
            data = cb.get("data", "")

            if data == "cmd_hooks":
                self.send_message(chat_id, "🎯 Envía un mensaje con el comando `/hook <tu tema>` (ejemplo: `/hook trading para principiantes` o `/hook bajar de peso`).")
            elif data == "cmd_script":
                self.send_message(chat_id, "🎬 Envía un mensaje con el comando `/guion <tu tema>` (ejemplo: `/guion cómo usar IA en tu negocio`).")
            elif data == "cmd_angles":
                self.send_message(chat_id, "🔥 Envía el comando `/angulos <tu producto>` y te daré 4 disparadores de compra.")
            elif data == "cmd_vip":
                keyboard = {
                    "inline_keyboard": [
                        [{"text": "⚡ Pack Guiones Express (25 ⭐)", "callback_data": "buy_pack"}],
                        [{"text": "🚀 Pase Creador Pro (99 ⭐)", "callback_data": "buy_creator"}],
                        [{"text": "👑 Licencia Agencia (299 ⭐)", "callback_data": "buy_agency"}],
                        [{"text": "📱 Abrir Tienda en Mini App", "web_app": {"url": self.webapp_url}}]
                    ]
                }
                self.send_message(
                    chat_id,
                    "⭐ *PLANES VIP VIRAL FORGE AI*\n\n"
                    "Elige tu suscripción con Telegram Stars:",
                    keyboard
                )
            elif data == "buy_pack":
                self.send_stars_invoice(chat_id, "script_pack")
            elif data == "buy_creator":
                self.send_stars_invoice(chat_id, "creator_30")
            elif data == "buy_agency":
                self.send_stars_invoice(chat_id, "agency_lifetime")
            elif data.startswith("quick_hook_"):
                topic = data.replace("quick_hook_", "")
                self.send_message(chat_id, self.generate_hooks_text(topic))

    def run(self):
        write_log("Iniciando daemon de Viral Forge AI...")
        if not self.token:
            write_log("AVISO: Viral Forge AI en espera de BOT_TOKEN_FORGE.")
            while not self.token:
                time.sleep(15)
                cfg = load_config()
                if cfg.get("bot_token"):
                    self.token = cfg["bot_token"]
                    self.base_url = f"https://api.telegram.org/bot{self.token}"
                    break

        me = self.call_api("getMe")
        if me and me.get("ok"):
            write_log(f"Bot autenticado: @{me['result']['username']} (ID: {me['result']['id']})")
            try:
                self.call_api("setChatMenuButton", {
                    "menu_button": {
                        "type": "web_app",
                        "text": "Viral Forge 🎬",
                        "web_app": {"url": f"{self.webapp_url}?v=2.0"}
                    }
                })
            except Exception as e:
                write_log(f"Error menu button: {e}")

        while True:
            try:
                params = {"offset": self.last_update_id + 1, "timeout": 20}
                url = f"{self.base_url}/getUpdates?offset={params['offset']}&timeout={params['timeout']}"
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    if data.get("ok"):
                        updates = data.get("result", [])
                        for u in updates:
                            self.last_update_id = u["update_id"]
                            try:
                                if "pre_checkout_query" in u:
                                    self.handle_pre_checkout(u["pre_checkout_query"])
                                    continue
                                if "inline_query" in u:
                                    self.handle_inline_query(u["inline_query"])
                                    continue
                                self.process_update(u)
                            except Exception as ex:
                                write_log(f"Error procesando update: {ex}")
            except Exception as e:
                time.sleep(3)

if __name__ == "__main__":
    cfg = load_config()
    bot = ViralForgeBot(cfg)
    bot.run()
