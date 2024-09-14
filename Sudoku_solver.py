# Program to solve sudoku's
import streamlit as st
import copy
import numpy
import pandas as pd
from io import StringIO
import requests

if "data" not in st.session_state:
    url = 'https://raw.githubusercontent.com/var-github/Sudoku/main/Sudoku_questions.txt'
    response = requests.get(url)
    while response.status_code != 200:
        pass
    f = StringIO(response.text)
    st.session_state["data"] = f.readlines()
st.header("Sudoku Solver")
data = st.session_state["data"]
n = st.number_input("The file has 46 sudoku's please enter which one to solve (1-46): ", min_value=1, max_value=46)
if st.button("Solve"):
    empty_rows = {}
    empty_columns = {}
    l = []
    sudoku = []
    for i in range(9):
        x = []
        y = []
        for j in range(9):
            x += [data[n * 10 - 9:n * 10][i][j]]
            if data[n * 10 - 9:n * 10][i][j] != "0":
                y += [data[n * 10 - 9:n * 10][i][j]]
            else:
                y += [{}]
                empty_rows[i] = [j] if i not in empty_rows else empty_rows[i] + [j]
                empty_columns[j] = [i] if j not in empty_columns else empty_columns[j] + [i]
        sudoku += [x]
        l += [y]
    sudoku = numpy.array(sudoku)
    l = numpy.array(l)


    # First element represents row number, second element is column no (: - means all columns)
    def row(row_no):
        return sudoku[int(row_no), :]


    def col(col_no):
        return sudoku[:, int(col_no)]


    def box(row_no, col_no):
        return sudoku[(row_no // 3) * 3:(row_no // 3) * 3 + 3, (col_no // 3) * 3:(col_no // 3) * 3 + 3].flatten()


    for i in empty_rows:
        for j in empty_rows[i]:
            l[int(i)][int(j)] = {"1", "2", "3", "4", "5", "6", "7", "8", "9"} - set(row(i)) - set(col(j)) - set(
                box(int(i), int(j)))


    def display(d):
        df = pd.DataFrame(d)
        df.replace("0", "", inplace=True)
        df = df.style.apply(lambda x: ['background-color: lightgrey']*3+['']*3+['background-color: lightgrey']*3, axis=0, subset=[0, 1, 2, 6, 7, 8])
        df.apply(lambda x: ['']*3 + ['background-color: lightgrey']*3, axis=0, subset=[3, 4, 5])
        df.hide(axis=0).hide(axis=1)
        df.set_table_styles([{'selector': '', 'props': [('border', '2px solid black')]}, {'selector': 'tr', 'props': [('height', '38px')]}, {'selector': 'td', 'props': [('width', '35px')]}])
        st.write(df.to_html(), unsafe_allow_html=True)


    st.text("Question")
    display(sudoku)


    def update(row_no, col_no, num, key="normal"):
        location_has_only_one_possibility = False
        if key == "normal":
            l[int(row_no)][int(col_no)] = num
            sudoku[int(row_no)][int(col_no)] = num
            empty_rows[row_no].remove(col_no)
            empty_columns[col_no].remove(row_no)
            for x in empty_rows[row_no]:
                l[int(row_no)][int(x)] = l[int(row_no)][int(x)] - set(num)
                if len(l[int(row_no)][int(x)]) == 1:
                    location_has_only_one_possibility = True
            for x in empty_columns[col_no]:
                l[int(x)][int(col_no)] = l[int(x)][int(col_no)] - set(num)
                if len(l[int(x)][int(col_no)]) == 1:
                    location_has_only_one_possibility = True
            for i in range((row_no // 3) * 3, (row_no // 3) * 3 + 3):
                for j in range((col_no // 3) * 3, (col_no // 3) * 3 + 3):
                    if type(l[i][j]) is set:
                        l[i][j] = l[i][j] - set(num)
                        if len(l[i][j]) == 1:
                            location_has_only_one_possibility = True
            if not empty_columns[col_no]:
                empty_columns.pop(col_no)
            if not empty_rows[row_no]:
                empty_rows.pop(row_no)
        elif key == "nakedpair_row":
            for x in empty_rows[row_no]:
                if l[int(row_no)][int(x)] != num:
                    l[int(row_no)][int(x)] = l[int(row_no)][int(x)] - set(num)
                    if len(l[int(row_no)][int(x)]) == 1:
                        location_has_only_one_possibility = True
        elif key == "nakedpair_column":
            for x in empty_columns[col_no]:
                if l[int(x)][int(col_no)] != num:
                    l[int(x)][int(col_no)] = l[int(x)][int(col_no)] - set(num)
                    if len(l[int(x)][int(col_no)]) == 1:
                        location_has_only_one_possibility = True
        elif key == "locked_row":
            for x in empty_rows[row_no]:
                if x not in range(col_no, col_no + 3):
                    l[row_no][x] = l[row_no][x] - set(num)
                    if len(l[row_no][x]) == 1:
                        location_has_only_one_possibility = True
        elif key == "locked_column":
            for x in empty_columns[col_no]:
                if x not in range(row_no, row_no + 3):
                    l[x][col_no] = l[x][col_no] - set(num)
                    if len(l[x][col_no]) == 1:
                        location_has_only_one_possibility = True
        elif key == "box_locked_row":
            for i in range((row_no // 3) * 3, (row_no // 3) * 3 + 3):
                for j in range((col_no // 3) * 3, (col_no // 3) * 3 + 3):
                    if type(l[i][j]) is set and i != row_no:
                        l[i][j] = l[i][j] - set(num)
                        if len(l[i][j]) == 1:
                            location_has_only_one_possibility = True
        elif key == "box_locked_column":
            for i in range((row_no // 3) * 3, (row_no // 3) * 3 + 3):
                for j in range((col_no // 3) * 3, (col_no // 3) * 3 + 3):
                    if type(l[i][j]) is set and j != col_no:
                        l[i][j] = l[i][j] - set(num)
                        if len(l[i][j]) == 1:
                            location_has_only_one_possibility = True
        return location_has_only_one_possibility


    changes = 0
    while True:
        rerun = False
        if changes != -1:
            changes = 0

        # Checking if any location has only one possibility
        for i in empty_rows.copy():
            for j in empty_rows[i]:
                if len(l[int(i)][int(j)]) == 1:
                    update(i, j, list(l[int(i)][int(j)])[0])
                    changes += 1

        if rerun:
            continue

        # Checking if a number appears only once in a row
        for i in empty_rows.copy():
            y = sum(list(map(lambda x: list(x) if type(x) is set else [], l[i, :])), [])
            if y:
                num = min(y, key=y.count)
                if y.count(num) == 1:
                    for a in empty_rows[i]:
                        if num in l[int(i)][int(a)]:
                            rerun = update(i, a, num)
                            changes += 1
                            break
                else:
                    num = sum(list(map(lambda x: [list(x)] if type(x) is set and len(x) == 2 else [], l[i, :])), [])
                    if len(num) == 2 and num[0] == num[1]:
                        if y.count(num[0][0]) + y.count(num[0][1]) != 4:
                            for j in empty_rows[i]:
                                if l[i][j] == set(num[0]):
                                    rerun = update(i, j, set(num[0]), "nakedpair_row")
                                    changes += 1

        if rerun:
            continue

        # Checking if a number appears only once in a column
        for i in empty_columns.copy():
            y = sum(list(map(lambda x: list(x) if type(x) is set else [], l[:, i])), [])
            if y:
                num = min(y, key=y.count)
                if y.count(num) == 1:
                    for a in empty_columns[i]:
                        if num in l[int(a)][int(i)]:
                            rerun = update(a, i, num)
                            changes += 1
                            break
                else:
                    num = sum(list(map(lambda x: [list(x)] if type(x) is set and len(x) == 2 else [], l[:, i])), [])
                    if len(num) == 2 and num[0] == num[1]:
                        if y.count(num[0][0]) + y.count(num[0][1]) != 4:
                            for j in empty_columns[i]:
                                if l[j][i] == set(num[0]):
                                    rerun = update(j, i, set(num[0]), "nakedpair_column")
                                    changes += 1

        if rerun:
            continue

        # Checking if a number appears only once in a box
        for i in range(0, 9, 3):
            for j in range(0, 9, 3):
                y = sum(list(map(lambda x: list(x) if type(x) is set else [],
                                 l[(i // 3) * 3:(i // 3) * 3 + 3, (j // 3) * 3:(j // 3) * 3 + 3].flatten())), [])
                if y:
                    num = min(y, key=y.count)
                    if y.count(num) == 1:
                        for x in set(empty_rows.keys()) - (set(range(0, 9)) - set(range((i // 3) * 3, (i // 3) * 3 + 3))):
                            for y in set(empty_rows[x]) - (set(range(0, 9)) - set(range((j // 3) * 3, (j // 3) * 3 + 3))):
                                if num in l[x][y]:
                                    rerun = update(x, y, num)
                                    changes += 1
                                    break
                            else:
                                continue
                            break
                    else:
                        num = list(map(lambda x: list(x) if type(x) is set else [],
                                       l[(i // 3) * 3:(i // 3) * 3 + 3, (j // 3) * 3:(j // 3) * 3 + 3].flatten()))
                        num[0], num[1], num[2], num[3:] = sum(num[:3], []), sum(num[3:6], []), sum(num[6:9], []), []
                        # num[0] has possibilities of the first row in the box, num[1] has possibilities of the second row in the box
                        box_possibilities = copy.deepcopy(num)
                        num[0], num[1], num[2] = set(num[0]), set(num[1]), set(num[2])
                        num[0], num[1], num[2] = num[0] - num[1] - num[2], num[1] - num[0] - num[2], num[2] - num[0] - num[
                            1]
                        # num[0] has possibilities unique to the first row, num[1] has possibilities unique to the second row
                        for x in range(3):
                            row_possibilities = list(map(lambda a: list(a) if type(a) is set else [], l[x + i, :]))
                            # Possibilities of the rest of the row except this box
                            row_possibilities = sum(row_possibilities[:(j // 3) * 3] + row_possibilities[(j // 3) * 3 + 3:],
                                                    [])
                            if num[x]:
                                if type(num[x]) is not set and num[x] in row_possibilities:
                                    rerun = update(x + i, j, num[x], "locked_row")
                                    changes += 1
                                    break
                                elif type(num[x]) is set:
                                    for k in num[x]:
                                        if k in row_possibilities:
                                            rerun = update(x + i, j, k, "locked_row")
                                            changes += 1
                                            break
                            n = list(set(box_possibilities[x]) - set(row_possibilities))
                            if len(n) == 1:
                                if n[0] in sum(box_possibilities[:x] + box_possibilities[x + 1:], []):
                                    rerun = update(x + i, j, n[0], "box_locked_row")
                                    changes += 1
                            elif len(n) > 1:
                                for k in n:
                                    if k in sum(box_possibilities[:x] + box_possibilities[x + 1:], []):
                                        rerun = update(x + i, j, k, "box_locked_row")
                                        changes += 1
                        num = list(map(lambda x: list(x) if type(x) is set else [], l[(i // 3) * 3:(i // 3) * 3 + 3,
                                                                                    (j // 3) * 3:(
                                                                                                             j // 3) * 3 + 3].transpose().flatten()))
                        num[0], num[1], num[2], num[3:] = sum(num[:3], []), sum(num[3:6], []), sum(num[6:9], []), []
                        box_possibilities = copy.deepcopy(num)
                        num[0], num[1], num[2] = set(num[0]), set(num[1]), set(num[2])
                        num[0], num[1], num[2] = num[0] - num[1] - num[2], num[1] - num[0] - num[2], num[2] - num[0] - num[
                            1]
                        for x in range(3):
                            col_possibilities = list(map(lambda a: list(a) if type(a) is set else [], l[:, x + j]))
                            # Possibilities of the rest of the column except this box
                            col_possibilities = sum(col_possibilities[:(i // 3) * 3] + col_possibilities[(i // 3) * 3 + 3:],
                                                    [])
                            if num[x]:
                                if type(num[x]) is not set and num[x] in col_possibilities:
                                    rerun = update(i, x + j, num[x], "locked_column")
                                    changes += 1
                                    break
                                elif type(num[x]) is set:
                                    for k in num[x]:
                                        if k in col_possibilities:
                                            rerun = update(i, x + j, k, "locked_column")
                                            changes += 1
                                            break
                            n = list(set(box_possibilities[x]) - set(col_possibilities))
                            if len(n) == 1:
                                if n[0] in sum(box_possibilities[:x] + box_possibilities[x + 1:], []):
                                    rerun = update(i, x + j, n[0], "box_locked_column")
                                    changes += 1
                            elif len(n) > 1:
                                for k in n:
                                    if k in sum(box_possibilities[:x] + box_possibilities[x + 1:], []):
                                        rerun = update(i, x + j, k, "box_locked_column")
                                        changes += 1

        if rerun:
            continue

        if changes == -1:
            break
        if changes == 0:
            changes = -1

    st.text("Solution")
    display(sudoku)
