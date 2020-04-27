import textwrap
from io import BytesIO

import requests
from PIL import ImageDraw, ImageFont, Image
from settings import WORK_DIR

TICKET_DIR = WORK_DIR / 'ticket'
TICKET_TEMPLATE = str(TICKET_DIR / 'Template.jpg')
FONT = str(TICKET_DIR / 'MyriadPro-Regular.otf')

BLACK_COLOR = (0, 0, 0)
GREEN_COLOR = (64, 111, 88)
GRAY_COLOR = (101, 101, 101)
DARK_PURPLE_COLOR = (35, 36, 51)

ALIGN_CENTER = 'align_center'
ALIGN_RIGHT = 'align_right'

TITLE_FONT_SIZE = 47
TITLE_OFFSET = (75, 334)
TITLE_LINE_WIDTH = 610
TITLE_CHARS_PER_LINE = 25

AVATAR_OFFSET = (88, 487)
AVATAR_SIZE = 210

NAME_FONT_SIZE = 47
NAME_OFFSET = (365, 510)
NAME_LINE_WIDTH = 380
NAME_CHARS_PER_LINE = 15

LOCATION_FONT_SIZE = 24
LOCATION_OFFSET = (75, 750)
LOCATION_LINE_WIDTH = 750
LOCATION_CHARS_PER_LINE = 65

NOTE_FONT_SIZE = 14
NOTE_OFFSET = (75, 787)
NOTE_LINE_WIDTH = 750
NOTE_CHARS_PER_LINE = 150


class TicketMaker:
    """ Класс создания билета на мероприятие по шаблону """
    def __init__(self):
        self.template = Image.open(str(TICKET_TEMPLATE))
        self.draw = ImageDraw.Draw(im=self.template, mode=self.template.mode)

    def write(self, text, xy, font_size, color=BLACK_COLOR, line_width=None, chars_per_line=None, align=None):
        """
        Размещение текста на шаблоне по заданным параметрам

        :param str text: Размещаемый текст
        :param tuple xy: Координаты размещения в виде (x, y)
        :param int font_size: Размер шрифта
        :param tuple color: RGB-цвет шрифта в виде (R, G, B). По умолчанию - черный (BLACK_COLOR).
        :param int line_width: Ширина строки в пикселях
        :param int chars_per_line: Максимальное число символов в строке
        :param str align: Выравнивание относительно края
        """
        x, y = xy
        font = ImageFont.truetype(font=FONT, size=font_size)
        line_spacing = font_size * 0.2
        line_width = line_width or font.getsize(text)[0]
        chars_per_line = chars_per_line or len(text)
        for line in textwrap.wrap(text=text, width=chars_per_line):
            if align == ALIGN_CENTER:
                text_position = ((line_width - font.getsize(line)[0]) / 2 + x, y)
            elif align == ALIGN_RIGHT:
                text_position = (line_width - font.getsize(line)[0], y)
            else:
                text_position = (x, y)
            self.draw.text(xy=text_position, text=line, font=font, fill=color)
            y += font.getsize(line)[1] + line_spacing

    def write_title(self, title):
        """ Размещение названия мероприятия """
        self.write(text=title, xy=TITLE_OFFSET, font_size=TITLE_FONT_SIZE, line_width=TITLE_LINE_WIDTH,
                   chars_per_line=TITLE_CHARS_PER_LINE, color=GREEN_COLOR, align=ALIGN_CENTER)

    def write_name(self, name):
        """ Размещение имени посетителя """
        self.write(text=name, xy=NAME_OFFSET, font_size=NAME_FONT_SIZE, line_width=NAME_LINE_WIDTH,
                   chars_per_line=NAME_CHARS_PER_LINE, color=DARK_PURPLE_COLOR)

    def write_location(self, location):
        """ Размещение места проведения """
        self.write(text=location, xy=LOCATION_OFFSET, font_size=LOCATION_FONT_SIZE, line_width=LOCATION_LINE_WIDTH,
                   chars_per_line=LOCATION_CHARS_PER_LINE, color=GRAY_COLOR, align=ALIGN_RIGHT)

    def write_note(self, note):
        """ Размещение примечания """
        self.write(text=note, xy=NOTE_OFFSET, font_size=NOTE_FONT_SIZE, line_width=NOTE_LINE_WIDTH,
                   chars_per_line=NOTE_CHARS_PER_LINE, color=GRAY_COLOR, align=ALIGN_RIGHT)

    def draw_avatar(self, ava_str):
        """
        Размещение аватара
        :param str ava_str: Строка, относительно которой будет формироваться аватар
        """
        response = requests.get(f'https://api.adorable.io/avatars/{AVATAR_SIZE}/{ava_str}')
        avatar = Image.open(BytesIO(response.content))
        self.template.paste(avatar, AVATAR_OFFSET)

    def show(self):
        """ Показать заполненный шаблон """
        self.template.show()

    @property
    def image_io(self):
        """
        Получить объект файла билета.

        :rtype IOBytes
        """
        _t = BytesIO()
        self.template.save(_t, 'png')
        _t.seek(0)
        return _t


if __name__ == '__main__':

    title = 'Конференция Moscow Python Meetup №73'
    location = '1 апреля 2020 г., БЦ "Олимпия Парк", Ленинградское ш. 39Ас2'
    note = 'Регистрация с 10:00 до 11:00'
    name = 'Владимир'

    ticket = TicketMaker()
    ticket.write_title(title=title)
    ticket.write_name(name=name)
    ticket.write_location(location=location)
    ticket.write_note(note=note)
    ticket.draw_avatar('gfdgdfghfd')
    ticket.show()


