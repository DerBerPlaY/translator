import flet as ft
from pymorphy2 import MorphAnalyzer
from rapidfuzz import process
import os
import json
from rapidfuzz import process

def find_component(self, lemmas, dictionary):
    for lemma in lemmas:
        if lemma in dictionary:
            return {'ru': lemma, 'en': dictionary[lemma]}
        # Попробуем найти ближайшее совпадение
        match = process.extractOne(lemma, dictionary.keys(), score_cutoff=80)
        if match:
            best_match = match[0]
            return {'ru': best_match, 'en': dictionary[best_match]}
    return None

import flet as ft

class DictionaryManager:
    def __init__(self):
        self.nouns = self.load_dictionary("nouns.json")
        self.verbs = self.load_dictionary("verbs.json")
        self.pronouns = self.load_dictionary("pronouns.json")
        self.irregular_verbs = self.load_dictionary("irregular_verbs.json")

    @staticmethod
    def load_dictionary(file_name):
        base_path = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_path, "data", file_name)
        with open(data_path, "r", encoding="utf-8") as f:
            return json.load(f)

class GrammarRules:
    def __init__(self, dictionaries):
        self.dicts = dictionaries
        self.tobe = ["am", "are", "is", "is", "is", "are"]
        self.do_does = ["do", "do", "does", "does", "does", "do"]
        self.definite_nouns = set(["cinema", "school", "beach", "hospital", "university", "park"])  # can expand

    def get_pronoun_index(self, pronoun):
        pronouns_ru = list(self.dicts.pronouns.keys())
        return pronouns_ru.index(pronoun) if pronoun in pronouns_ru else 2

    def get_verb_form(self, verb, tense):
        if verb in self.dicts.irregular_verbs:
            return self.dicts.irregular_verbs[verb].get(tense, f"{verb}ed")
        return f"{verb}ed" if tense == "past" else verb

    def add_article(self, noun):
        if noun in self.definite_nouns:
            return f"the {noun}"
        if noun.endswith('s'):  # plural forms
            return noun
        article = "an" if noun[0].lower() in "aeiou" else "a"
        return f"{article} {noun}"

class Translator:
    def __init__(self, dictionaries, grammar):
        self.morph = MorphAnalyzer()
        self.dicts = dictionaries
        self.grammar = grammar
        self.question_words = {
            "что": "what",
            "кто": "who",
            "где": "where",
            "почему": "why",
            "когда": "when",
            "как": "how"
        }

    def lemmatize(self, text):
        return [self.morph.parse(word)[0].normal_form for word in text.split()]

    def translate_sentence(self, text, tense):
        lemmas = self.lemmatize(text)

        question_word = next((self.question_words[w] for w in self.question_words if w in text.lower()), None)

        components = {
            'pronoun': self.find_component(lemmas, self.dicts.pronouns),
            'verb': self.find_component(lemmas, self.dicts.verbs),
            'noun': self.find_component(lemmas, self.dicts.nouns)
        }

        if not all(components.values()):
            return "Translation error: missing components"

        return self.build_sentence(components, tense, text, question_word)

    def find_component(self, lemmas, dictionary):
        for lemma in lemmas:
            if lemma in dictionary:
                return {'ru': lemma, 'en': dictionary[lemma]}
            match = process.extractOne(lemma, dictionary.keys(), score_cutoff=80)
            if match:
                best_match = match[0]
                return {'ru': best_match, 'en': dictionary[best_match]}
        return None

    def build_sentence(self, components, tense, original_text, question_word):
        pronoun = components['pronoun']['en']
        verb = components['verb']['en']
        noun_raw = components['noun']['en']
        noun = self.grammar.add_article(noun_raw)

        p_index = self.grammar.get_pronoun_index(components['pronoun']['ru'])
        to_be = self.grammar.tobe[p_index]
        to_do = self.grammar.do_does[p_index]

        question = '?' in original_text or question_word is not None
        negative = any(word in original_text.lower() for word in ['не', 'нет'])

        tense_map = {
            'past': self.handle_past_tense,
            'present': self.handle_present_tense,
            'future': self.handle_future_tense
        }

        return tense_map[tense](pronoun, verb, noun, to_be, to_do, question, negative, question_word)

    def handle_past_tense(self, pronoun, verb, noun, _, __, question, negative, question_word):
        verb_form = self.grammar.get_verb_form(verb, "past")
        base = f"{pronoun} {verb_form} {noun}"

        if negative:
            return f"{pronoun} didn't {verb} {noun}".capitalize()
        if question:
            if question_word:
                return f"{question_word.capitalize()} did {pronoun} {verb} {noun}?"
            return f"Did {pronoun} {verb} {noun}?".capitalize()
        return base.capitalize()

    def handle_present_tense(self, pronoun, verb, noun, to_be, to_do, question, negative, question_word):
        if negative:
            return f"{pronoun} {to_do}n't {verb} {noun}".capitalize()
        if question:
            if question_word:
                return f"{question_word.capitalize()} {to_do} {pronoun} {verb} {noun}?"
            return f"{to_do.capitalize()} {pronoun} {verb} {noun}?"
        return f"{pronoun} {verb} {noun}".capitalize()

    def handle_future_tense(self, pronoun, verb, noun, _, __, question, negative, question_word):
        base = f"{pronoun} will {verb} {noun}"
        if negative:
            return f"{pronoun} won't {verb} {noun}".capitalize()
        if question:
            if question_word:
                return f"{question_word.capitalize()} will {pronoun} {verb} {noun}?"
            return f"Will {pronoun} {verb} {noun}?".capitalize()
        return base.capitalize()

class TranslatorApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Русско-Английский Переводчик"
        self.output_field = ft.Text()

        try:
            self.dictionaries = DictionaryManager()
            self.grammar = GrammarRules(self.dictionaries)
            self.translator = Translator(self.dictionaries, self.grammar)
        except Exception as e:
            self.output_field.value = f"Ошибка инициализации: {str(e)}"
            self.page.add(self.output_field)
            self.page.update()
            return

        self.setup_ui()

    def setup_ui(self):
        self.input_field = ft.TextField(
            label="Введите текст на русском",
            multiline=True,
            text_size=18
        )

        self.time_dropdown = ft.Dropdown(
            label="Выберите время",
            options=[
                ft.dropdown.Option("past", "Прошедшее"),
                ft.dropdown.Option("present", "Настоящее"),
                ft.dropdown.Option("future", "Будущее")
            ],
            text_size=18
        )

        self.translate_btn = ft.ElevatedButton(
            text="Перевести",
            on_click=self.translate_text,
            height=50
        )

        self.output_field = ft.Text(
            size=18,
            text_align=ft.TextAlign.CENTER
        )

        self.page.add(
            ft.Column(
                controls=[
                    self.input_field,
                    self.time_dropdown,
                    self.translate_btn,
                    self.output_field
                ],
                spacing=15,
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER
            )
        )

    def translate_text(self, e):
        text = self.input_field.value.strip()
        tense = self.time_dropdown.value

        if not text:
            self.output_field.value = "Введите текст для перевода"
            self.page.update()
            return

        if not tense:
            self.output_field.value = "Выберите время!"
            self.page.update()
            return

        try:
            result = self.translator.translate_sentence(text.lower(), tense)
            self.output_field.value = result
        except Exception as ex:
            self.output_field.value = f"Ошибка перевода: {str(ex)}"
        finally:
            self.page.update()

if __name__ == "__main__":
    ft.app(target=TranslatorApp, assets_dir="data")
