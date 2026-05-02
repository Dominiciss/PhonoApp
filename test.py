import keyboard

def on_key(event):
    print(event.scan_code)


keyboard.hook(on_key)
keyboard.wait()