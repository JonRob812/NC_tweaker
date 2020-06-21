import sys
import re
import os
import math

file_path = ''
file_base_name = ''
file = None

location_codes = ['X', 'Y']
arc_codes = ['I', 'J']


def main():
    global file_path, file_base_name, file
    if len(sys.argv) < 2:
        print('no file dropped')
        kill()
    file_path, file_base_name, file = open_file()
    display_menu()
    menu_key = get_value('', int)
    func = menu_items[menu_key][1]
    new_code = tweak(func, file)
    save_file(new_code)
    kill()


def open_file():
    path = sys.argv[1]
    base = os.path.basename(path)
    with open(path) as src:
        f = src
        f.raw_lines = f.readlines()
        f.raw_lines = [line.upper() for line in f.raw_lines]
        f.lines = [Line(line) for line in f.raw_lines]
    if f.raw_lines[0][0] != '%' and f.raw_lines[-1][-1]:
        print('invalid file dropped')
        kill()
    return path, base, f


def save_file(new_code):
    with open('tweaked_' + file_base_name, 'w') as new_file:
        for line in new_code:
            new_file.write(line)


def kill():
    input('press enter to terminate')
    exit()


def display_menu():
    for k in menu_items:
        print(k, menu_items[k][0])


def tweak(func, f):
    code = func(f)
    return code


def get_value(help_string, type_):
    value = None
    while not value:
        try:
            value = type_(input(help_string))
        except ValueError:
            pass
    return value


def rotate(f):
    """rotate the x,y location about desired location relative to wfo
    rotate the i,j values about 0,0 opposite way"""

    center = 0, 0
    angle = get_value('angle: ', float)

    use_origin = input('use wfo origin for center? (y or n): ')
    print(use_origin)
    if use_origin == 'n':
        center_x = get_value('center_x = ', float)
        center_y = get_value('center_y = ', float)
        center = center_x, center_y


    find_modals(f.lines)

    for line in f.lines:
        line.rotate_(angle, center)
    return [x.tweaked_code_block for x in f.lines]


def find_modals(lines):
    modal_x, modal_y = None, None
    position_lines = [x for x in lines if 'X' in x.codes or 'Y' in x.codes]
    for line in position_lines:

        if 'X' in line.codes:
            modal_x = line.codes['X']
        else:
            line.codes['X'] = modal_x
            line.insert = 'X'
        if 'Y' in line.codes:
            modal_y = line.codes['Y']
        else:
            line.codes['Y'] = modal_y
            line.insert = 'Y'

        if not isinstance(modal_x, float) or not isinstance(modal_y, float):
            print('First location missing X or Y - Aborting')
            kill()


def translate(f):
    print('Enter translation values')
    x_shift = get_value('X ', float)
    y_shift = get_value('Y ', float)
    for line in f.lines:
        line.translate_(x_shift, y_shift)
    return [x.tweaked_code_block for x in f.lines]


def change_tool_num(f):
    """scan for all tools #s in the file - walk user through assigning new values for each one
    replace all that are changed"""
    f.t_codes = []
    f.h_codes = []
    f.d_codes = []
    for line in f.lines:
        line.matches = []
        for match in line.code_matches_2:
            line.matches.append(match)
            if match.group('code') == 'T':
                f.t_codes.append([match.group('word'), match.group('code'), match.group('val'), match])
            if match.group('code') == 'H':
                f.h_codes.append([match.group('word'), match.group('code'), match.group('val'), match])
            if match.group('code') == 'D':
                f.d_codes.append([match.group('word'), match.group('code'), match.group('val'), match])
    distinct_t = set([t[0] for t in f.t_codes])
    distinct_d = set([d[0] for d in f.d_codes])
    offset_guess = []
    d_plus = 0
    for d in distinct_d:
        for t in distinct_t:
            if int(d[1:]) == int(t[1:]):
                print('same tool and D offset numbers')
    for d in distinct_d:
        for t in distinct_t:
            for i in range(1, 10):
                d_val, t_val = int(d[1:]), int(t[1:])
                d_t_diff = d_val - t_val
                if not d_t_diff % (i*10):
                    offset_guess = d_t_diff
                    break
    print(f'I think the D number is +{offset_guess} from T number, am I correct?')
    correct_guess = get_value('y or n\n', str).upper()
    if correct_guess == 'Y':
        d_plus = offset_guess
    elif correct_guess == 'N':
        d_plus = get_value('enter correct D+ amount\n', int)
    else:
        kill()
    use_same = get_value('use same D+ for new tool numbers? (y or n)\n', str).upper()
    if use_same == 'Y':
        new_d_plus = d_plus
    elif use_same == 'N':
        new_d_plus = get_value('enter new D+ amount\n', int)
    else:
        new_d_plus = -1
        kill()

    new_tool_key = {}
    new_tool_key_filled_correctly = False
    while not new_tool_key_filled_correctly:
        print('enter new tool numbers')
        for t in distinct_t:
            new_t = -1
            while new_t < 0:
                new_t = get_value(f'{t} = T', int)
                if new_t < 0:
                    print('please enter positive integer')
            new_tool_key[int(t[1:])] = new_t
        distinct_new_tools = set([new_tool_key[v] for v in new_tool_key])
        if len(distinct_new_tools) != len(new_tool_key):
            print('duplicate tool numbers - please enter unique integers')
            pass
        else:
            new_tool_key_filled_correctly = True
    for line in f.lines:
        line.change_tool_numbers_(new_tool_key, d_plus, new_d_plus)
    return [line.tweaked_code_block for line in f.lines]


