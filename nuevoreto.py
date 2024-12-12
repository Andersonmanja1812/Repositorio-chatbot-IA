from fastapi import FastAPI
from pydantic import BaseModel
from NaiveBayes import NaiveBayes
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import unicodedata
import string
import random

# Diccionario actualizado con frases y respuestas más completas
categorias_actualizadas = {
    "saludo": {
        "frases": [
            "hola", "buenos dias", "buenas tardes", "buenas noches", 
            "qué tal", "cómo estás", "hey", "holi", "saludos"
        ],
        "respuestas": [
            "¡Hola! ¿Cómo puedo ayudarte hoy?",
            "Hola, es un gusto saludarte.",
            "¡Hola! Espero que tengas un excelente día.",
            "Buenos días, ¿en qué puedo asistirte?",
            "Buenas tardes, ¿cómo te ayudo hoy?",
            "Buenas noches, espero que estés teniendo un buen día."
        ]
    },
    "despedida": {
        "frases": [
            "adios", "chao", "hasta luego", "nos vemos", "bye", 
            "hasta pronto", "que estés bien", "me despido", "hasta mañana"
        ],
        "respuestas": [
            "Adiós, ¡que tengas un excelente día!",
            "Hasta luego, fue un placer atenderte.",
            "Nos vemos pronto, ¡cuídate mucho!",
            "Gracias por tu visita, que estés muy bien.",
            "Hasta mañana, ¡te esperamos de nuevo!"
        ]
    },
    "precio": {
        "frases": [
            "precio", "cuánto cuesta", "cuánto vale", "cuánto es", "valor", 
            "cuánto cuesta el producto", "cuál es el precio del servicio",
            "tarifa", "coste", "importe", "precio total"
        ],
        "respuestas": [
            "Los precios varían según el producto o servicio. ¿Hay algo específico que te interese?",
            "Por favor, indícanos el modelo o servicio para brindarte más información sobre el precio.",
            "El precio depende de las características. ¿Podrías ser más específico?",
            "Tenemos varios rangos de precios. Cuéntame qué necesitas y te ayudaré."
        ]
    },
    "modelo1": {
        "frases": [
            "basico", "intermedio", "avanzado", 
            "modelo básico", "modelo intermedio", "modelo avanzado"
        ],
        "respuestas": [
            "El modelo básico cuesta 300,000 pesos, el intermedio 400,000 pesos, y el avanzado 500,000 pesos. ¿Cuál prefieres?",
            "Para el modelo uno, el precio es de 300,000 pesos en básico, 400,000 pesos en intermedio y 500,000 pesos en avanzado.",
            "Elige entre básico (300,000), intermedio (400,000) o avanzado (500,000). ¿Cuál se ajusta a lo que buscas?"
        ]
    },
    "modelo2": {
        "frases": [
            "xl plus", "xl lite", "xl pro", 
            "modelo xl plus", "modelo xl lite", "modelo xl pro"
        ],
        "respuestas": [
            "El modelo XL Plus cuesta 400,000 pesos, el XL Lite 500,000 pesos y el XL Pro 600,000 pesos.",
            "Para el modelo XL, el precio varía según la versión: Plus (400,000), Lite (500,000) y Pro (600,000).",
            "Los modelos XL están disponibles en tres versiones: Plus, Lite y Pro. Cuéntame cuál te interesa."
        ]
    },
    "informacion_contacto": {
        "frases": [
            "cómo puedo contactarlos", "cuál es el número de teléfono", 
            "contacto", "email", "correo electrónico", "teléfono de contacto",
            "número para llamar", "cómo los contacto", "información de contacto"
        ],
        "respuestas": [
            "Puedes contactarnos al teléfono 123-456-7890 o al correo contacto@empresa.com.",
            "Nuestro número de contacto es 123-456-7890 y nuestro correo electrónico es contacto@empresa.com.",
            "Estamos disponibles en el 123-456-7890 o por correo en contacto@empresa.com. ¡Escríbenos!"
        ]
    },
    "horario_atencion": {
        "frases": [
            "cuál es el horario de atención", "en qué días están abiertos", 
            "cuál es su horario", "qué días trabajan", "horas de atención",
            "horario laboral", "a qué hora abren", "cuándo están disponibles"
        ],
        "respuestas": [
            "Nuestro horario de atención es de lunes a viernes, de 9:00 AM a 6:00 PM.",
            "Estamos abiertos de lunes a viernes de 9:00 AM a 6:00 PM. ¿En qué día planeas visitarnos?",
            "Puedes visitarnos de lunes a viernes en horario laboral, de 9:00 AM a 6:00 PM."
        ]
    },
    "politica_devolucion": {
        "frases": [
            "cuál es la política de devoluciones", "puedo devolver el producto", 
            "cómo devuelvo", "devoluciones", "tienen devoluciones", 
            "cómo funcionan las devoluciones", "regresar un producto",
            "quiero devolver algo"
        ],
        "respuestas": [
            "Nuestra política permite devoluciones dentro de los 30 días posteriores a la compra, siempre que el producto esté en su estado original.",
            "Puedes devolver el producto dentro de los 30 días, con su empaque original y factura.",
            "Aceptamos devoluciones en los primeros 30 días. Por favor, asegúrate de que el producto esté en buenas condiciones."
        ]
    },
    "soporte_tecnico": {
        "frases": [
            "tengo un problema técnico", "cómo solucionar un error", 
            "problema técnico", "soporte técnico", "error", 
            "mi producto no funciona", "necesito ayuda con un problema",
            "fallo técnico", "problema con el dispositivo", "no funciona"
        ],
        "respuestas": [
            "Para problemas técnicos, puedes contactarnos al 123-456-7890 o escribirnos a soporte@empresa.com.",
            "Visita nuestra página de soporte en www.empresa.com/soporte para guías de solución de problemas.",
            "Si necesitas ayuda con un error, contáctanos al 123-456-7890. Estamos aquí para ayudarte."
        ]
    },
    "garantias": {
        "frases": [
            "cuánto tiempo de garantía tiene el producto", "garantía del producto",
             "qué cubre la garantía", "mi producto tiene garantía", "cómo usar la garantía",
            "cómo hago válida la garantía", "tiempo de garantía"
        ],
        "respuestas": [
            "Nuestros productos cuentan con una garantía de 12 meses desde la fecha de compra.",
            "La garantía cubre defectos de fabricación, pero no daños causados por uso indebido.",
            "Si deseas hacer válida la garantía, debes presentar el producto con su factura de compra.",
            "Para más detalles sobre lo que cubre la garantía, consulta nuestro sitio web o comunícate con soporte.",
            "Recuerda que nuestra garantía no cubre daños accidentales o por uso inadecuado."
        ]
    }
}

