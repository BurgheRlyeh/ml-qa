from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from numpy import dot
from numpy.linalg import norm
import numpy as np
import os


def read_dataset(filename):
    if not os.path.exists(filename):
        return []

    # Открываем файл для чтения
    with open(filename, 'r') as file:
        lines = file.readlines()

    # Создаем список для хранения текстов
    dataset = []
    current_text = ''

    # Обходим строки файла
    for line in lines:
        # Если строка не пустая, добавляем ее к текущему тексту
        if line.strip() != '':
            current_text += line.strip() + '\n'
        # Если строка пустая и текущий текст не пустой, добавляем его в датасет
        elif current_text and "." in current_text:
            dataset.append(current_text.strip())
            current_text = ''

    # Добавляем последний текст в датасет, если он не пустой
    if current_text:
        dataset.append(current_text.strip())

    return dataset


def cos_sim(a, b):
    return dot(a, b) / (norm(a) * norm(b))


def retriever_cos(question, texts):
    max_similarity_id = 0
    max_similarity = 0

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit(texts)

    quest_vector = X.transform([question]).toarray()
    context_vectorized = X.transform(texts).toarray()

    for (id_row, text) in enumerate(context_vectorized):
        if cos_sim(quest_vector, text) > max_similarity:
            max_similarity_id = id_row
            max_similarity = cos_sim(quest_vector, text)

    return texts[max_similarity_id]


model_pipeline = pipeline(
    task='question-answering',
    model='timpal0l/mdeberta-v3-base-squad2'
)


def reader(quest, likely_text):
    return model_pipeline(question=quest, context=likely_text)


def get_answer(quest, texts):
    likely_text = retriever_cos(quest, texts)
    # print(likely_text)
    answer = reader(quest, likely_text)
    # print(f"Question: {quest}")
    print(f"Answer: {answer}\n")
    return answer['answer'], likely_text


# if __name__ == '__main__':
#     # question = 'Когда идеально улучшать свою лейку'
#     # question = 'Как повысить навык рыбной ловли'
#     # question = 'Что можно узнать по телевизору'
#     # question = 'Что такое дневной цикл'
#     question = 'Где можно хранить ингредиенты для блюд'
#     texts = read_dataset('pages.txt')

#     print(get_answer(question, texts))
