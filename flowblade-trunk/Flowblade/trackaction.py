"""
    Flowblade Movie Editor is a nonlinear video editor.
    Copyright 2014 Janne Liljeblad.

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
    along with Flowblade Movie Editor. If not, see <http://www.gnu.org/licenses/>.
"""

"""
This module handles track actions; mute, change active state, size change.
"""

from gi.repository import GLib

import appconsts
import audiomonitoring
import dialogutils
import gui
import guicomponents
import editorstate
#import edit
import editorpersistance
from editorstate import get_track
from editorstate import current_sequence
from editorstate import PROJECT
from editorstate import PLAYER
import snapping
import tlinewidgets
import updater

# --------------------------------------- menu events
def _track_menu_item_activated(widget, data):
    track, item_id, selection_data = data
    handler = POPUP_HANDLERS[item_id]
    if selection_data == None:
        handler(track)
    else:
        handler(track, selection_data)
        
def lock_track(track_index):
    track = get_track(track_index)
    track.edit_freedom = appconsts.LOCKED
    updater.repaint_tline()

def unlock_track(track_index):
    track = get_track(track_index)
    track.edit_freedom = appconsts.FREE
    updater.repaint_tline()

def set_track_high_height(track_index, is_retry=False):
    track = get_track(track_index)
    track.height = appconsts.TRACK_HEIGHT_HIGH

    # Check that new height tracks can be displayed and cancel if not.
    new_h = current_sequence().get_tracks_height()
    allocation = gui.tline_canvas.widget.get_allocation()
    x, y, w, h = allocation.x, allocation.y, allocation.width, allocation.height

    if new_h > h and is_retry == False:
        current_paned_pos = gui.editor_window.app_v_paned.get_position()
        new_paned_pos = current_paned_pos - (new_h - h) - 5
        gui.editor_window.app_v_paned.set_position(new_paned_pos)
        GLib.timeout_add(200, lambda: set_track_high_height(track_index, True))
        return False
    
    allocation = gui.tline_canvas.widget.get_allocation()
    x, y, w, h = allocation.x, allocation.y, allocation.width, allocation.height
    
    if new_h > h:
        track.height = appconsts.TRACK_HEIGHT_SMALL
        dialogutils.warning_message(_("Not enough vertical space on Timeline to expand track"), 
                                _("Maximize or resize application window to get more\nspace for tracks if possible."),
                                gui.editor_window.window,
                                True)
        return False

    tlinewidgets.set_ref_line_y(gui.tline_canvas.widget.get_allocation())
    gui.tline_column.init_listeners()
    updater.repaint_tline()

    return False

def set_track_normal_height(track_index, is_retry=False, is_auto_expand=False):
    track = get_track(track_index)
    track.height = appconsts.TRACK_HEIGHT_NORMAL

    # Check that new height tracks can be displayed and cancel if not.
    new_h = current_sequence().get_tracks_height()
    allocation = gui.tline_canvas.widget.get_allocation()
    x, y, w, h = allocation.x, allocation.y, allocation.width, allocation.height

    if new_h > h and is_retry == False:
        current_paned_pos = gui.editor_window.app_v_paned.get_position()
        new_paned_pos = current_paned_pos - (new_h - h) - 5
        gui.editor_window.app_v_paned.set_position(new_paned_pos)
        GLib.timeout_add(200, lambda: set_track_normal_height(track_index, True, is_auto_expand))
        return False
    
    allocation = gui.tline_canvas.widget.get_allocation()
    x, y, w, h = allocation.x, allocation.y, allocation.width, allocation.height
    
    if new_h > h:
        if is_auto_expand == True:
            return False
        
        track.height = appconsts.TRACK_HEIGHT_SMALL
        dialogutils.warning_message(_("Not enough vertical space on Timeline to expand track"), 
                                _("Maximize or resize application window to get more\nspace for tracks if possible."),
                                gui.editor_window.window,
                                True)
        return False

    tlinewidgets.set_ref_line_y(gui.tline_canvas.widget.get_allocation())
    gui.tline_column.init_listeners()
    updater.repaint_tline()

    return False

def set_track_small_height(track_index):
    track = get_track(track_index)
    track.height = appconsts.TRACK_HEIGHT_SMALL
    if editorstate.SCREEN_HEIGHT < 863:
        track.height = appconsts.TRACK_HEIGHT_SMALLEST
    
    tlinewidgets.set_ref_line_y(gui.tline_canvas.widget.get_allocation())
    gui.tline_column.init_listeners()
    updater.repaint_tline()

