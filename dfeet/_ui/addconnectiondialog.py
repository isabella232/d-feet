import gtk
from uiloader import UILoader

class AddConnectionDialog:
    RESPONSE_CANCEL = -1
    RESPONSE_CONNECT = 1

    def __init__(self, parent):
        ui = UILoader(UILoader.UI_ADDCONNECTIONDIALOG) 

        self.dialog = ui.get_root_widget()
        self.combo_entry = ui.get_widget('address_comboentry1')
        
        self.combo_entry.get_child().connect('activate', self.activate_combo)
        self.dialog.add_button('gtk-cancel', self.RESPONSE_CANCEL)
        self.dialog.add_button('gtk-connect', self.RESPONSE_CONNECT)

    def get_address(self):
        return self.combo_entry.get_active_text()

    def run(self):
        return self.dialog.run()

    def destroy(self):
        self.dialog.destroy()

    def activate_combo(self, user_data):
        self.dialog.response(self.RESPONSE_CONNECT)
        return True

    def set_model(self, model):
        self.combo_entry.set_model(model)
        self.combo_entry.set_text_column(0)

