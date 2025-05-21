import types
import pytest

pytest.importorskip("pywayland")
pytest.importorskip("xkbcommon")

from libqtile.backend.wayland.inputs import Keyboard, KEY_PRESSED, lib


def test_bindings_use_first_layout(monkeypatch):
    """Ensure first layout is used when resolving keysyms."""

    called_layout = None

    def fake_get_syms(keymap, keycode, layout_index, level, syms):
        nonlocal called_layout
        called_layout = layout_index
        return 0

    monkeypatch.setattr(lib, "xkb_keymap_key_get_syms_by_level", fake_get_syms)

    core = types.SimpleNamespace(
        qtile=types.SimpleNamespace(
            process_key_event=lambda *a, **k: (None, False),
            call_later=lambda *a, **k: None,
        ),
        seat=types.SimpleNamespace(
            keyboard_notify_key=lambda *a: None,
            keyboard_notify_modifiers=lambda *a: None,
            set_keyboard=lambda *a: None,
        ),
        idle=types.SimpleNamespace(notify_activity=lambda *a: None),
        exclusive_client=False,
        keyboards=[],
        grabbed_keys=set(),
    )

    device = types.SimpleNamespace(
        destroy_event=None,
        type=types.SimpleNamespace(name="keyboard"),
        name="kbd",
        vendor=1,
        product=1,
        libinput_get_device_handle=lambda: None,
    )

    keyboard = types.SimpleNamespace(
        _ptr=types.SimpleNamespace(
            keymap=object(),
            repeat_info=types.SimpleNamespace(rate=0, delay=0),
        ),
        modifier=0,
        set_repeat_info=lambda *a, **k: None,
        set_keymap=lambda *a, **k: None,
    )

    k = Keyboard(core, device, keyboard)
    event = types.SimpleNamespace(keycode=10, state=KEY_PRESSED)
    k._on_key(None, event)

    assert called_layout == 0
