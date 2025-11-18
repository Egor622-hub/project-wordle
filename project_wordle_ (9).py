import sys

from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QGridLayout,
                             QPushButton, QLabel)
from random import choice

import sqlite3


class Wordle(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wordle")
        self.setGeometry(100, 100, 400, 600)

        self.roundd = 0
        self.lables = []

        self.init_ui()

        self.used_words = set()

        self.db_read()

        self.setoffwords = set()
        self.read_words()
        self.word = choice(list(self.setoffwords.difference(self.used_words)))
        self.set_off_letters = set(list(self.word))
        self.user_enter = ''
        self.flag = True

    def init_ui(self):
        main_layout = QVBoxLayout()
        button_layout = QGridLayout()
        lable_layout = QGridLayout()
        lable_layout.setSpacing(5)
        self.label_print = QLabel(self)
        self.label_print.setText('У вас 6 попыток')
        self.label_print.setStyleSheet("font-size: 18px; font-weight: bold;")
        print_layout = QGridLayout()
        print_layout.addWidget(self.label_print)
        new_game_btn = QPushButton('Новая игра', self)
        new_game_btn.clicked.connect(self.new_game)
        print_layout.addWidget(new_game_btn, 0, 1)
        main_layout.addLayout(print_layout)
        for i in range(30):
            lable = QLabel(self)
            lable.setFixedSize(60, 60)
            lable.setText("")
            lable.setStyleSheet("""background: white;
                                    border: 2px solid #d3d6da;
                                    font-size: 32px;
                                    font-weight: bold;
                                    color: black;
                                    qproperty-alignment: AlignCenter;""")
            self.lables.append(lable)
            lable_layout.addWidget(lable, i // 5, i % 5)

        main_layout.addLayout(lable_layout)

        alphabet = "йцукенгшщзхъфывапролджэячсмитьбюё".upper()
        ln = len(alphabet)
        for i in range(ln):
            button = QPushButton(alphabet[i])
            button.clicked.connect(self.run)
            button_layout.addWidget(button, i // (12 - i // 23), i % (12 - i // 23))

        btn = QPushButton('Backspase', self)
        btn.clicked.connect(self.backspase)
        button_layout.addWidget(btn, 1, 11)
        benter = QPushButton('Enter', self)
        benter.clicked.connect(self.enter)
        button_layout.addWidget(benter, 2, 11)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def run(self):
        if self.flag:
            self.user_enter = self.user_enter + self.sender().text()
            self.user_enter = self.user_enter[:5]
            for i in range(5):
                self.lables[i + self.roundd * 5].setText('')
            for i in range(len(self.user_enter)):
                self.lables[i + self.roundd * 5].setText(self.user_enter[i])

    def backspase(self):
        if self.flag:
            self.user_enter = self.user_enter[0:len(self.user_enter) - 1]
            for i in range(5):
                self.lables[i + self.roundd * 5].setText('')
            for i in range(len(self.user_enter)):
                self.lables[i + self.roundd * 5].setText(self.user_enter[i])

    def read_words(self):
        with open("dict.txt", 'r', encoding="utf-8") as file:
            for line in file:
                self.setoffwords.add(line.replace('\n', '').upper())

    def check_letters(self):
        set3 = self.set_off_letters.intersection(set(list(self.user_enter)))
        for i in range(5):
            j = i + self.roundd * 5
            letter = self.lables[j].text()
            if letter in set3:
                if letter == self.word[i]:
                    self.lables[j].setStyleSheet("""
                                        background: #6aaa64;
                                        border: 2px solid #6aaa64;
                                        color: white;
                                        font-size: 32px;
                                        font-weight: bold;
                                        qproperty-alignment: AlignCenter;
                                    """)
                else:
                    self.lables[j].setStyleSheet("""
                                        background: #c9b458;
                                        border: 2px solid #c9b458;
                                        color: white;
                                        font-size: 32px;
                                        font-weight: bold;
                                        qproperty-alignment: AlignCenter;
                                    """)
            else:
                self.lables[j].setStyleSheet("""
                                background: #787c7e;
                                border: 2px solid #787c7e;
                                color: white;
                                font-size: 32px;
                                font-weight: bold;
                                qproperty-alignment: AlignCenter;
                            """)
        self.user_enter = ''

    def db_read(self):
        conn = sqlite3.connect('mydatabase.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT word FROM words")
        words = cursor.fetchall()
        for (word,) in words:
            self.used_words.add(word)
        conn.close()

    def db_add(self):
        conn = sqlite3.connect('mydatabase.db')
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO words (word) VALUES ('{self.word}')")
        conn.commit()
        conn.close()

    def enter(self):
        if self.flag:
            if len(self.user_enter) == 5:
                if self.user_enter in self.setoffwords:
                    if self.user_enter == self.word:
                        self.label_print.setText('Вы победили!')
                        self.check_letters()
                        self.flag = False
                        self.db_add()
                    else:
                        self.label_print.setText("Слово не подходит")
                        self.check_letters()
                        self.roundd += 1
                        if self.roundd >= 6:
                            self.label_print.setText(f'Вы проиграли! Слово было: {self.word}')
                            self.flag = False
                            self.db_add()
                else:
                    self.label_print.setText('Я не знаю такого слова')
                    self.user_enter = ''
                    self.backspase()
            else:
                self.label_print.setText('Слово содержит ровно 5 букв')
                self.user_enter = ''
                self.backspase()

    def new_game(self):
        self.roundd = 0
        self.user_enter = ''
        self.flag = True
        self.used_words = set()

        self.db_read()

        self.setoffwords = set()
        self.read_words()
        self.word = choice(list(self.setoffwords.difference(self.used_words)))
        self.set_off_letters = set(list(self.word))
        for lable in self.lables:
            lable.setText('')
            lable.setStyleSheet("""background: white;
                                    border: 2px solid #d3d6da;
                                    font-size: 32px;
                                    font-weight: bold;
                                    color: black;
                                    qproperty-alignment: AlignCenter;""")
        self.label_print.setText('У вас 6 попыток')


if __name__ == '__main__':

    app = QApplication(sys.argv)
    wordle = Wordle()
    wordle.show()
    sys.exit(app.exec())
