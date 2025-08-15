import random
import re

degrees = ["I", "II", "III", "IV", "V", "VI", "VII"]
properties = ["", "m", "m", "", "", "m", "dim"]
properties7 = ["M7", "m7", "m7", "M7", "7", "m7", "dim7"]
distance7 = {"M7": [4, 7, 11], "m7": [3, 7, 10], "7": [4, 7, 10], "dim7": [3, 6, 10]}
up_notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
down_notes = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
distances = [
    "Unision",
    "Minor 2nd",
    "Major 2nd",
    "Minor 3rd",
    "Major 3rd",
    "Perfect 4th",
    "Tritone",
    "Perfect 5th",
    "Minor 6th",
    "Major 6th",
    "Minor 7th",
    "Major 7th",
    "Octave",
]
ds = ["P1", "m2", "M2", "m3", "M3", "P4", "D5", "P5", "m6", "M6", "m7", "M7", "P8"]
up_set = [0, 7, 2, 9, 4, 11]
down_set = [5, 10, 3, 8, 1, 6]
rule = [2, 2, 1, 2, 2, 2]
guitar = [["E"], ["B"], ["G"], ["D"], ["A"], ["E"]]
bass = [["G"], ["D"], ["A"], ["E"]]
scales = [[], [], [], [], [], [], [], [], [], [], [], []]
for i in range(12):
    if i in up_set:
        notes = up_notes
    else:
        notes = down_notes
    num = i
    scales[i].append(notes[i])
    for j in range(len(rule)):
        num += rule[j]
        temp = notes[num % 12]
        if not (temp == "B" and scales[i][0] == "Gb"):
            scales[i].append(temp)
        else:
            scales[i].append("Cb")

for i in range(len(guitar)):
    for j in range(21):
        guitar[i].append(up_notes[(up_notes.index(guitar[i][j]) + 1) % 12])

for i in range(len(bass)):
    for j in range(21):
        bass[i].append(up_notes[(up_notes.index(bass[i][j]) + 1) % 12])


def function1():  # 和弦音
    while True:
        n0 = random.randint(0, 1)
        n1 = random.randint(0, 11)
        n2 = random.randint(0, 3)
        if n0 == 0:
            notes = up_notes
        else:
            notes = down_notes
        d = list(set(properties7.copy()))
        question = notes[n1] + d[n2]
        answer = [notes[n1]]
        for i in range(3):
            answer.append(notes[(n1 + distance7[d[n2]][i]) % 12])

        get = input("\nWhat is the notes of {}? (example: C C C C)\n".format(question))
        a = get.split(" ")
        if compare_list(a,answer):
            print("True, ", answer)
        else:
            print("False, ", answer)


def function2():  # 1反
    while True:
        number = random.randint(0, 11)
        scale = scales[number]

        question = random.randint(1, 5)
        get = input(
            "\nIn {0} Major, which is at the number {1}? 0 for tips. \n".format(
                scale[0], question + 1
            )
        ).strip()
        while 1:
            if get == scale[question] or get_another(get) == scale[question]:
                print("True", scale)
                break
            elif get.isdigit() and int(get) == 0:
                print(scale)
                get = input()
            else:
                print(scale)
                print("False, " + scale[question])
                break


def function3():  # 包含音的音阶
    while True:
        number = random.randint(0, 11)
        temp = number
        if number in up_set:
            notes = up_notes
        else:
            notes = down_notes
        answer = [1, 2, 3, 4, 5, 6, 7]
        while 1:
            get = input(
                "\nWhich major scales include {0}? (Use ',' to separate) Remain: {1}\n".format(
                    notes[number], answer
                )
            )
            scale = [0] * (len(rule) + 1)
            scales = []
            for i in range(len(rule) + 1):
                scale[i] = [notes[number]]
                for j in range(i, i + len(rule), 1):
                    if j < len(rule):
                        number += rule[j % (len(rule) + 1)]
                        scale[i].insert(j % (len(rule) + 1) + 1, notes[number % 12])
                    else:
                        number = temp + len(notes)
                        number2 = i - 1
                        for k in range(j % len(rule) + 1):
                            number -= rule[number2]
                            number2 -= 1
                        scale[i].insert(0, notes[number % 12])
                scales.append(scale[i][0])
                number = temp
            get = list(filter(None, re.split(", |,| ", get)))
            isRight = False
            for i in range(len(get)):
                for j in range(len(rule) + 1):
                    if get[i] == scale[j][0] or get_another(get[i]) == scale[j][0]:
                        if j + 1 in answer:
                            answer.remove(j + 1)
                        isRight = True
                if not isRight:
                    print(get[i] + " is not right. ")
                    break
                else:
                    isRight = False
            if len(answer) == 0:
                print("True. " + str(scales) + "\n" + str(scale))
                break


