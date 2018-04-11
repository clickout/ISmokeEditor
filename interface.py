from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ObjectProperty
from kivy.core.window import Window

from unidecode import unidecode

from difflib import get_close_matches

import items


class ISmokeLayout(GridLayout):
    Window.size = (300, 600)
    items_scroll_view = ObjectProperty()
    search_text_input = ObjectProperty()
    amount_text_input = ObjectProperty()
    console = ObjectProperty()
    all_items_dict = items.Item.get_all_items()
    all_items_names = [item_name[1].name for item_name in all_items_dict.items()]

    def add_item(self):
        if self.items_scroll_view.adapter.selection:
            item_name = unidecode(self.items_scroll_view.adapter.selection[0].text.lower())
            selected_item = self.all_items_dict.get(item_name)
            amount = int(self.amount_text_input.text) if self.amount_text_input.text else 1
            selected_item.add(amount)
            self.console.text += str(selected_item) + " - přidáno {} položek.\n".format(amount)

    def sell_item(self):
        if self.items_scroll_view.adapter.selection:
            item_name = unidecode(self.items_scroll_view.adapter.selection[0].text.lower())
            selected_item = self.all_items_dict.get(item_name)
            amount = int(self.amount_text_input.text) if self.amount_text_input.text else 1
            try:
                selected_item.sell(amount)
            except ValueError as error:
                self.console.text += error.args[0] + '({})'.format(str(selected_item))
            else:
                self.console.text += str(selected_item) + " - prodáno {} položek.\n".format(amount)

    def search_list(self):
        if self.search_text_input.text:
            text = unidecode(self.search_text_input.text.lower())
            close_matches = get_close_matches(text, self.all_items_dict.keys(), 20, 0.3)
            new_data = [self.all_items_dict.get(item).name for item in close_matches]
            self.items_scroll_view.adapter.data = new_data
            self.items_scroll_view._trigger_reset_populate()
        else:
            self.items_scroll_view.adapter.data = self.all_items_names
            self.items_scroll_view._trigger_reset_populate()


class ISmokeItemEditorApp(App):

    def build(self):
        return ISmokeLayout()


if __name__ == '__main__':
    ISmokeItemEditorApp().run()
