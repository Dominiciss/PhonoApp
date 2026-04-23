import keyboard

def get_key_from_scancode(scancode):
    """
    Returns the key name for a given scan code.
    """
    try:
        key_name = keyboard.key_to_scan_codes(keyboard.key_to_scan_codes(scancode))
        return key_name
    except Exception as e:
        return f"Error: {e}"

# Listen for key events and print scan code + key name
print("Press any key (Press ESC to exit)...")
while True:
    event = keyboard.read_event()
    if event.event_type == keyboard.KEY_DOWN:
        print(f"Scan code: {event.scan_code}, Key: {event.name}")
        if event.name == "esc":
            break