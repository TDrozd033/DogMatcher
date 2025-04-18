import google.generativeai as genai
import pandas as pd
import os
import requests
import re
from dotenv import load_dotenv
from prompts import *

"""
# Dostosowanie bazy do projektu

df = pd.read_csv('akc-data-latest.csv')
df = df.drop(columns=["popularity"])
df = df.dropna()
df['avg_weight'] = (df['min_weight'] + df['max_weight']) / 2
df = df[df['avg_weight'] != 0]
df = df.drop(columns=['group', 'min_height', 'max_height', 'min_weight', 'max_weight', 'min_expectancy', 'max_expectancy'])
df = df.loc[:, ~df.columns.str.contains('category')]
df.to_csv('dog_breeds.csv', index=False)
"""

# Wczytanie bazy danych
dogs = pd.read_csv('dog_breeds.csv')

# Konfiguracja kluczy API
load_dotenv()
google_api_key = os.getenv('GOOGLE_API_KEY')
dog_api_key = os.getenv('DOG_API_KEY')

# Konfiguracja Gemini
genai.configure(api_key=google_api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

def interpret_input(user_input, prompt_temp):
    """
    Uniwersalny interpreter zapytań użytkownika
    """
    prompt = prompt_temp.format(user_input=user_input)
    try:
        response = model.generate_content(contents=prompt)
        result =  response.text.strip()
        if result == "0":
            print("Twoja odpowiedź była niejasna.")
            user_input = input("Odpowiedz bardziej szczegółowo: ")
            prompt = prompt_temp.format(user_input=user_input)
            response = model.generate_content(contents=prompt)
            result = response.text.strip()
        return result
    
    except Exception as e:
        return "0"

def filter_weight(user_input, data):
    """
    Filtracja według wielkości
    """
    options = interpret_input(user_input, WEIGHT_PROMPT).split(",")
    filtered = pd.DataFrame()
    
    if "1" in options:
        filtered = pd.concat([filtered, data[data['avg_weight'] < 10]])
    if "2" in options:
        filtered = pd.concat([filtered, data[(data['avg_weight'] >= 10) & (data['avg_weight'] <= 25)]])
    if "3" in options:
        filtered = pd.concat([filtered, data[data['avg_weight'] > 25]])

    return filtered if not filtered.empty else None

def filter_grooming(user_input, data):
    """
    Filtracja według częstotliwości pielęgnacji
    """
    options = float(re.sub(r"[^\d.]", "", interpret_input(user_input, GROOMING_PROMPT)))
    filtered = data[data['grooming_frequency_value'] <= options]
    return filtered if not filtered.empty else None

def filter_shedding(user_input, data):
    """
    Filtracja według linienia
    """
    options = float(re.sub(r"[^\d.]", "", interpret_input(user_input, SHEDDING_PROMPT)))
    filtered = data[data['shedding_value'] <= options]
    return filtered if not filtered.empty else None

def filter_energy(user_input, data):
    """
    Filtracja według zapotrzebowania energetycznego
    """
    options = float(re.sub(r"[^\d.]", "", interpret_input(user_input, ENERGY_PROMPT)))
    filtered = data[data['energy_level_value'] <= options]
    return filtered if not filtered.empty else None

def filter_trainability(user_input, data):
    """
    Filtracja według podatności na tresurę
    """
    options = float(re.sub(r"[^\d.]", "", interpret_input(user_input, TRAINABILITY_PROMPT)))
    filtered = data[data['trainability_value'] >= options]
    return filtered if not filtered.empty else None

def filter_demeanor(user_input, data):
    """
    Filtracja według postawy w stosunku do obcych
    """
    options = float(re.sub(r"[^\d.]", "", interpret_input(user_input, DEMEANOR_PROMPT)))
    filtered = data[data['demeanor_value'] >= options]
    return filtered if not filtered.empty else None

def filter_temperament(user_input, data):
    """
    Filtracja według temperamentu
    """
    prompt_data = data[['breeds', 'temperament']].to_json(orient='records')
    prompt = TEMPERAMENT_PROMPT.format(user_input=user_input, prompt_data=prompt_data)
    
    try:
        response = model.generate_content(contents=prompt)
        response = response.text.strip()
        filtered = data[data['breeds'] == response]
        return filtered if not filtered.empty else None
    except Exception as e:
        print(f"Błąd podczas interpretacji zapytania: {e}")
        return None

def translate_description(text):
    """
    Tłumaczenie opisu
    """
    prompt = TRANSLATE_PROMPT.format(text=text)
    try:
        response = model.generate_content(contents=prompt)
        translated_text = response.text.strip()
        return translated_text
    except Exception as e:
        print(f"Błąd podczas tłumaczenia opisu: {e}")
        return text

def get_dog_image(name):
    """
    Pobranie zdjęć po API
    """
    search_url = f"https://api.thedogapi.com/v1/breeds/search?q={name}"
    headers = {"x-api-key": dog_api_key}
    response = requests.get(search_url, headers=headers)
    
    if response.status_code == 200 and response.json():
        breed_id = response.json()[0]["id"]
        image_url = f"https://api.thedogapi.com/v1/images/search?breed_ids={breed_id}&limit=1"
        image_response = requests.get(image_url, headers=headers)
        
        if image_response.status_code == 200 and image_response.json():
            return image_response.json()[0]["url"]
        else:
            return None
    else:
        return None

filters = [
    ("Jaki rozmiar psa najlepiej by Ci odpowiadał?", filter_weight),
    ("Jak często możesz zajmować się pielęgnacją swojego zwierzaka?", filter_grooming),
    ("Jak często może linieć Twój idealny pies?", filter_shedding),
    ("Jak aktywny powinien być Twój pies?", filter_energy),
    ("Jakie są Twoje oczekiwania wobec podatności psa na tresurę?", filter_trainability),
    ("Jaki sposób zachowania psa wobec obcych najlepiej by Ci odpowiadał?", filter_demeanor),
    ("Jakie cechy charakteru psa są dla Ciebie najważniejsze?", filter_temperament)
]

def process_user_input(user_answers):
    """ Przetwarza odpowiedzi użytkownika i zwraca wynik. """
    filtered_dogs = dogs.copy()
    print("Rozpoczynanie filtrowania psów.")

    # Iteracja przez filtry
    for i, (question, filter_func) in enumerate(filters):
        print(f"Przetwarzanie pytania {i + 1}: {question}")
        filtered_dogs = filter_func(user_answers[i], filtered_dogs)

        # Sprawdzanie, czy filtr zwrócił None
        if filtered_dogs is None:
            print(f"Brak wyników po filtrze {i + 1}: {question}")
            print("Zwracamy: None, None")
            return None, None  # 1. return None, None  

    # Sprawdzanie, czy po filtracji są jakiekolwiek psy
    if filtered_dogs is not None and not filtered_dogs.empty:
        breed = filtered_dogs.iloc[0]["breeds"]
        description = filtered_dogs.iloc[0]["description"]
        translated_description = translate_description(description)
        print(f"\nNajlepiej dobrana rasa psa dla Ciebie to {breed}!\n")
        print(translated_description)
        
        # Pobieranie zdjęcia psa
        image_url = get_dog_image(breed)
        print(f"Obrazek dla {breed}: {image_url}")

        print("Zwracamy: breed, translated_description, image_url")
        return breed, translated_description, image_url  # 2. return breed, translated_description, image_url
    
    # Jeśli nie ma wyników po filtrach
    print("Brak psów po przejściu wszystkich filtrów.")
    print("Zwracamy: None, None")
    return None, None, None  # 3. return None, None, None

