import re
import string
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
from transformers import pipeline

nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('wordnet')

def limpiar_texto(texto):
    texto = re.sub(r'[¡¿]', '', texto)
    texto = re.sub(r'[–\"“”‘’]', ' ', texto)
    texto = texto.replace("\n", " ")
    texto = texto.replace("…", ".")
    texto = texto.replace("−", "")
    texto = texto.strip() 
    return texto

def separar_oraciones(texto):
    texto = texto.lower()
    texto_limpio = limpiar_texto(texto)
    oraciones = sent_tokenize(texto_limpio)
    oraciones = [oracion.translate(str.maketrans('', '', string.punctuation)) for oracion in oraciones]
    return oraciones

def preprocesar_texto(texto):
    oraciones = separar_oraciones(texto)
    palabras = [word_tokenize(oracion) for oracion in oraciones]
    lematizador = WordNetLemmatizer()
    palabras_lematizadas = [
        [lematizador.lemmatize(palabra) for palabra in palabra_lista]
        for palabra_lista in palabras
    ]
    return oraciones, palabras_lematizadas

model_path = "daveni/twitter-xlm-roberta-emotion-es"
emotion_analysis = pipeline("text-classification", framework="pt", model=model_path, tokenizer=model_path)

def analizar_emociones(texto):
    oraciones, texto_procesado = preprocesar_texto(texto)
    emociones_por_oracion = []

    for i, oracion in enumerate(texto_procesado): 
        texto_oracion = ' '.join(oracion)
        emociones = emotion_analysis(texto_oracion)
        emociones_por_oracion.append({"oracion": oraciones[i], "emocion": emociones[0]['label'], "intensidad": emociones[0]['score']})

    return emociones_por_oracion