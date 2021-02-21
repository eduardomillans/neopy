import os
import platform
import json

from PyInquirer import prompt, style_from_dict, Token
from prettytable import PrettyTable

# Promp styles
__prompt_style = style_from_dict({
    Token.QuestionMark: '#f01a81 bold',
    Token.Selected: '#19afd1 bold',
    Token.Instruction: '',
    Token.Answer: '#22e694 bold',
    Token.Question: '',
})


def clear_screen():
    if (platform.system()).lower() == 'windows':
        os.system('cls')
    else:
        os.system('clear')


def get_answers(questions):
    response = prompt(questions, style=__prompt_style)

    if type(questions) is list:
        answers = []
        for question in questions:
            answers.append(response[question['name']])
        return answers
    else:
        return response[questions['name']]


def save_data_to_json(filename, data):
    with open(filename, 'w') as json_file:
        json.dump(data, json_file)


def get_data_from_json(filename):
    try:
        with open(filename, 'r') as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        return []


def show_table(header, data, data_type):
    table = PrettyTable(header)
    for item in data:
        row = []
        for caption in header:
            row.append(item[caption.lower().replace(' ', '_')])
        table.add_row(row)
    print(f'\n{data_type.capitalize()} Table')
    print(table)


if __name__ == '__main__':
    print('You need to run \'main.py\'')