def function4():  # 显示音阶
    while True:
        get = input("\nInput note name\n").strip()
        if get in up_notes:
            notes = up_notes
        elif get in down_notes:
            notes = down_notes
        else:
            print("Error")
            continue
        number = notes.index(get)
        if number in up_set:
            notes = up_notes
        else:
            notes = down_notes
        scale = [notes[number]]
        for i in range(len(rule)):
            number += rule[i]
            temp = notes[number % 12]
            if not (temp == "B" and scale[0] == "Gb"):
                scale.append(temp)
            else:
                scale.append("Cb")
        print(scale)


def function5():  # 距离上的音
    while True:
        number1 = random.randint(0, 11)
        if number1 in up_set:
            notes = up_notes
        else:
            notes = down_notes
        note1 = notes[number1]
        number2 = random.randint(0, 11)
        if number2 in up_set:
            notes = up_notes
        else:
            notes = down_notes
        note2 = notes[number2]
        a = -1
        d = random.randint(0, 1)  # 0:down, 1:up
        direction = ""
        if d == 0:
            direction = "down"
            if number1 < number2:
                a = 12 + number1 - number2
            else:
                a = number1 - number2

        else:
            direction = "up"
            if number1 > number2:
                a = 12 + number2 - number1
            else:
                a = number2 - number1

        answer = ds[a]
        get = input(
            "\nWhat is the distance from {0} go {1} to {2}?\n".format(
                note1, direction, note2
            )
        ).strip()
        if get == "P8":
            get = "P1"
        elif get == "A4":
            get = "D5"
        if get == answer:
            print("True")
        else:
            print("False, " + answer)


def function6():  # 5反
    while True:
        number1 = random.randint(0, 11)
        if number1 in up_set:
            notes = up_notes
        else:
            notes = down_notes
        note = notes[number1]
        number2 = random.randint(0, 11)
        if number2 in up_set:
            notes = up_notes
        else:
            notes = down_notes
        question = notes[number2]
        a = -1
        d = random.randint(0, 1)  # 0:down, 1:up
        direction = ""
        if d == 0:
            direction = "down"
            if number1 < number2:
                a = 12 + number1 - number2
            else:
                a = number1 - number2

        else:
            direction = "up"
            if number1 > number2:
                a = 12 + number2 - number1
            else:
                a = number2 - number1

        distance = distances[a]
        answer = question

        get = input(
            "\nWhat is the note from {0} go {1} {2}?\n".format(
                note, direction, distance
            )
        ).strip()

        if get == answer or get == get_another(answer):
            print("True")
        else:
            print("False, " + answer)


def function7():  # 显示随机音
    import time
    from threading import Thread

    bpm = 90
    num = ""
    pre = ""
    arr = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

    def get_input():
        global bpm, pre, num
        import msvcrt

        while 1:
            num = msvcrt.getch()
            if num == "\r":
                try:
                    if int(pre) != 0:
                        bpm = int(pre)
                        print("\033[12;0H\033[KSpeed now: {}".format(bpm)),
                    pre = ""
                except Exception:
                    pass
                print("\033[13;0H\033[0KChange to: ")
            else:
                if num == "\x08":
                    pre = pre[:-1]
                else:
                    pre += num
                print("\033[13;0HChange to: {}".format(pre)),
                print("\033[14;0H"),

    t1 = Thread(target=get_input)
    t1.start()
    print("\033[12;0H\033[KSpeed now: {}".format(bpm)),
    print("\033[13;0HChange to: "),
    print("\033[14;0H"),
    j = 0
    while 1:
        set = [i for i in arr]
        while len(set) != 0:
            ask = random.randint(0, len(set) - 1)
            print("\033[" + str(j % 8 + 3) + ";0H" + "\033[2K")
            print(
                "\033["
                + str(j % 8 + 3)
                + ";3H"
                + up_notes[set[ask]]
                + "\033["
                + str(j % 8 + 2)
                + ";0H"
            )
            j += 1
            set.pop(ask)
            time.sleep(round(60.0 / bpm, 1))

    t1.join()


