#!/usr/bin/env python
# coding: utf-8
#
# Copyright (c) 2008, Aldo Cortesi <aldo@corte.si>
# Copyright (c) 2011, Andrew Grigorev <andrew@ei-grad.ru>
#
# All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import sys
import traceback

from libqtile.config import Key, Screen, Group
from libqtile.command import lazy
from libqtile import layout, bar, widget


class EmptyConfig(object):
    pass


class ConfigError(Exception):
    pass


class File(object):

    def __init__(self, fname=None, is_restart=False):

        if fname is None:
            config_directory = os.path.expandvars('$XDG_CONFIG_HOME')
            if config_directory == '$XDG_CONFIG_HOME':
                # if variable wasn't set
                config_directory = os.path.expanduser("~/.config")
            fname = os.path.join(config_directory, "qtile", "config.py")

        self.fname = fname

        if os.path.isfile(fname):
            try:
                sys.path.insert(0, os.path.dirname(fname))
                config = __import__(os.path.basename(fname)[:-3])
            except Exception, v:
                # On restart, user potentially has some windows open, but they
                # screwed up their config. So as not to lose their apps, we
                # just load the default config here.
                if is_restart:
                    config = EmptyConfig()
                else:
                    tb = traceback.format_exc()
                    raise ConfigError(str(v) + "\n\n" + tb)
        else:
            config = EmptyConfig()

        if not hasattr(config, 'keys'):
            config.keys = [
                # Switch between windows in current stack pane
                Key(["mod1"], "k", lazy.layout.down()),
                Key(["mod1"], "j", lazy.layout.up()),

                # Move windows up or down in current stack
                Key(["mod1", "control"], "k", lazy.layout.shuffle_down()),
                Key(["mod1", "control"], "j", lazy.layout.shuffle_up()),

                # Switch window focus to other pane(s) of stack
                Key(["mod1"], "space", lazy.layout.next()),

                # Swap panes of split stack
                Key(["mod1", "shift"], "space", lazy.layout.rotate()),

                # Toggle between split and unsplit sides of stack.
                # Split = all windows displayed
                # Unsplit = 1 window displayed, like Max layout, but still with
                # multiple stack panes
                Key(["mod1", "shift"], "Return", lazy.layout.toggle_split()),

                Key(["mod1"], "h",      lazy.to_screen(1)),
                Key(["mod1"], "l",      lazy.to_screen(0)),
                Key(["mod1"], "Return", lazy.spawn("xterm")),

                # Toggle between different layouts as defined below
                Key(["mod1"], "Tab",    lazy.nextlayout()),
                Key(["mod1"], "w",      lazy.window.kill()),

                Key(["mod1", "control"], "r", lazy.restart()),
            ]

        if not hasattr(config, "mouse"):
            config.mouse = []

        if not hasattr(config,"groups"):
            config.groups = [Group(i) for i in "asdfuiop"]
            for i in "asdfuiop":
                # mod1 + letter of group = switch to group
                config.keys.append(Key(["mod1"], i, lazy.group[i].toscreen()))
                # mod1 + shift + letter of group = switch to & move
                # focused window to group
                config.keys.append(Key(["mod1", "shift"], i,
                                       lazy.window.togroup(i)))

        if not hasattr(config, "dgroups_key_binder"):
            config.dgroups_key_binder = None

        if not hasattr(config, "follow_mouse_focus"):
            config.follow_mouse_focus = True

        if not hasattr(config, "cursor_warp"):
            config.cursor_warp = False

        if not hasattr(config, "layouts"):
            config.layouts = [layout.Max(),
                              layout.Stack(stacks=2)]

        if not hasattr(config, "floating_layout"):
            config.floating_layout = layout.Floating()

        if not hasattr(config, "screens"):
            config.screens = [Screen(bottom=bar.Bar([
                widget.GroupBox(),
                widget.WindowName(),
                widget.TextBox("default config", name="default"),
                widget.Systray(),
                widget.Clock('%Y-%m-%d %a %I:%M %p'),
            ], 30))]

        if not hasattr(config, "main"):
            config.main = None

        if not hasattr(config, "auto_fullscreen"):
            config.auto_fullscreen = True

        # if you add something here, be sure to add a reasonable default value
        # to resources/default-config.py
        config_options = [
            "keys",
            "mouse",
            "groups",
            "dgroups_key_binder",
            "follow_mouse_focus",
            "cursor_warp",
            "layouts",
            "floating_layout",
            "screens",
            "main",
            "auto_fullscreen",
        ]

        for option in config_options:
            setattr(self, option, getattr(config, option))
