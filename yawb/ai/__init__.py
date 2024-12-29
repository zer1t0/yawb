
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import nltk
from nltk.stem.wordnet import WordNetLemmatizer

import pickle
import re
import string

from .html_text_extraction import extract_title_and_texts_from_html
from .json_text_extraction import extract_texts_from_json
from .xml_text_extraction import extract_texts_from_xml
from .text_extraction import extract_text

model = None
vectorizer = None

def classify_response(resp):
    if not model:
        load_model_and_vectorizer()

    content_type = resp.headers.get('content-type', "/")
    body = resp.content

    text = extract_text(content_type, body)
    text_tokens = tokenize(text)
    clean_tokens = list(clean_term_sentence(text_tokens))
    X = vectorizer.transform([" ".join(clean_tokens)])
    return model.predict(X)[0]

def load_model_and_vectorizer():
    global model
    global vectorizer
    
    model = load_model()
    vectorizer = load_tfidf_vectorizer()

def load_tfidf_vectorizer():
    with open("models/tfidf.pickle", "rb") as fi:
        return pickle.load(fi)

def load_model():
    with open("models/svc.pickle", "rb") as fi:
        return pickle.load(fi)

def tokenize(text):
    return nltk.word_tokenize(text.lower())

def is_token_just_word(token):
    return re.match("^[a-z'_]+$", token)

def is_token_stop_word(token):
    if "not" in token \
        or "n't" in token:
        return False
    
    return token in stopwords

def token_is_punctuation(token):
    for c in token:
        if c not in string.punctuation:
            return False
    return True

def clean_term_sentence(ts):
    for token in ts:
        token = token.strip()
        token = token.replace("’", "'")
        if token and not token_is_punctuation(token) \
            and is_token_just_word(token):
            yield WordNetLemmatizer().lemmatize(token)
