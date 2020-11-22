import gi
import logging

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

from KlippyGtk import KlippyGtk
from KlippyGcodes import KlippyGcodes
from panels.screen_panel import ScreenPanel

logger = logging.getLogger("KlipperScreen.FanPanel")

class FanPanel(ScreenPanel):
    user_selecting = False

    def initialize(self, panel_name):
        _ = self.lang.gettext

        grid = KlippyGtk.HomogeneousGrid()

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box.set_hexpand(True)

        adj = Gtk.Adjustment(0, 0, 100, 1, 5, 0)
        self.labels["scale"] = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adj)
        self.labels["scale"].set_value(0)
        self.labels["scale"].set_hexpand(True)
        self.labels["scale"].connect("value-changed", self.select_fan_speed)
        self.labels["scale"].get_style_context().add_class("fan_slider")
        box.add(self.labels["scale"])

        self.labels["fanoff"] = KlippyGtk.ButtonImage("fan-off", _("Fan Off"))
        self.labels["fanoff"].get_style_context().add_class("color1")
        self.labels["fanoff"].connect("clicked", self.set_fan_on, False)
        self.labels["fanon"] = KlippyGtk.ButtonImage("fan", _("Fan On"))
        self.labels["fanon"].get_style_context().add_class("color3")
        self.labels["fanon"].connect("clicked", self.set_fan_on, True)

        self.labels["apply"] = KlippyGtk.ButtonImage("resume", _("Set Speed"))
        self.labels["apply"].get_style_context().add_class("color2")
        self.labels["apply"].connect("clicked", self.set_fan_speed)
        self.labels["cancel"] = KlippyGtk.ButtonImage("stop", _("Cancel Change"))
        self.labels["cancel"].get_style_context().add_class("color4")
        self.labels["cancel"].connect("clicked", self.cancel_select_fan_speed)
        self.labels["cancel"].hide()

        grid.attach(Gtk.Label(), 0, 0, 1, 1)
        grid.attach(box, 0, 1, 4, 1)
        grid.attach(self.labels["fanoff"], 0, 2, 1, 1)
        grid.attach(self.labels["fanon"], 1, 2, 1, 1)

        b = KlippyGtk.ButtonImage('back', _('Back'))
        b.connect("clicked", self._screen._menu_go_back)
        grid.attach(b,3,2,1,1)

        self.panel = grid
        self._screen.add_subscription(panel_name)

    def process_update(self, data):
        if "fan" in data and "speed" in data["fan"] and self.user_selecting == False:
            self.labels["scale"].disconnect_by_func(self.select_fan_speed)
            self.labels["scale"].set_value(float(int(float(data["fan"]["speed"]) * 100)))
            self.labels["scale"].connect("value-changed", self.select_fan_speed)

    def select_fan_speed(self, widget):
        if self.user_selecting == True:
            return

        self.user_selecting = True
        self.panel.attach(self.labels["apply"], 3, 0, 1, 1)
        self.panel.attach(self.labels["cancel"], 0, 0, 1, 1)
        self._screen.show_all()

    def cancel_select_fan_speed(self, widget):
        self.user_selecting = False
        self.panel.remove(self.labels["apply"])
        self.panel.remove(self.labels["cancel"])


    def set_fan_speed(self, widget):
        self._screen._ws.klippy.gcode_script(KlippyGcodes.set_fan_speed(self.labels['scale'].get_value()))
        self.cancel_select_fan_speed(widget)

    def set_fan_on(self, widget, fanon):
        speed = 100 if fanon == True else 0
        self.labels["scale"].disconnect_by_func(self.select_fan_speed)
        self.labels["scale"].set_value(speed)
        self.labels["scale"].connect("value-changed", self.select_fan_speed)
        self._screen._ws.klippy.gcode_script(KlippyGcodes.set_fan_speed(speed))
