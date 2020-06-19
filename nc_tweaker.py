import sys
import re
import os
import math

file_path = ''
file_base_name = ''
file = None


def main():
    global file_path, file_base_name, file
    if len(sys.argv) < 2:
        print('no file dropped')
        kill()
    file_path, file_base_name, file = open_file()
    display_menu()
    func = input('Enter Tweak #: ')
    new_code = tweak(func)
    save_file(new_code)
    kill()


def open_file():
    path = sys.argv[1]
    base = os.path.basename(path)
    with open(path) as src:
        f = src
        f.lines = f.readlines()
    if f.lines[0][0] != '%' and f.lines[-1][-1]:
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


def tweak(func):
    code = func()
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

    use_origin = None
    while use_origin != 'y' or use_origin != 'n':
        use_origin = input('use for wfo origin? (y or n): ')
    if use_origin == 'n':
        center_x = get_value('center_x = ', float)
        center_y = get_value('center_y = ', float)
        center = center_x, center_y

    code = []
    lines = [Line(line) for line in f.lines]
    for line in lines:
        if line.codes


def rotate_(point, angle, center_point):
    angle = math.radians(angle)
    x, y = point
    center_x, center_y = center_point

    sin = math.sin(angle)
    cos = math.cos(angle)
    temp_x = x - center_x
    temp_y = y - center_y
    rotated_temp_x = temp_x * cos + temp_y * sin
    rotated_temp_y = (temp_x * -1) * sin + temp_y * cos

    rotated_x = round(rotated_temp_x + center_x, 4)
    rotated_y = round(rotated_temp_y + center_y, 4)
    return rotated_x, rotated_y


def translate():
    """shift x,y values"""
    pass


def translate_(point, translation):
    x, y = point
    trans_x, trans_y = translation
    return x + trans_x, y + trans_y


def change_tool_num():
    """scan for all tools #s in the file - walk user through assigning new values for each one
    replace all that are changed"""
    pass


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
        self.tweaked_code_block = None
        self.code_matches = self.code_pattern.finditer(code_block)
        self.codes = {match.group('code'): float(match.group('val')) for match in self.code_matches}

    def rotate_(self, angle, center_point):
        location_codes = ['X', 'x', 'Y', 'y']
        arc_codes = ['I', 'i', 'J', 'j']
        for code in location_codes:
            if code in self.codes:
                if not self.tweaked_code_block:
                    self.tweaked_code_block = self.code_block
                self.tweaked_code_block = change_code_string(self.tweaked_code_block, )



        angle = math.radians(angle)
        for location in
        x, y = point
        center_x, center_y = center_point

        sin = math.sin(angle)
        cos = math.cos(angle)
        temp_x = x - center_x
        temp_y = y - center_y
        rotated_temp_x = temp_x * cos + temp_y * sin
        rotated_temp_y = (temp_x * -1) * sin + temp_y * cos

        rotated_x = round(rotated_temp_x + center_x, 4)
        rotated_y = round(rotated_temp_y + center_y, 4)
        return rotated_x, rotated_y

if __name__ == '__main__':
    main()
