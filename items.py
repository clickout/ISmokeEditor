"""This module reads a spreadsheet of products from shop and defines their properties.

Everything is based on our custom spreasheed with a given format.

Every line of sheet corresponds to one product which will be saved as instance ouf our defined class Item.
With these atributes and methods we can create various features in the final app. Such as selling/adding products, or
exporting all missing products from stock to a list etc...
"""
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from datetime import date

import unidecode


class Item(object):
   """Every instance of this class will correspond to one product from our spreadsheet.
   
   This spreadsheet is made from multiple sheets, with diffrent kind of products. Every sheet is in the same format.
   Name of the product is in the first column, second - prices of one piece, third - bonus for salesman, forth is the amount
   of items in stock.
   
   Reading and writing to these sheets is done by Google Spreadsheet API(gspread)
   """
   @staticmethod
    def open_spreadsheet():
        """This method returns opened spreadsheet as instance of class defined by gspread"""
        scope = ['https://spreadsheets.google.com/feeds']
        credentials = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
        gspread_creds = gspread.authorize(credentials)
        spreadsheet = gspread_creds.open_by_key('1m0Vhn2eDaGDAh5XcUzUvw2LCbHlHkju_bVnWsu60kW4')
        return spreadsheet

    @classmethod
    def get_all_items(cls):
        """Reads all sheets and returns dictionary of all products.
        
        Key is name of product in lowercase and with no special charcaters for easier accesing.
        The value of every key is a instance of this class.
        """
        spreadsheet = cls.open_spreadsheet()
        all_items = {}
        for index, worksheet in enumerate(spreadsheet.worksheets()): # Works for any number of sheets in spreadsheet.
            whole_list_of_cells = worksheet.range(2, 1, worksheet.row_count, 4) # First row has only titles of colmuns so its not included.
            for x in range(0, len(whole_list_of_cells), 4):
                if whole_list_of_cells[x + 3].value: # This avoids empty rows
                    all_items[unidecode.unidecode(whole_list_of_cells[x].value).lower()] = 
                    cls.get_item_from_list(whole_list_of_cells[x:x + 4], index)
        return all_items

    @classmethod
    def get_item_from_list(cls, list_of_cells, index_of_worksheet):
        """A custom constructor which returns instance of this class from row of 4 cells used by get_all_items clsmethod"""
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
        return "{} - price: {},- Czk, bonus {},- Czk, quantity: {}.".format(self.name, self.price, self.bonus,
                                                                            self.quantity)

    def sell(self, number_of_sold_items=1):
        """Method used when we sell a product.
        
        Updates the amount of items in stock(quantity) of the particular product and writes updated amount to the sheet.
        Also records when and how much we sold to the sheet to the rightmost column.
        """
        spreadsheet = self.open_spreadsheet()
        worksheet = spreadsheet.get_worksheet(self.index_of_worksheet)
        if self.quantity - number_of_sold_items < 0:
            raise ValueError("There aren't enough items in stock.")
        else:
            self.quantity -= number_of_sold_items
            worksheet.update_cell(self.row, 4, self.quantity)
            self.update_history_of_changes(-number_of_sold_items, worksheet)

    def add(self, number_of_added_items=1):
        """Method used when we add a items of product to stock. See docstring of method sell for additional info"""
        self.quantity += number_of_added_items
        spreadsheet = self.open_spreadsheet()
        worksheet = spreadsheet.get_worksheet(self.index_of_worksheet)
        worksheet.update_cell(self.row, 4, self.quantity)
        self.update_history_of_changes(number_of_added_items, worksheet)

    def update_history_of_changes(self, change, worksheet):
        """Records the changes made to the amount of items at stock in one day.
        
        Creats a new column with current date at first cell. And below the changes to corresponding products.
        This change can be modified throughout the day, but only the final change will be stored at the end of the day.
        """
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
    """Function which filters out mistakes made in sheet."""
    number = ""
    for letter in string:
        if letter.isdigit():
            number += letter
    if number:
        return int(number)
    else:
        return 0
