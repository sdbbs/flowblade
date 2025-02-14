"""
    Flowblade Movie Editor is a nonlinear video editor.
    Copyright 2012 Janne Liljeblad.

    This file is part of Flowblade Movie Editor <http://code.google.com/p/flowblade>.

    Flowblade Movie Editor is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Flowblade Movie Editor is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Flowblade Movie Editor.  If not, see <http://www.gnu.org/licenses/>.
"""

"""
Module holds references to GUI widgets and offers some helper fuctions used in GUI creation.
"""

from gi.repository import Gtk, Gdk, GdkPixbuf

import pickle

import appconsts
import atomicfile
import editorpersistance
import respaths
import userfolders
import utils


# Editor window
editor_window = None

# Menu
editmenu = None

# Project data lists and related views.
media_list_view = None # This is guicomponents.MediaPanel (not the treeview)
bin_list_view = None
bin_panel = None
sequence_list_view = None

project_info_vbox = None

effect_select_list_view = None
effect_select_combo_box = None

render_out_folder = None

# Media tab
media_view_filter_selector = None

# Monitor
pos_bar = None

# Timeline
tline_display = None
tline_scale = None
tline_canvas = None
tline_render_strip = None
tline_scroll = None
tline_info = None # Shows save icon
tline_column = None
tline_left_corner = None
big_tc = None
comp_mode_launcher = None
monitor_widget = None
monitor_switch = None
# indexes match editmode values in editorstate.py
notebook_buttons = None

sequence_editor_b = None


# Theme colors
# Theme colors are given as 4 RGB tuples and string, ((LIGHT_BG), (DARK_BG), (SELECTED_BG), (DARK_SELECTED_BG), name)
_UBUNTU_COLORS = ((0.949020, 0.945098, 0.941176), (0.172, 0.172, 0.172), (0.941, 0.466, 0.274, 0.9), (0.951, 0.30, 0.0, 0.9), "Ubuntu")
_GNOME_COLORS = ((0.929412, 0.929412, 0.929412), (0.172, 0.172, 0.172), (0.28627451, 0.560784314, 0.843137255), (0.192, 0.361, 0.608), "Gnome")
_MINT_COLORS = ((0.839215686, 0.839215686, 0.839215686), (0.172, 0.172, 0.172), (0.556862745, 0.678431373, 0.439215686), (0.556862745, 0.678431373, 0.439215686), "Linux Mint")
_ARC_COLORS = ((0.960784, 0.964706, 0.968627), (0.266667, 0.282353, 0.321569), (0.321568627, 0.580392157, 0.88627451), (0.321568627, 0.580392157, 0.88627451), "Arc (theme)")
_FLOWBLADE_COLORS = ((0.960784, 0.964706, 0.968627), (0.266667, 0.282353, 0.321569), (0.065, 0.342, 0.66), (0.065, 0.342, 0.66), "Flowblade Theme")

_THEME_COLORS = (_UBUNTU_COLORS, _GNOME_COLORS, _MINT_COLORS, _ARC_COLORS, _FLOWBLADE_COLORS)

_CURRENT_THEME_COLORS_FILE = "currentcolors.data" # Used to communicate theme colors to tools like gmic.py running on separate process

LIGHT_GRAY_THEME_GRAY = ((50.3/255.0), (50.3/255.0), (59.9/255.0), 1.0)
LIGHT_GRAY_THEME_BG = (0.153, 0.153, 0.188, 1.0)
LIGHT_NEUTRAL_THEME_NEUTRAL = ((68.0/255.0), (68.0/255.0), (68.0/255.0), 1.0)
MID_NEUTRAL_THEME_NEUTRAL= ((54.0/255.0), (54.0/255.0), (54.0/255.0), 1.0)
DARKER_NEUTRAL_THEME_NEUTRAL = ((48.0/255.0), (48.0/255.0), (48.0/255.0), 1.0)

_selected_bg_color = None
_bg_color = None
_bg_unmodified_normal = None
_button_colors = None

def capture_references(new_editor_window):
    """
    Create shorter names for some of the frequently used GUI objects.
    """
    global editor_window, media_list_view, bin_list_view, sequence_list_view, pos_bar, \
    tline_display, tline_scale, tline_canvas, tline_scroll, tline_v_scroll, tline_info, \
    tline_column, play_b, effect_select_list_view, effect_select_combo_box, \
    project_info_vbox, big_tc, editmenu, notebook_buttons, tline_left_corner, \
    monitor_widget, bin_panel, monitor_switch, comp_mode_launcher, tline_render_strip

    editor_window = new_editor_window

    media_list_view = editor_window.media_list_view
    bin_list_view = editor_window.bin_list_view
    bin_panel = editor_window.bins_panel
    sequence_list_view = editor_window.sequence_list_view

    effect_select_list_view = editor_window.effect_select_list_view
    effect_select_combo_box = editor_window.effect_select_combo_box

    pos_bar = editor_window.pos_bar

    monitor_widget = editor_window.monitor_widget
    monitor_switch = editor_window.monitor_switch
    
    tline_display = editor_window.tline_display
    tline_scale = editor_window.tline_scale
    tline_canvas = editor_window.tline_canvas
    tline_render_strip = editor_window.tline_render_strip
    tline_scroll = editor_window.tline_scroller
    tline_info = editor_window.tline_info
    tline_column = editor_window.tline_column
    tline_left_corner = editor_window.left_corner
    comp_mode_launcher = editor_window.comp_mode_launcher

    big_tc = editor_window.big_TC

    editmenu = editor_window.uimanager.get_widget('/MenuBar/EditMenu')