# Función para normalizar texto
def normalizar_texto(texto):
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    texto = texto.lower().translate(str.maketrans('', '', string.punctuation))
    return texto.strip()

# Crear un mapeo de categorías a sus frases
frases_por_categoria = {
    categoria: [normalizar_texto(frase) for frase in datos["frases"]]
    for categoria, datos in categorias_actualizadas.items()
}

# Combinar todas las frases y categorías para vectorización
frases_totales = [
    frase for frases in frases_por_categoria.values() for frase in frases
]
categorias_totales = [
    categoria for categoria, frases in frases_por_categoria.items() for _ in frases
]

# Vectorización con TfidfVectorizer
vectorizador = TfidfVectorizer()
X = vectorizador.fit_transform(frases_totales)  # Matriz TF-IDF de frases

# Crea una instancia de FastAPI
app = FastAPI()
app.title = "Mi aplicación con FastAPI (c) Anderson - Nelson - LuisFer - Valentina - Jorge - Neiver"
app.version = "2.0.0"

@app.get("/")
def read_root():
    return {"message": "Bienvenido a clasificador de FastAPI y TF-IDF (@) Anderson - Nelson - LuisFer - Valentina - Jorge - Neiver"}

# Modelo para entrada de datos
class FraseEntrada(BaseModel):
    frase: str

# Clasificar frase basada en similitud
def clasificar_frase_vectorizada(frase):
    frase_normalizada = normalizar_texto(frase)
    vector_frase = vectorizador.transform([frase_normalizada])  # Vectorizar la frase
    similitudes = cosine_similarity(vector_frase, X)  # Calcular similitudes
    indice_max = similitudes.argmax()  # Índice del vector más similar
    categoria = categorias_totales[indice_max]  # Categoría asociada
    return categoria

# Endpoint del chatbot
@app.post("/chatbot/")
def obtener_respuesta(entrada: FraseEntrada):
    categoria = clasificar_frase_vectorizada(entrada.frase)
    if categoria not in categorias_actualizadas:
        return {"respuesta": "Lo siento, no entendí tu solicitud. ¿Puedes ser más específico?"}

    # Seleccionar una respuesta aleatoria de la categoría detectada
    respuesta = random.choice(categorias_actualizadas[categoria]["respuestas"])
    return {"respuesta": respuesta}
