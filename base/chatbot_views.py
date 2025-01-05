from pathlib import Path
import nltk
import random
import json
import pickle
import numpy as np
import os
from django.http import JsonResponse
from django.shortcuts import render
from tensorflow.keras.models import load_model
from nltk.stem import WordNetLemmatizer

BASE_DIR = Path(__file__).resolve().parent.parent
models_dir = os.path.join(BASE_DIR, 'base', 'model')
print("Ścieżka do modelu:", os.path.join(models_dir, 'chatbot_model_polish.h5'))

nltk.download('popular')
nltk.download('punkt')
nltk.download('punkt_tab')

lemmatizer = WordNetLemmatizer()

model_ = load_model(os.path.join(models_dir, 'chatbot_model_polish.h5'))
intents = json.loads(open(os.path.join(models_dir, 'intents.json')).read())
words = pickle.load(open(os.path.join(models_dir, 'slowa.pkl'), 'rb'))
classes = pickle.load(open(os.path.join(models_dir, 'klasy.pkl'), 'rb'))


def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words


def bow(sentence, words, show_details=True):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
                if show_details:
                    print(f"found in bag: {w}")
    return np.array(bag)


def predict_class(sentence, model_):
    p = bow(sentence, words, show_details=False)
    res = model_.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = [{"intent": classes[r[0]], "probability": str(r[1])} for r in results]
    return return_list


def getResponse(ints, intents_json):
    if ints:
        tag = ints[0]['intent']
    else:
        return JsonResponse({'response': 'Sorry, I didn\'t understand that.'})
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            break
    return result


def chatbot_response(request):
    if request.method == "POST":
        message = request.POST.get('message', '')
        if message:
            ints = predict_class(message, model_)
            if not ints:
                return JsonResponse({"response": 'Niestety nie znam odpowiedzi na to pytanie.'})
            response = fix_polish_chars(str(getResponse(ints, intents)))
            return JsonResponse({"response": response})
    return render(request, 'base/chatbot.html')


def fix_polish_chars(text):
    corrections = {
        "Ăł": "ó",
        "Ä…": "ą",
        "ĹĽ": "ż",
        "Ĺ›": "ś",
        "Ä‡": "ć",
        "Ä™": "ę",
        "Ă‡": "Ć",
        'Ĺ‚': 'ł',
        'Ĺş': 'ź',
    }

    for wrong, right in corrections.items():
        text = text.replace(wrong, right)

    return text
