import re

def generate_ssml(text_data, voice="es-MX-DaliaNeural", role="Girl"):
    sentence = text_data["sentence"]
    emotion = text_data["emotion"]
    intensity = text_data["intensity"]

    if emotion == "joy" or emotion == "sadness":
        style, intensity_val = get_style(emotion, intensity)
        sentence = f"""
        <mstts:express-as role="{role}" style="{style}" styledegree="{intensity_val}">
            {sentence}
        </mstts:express-as>
        """
    else:
        if emotion != "others":
            word_count = len(sentence.split())
            contour = get_contour_by_emotion(emotion, word_count)
            prosody = get_prosody_by_emotion(emotion)
            sentence = process_emotion_with_pauses(sentence, emotion)
            sentence = apply_intonation(sentence, emotion)
            if contour:
                sentence = f"""
                <prosody rate="{prosody['rate']}" volume="{prosody['volume']}" contour="{contour}">
                    {sentence}
                </prosody>
                """
            else:
                sentence = f"""
                <prosody rate="{prosody['rate']}" pitch="{prosody['pitch']}" volume="{prosody['volume']}">
                    {sentence}
                </prosody>
                """
        sentence = f"""
        <mstts:express-as role="{role}">
            {sentence}
        </mstts:express-as>
        """

    ssml = f"""
    <speak xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" version="1.0" xml:lang="es-MX">
        <voice name="{voice}">
            {sentence} <break time='200ms'/>
        </voice>
    </speak>
    """
    return ssml.strip()

def get_style(emotion, intensity):
    styles = {
        "joy": "cheerful",
        "sadness": "sad"
    }
    style = styles.get(emotion, None)
    if style:
        styledegree = 0.01 + (intensity * (2.0 - 0.01))
        return style, round(styledegree, 3)
    return None, None
    
def get_contour_by_emotion(emocion, longitud_texto):
    """
    Devuelve el contorno (contour) de la prosodia para cada emoción,
    ajustando entre sin contorno, contorno simple y contorno complejo
    según la longitud del texto.
    """
    if longitud_texto <= 5:
        # Sin contorno para textos muy cortos
        return None
    
    contornos_por_emocion = {
        "joy": {
            "simple": "(0%,+10%) (100%,+30%)",
            "complejo": "(0%,+10%) (50%,+20%) (100%,+30%)"
        },
        "sadness": {
            "simple": "(0%,-10%) (100%,-30%)",
            "complejo": "(0%,-10%) (50%,-20%) (100%,-30%)"
        },
        "fear": {
            "simple": "(0%,+15%) (100%,-10%)",
            "complejo": "(0%,+15%) (30%,+5%) (60%,-5%) (100%,-10%)"
        },
        "anger": {
            "simple": "(0%,+10%) (100%,+20%)",
            "complejo": "(0%,+10%) (50%,+15%) (100%,+20%)"
        },
        "others": {
            "simple": "(0%,0%) (100%,0%)",
            "complejo": "(0%,0%) (50%,0%) (100%,0%)"
        },
        "disgust": {
            "simple": "(0%,-5%) (100%,-15%)",
            "complejo": "(0%,-5%) (50%,-10%) (100%,-15%)"
        },
        "surprise": {
            "simple": "(0%,+20%) (100%,+25%)",
            "complejo": "(0%,+20%) (50%,+22%) (100%,+25%)"
        }
    }

    # Seleccionar el contorno según la longitud del texto
    if 5 < longitud_texto <= 10:
        return contornos_por_emocion.get(emocion, {}).get("simple")

    return contornos_por_emocion.get(emocion, {}).get("complejo")

def get_prosody_by_emotion(emocion):
    """
    Devuelve los ajustes de prosodia (rate, pitch, volume) según la emoción.
    Cambios sutiles en pitch para mantener coherencia de la voz.
    """
    configuraciones = {
        "joy": {"rate": "1.3", "pitch": "high", "volume": "loud"},
        "sadness": {"rate": "0.7", "pitch": "low", "volume": "x-soft"},
        "fear": {"rate": "1.2", "pitch": "high", "volume": "soft"},
        "anger": {"rate": "1.1", "pitch": "low", "volume": "loud"},
        "others": {"rate": "1.0", "pitch": "medium", "volume": "medium"},
        "disgust": {"rate": "1.0", "pitch": "low", "volume": "medium"},
        "surprise": {"rate": "1.1", "pitch": "high", "volume": "loud"},
    }
    return configuraciones.get(emocion, configuraciones["others"])

def process_emotion_with_pauses(texto, emocion):
    """
    Procesa el texto para emociones con pausas o efectos temblorosos.
    """
    palabras = texto.split()
    brake = None

    if emocion == "fear":
        # Dividir en segmentos por comas
        #segmentos = texto.split(",")
        #resultado = []

        #for segmento in segmentos:
        #    palabras = segmento.strip().split()
        #    temblorosas = [
        #        aplicar_efecto_tembloroso(palabras[i]) if i < 2 else palabras[i]
        #        for i in range(len(palabras))
        #    ]
            # Pausa corta entre palabras para miedo
            #resultado.append(" ".join([f"{palabra} <break time='300ms'/>" for palabra in temblorosas[:-1]] + [temblorosas[-1]]))

        #return ", ".join(resultado)
        return " ".join([f"{palabra} <break time='200ms'/>" for palabra in palabras[:-1]] + [palabras[-1]])


    elif emocion == "disgust":
        resultado = []

        for i, palabra in enumerate(palabras):
            if i == 0 or len(palabra) < 3:
                resultado.append(palabra)
            else:
                resultado.append(f"<break time='200ms'/> {palabra}")

        return " ".join(resultado)

    else:
        return texto
    #despues de las comas

def aplicar_efecto_tembloroso(palabra):
    """
    Aplica el efecto tembloroso repitiendo la primera vocal o sílaba.
    """
    # Detectar si la palabra ya tiene el efecto tembloroso
    if re.match(r"^([a-záéíóúñ]+-){2,}[a-záéíóúñ]+$", palabra, re.IGNORECASE):
        return palabra  # Ya tiene el efecto, no modificar

    if len(palabra) <= 2 or re.match(r"^[^aeiouáéíóú]*[aeiouáéíóú]+$", palabra, re.IGNORECASE):
        # Comienza con vocal
        letra = palabra[0]
        return f"{letra} <break time='50ms'/> {letra} <break time='50ms'/> {letra} <break time='50ms'/> {palabra}"

    else:
        # Comienza con consonante
        silaba = re.match(r"^[^aeiouáéíóú]*[aeiouáéíóú]+", palabra, re.IGNORECASE)
        if silaba:
            silaba = silaba.group()
            return f"{silaba} <break time='50ms'/> {silaba} <break time='50ms'/> {silaba} <break time='50ms'/> {palabra}"

    return palabra

def apply_intonation(texto, emocion):
    """
    Aplica reglas específicas de entonación según la emoción.
    """
    palabras = texto.split()

    if emocion == "anger":
        # Enojo: Fuerza en toda la oración
        return f"<emphasis level='strong'>{texto}</emphasis>"

    elif emocion == "disgust":
        # Disgusto: Fuerza en la última palabra
        palabras[-1] = f"<emphasis level='strong'>{palabras[-1]}</emphasis>"
        return " ".join(palabras)

    # Otras emociones no requieren entonación especial
    return texto