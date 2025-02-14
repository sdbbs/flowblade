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
Module handles cut tool functionality
"""

from gi.repository import Gdk

import appconsts
import dialogutils
import gui
import edit
from editorstate import current_sequence
import editorstate
import tlinewidgets
import updater

# ------------------------------------- edit mode setting
def set_default_edit_mode(disable_mouse=False):
    """
    We interpret clicks on empty in this tool as request to exit to default edit tool.
    """
    gui.editor_window.set_default_edit_tool()
    if disable_mouse:
        editorstate.timeline_mouse_disabled = True
 
# ---------------------------------------------- mouse events
def mouse_press(event, frame):
    if not (event.get_state() & Gdk.ModifierType.CONTROL_MASK):
        cut_single_track(event, frame)
    else:
        cut_all_tracks(frame)
        
def mouse_move(x, y, frame, state):
    pass
    
def mouse_release(x, y, frame, state):
    pass

# ---------------------------------------------- cut actions
def cut_single_track(event, frame):
    track = tlinewidgets.get_track(event.y)
    if track == None or track.id == 0 or track.id == len(current_sequence().tracks) - 1:
        set_default_edit_mode(True)
        return

    if dialogutils.track_lock_check_and_user_info(track):
        set_default_edit_mode(True)
        return
        
    data = get_cut_data(track, frame)
    if data == None:
        set_default_edit_mode(True)
        return

    action = edit.cut_action(data)
    action.do_edit()

    updater.repaint_tline()

def cut_all_tracks(frame):
    tracks_cut_data = []

    for i in range(1, len(current_sequence().tracks) - 1):
        if current_sequence().tracks[i].edit_freedom == appconsts.LOCKED:
            tracks_cut_data.append(None) # Don't cut locked tracks.
        else:
            tracks_cut_data.append(get_cut_data(current_sequence().tracks[i], frame))

    data = {"tracks_cut_data":tracks_cut_data}
    action = edit.cut_all_action(data)
    action.do_edit()

    updater.repaint_tline()

def get_cut_data(track, frame):
    # Get index and clip
    index = track.get_clip_index_at(int(frame))
    try:
        clip = track.clips[index]            
        # don't cut blanck clip
        if clip.is_blanck_clip:
            return None
    except Exception:
        return None

    # Get cut frame in clip frames
    clip_start_in_tline = track.clip_start(index)
    clip_frame = frame - clip_start_in_tline + clip.clip_in

    # No data if frame on cut.
    if clip_frame == clip.clip_in:
        return None

    data = {"track":track,
            "index":index,
            "clip":clip,
            "clip_cut_frame":clip_frame}
    
    return data