def function8():  # 音阶音级
    while True:
        number = random.randint(0, 11)
        scale = scales[number]
        answers = [scale[i] + properties[i] for i in range(len(scale))]
        answer = []
        a = []
        d = []
        e = [0, 1, 2, 3, 4, 5, 6]
        for i in range(7):
            n = e[random.randint(0, len(e) - 1)]
            a.append(n)
            d.append(degrees[n])
            answer.append(answers[n])
            e.remove(n)
        b = input(
            "\nIn {1} major, What is the chords of {0}? (example:C C Am Am)\n".format(
                d, scale[0]
            )
        )
        c = b.split(" ")
        answerFlag = True
        for i in range(len(c)):
            if c[i] != answer[i]:
                answerFlag = False
                break
        if answerFlag:
            print("Correct! All chords are: {}".format(answers))
        else:
            print(
                "Wrong! They should be: {0} All chords are: {1}".format(answer, answers)
            )


def function9():  # 8反
    while True:
        number = random.randint(0, 11)
        scale = scales[number]
        answers = [scale[i] + properties[i] for i in range(len(scale))]
        answer = []
        a = []
        d = []
        e = [0, 1, 2, 3, 4, 5, 6]
        an = ""
        for i in range(4):
            n = e[random.randint(0, len(e) - 1)]
            a.append(n)
            an = an + str(n + 1)
            d.append(degrees[n])
            answer.append(answers[n])
            e.remove(n)
        b = input(
            "\nIn {1} major, What is the degrees of {0}? (example:1111)\n".format(
                answer, scale[0]
            )
        )
        answerFlag = True
        if b != an:
            answerFlag = False
        if answerFlag:
            print("Correct! All chords are: {}".format(answers))
        else:
            print("Wrong! They should be: {0} All chords are: {1}".format(d, answers))


def function10():  # 琴上音的位置
    type = int(input("\n1 for guitar, 2 for bass\n"))
    if type == 1:
        board = guitar
    else:
        board = bass
    while True:
        number = random.randint(0, 11)
        string = random.randint(0, 5)
        note = up_notes[number]
        for i in range(12):
            if board[string][i] == note:
                answer = i
                break
        get = input(
            "\nOn string {} , which frets is {} on?(example 0)\n".format(
                string + 1, note
            )
        )
        if get.isdigit() and int(get) == answer:
            print("Correct! Another answer is {}".format(answer + 12))
        elif get.isdigit() and int(get) == answer + 12:
            print("Correct! Another answer is {}".format(answer))
        else:
            print("Wrong! Answer is: {} {}".format(answer, answer + 12))


def function11():  # 10反
    type = int(input("\n1 for guitar, 2 for bass\n"))
    if type == 1:
        board = guitar
    else:
        board = bass
    while True:
        string = random.randint(0, 5)
        fret = random.randint(0, 21)
        answer = board[string][fret]

        get = input(
            "\nWhat is the note on string {}, fret {}?(example 0)\n".format(
                string + 1, fret
            )
        )
        if get == answer:
            print("Correct! ".format(answer))
        else:
            print("Wrong! Answer is: {} ".format(answer))


def get_another(note):
    if len(note) == 2:
        if note in up_notes:
            return down_notes[up_notes.index(note)]
        elif note in down_notes:
            return up_notes[down_notes.index(note)]
    else:
        return note

def compare_list(get,answer):
    for i in range(len(get)):
        if get[i] != answer[i]:
            if len(get[i]) != 2:
                return False
            else:
                if get_another(get[i]) != answer[i]:
                    return False
    return True

if __name__ == "__main__":
    flag = True
    while flag:
        n = input(
            "\n0 close, 1 answer the position of a note, 2 for inverse 1, 3 answer the scales including a note, 4 show scale, 5 answer a note with a distance, 6 for inverse 5, 7 for random, 8 for degree chords in a scale, 9 for inverse 8, 10 for note position on guitars, 11 for inverse 10\n"
        )
        if n.isdigit():
            n = int(n)
            match n:
                case 0:
                    flag = False
                case 1:
                    function1()
                case 2:
                    function2()
                case 3:
                    function3()
                case 4:
                    function4()
                case 5:
                    function5()
                case 6:
                    function6()
                case 7:
                    function7()
                case 8:
                    function8()
                case 9:
                    function9()
                case 10:
                    function10()
                case 11:
                    function11()
                case _:
                    pass
