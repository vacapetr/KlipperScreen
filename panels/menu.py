import gi
import logging

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

from KlippyGtk import KlippyGtk
from panels.screen_panel import ScreenPanel

logger = logging.getLogger("KlipperScreen.MenuPanel")

class MenuPanel(ScreenPanel):
    def initialize(self, panel_name, items):
        print("### Making a new menu")

        grid = self.arrangeMenuItems(items, 4)

        b = KlippyGtk.ButtonImage('back', 'Back')
        b.connect("clicked", self._screen._menu_go_back)
        grid.attach(b, 3, 1, 1, 1)

        self.panel = grid

    def arrangeMenuItems (self, items, columns, expandLast=False):
        grid = Gtk.Grid()
        grid.set_row_homogeneous(True)
        grid.set_column_homogeneous(True)

        l = len(items)
        i = 0
        for i in range(l):
            col = i % columns
            row = int(i/columns)
            width = 1

            if expandLast == True and i+1 == l and l%2 == 1:
                width = 2

            key = list(items[i])[0]
            logger.debug("Key: %s" % key)
            item = items[i][key]
            b = KlippyGtk.ButtonImage(
                item['icon'], item['name'], "color"+str((i%4)+1)
            )
            logger.debug("Item: %s" % item)
            if item['panel'] != False:
                b.connect("clicked", self.menu_item_clicked, item['panel'], item)
            elif item['method'] != False:
                params = item['params'] if item['params'] != False else {}
                if item['confirm'] != False:
                    b.connect("clicked", self._screen._confirm_send_action, item['confirm'], item['method'], params)
                else:
                    b.connect("clicked", self._screen._send_action, item['method'], params)
            else:
                b.connect("clicked", self._screen._go_to_submenu, key)

            grid.attach(b, col, row, width, 1)

            i += 1

        return grid