def enable_save(project):
    if project.last_save_path != None:
        editor_window.uimanager.get_widget("/MenuBar/FileMenu/Save").set_sensitive(True)

# returns Gdk.RGBA color
def get_bg_color():
    return _bg_color

# returns Gdk.RGBA color
def get_selected_bg_color():
    return _selected_bg_color

def get_light_gray_light_color():
    return Gdk.RGBA(*LIGHT_GRAY_THEME_GRAY)
    
def get_light_gray_bg_in_cairo_rgb():
    return LIGHT_GRAY_THEME_BG

def get_light_neutral_color():
    return Gdk.RGBA(*LIGHT_NEUTRAL_THEME_NEUTRAL)

def get_mid_neutral_color():
    return Gdk.RGBA(*MID_NEUTRAL_THEME_NEUTRAL)
    
def get_darker_neutral_color():
    return Gdk.RGBA(*DARKER_NEUTRAL_THEME_NEUTRAL)
    
def get_bg_unmodified_normal_color():
    return _bg_unmodified_normal

def set_theme_colors():
    # Find out if theme color discovery works and set selected bg color apppropiately when
    # this is first called.
    global _selected_bg_color, _bg_color, _button_colors, _bg_unmodified_normal

    fallback_theme_colors = editorpersistance.prefs.theme_fallback_colors
    theme_colors = _THEME_COLORS[fallback_theme_colors]

    # Try to detect selected color and set from fallback if fails
    style = editor_window.bin_list_view.get_style_context()
    sel_bg_color = style.get_background_color(Gtk.StateFlags.SELECTED)

    r, g, b, a = unpack_gdk_color(sel_bg_color)
    if r == 0.0 and g == 0.0 and b == 0.0:
        print("Selected color NOT detected")
        if editorpersistance.prefs.theme == appconsts.LIGHT_THEME:
            c = theme_colors[2]
        else:
            c = theme_colors[3]
        _selected_bg_color = Gdk.RGBA(*c)
    else:
        print("Selected color detected")
        _selected_bg_color = sel_bg_color

    # Try to detect bg color and set frow fallback if fails
    style = editor_window.window.get_style_context()
    bg_color = style.get_background_color(Gtk.StateFlags.NORMAL)

    _bg_unmodified_normal = bg_color # this was used to work on grey, theme probably not necessary anymore

    r, g, b, a = unpack_gdk_color(bg_color)

    if r == 0.0 and g == 0.0 and b == 0.0:
        print("BG color NOT detected")
        if editorpersistance.prefs.theme == appconsts.LIGHT_THEME:
            c = theme_colors[0]
        else:
            c = theme_colors[1]
        _bg_color = Gdk.RGBA(*c)
        _button_colors = Gdk.RGBA(*c)
    else:
        print("BG color detected")
        _bg_color = bg_color
        _button_colors = bg_color

    # Adwaita and some others show big area of black without this, does not bother Ambient on Ubuntu
    editor_window.tline_pane.override_background_color(Gtk.StateFlags.NORMAL, get_bg_color())
    editor_window.media_panel.override_background_color(Gtk.StateFlags.NORMAL, get_bg_color())
    editor_window.mm_paned.override_background_color(Gtk.StateFlags.NORMAL, get_bg_color())
    
def unpack_gdk_color(gdk_color):
    return (gdk_color.red, gdk_color.green, gdk_color.blue, gdk_color.alpha)

def save_current_colors():
    # Used to communicate theme colors to tools like gmic.py running on separate process
    colors = (unpack_gdk_color(_selected_bg_color), unpack_gdk_color(_bg_color), unpack_gdk_color(_button_colors))
    save_file_path = _colors_data_path()
    with atomicfile.AtomicFileWriter(save_file_path, "wb") as afw:
        write_file = afw.get_file()
        pickle.dump(colors, write_file)

