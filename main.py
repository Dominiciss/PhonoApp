from PIL import Image
import keyboard
import pystray

cycle_map = {
    # --- ALT + [KEY] (Base Phonetics) ---
    30: ['ɑ', 'æ', 'ʌ'],
    48: ['β'],
    32: ['ð'],
    18 : ['ə', 'ᵊ', 'ɛ', 'ɜ'],
    33: ['‿'],
    34: ['ɣ'],
    35: ['ʰ'],
    23: ['ɪ'],
    36: ['ʲ'],
    37: ['|', '‖'],
    38: ['ɫ'],
    50: ['ɱ'],
    49: ['ŋ', 'ɲ', 'ñ'],
    24: ['ɔ', 'ɒ'],
    19: ['ɾ'],
    31: ['ʃ'],
    20: ['θ', 'ʔ'],
    22: ['ʊ'],
    47: ['ʌ'],
    44: ['ʒ'],
    17: ['ʷ'],

    39: ['ː'],

    2: ['|', '‖'],
    3: ['ˈ', 'ˌ'],
    4: ['̥', '̊'],
    5: ['̪'],
    6: ['↗', '↘'],
    7: ['→'],
    8: ['ꜜ', 'ꜛ'],

    77: ['→'],
}

cycle_index = {key: 0 for key in cycle_map}
toggle_phonemes = True
first_check = False
previous_letter = -1
icon = Image.open('icon.ico')

def is_altgr_pressed() -> bool:
    return keyboard.is_pressed(514) or (
        keyboard.is_pressed(29) and keyboard.is_pressed(56)
    ) or keyboard.is_pressed('alt gr')

def reset_cycle_states() -> None:
    for key in cycle_index:
        cycle_index[key] = 0

def on_key(event: keyboard.KeyboardEvent) -> bool:
    global previous_letter
    global first_check
    global first_shift_check
    global toggle_phonemes

    if event.event_type != keyboard.KEY_DOWN or "Unknown" in event.__str__():
        return True

    if is_altgr_pressed():
        for letter in cycle_map:
            if (letter == event.scan_code and toggle_phonemes):
                symbol = cycle_map[letter][cycle_index[letter]]

                if (first_check and previous_letter == event.scan_code):
                    keyboard.send('backspace')
                first_check = True

                keyboard.write(symbol, delay=0)

                if (cycle_index[letter] >= len(cycle_map[letter]) - 1):
                    cycle_index[letter] = 0
                else:
                    cycle_index[letter] = cycle_index[letter] + 1

                previous_letter = event.scan_code
                return False
    elif (event.scan_code == 28):
        toggle_phonemes = not toggle_phonemes
            
    return True

def on_key_release(event: keyboard.KeyboardEvent) -> None:
    if event.event_type == keyboard.KEY_UP and (event.scan_code == 514 or (event.scan_code == 29 and event.scan_code == 56) or event.name in ('alt gr', 'right alt', 'alt')):
        global first_check
        
        first_check = False
        reset_cycle_states()

def toggle_phonetic_keyboard() -> None:
    global toggle_phonemes
    toggle_phonemes = not toggle_phonemes

if __name__ == '__main__': 
    system_tray = pystray.Icon('TypeIt', icon, 'Phonetic Keyboard')

    keyboard.hook(on_key, suppress=True)
    keyboard.on_release(on_key_release)

    system_tray.menu = pystray.Menu(
        pystray.MenuItem('Toggle', lambda: toggle_phonetic_keyboard()),
        pystray.MenuItem('Exit', lambda: system_tray.stop())
    )
    system_tray.run()