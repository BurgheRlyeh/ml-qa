import PySimpleGUI as sg

from crawler import update_pages
from qa import read_dataset, get_answer

layout = [
    [sg.Text("URL:"), sg.Input(key="-URL-")],
    [sg.Text("Pages limit:"), sg.Slider(range=(1, 100), default_value=20, orientation="h", key="-LIM-")],
    [sg.Button("Update pages")],
    [sg.Text("Question:"), sg.Input(key="-QUESTION-")],
    [sg.Button("Get answers")],
    [sg.Text("Short answer"), sg.Output(size=(50, 5), key='-SHORT-')],
    [sg.Text("Long answer"), sg.Output(size=(50, 10), key='-LONG-')]
]

window = sg.Window("QA", layout)

dataset = read_dataset('pages.txt')

while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break
    if event == "Update pages":
        update_pages(values["-URL-"], values["-LIM-"])
        dataset = read_dataset('pages.txt')
        print("Texts updated!")
    if event == "Get answers":
        question = values["-QUESTION-"]
        short, long = get_answer(question, dataset)
        window['-SHORT-'].update(short)
        window['-LONG-'].update(long)

window.close()
