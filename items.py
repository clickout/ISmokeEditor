import gspread
from oauth2client.service_account import ServiceAccountCredentials

from datetime import date

import unidecode


class Item(object):

    @staticmethod
    def open_spreadsheet():
        scope = ['https://spreadsheets.google.com/feeds']
        credentials = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
        gspread_creds = gspread.authorize(credentials)
        spreadsheet = gspread_creds.open_by_key('1m0Vhn2eDaGDAh5XcUzUvw2LCbHlHkju_bVnWsu60kW4')
        return spreadsheet

    @classmethod
    def get_all_items(cls):
        spreadsheet = cls.open_spreadsheet()
        all_items = {}
        for index, worksheet in enumerate(spreadsheet.worksheets()):
            items = worksheet.range(2, 1, worksheet.row_count, 4)
            for x in range(0, len(items), 4):
                if items[x + 3].value:
                    all_items[unidecode.unidecode(items[x].value).lower()] = cls.get_item_from_list(items[x:x + 4],
                                                                                                    index)
        return all_items

    @classmethod
    def get_item_from_list(cls, list_of_cells, index_of_worksheet):
        name = list_of_cells[0].value
        price = list_of_cells[1].value
        bonus = list_of_cells[2].value
        quantity = list_of_cells[3].value
        row = list_of_cells[0].row
        return cls(name, price, bonus, quantity, row, index_of_worksheet)

    def __init__(self, name, price, bonus, quantity, row, index_of_worksheet):
        self.name = name
        self.price = get_digit_from_str(price)
        self.bonus = get_digit_from_str(bonus)
        self.quantity = int(quantity)
        self.row = row
        self.index_of_worksheet = index_of_worksheet

    def __repr__(self):
        return "Item(name = {}, price = {}, bonus = {}, " \
               "quantity = {}, row = {}, index = {})".format(self.name, self.price, self.bonus, self.quantity,
                                                             self.row, self.index_of_worksheet)

    def __str__(self):
        return "{} - cena: {},- Kč, provize: {},- Kč, množství: {}.".format(self.name, self.price, self.bonus,
                                                                            self.quantity)

    def sell(self, number_of_sold_items=1):
        spreadsheet = self.open_spreadsheet()
        worksheet = spreadsheet.get_worksheet(self.index_of_worksheet)
        if self.quantity - number_of_sold_items < 0:
            raise ValueError('Na sklade neni dostatek zbozi.')
        else:
            self.quantity -= number_of_sold_items
            worksheet.update_cell(self.row, 4, self.quantity)
            self.update_history_of_changes(-number_of_sold_items, worksheet)

    def add(self, number_of_added_items=1):
        self.quantity += number_of_added_items
        spreadsheet = self.open_spreadsheet()
        worksheet = spreadsheet.get_worksheet(self.index_of_worksheet)
        worksheet.update_cell(self.row, 4, self.quantity)
        self.update_history_of_changes(number_of_added_items, worksheet)

    def update_history_of_changes(self, change, worksheet):
        index_of_last_nonempty_col = len(worksheet.row_values(1))
        current_date = "{}.{}.".format(date.today().day, date.today().month)
        if worksheet.cell(1, index_of_last_nonempty_col).value != current_date:
            if index_of_last_nonempty_col == worksheet.col_count:
                worksheet.add_cols(1)
            index_of_last_nonempty_col += 1
            worksheet.update_cell(1, index_of_last_nonempty_col, current_date)
        curr_value = (int(worksheet.cell(self.row, index_of_last_nonempty_col).value)
                      if worksheet.cell(self.row, index_of_last_nonempty_col).value.strip() else 0)
        worksheet.update_cell(self.row, index_of_last_nonempty_col, str(curr_value + change))


def get_digit_from_str(string):
    number = ""
    for letter in string:
        if letter.isdigit():
            number += letter
    if number:
        return int(number)
    else:
        return 0
