# Integración con un LLM (modelo de lenguaje) para resumir las reseñas de un producto.
#
# Se usa el formato "Chat Completions" de OpenAI, que hoy es un estándar de facto:
# lo aceptan OpenAI, Groq, OpenRouter y también Ollama (que corre modelos gratis en tu PC).
# La petición se hace con urllib (librería estándar) para no sumar dependencias.
import json
import urllib.request
import urllib.error
from flask import current_app

PROMPT_SISTEMA = (
    "Sos el asistente de una rotisería. Recibís reseñas de clientes sobre un producto "
    "y escribís un resumen breve en español rioplatense (máximo 3 oraciones): "
    "qué destacan, qué critican y una conclusión. No inventes datos que no estén en las reseñas."
)


def resumir_resenas(nombre_producto, resenas):
    """Devuelve {'resumen': str, 'fuente': 'llm' | 'estadistico'}.

    Si el LLM está deshabilitado o falla, arma un resumen estadístico para que
    la funcionalidad nunca deje de responder (degradación elegante).
    """
    if not resenas:
        return {'resumen': 'Este producto todavía no tiene reseñas.', 'fuente': 'estadistico'}

    if current_app.config.get('LLM_ENABLED'):
        try:
            texto = _consultar_llm(nombre_producto, resenas)
            if texto:
                return {'resumen': texto.strip(), 'fuente': 'llm'}
        except (urllib.error.URLError, TimeoutError, KeyError, ValueError) as error:
            current_app.logger.warning(f'LLM no disponible, se usa resumen estadístico: {error}')

    return {'resumen': _resumen_estadistico(resenas), 'fuente': 'estadistico'}


def _consultar_llm(nombre_producto, resenas):
    # 1) Armar el prompt con las reseñas (máximo 30 para no exceder el contexto)
    lineas = [f"- {r.puntuacion}/5: {r.comentario or '(sin comentario)'}" for r in resenas[:30]]
    prompt_usuario = f"Producto: {nombre_producto}\nReseñas:\n" + "\n".join(lineas)

    # 2) Cuerpo de la petición en formato Chat Completions
    cuerpo = {
        'model': current_app.config['LLM_MODEL'],
        'messages': [
            {'role': 'system', 'content': PROMPT_SISTEMA},
            {'role': 'user', 'content': prompt_usuario}
        ],
        'temperature': 0.3,   # baja = respuestas más estables y menos "creativas"
        'max_tokens': 200
    }
    headers = {'Content-Type': 'application/json'}
    if current_app.config.get('LLM_API_KEY'):
        headers['Authorization'] = 'Bearer ' + current_app.config['LLM_API_KEY']

    # 3) POST HTTP a la API del proveedor
    peticion = urllib.request.Request(
        current_app.config['LLM_API_URL'],
        data=json.dumps(cuerpo).encode('utf-8'),
        headers=headers,
        method='POST'
    )
    with urllib.request.urlopen(peticion, timeout=current_app.config['LLM_TIMEOUT']) as respuesta:
        datos = json.loads(respuesta.read().decode('utf-8'))

    # 4) La respuesta del modelo viene en choices[0].message.content
    return datos['choices'][0]['message']['content']


def _resumen_estadistico(resenas):
    puntajes = [r.puntuacion for r in resenas]
    promedio = sum(puntajes) / len(puntajes)
    positivas = sum(1 for p in puntajes if p >= 4)
    negativas = sum(1 for p in puntajes if p <= 2)
    texto = (f"{len(puntajes)} reseña(s) con un promedio de {promedio:.1f} estrellas: "
             f"{positivas} positiva(s) y {negativas} negativa(s).")
    comentarios = [r.comentario.strip() for r in resenas if r.comentario and r.comentario.strip()]
    if comentarios:
        texto += f' Comentario más reciente: "{comentarios[-1][:120]}".'
    return texto
