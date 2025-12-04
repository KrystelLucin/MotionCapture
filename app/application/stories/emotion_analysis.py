import re
import string
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
from transformers import pipeline

nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

def clean_text(text):
    text = re.sub(r'[¡¿]', '', text)
    text = re.sub(r'[–\"“”‘’]', ' ', text)
    text = text.replace("\n", " ")
    text = text.replace("…", ".")
    text = text.replace("−", "")
    text = text.strip()
    return text

def split_sentences(text):
    text = text.lower()
    clean = clean_text(text)
    sentences = sent_tokenize(clean)
    sentences = [sentence.translate(str.maketrans('', '', string.punctuation)) for sentence in sentences]
    return sentences

def preprocess_text(text):
    sentences = split_sentences(text)
    words = [word_tokenize(sentence) for sentence in sentences]
    lemmatizer = WordNetLemmatizer()
    lemmatized_words = [[lemmatizer.lemmatize(word) for word in word_list] for word_list in words]
    return sentences, lemmatized_words

model_path = "daveni/twitter-xlm-roberta-emotion-es"
emotion_analysis = pipeline("text-classification", framework="pt", model=model_path, tokenizer=model_path)

def analyze_emotions(text):
    sentences, processed_text = preprocess_text(text)
    emotions_per_sentence = []

    for i, sentence in enumerate(processed_text):
        sentence_text = ' '.join(sentence)
        emotions = emotion_analysis(sentence_text)
        emotions_per_sentence.append({
            "sentence": sentences[i],
            "emotion": emotions[0]['label'],
            "intensity": emotions[0]['score']
        })

    return emotions_per_sentence