def change_wfo():
    """scan for wfo offsets, walk user through reassigning"""
    pass


def split():
    """split at certain tool or line number"""
    pass


menu_items = {
    1: ('rotate', rotate),
    2: ('translate', translate),
    3: ('change tool number', change_tool_num),
    4: ('change work offset', change_wfo),
    5: ('split', split)
}


def change_code_string(string, start, end, new_value):
    return string[:start] + new_value + string[end:]


class Line:
    code_pattern = re.compile(r"(?P<word>(?P<code>[A-z])(?P<val>-?\d*\.?\d+\.?))")

    def __init__(self, code_block):
        self.code_block = code_block
        self.tweaked_code_block = code_block
        self.code_matches = self.code_pattern.finditer(code_block)
        self.code_matches_2 = self.code_pattern.finditer(code_block)
        self.codes = {match.group('code'): float(match.group('val')) for match in self.code_matches}
        self.insert = None

    def rotate_(self, angle, center_point):
        angle = math.radians(angle)
        if 'X' in self.codes:
            if self.codes.get('G') == 28:
                pass
            else:
                x, y = self.codes['X'], self.codes['Y']
                point = rotate_point((x, y), angle, center_point)
                self.codes['X'] = str(point[0])
                self.codes['Y'] = str(point[1])
        if 'I' in self.codes or 'J' in self.codes:
            i, j = 0, 0
            if 'I' in self.codes:
                i = self.codes['I']
            if 'J' in self.codes:
                j = self.codes['J']
            arc_point = rotate_point((i, j), angle)
            if 'I' in self.codes:
                self.codes['I'] = str(arc_point[0])
            if 'J' in self.codes:
                self.codes['J'] = str(arc_point[1])
        for code in self.codes:
            if code in ['X', 'Y', 'I', 'J']:
                rotate_code_block(self)

    def translate_(self, x, y):
        if self.codes.get('G') == 28:
            pass
        else:
            x_replace = ''
            y_replace = ''

            for match in self.code_matches_2:
                if match.group('code') == 'X':
                    x_replace = match.group('word')
                if match.group('code') == 'Y':
                    y_replace = match.group('word')

            if self.codes.get('X') is not None:
                self.codes['X'] = round(self.codes['X'] + x, 4)
                self.tweaked_code_block = self.tweaked_code_block.replace(x_replace, 'X' + str(self.codes['X']))
            if self.codes.get('Y') is not None:
                self.codes['Y'] = round(self.codes['Y'] + y, 4)
                self.tweaked_code_block = self.tweaked_code_block.replace(y_replace, 'Y' + str(self.codes['Y']))

    def change_tool_numbers_(self, new_tools, original_d, new_d): #TODO we found the off set but we ned to match them to orignal for renumberind d correctly
        for code in self.codes:
            if code == 'T':
                self.tweaked_code_block = self.tweaked_code_block.\
                    replace('T' + str(int(self.codes['T'])), 'T' + str(new_tools[int(self.codes['T'])]))
            if code == 'D':
                tool_num = self.codes['D'] - original_d
                self.tweaked_code_block = self.tweaked_code_block.\
                    replace('D' + str(int(self.codes['D'])), 'D' + str(new_tools[tool_num] + new_d))
            if code == 'H':
                self.tweaked_code_block = self.tweaked_code_block. \
                    replace('H' + str(int(self.codes['H'])), 'H' + str(new_tools[int(self.codes['H'])]))






def rotate_code_block(line):
    x_y_insert_string = 'X' + str(line.codes['X']) + ' Y' + str(line.codes['Y'])
    inserted = False
    if line.codes.get('G') == 28:
        pass
    else:
        for match in line.code_matches_2:
            if match.group('code') in arc_codes:
                new_code_word = match.group('code') + str(line.codes[match.group('code')])
                line.tweaked_code_block = line.tweaked_code_block.replace(match.group('word'), new_code_word)
            if not line.insert:
                if match.group('code') == 'Y':
                    line.tweaked_code_block = line.tweaked_code_block.replace(match.group('word'), '')
            if match.group('code') == line.insert:
                continue
            if match.group('code') in location_codes:
                if not inserted:
                    line.tweaked_code_block = line.tweaked_code_block.replace(match.group('word'), x_y_insert_string)
                    inserted = True


def rotate_point(point, angle, center=(0, 0)):
    x, y = point
    center_x, center_y = center
    sin = math.sin(angle)
    cos = math.cos(angle)
    temp_x = x + center_x
    temp_y = y + center_y
    rotated_temp_x = temp_x * cos + temp_y * sin
    rotated_temp_y = (temp_x * -1) * sin + temp_y * cos
    x = round(rotated_temp_x - center_x, 4)
    if x == 0:
        x = abs(x)
    y = round(rotated_temp_y - center_y, 4)
    if y == 0:
        y = abs(y)
    return x, y


def translate_point(point, translation):
    x, y = point
    trans_x, trans_y = translation
    return x + trans_x, y + trans_y


if __name__ == '__main__':
    main()