def maybe_do_auto_expand(tracks_clips_count_before_exit):
    initial_drop_track_index = current_sequence().get_inital_drop_target_track(tracks_clips_count_before_exit)
    if initial_drop_track_index == None or editorpersistance.prefs.auto_expand_tracks == False:
        return

    if current_sequence().tracks[initial_drop_track_index].height == appconsts.TRACK_HEIGHT_SMALL:
        GLib.timeout_add(50, lambda: _do_auto_expand(initial_drop_track_index))

def _do_auto_expand(initial_drop_track_index):
    set_track_normal_height(initial_drop_track_index, is_retry=False, is_auto_expand=True)
    
def mute_track(track, new_mute_state):
    # NOTE: THIS IS A SAVED EDIT OF SEQUENCE, BUT IT IS NOT AN UNDOABLE EDIT.
    current_sequence().set_track_mute_state(track.id, new_mute_state)
    gui.tline_column.widget.queue_draw()
    
def all_tracks_menu_launch_pressed(widget, event):
    guicomponents.get_all_tracks_popup_menu(event, _all_tracks_item_activated)

def _all_tracks_item_activated(widget, msg):
    if msg == "min":
        current_sequence().minimize_tracks_height()
        _tracks_resize_update()
    
    if msg == "max":
        current_sequence().maximize_tracks_height(gui.tline_canvas.widget.get_allocation())
        _tracks_resize_update()
    
    if msg == "maxvideo":
        current_sequence().maximize_video_tracks_height(gui.tline_canvas.widget.get_allocation())
        _tracks_resize_update()

    if msg == "maxaudio":
        current_sequence().maximize_audio_tracks_height(gui.tline_canvas.widget.get_allocation())
        _tracks_resize_update()

    if msg == "allactive":
        _activate_all_tracks()

    if msg == "topactiveonly":
        _activate_only_current_top_active()
    
    if msg == "shrink":
         _tline_vertical_shrink_changed(widget)
    
    if msg == "autoexpand_on_drop":
        editorpersistance.prefs.auto_expand_tracks = widget.get_active()
        editorpersistance.save()
        
def _tracks_resize_update():
    tlinewidgets.set_ref_line_y(gui.tline_canvas.widget.get_allocation())
    gui.tline_column.init_listeners()
    updater.repaint_tline()
    gui.tline_column.widget.queue_draw()

def _tline_vertical_shrink_changed(widget):
    PROJECT().project_properties[appconsts.P_PROP_TLINE_SHRINK_VERTICAL] = widget.get_active()
    updater.set_timeline_height()

def _activate_all_tracks():
    for i in range(0, len(current_sequence().tracks) - 1):
        current_sequence().tracks[i].active = True

    gui.tline_column.widget.queue_draw()
    
def _activate_only_current_top_active():
    for i in range(0, len(current_sequence().tracks) - 1):
        if i == current_sequence().get_first_active_track().id:
            current_sequence().tracks[i].active = True
        else:
            current_sequence().tracks[i].active = False

    gui.tline_column.widget.queue_draw()
    
def audio_levels_menu_launch_pressed(widget, event):
    guicomponents.get_audio_levels_popup_menu(event, _audio_levels_item_activated)

# THIS HANDLES MORE NOW, NAME _audio_levels_item_activated name needs changing
def _audio_levels_item_activated(widget, msg):
    if msg == "all":
        editorstate.display_all_audio_levels = widget.get_active()
        updater.repaint_tline()
    elif msg == "snapping":
        snapping.snapping_on = widget.get_active()
    elif msg == "scrubbing":
        editorpersistance.prefs.audio_scrubbing = widget.get_active()
        editorpersistance.save()
        PLAYER().set_scrubbing(widget.get_active())
    else: # media thumbnails
        editorstate.display_clip_media_thumbnails = widget.get_active()
        updater.repaint_tline()

# ------------------------------------------------------------- mouse events
def track_active_switch_pressed(data):
    track = get_track(data.track) # data.track is index, not object

    # Flip active state
    if data.event.button == 1:
        track.active = (track.active == False)
        if current_sequence().all_tracks_off() == True:
            track.active = True
        gui.tline_column.widget.queue_draw()
    elif data.event.button == 3:
        guicomponents.display_tracks_popup_menu(data.event, data.track, \
                                                _track_menu_item_activated)

