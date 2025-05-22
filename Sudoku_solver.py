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
n = st.number_input("The file has 50 sudoku's please enter which one to solve (1-50): ", min_value=1, max_value=50)
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


    # l[:, :] First element is slicing for rows, second element is slicing for columns
    def box(row_no, col_no):
        return sudoku[(row_no//3)*3:(row_no//3)*3+3, (col_no//3)*3:(col_no//3)*3+3].flatten()
    
    
    for i in empty_rows:
        for j in empty_rows[i]:
            l[int(i)][int(j)] = {"1", "2", "3", "4", "5", "6", "7", "8", "9"} - set(sudoku[int(i), :]) - set(sudoku[:, int(j)]) - set(box(int(i), int(j)))


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


    location_has_only_one_possibility = []
    def update(row_no, col_no, num, key="normal"):
        global location_has_only_one_possibility
        if key == "normal":
            l[int(row_no)][int(col_no)] = num
            sudoku[int(row_no)][int(col_no)] = num
            empty_rows[row_no].remove(col_no)
            empty_columns[col_no].remove(row_no)
            for x in empty_rows[row_no]:
                l[int(row_no)][int(x)] = l[int(row_no)][int(x)] - set(num)
                if len(l[int(row_no)][int(x)]) == 1:
                    location_has_only_one_possibility += [(int(row_no), int(x))]
            for x in empty_columns[col_no]:
                l[int(x)][int(col_no)] = l[int(x)][int(col_no)] - set(num)
                if len(l[int(x)][int(col_no)]) == 1:
                    location_has_only_one_possibility += [(int(x), int(col_no))]
            for i in range((row_no//3)*3, (row_no//3)*3+3):
                for j in range((col_no//3)*3, (col_no//3)*3+3):
                    if type(l[i][j]) is set:
                        l[i][j] = l[i][j] - set(num)
                        if len(l[i][j]) == 1:
                            location_has_only_one_possibility += [(i, j)]
            if not empty_columns[col_no]:
                empty_columns.pop(col_no)
            if not empty_rows[row_no]:
                empty_rows.pop(row_no)
    
        elif key == "nakedpair_row":
            for x in empty_rows[row_no]:
                if l[int(row_no)][int(x)] != num:
                    l[int(row_no)][int(x)] = l[int(row_no)][int(x)] - set(num)
                    if len(l[int(row_no)][int(x)]) == 1:
                        location_has_only_one_possibility += [(int(row_no), int(x))]
    
        elif key == "nakedpair_column":
            for x in empty_columns[col_no]:
                if l[int(x)][int(col_no)] != num:
                    l[int(x)][int(col_no)] = l[int(x)][int(col_no)] - set(num)
                    if len(l[int(x)][int(col_no)]) == 1:
                        location_has_only_one_possibility += [(int(x), int(col_no))]
    
        elif key == "locked_row":
            for x in empty_rows[row_no]:
                if x not in range(col_no, col_no + 3):
                    l[row_no][x] = l[row_no][x] - set(num)
                    if len(l[row_no][x]) == 1:
                        location_has_only_one_possibility += [(row_no, x)]
    
        elif key == "locked_column":
            for x in empty_columns[col_no]:
                if x not in range(row_no, row_no + 3):
                    l[x][col_no] = l[x][col_no] - set(num)
                    if len(l[x][col_no]) == 1:
                        location_has_only_one_possibility += [(x, col_no)]
    
        elif key == "box_locked_row":
            for i in range((row_no//3)*3, (row_no//3)*3+3):
                for j in range((col_no//3)*3, (col_no//3)*3+3):
                    if type(l[i][j]) is set and i != row_no:
                        l[i][j] = l[i][j] - set(num)
                        if len(l[i][j]) == 1:
                            location_has_only_one_possibility += [(i, j)]
    
        elif key == "box_locked_column":
            for i in range((row_no//3)*3, (row_no//3)*3+3):
                for j in range((col_no//3)*3, (col_no//3)*3+3):
                    if type(l[i][j]) is set and j != col_no:
                        l[i][j] = l[i][j] - set(num)
                        if len(l[i][j]) == 1:
                            location_has_only_one_possibility += [(i, j)]
    
        elif key == "x-wing":
            for i in col_no:
                for j in empty_columns[i]:
                    if j not in row_no:
                        l[j][i] = l[j][i] - set(num)
                        if len(l[j][i]) == 1:
                            location_has_only_one_possibility += [(j, i)]
            for i in row_no:
                for j in empty_rows[i]:
                    if j not in col_no:
                        l[i][j] = l[i][j] - set(num)
                        if len(l[i][j]) == 1:
                            location_has_only_one_possibility += [(i, j)]
    
        location_has_only_one_possibility = list(set(location_has_only_one_possibility))
        if location_has_only_one_possibility:
            i, j = location_has_only_one_possibility[0]
            location_has_only_one_possibility.pop(0)
            update(i, j, list(l[i][j])[0])


    # Checking if any location has only one possibility
    for i in empty_rows.copy():
        if i in empty_rows:
            for j in empty_rows[i].copy():
                if type(l[int(i)][int(j)]) is set and len(l[int(i)][int(j)]) == 1:
                    update(i, j, list(l[int(i)][int(j)])[0])


    def main():
        global changes
        # Checking if a number appears only once in a row
        for i in empty_rows.copy():
            y = sum(list(map(lambda x: list(x) if type(x) is set else [], l[i, :])), [])
            if y:
                num = min(y, key=y.count)
                if y.count(num) == 1:
                    for a in empty_rows[i]:
                        if num in l[int(i)][int(a)]:
                            update(i, a, num)
                            changes += 1
                            return
                else:
                    for j in range(len(empty_rows[i])-1):
                        for k in range(j+1, len(empty_rows[i])):
                            common = l[i][empty_rows[i][j]].intersection(l[i][empty_rows[i][k]])
                            # 2 cells have 2 numbers in common and no other number in common
                            if len(common) == 2:
                                # If the union has more than 2 elements - hiddenpair (not yet checked)
                                if len(l[i][empty_rows[i][j]].union(l[i][empty_rows[i][k]])) > 2 and y.count(list(common)[0]) + y.count(list(common)[1]) == 4:
                                    l[i][empty_rows[i][j]] = common
                                    l[i][empty_rows[i][k]] = common
                                    changes += 1
                                # If this condition is true then - nakedpair (not yet checked)
                                elif y.count(list(common)[0]) + y.count(list(common)[1]) != 4 and l[i][empty_rows[i][j]] == l[i][empty_rows[i][k]]:
                                    update(i, empty_rows[i][j], common, "nakedpair_row")
                                    changes += 1
                                    return
    
                             # Checking for X-wing - no need to do separately for column x-wing this code checks both column and row x-wing
                            for a in set(empty_columns[empty_rows[i][j]]).intersection(set(empty_columns[empty_rows[i][k]])):
                                common = list(l[a][empty_rows[i][j]].intersection(l[a][empty_rows[i][k]]).intersection(common))
                                if a != i and len(common) == 1:
                                    z = sum(list(map(lambda x: list(x) if type(x) is set else [], l[a, :])), []).count(common[0])
                                    b = sum(list(map(lambda x: list(x) if type(x) is set else [], l[:, empty_rows[i][j]])), []).count(common[0])
                                    c = sum(list(map(lambda x: list(x) if type(x) is set else [], l[:, empty_rows[i][k]])), []).count(common[0])
                                    if y.count(common[0]) + z == 4 and b + c > 4 or y.count(common[0]) + z > 4 and b + c == 4:
                                        update([i, a], [empty_rows[i][j], empty_rows[i][k]], common[0], "x-wing")
                                        changes += 1
                                        return
    
    
        # Checking if a number appears only once in a column
        for i in empty_columns.copy():
            y = sum(list(map(lambda x: list(x) if type(x) is set else [], l[:, i])), [])
            if y:
                num = min(y, key=y.count)
                if y.count(num) == 1:
                    for a in empty_columns[i]:
                        if num in l[int(a)][int(i)]:
                            update(a, i, num)
                            changes += 1
                            return
                else:
                    for j in range(len(empty_columns[i])-1):
                        for k in range(j+1, len(empty_columns[i])):
                            common = l[empty_columns[i][j]][i].intersection(l[empty_columns[i][k]][i])
                            # 2 cells have 2 numbers in common and no other number in common
                            if len(common) == 2:
                                # If the union has more than 2 elements - hiddenpair (not yet checked)
                                if len(l[empty_columns[i][j]][i].union(l[empty_columns[i][k]][i])) > 2 and y.count(list(common)[0]) + y.count(list(common)[1]) == 4:
                                    l[empty_columns[i][j]][i] = common
                                    l[empty_columns[i][k]][i] = common
                                    changes += 1
                                # If this condition is true then - nakedpair (not yet checked)
                                elif y.count(list(common)[0]) + y.count(list(common)[1]) != 4 and l[empty_columns[i][j]][i] == l[empty_columns[i][k]][i]:
                                    update(empty_columns[i][j], i, common, "nakedpair_column")
                                    changes += 1
                                    return
    
    
        # Checking if a number appears only once in a box
        for i in range(0, 9, 3):
            for j in range(0, 9, 3):
                y = sum(list(map(lambda x: list(x) if type(x) is set else [], l[(i // 3) * 3:(i // 3) * 3 + 3, (j // 3) * 3:(j // 3) * 3 + 3].flatten())), [])
                if y:
                    num = min(y, key=y.count)
                    if y.count(num) == 1:
                        for x in set(empty_rows.keys()) - (set(range(0, 9)) - set(range((i // 3) * 3, (i // 3) * 3 + 3))):
                            for y in set(empty_rows[x]) - (set(range(0, 9)) - set(range((j // 3) * 3, (j // 3) * 3 + 3))):
                                if num in l[x][y]:
                                    update(x, y, num)
                                    changes += 1
                                    return
                    else:
                        num = list(map(lambda x: list(x) if type(x) is set else [], l[(i // 3) * 3:(i // 3) * 3 + 3, (j // 3) * 3:(j // 3) * 3 + 3].flatten()))
                        num[0], num[1], num[2], num[3:] = set(sum(num[:3], [])), set(sum(num[3:6], [])), set(sum(num[6:9], [])), []
                        # num[0] has possibilities of the first row in the box, num[1] has possibilities of the second row in the box
                        box_possibilities = copy.deepcopy(num)
                        num[0], num[1], num[2] = num[0] - num[1] - num[2], num[1] - num[0] - num[2], num[2] - num[0] - num[1]
                        # num[0] has possibilities unique to the first row, num[1] has possibilities unique to the second row
                        for x in range(3):
                            row_possibilities = list(map(lambda a: list(a) if type(a) is set else [], l[x + i, :]))
                            # Possibilities of the rest of the row except this box
                            row_possibilities = sum(row_possibilities[:(j // 3) * 3] + row_possibilities[(j // 3) * 3 + 3:], [])
                            if num[x]:
                                for k in num[x].intersection(set(row_possibilities)):
                                    update(x + i, j, k, "locked_row")
                                    changes += 1
                                    return
                            # n has the list of numbers that appear only in this row inside this box not anywhere else in the row
                            # therefore remove this number from any other row inside the box as the number has to appear in this row
                            n = list(set(box_possibilities[x]) - set(row_possibilities))
                            for k in n:
                                if k in sum(list(map(list, box_possibilities[:x] + box_possibilities[x + 1:])), []):
                                    update(x + i, j, k, "box_locked_row")
                                    changes += 1
                                    return
    
                        # Repeating same process for columns
                        num = list(map(lambda x: list(x) if type(x) is set else [], l[(i // 3) * 3:(i // 3) * 3 + 3, (j // 3) * 3:(j // 3) * 3 + 3].transpose().flatten()))
                        num[0], num[1], num[2], num[3:] = set(sum(num[:3], [])), set(sum(num[3:6], [])), set(sum(num[6:9], [])), []
                        box_possibilities = copy.deepcopy(num)
                        num[0], num[1], num[2] = num[0] - num[1] - num[2], num[1] - num[0] - num[2], num[2] - num[0] - num[1]
                        for x in range(3):
                            col_possibilities = list(map(lambda a: list(a) if type(a) is set else [], l[:, x + j]))
                            # Possibilities of the rest of the column except this box
                            col_possibilities = sum(col_possibilities[:(i // 3) * 3] + col_possibilities[(i // 3) * 3 + 3:], [])
                            if num[x]:
                                for k in num[x]:
                                    if k in col_possibilities:
                                        update(i, x + j, k, "locked_column")
                                        changes += 1
                                        return
                            n = list(set(box_possibilities[x]) - set(col_possibilities))
                            for k in n:
                                if k in sum(list(map(list, box_possibilities[:x] + box_possibilities[x + 1:])), []):
                                    update(i, x + j, k, "box_locked_column")
                                    changes += 1
                                    return

    while True:
        changes = 0
        main()
        if changes == 0:
            break

    st.text("Solution")
    display(sudoku)