def load_current_colors():
    load_path = _colors_data_path()
    colors = utils.unpickle(load_path)
    
    sel, bg, button = colors
    global _selected_bg_color, _bg_color, _button_colors
    _selected_bg_color = Gdk.RGBA(*sel)
    _bg_color = Gdk.RGBA(*bg)
    _button_colors = Gdk.RGBA(*button)

def _colors_data_path():
    return userfolders.get_cache_dir() + _CURRENT_THEME_COLORS_FILE
  
def _print_widget(widget): # debug
    path_str = widget.get_path().to_string()
    path_str = path_str.replace("GtkWindow:dir-ltr.background","")
    path_str = path_str.replace("dir-ltr","")
    path_str = path_str.replace("vertical","")
    path_str = path_str.replace("horizontal","")
    path_str = path_str.replace("[1/2]","")
    path_str = path_str.replace("GtkVBox:. GtkVPaned:[2/2]. GtkHBox:. GtkHPaned:. GtkVBox:. GtkNotebook:[1/1]","notebook:")
    print(path_str)

def apply_theme(theme):
    if theme != appconsts.LIGHT_THEME:
        Gtk.Settings.get_default().set_property("gtk-application-prefer-dark-theme", True)
        
        # We dropped these themes and need to force change the pref for them.
        if theme == appconsts.FLOWBLADE_THEME or theme == appconsts.FLOWBLADE_THEME_GRAY:
            editorpersistance.prefs.theme = appconsts.FLOWBLADE_THEME_NEUTRAL
            theme = appconsts.FLOWBLADE_THEME_NEUTRAL
            editorpersistance.save()
            
        if theme == appconsts.FLOWBLADE_THEME_NEUTRAL:
            apply_gtk_css()
            
def apply_gtk_css():
    gtk_version = "%s.%s.%s" % (Gtk.get_major_version(), Gtk.get_minor_version(), Gtk.get_micro_version())
    if Gtk.get_major_version() == 3 and Gtk.get_minor_version() >= 22:
        print("Gtk version is " + gtk_version + ", Flowblade theme is available.")
    else:
        print("Gtk version is " + gtk_version + ", Flowblade theme only available for Gtk >= 3.22")
        editorpersistance.prefs.theme = appconsts.LIGHT_THEME
        editorpersistance.save()
        return False
        
    provider = Gtk.CssProvider.new()
    display = Gdk.Display.get_default()
    screen = display.get_default_screen()
    Gtk.StyleContext.add_provider_for_screen (screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    css_path = "/res/css3/gtk-flowblade-dark.css"

    provider.load_from_path(respaths.ROOT_PATH + css_path)

    return True

def get_default_filter_icon():
    return GdkPixbuf.Pixbuf.new_from_file(respaths.IMAGE_PATH + "filter.png")
    
def get_filter_group_icons(default_icon):
    group_icons = {}
    group_icons["Color"] = GdkPixbuf.Pixbuf.new_from_file(respaths.IMAGE_PATH + "color.png")
    group_icons["Color Effect"] = GdkPixbuf.Pixbuf.new_from_file(respaths.IMAGE_PATH + "color_filter.png")
    group_icons["Audio"] = GdkPixbuf.Pixbuf.new_from_file(respaths.IMAGE_PATH + "audio_filter.png")
    group_icons["Audio Filter"] = GdkPixbuf.Pixbuf.new_from_file(respaths.IMAGE_PATH + "audio_filter_sin.png")
    group_icons["Blur"] = GdkPixbuf.Pixbuf.new_from_file(respaths.IMAGE_PATH + "blur_filter.png")
    group_icons["Distort"] = GdkPixbuf.Pixbuf.new_from_file(respaths.IMAGE_PATH + "distort_filter.png")
    group_icons["Alpha"] = GdkPixbuf.Pixbuf.new_from_file(respaths.IMAGE_PATH + "alpha_filter.png")
    group_icons["Movement"] = GdkPixbuf.Pixbuf.new_from_file(respaths.IMAGE_PATH + "movement_filter.png")
    group_icons["Transform"] = GdkPixbuf.Pixbuf.new_from_file(respaths.IMAGE_PATH + "transform.png")
    group_icons["Edge"] = GdkPixbuf.Pixbuf.new_from_file(respaths.IMAGE_PATH + "edge.png")
    group_icons["Fix"] = GdkPixbuf.Pixbuf.new_from_file(respaths.IMAGE_PATH + "fix.png")
    group_icons["Fade"] = GdkPixbuf.Pixbuf.new_from_file(respaths.IMAGE_PATH + "fade_filter.png")
    group_icons["Artistic"] = default_icon
    group_icons["FILTER_MASK"] = GdkPixbuf.Pixbuf.new_from_file(respaths.IMAGE_PATH + "filter_mask.png")
    group_icons["Blend"] = GdkPixbuf.Pixbuf.new_from_file(respaths.IMAGE_PATH + "blend_filter.png")

    return group_icons