def track_double_click(track_id):
    track = get_track(track_id) # data.track is index, not object
    if track.height == appconsts.TRACK_HEIGHT_HIGH:
        set_track_small_height(track_id)
    elif track.height == appconsts.TRACK_HEIGHT_NORMAL:
        set_track_high_height(track_id)
    elif track.height == appconsts.TRACK_HEIGHT_SMALL:
        set_track_normal_height(track_id)
    
def track_center_pressed(data):
    if data.event.button == 1:
        # handle possible mute icon presses
        press_x = data.event.x
        press_y = data.event.y
        track = tlinewidgets.get_track(press_y)
        if track == None:
            return
        y_off = press_y - tlinewidgets._get_track_y(track.id)
        ICON_WIDTH = 14
        ICON_HEIGHT = 10
        if editorpersistance.prefs.double_track_hights == True:
            ICON_WIDTH = 28
            ICON_HEIGHT = 20
        X_CORR_OFF = 4 # icon edge not on image left edge
        if press_x > tlinewidgets.COLUMN_LEFT_PAD + X_CORR_OFF and press_x < tlinewidgets.COLUMN_LEFT_PAD + ICON_WIDTH + X_CORR_OFF:
            # Mute icon x area hit
            ix, iy = tlinewidgets.MUTE_ICON_POS
            if track.height == appconsts.TRACK_HEIGHT_HIGH:
                ix, iy = tlinewidgets.MUTE_ICON_POS_HIGH
            elif track.height == appconsts.TRACK_HEIGHT_NORMAL: 
                ix, iy = tlinewidgets.MUTE_ICON_POS_NORMAL

            if track.id >= current_sequence().first_video_index:
                # Video tracks
                # Test mute switches
                if y_off > iy and y_off < iy + ICON_HEIGHT:
                    # Video mute icon hit
                    if track.mute_state == appconsts.TRACK_MUTE_NOTHING:
                        new_mute_state = appconsts.TRACK_MUTE_VIDEO
                    elif track.mute_state == appconsts.TRACK_MUTE_VIDEO:
                        new_mute_state = appconsts.TRACK_MUTE_NOTHING
                    elif track.mute_state == appconsts.TRACK_MUTE_AUDIO:
                        new_mute_state = appconsts.TRACK_MUTE_ALL
                    elif track.mute_state == appconsts.TRACK_MUTE_ALL:
                        new_mute_state = appconsts.TRACK_MUTE_AUDIO
                elif y_off > iy + ICON_HEIGHT and y_off < iy + ICON_HEIGHT * 2:
                    # Audio mute icon hit
                    if track.mute_state == appconsts.TRACK_MUTE_NOTHING:
                        new_mute_state = appconsts.TRACK_MUTE_AUDIO
                    elif track.mute_state == appconsts.TRACK_MUTE_VIDEO:
                        new_mute_state = appconsts.TRACK_MUTE_ALL
                    elif track.mute_state == appconsts.TRACK_MUTE_AUDIO:
                        new_mute_state = appconsts.TRACK_MUTE_NOTHING
                    elif track.mute_state == appconsts.TRACK_MUTE_ALL:
                        new_mute_state = appconsts.TRACK_MUTE_VIDEO
                else:
                    return
            else:
                # Audio tracks
                # Test mute switches
                iy = iy + 6 # Mute icon is lower on audio tracks
                if y_off > iy and y_off < iy + ICON_HEIGHT:
                    if track.mute_state == appconsts.TRACK_MUTE_VIDEO:
                        new_mute_state = appconsts.TRACK_MUTE_ALL
                    else:
                        new_mute_state = appconsts.TRACK_MUTE_VIDEO
                else:
                    return 
            # Update track mute state
            current_sequence().set_track_mute_state(track.id, new_mute_state)
            
            audiomonitoring.update_mute_states()
            gui.tline_column.widget.queue_draw()
    
    if data.event.button == 3:
        guicomponents.display_tracks_popup_menu(data.event, data.track, \
                                                _track_menu_item_activated)

POPUP_HANDLERS = {"lock":lock_track,
                  "unlock":unlock_track,
                  "high_height":set_track_high_height,
                  "normal_height":set_track_normal_height,
                  "small_height":set_track_small_height,
                  "mute_track":mute_track}
