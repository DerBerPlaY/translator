import urllib.parse
import urllib.request
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from natasha import MorphVocab, NewsEmbedding, NewsMorphTagger


# Инициализация морфологического словаря и теггера
morph_vocab = MorphVocab()
emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)


tobe = ["am", "are", "is", "is", "is", "are"]
do_does = ["do", "do", "does", "does", "does", "do"]


nouns_ru = ([str(x)[:-1] for x in open('nouns_ru.txt')])
nouns_en = ([str(x)[:-1] for x in open('nouns_en.txt')])
verbs_ru = ([str(x)[:-1] for x in open('verbs_ru.txt')])
verbs_en = ([str(x)[:-1] for x in open('verbs_en.txt')])
pronouns_ru = ([str(x)[:-1] for x in open('pronouns_ru.txt')])
pronouns_en = ([str(x)[:-1] for x in open('pronouns_en.txt')])


def translate_ru_to_en(text_input, time):
    print(text_input)


    noun_en = ""
    noun_ru = ""
    verb_en = ""
    verb_ru = ""
    pronoun_en = ""
    pronoun_ru = ""
    to_be = ""
    to_do = ""


    text = text_input.split()
    text = [text[x].lower() for x in range(0, len(text))]
    text = lemmatize_text(' '.join(text))


    print(text)


    for i in range(0, len(nouns_en)):
        if nouns_ru[i] in text:
            noun_en = nouns_en[i]
            noun_ru = nouns_ru[i]


    if noun_en == "": return "Missing noun"
    if noun_ru == "": return "Missing noun"


    for i in range(0, len(pronouns_en)):
        if pronouns_ru[i] in text:
            pronoun_en = pronouns_en[i]
            pronoun_ru = pronouns_ru[i]
            to_be = tobe[i]
            to_do = do_does[i]
    if pronoun_en == "": return "Missing pronoun"
    if pronoun_ru == "": return "Missing pronoun"


    for i in range(0, len(verbs_en)):
        if verbs_ru[i] in text:
            verb_en = verbs_en[i]
            verb_ru = verbs_ru[i]


    verb_ru = morph_vocab.lemmatize(verb_ru)[0]
    if verb_en == "": return "Missing verb"
    if verb_ru == "": return "Missing verb"


    question = 0
    deny = 0


    if (text_input[-1] == '?'):
        question = 1
    if ("не" in text):
        deny = 1


    if (deny == 1):
        if (time == 1):
            return((pronoun_en + " didn't " + verb_en + " to the " + noun_en).capitalize())
        if (time == 2):
            return((pronoun_en + " " + to_do + "n't" + " " + verb_en + " to the " + noun_en).capitalize())
        if (time == 3):
            return((pronoun_en + " won't " + verb_en + " to the " + noun_en).capitalize())
    if (question == 1):
        if (time == 1):
            return(("had " + pronoun_en + " " + verb_en + "ed to the " + noun_en + "?").capitalize())
        if (time == 2):
            return((to_do + " " + pronoun_en + " " + verb_en + " to the " + noun_en + "?").capitalize())
        if (time == 3):
            return(("will " + pronoun_en + " " + verb_en + " to the " + noun_en + "?").capitalize())
    if (time == 1):
        return((pronoun_en + " " + verb_en + "ed to the " + noun_en).capitalize())
    if (time == 2):
        return((pronoun_en + " " + verb_en + " to the " + noun_en).capitalize())
    if (time == 3):
        return((pronoun_en + " will " + verb_en + " to the " + noun_en).capitalize())


class TranslatorApp(App):
    def build(self):
        # Создаем основной контейнер
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)


        # Создаем текстовое поле для ввода текста
        self.input_text = TextInput(hint_text="Введите текст для перевода", size_hint=(1, None), height=40)
        layout.add_widget(self.input_text)


        # Создаем выпадающий список для выбора времени
        self.dropdown = DropDown()
        for time in ["Прошедшее", "Настоящее", "Будущее"]:
            btn = Button(text=time, size_hint_y=None, height=40)
            btn.bind(on_release=lambda btn: self.dropdown.select(btn.text))
            self.dropdown.add_widget(btn)


        self.time_button = Button(text="Выберите время", size_hint=(1, None), height=40)
        self.time_button.bind(on_release=self.dropdown.open)
        self.dropdown.bind(on_select=lambda instance, x: setattr(self.time_button, 'text', x))
        layout.add_widget(self.time_button)


        # Создаем кнопку для перевода
        translate_button = Button(text="Перевести", size_hint=(1, None), height=40)
        translate_button.bind(on_press=self.translate_text)
        layout.add_widget(translate_button)


        # Создаем метку для отображения переведенного текста
        self.output_label = Label(text="Переведенный текст будет здесь", size_hint=(1, None), height=40)
        layout.add_widget(self.output_label)


        return layout


    def translate_text(self, instance):
        # Здесь должна быть ваша функция для перевода текста
        # Например: translated_text = translate(self.input_text.text)
        # Но мы оставим заглушку
        input_text = self.input_text.text
        time_text = self.time_button.text
        time = 0
        if time_text == "Прошедшее":
            time = 1
        elif time_text == "Настоящее":
            time = 2
        elif time_text == "Будущее":
            time = 3


        if time == 0:
            self.output_label.text = "Возникла ошибка при выборе времени"
            return


        translated_text = translate_ru_to_en(input_text, time)


        # Обновляем метку с переведенным текстом
        self.output_label.text = translated_text


if __name__ == '__main__':
    TranslatorApp().run()