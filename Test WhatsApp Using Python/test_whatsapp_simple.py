import asyncio
import pyautogui
import platform
from datetime import datetime

# Optional Text-to-Speech
try:
    import pyttsx3
    tts_engine = pyttsx3.init()
    tts_engine.setProperty("rate", 150)
    tts_engine.setProperty("volume", 0.8)
except ImportError:
    tts_engine = None

async def speak(text):
    if tts_engine:
        tts_engine.stop()
        tts_engine.say(text)
        tts_engine.runAndWait()

async def send_whatsapp_message(contact_name: str, message: str):
    """
    Send WhatsApp message using keyboard automation (Windows only)
    """
    
    if platform.system() != "Windows":
        print("❌ This script works only on Windows")
        return

    try:
        print("🚀 Opening Start Menu...")
        pyautogui.press("win")
        await asyncio.sleep(2)

        print("🔍 Searching WhatsApp...")
        pyautogui.typewrite("WhatsApp", interval=0.1)
        await asyncio.sleep(3)

        print("📱 Launching WhatsApp...")
        pyautogui.press("enter")
        await asyncio.sleep(15)  # wait for WhatsApp to fully load

        print("🔎 Opening search inside WhatsApp...")
        pyautogui.hotkey("ctrl", "f")
        await asyncio.sleep(2)

        pyautogui.hotkey("ctrl", "a")
        pyautogui.press("backspace")
        await asyncio.sleep(1)

        print(f"👤 Searching contact: {contact_name}")
        pyautogui.typewrite(contact_name, interval=0.08)
        await asyncio.sleep(4)

        print("⬇ Selecting contact...")
        pyautogui.press("down")
        await asyncio.sleep(1)
        pyautogui.press("enter")
        await asyncio.sleep(5)

        print("⌨️ Focusing message box...")
        pyautogui.hotkey("ctrl", "l")
        await asyncio.sleep(1)

        print("✍️ Typing message...")
        for char in message:
            if char == "\n":
                pyautogui.hotkey("shift", "enter")
            else:
                pyautogui.typewrite(char, interval=0.04)

        await asyncio.sleep(1)

        print("📤 Sending message...")
        pyautogui.press("enter")

        print("✅ Message sent successfully!")
        await speak("Message sent successfully")

    except Exception as e:
        print("❌ Error occurred:", e)
        await speak("An error occurred")

        # Take screenshot for debugging
        filename = f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        pyautogui.screenshot(filename)
        print(f"📸 Screenshot saved as {filename}")

if __name__ == "__main__":
    print("🤖 WhatsApp Automation (VS Code)")
    print("=" * 40)

    name = input("Enter contact name: ").strip()
    msg = input("Enter message: ").strip()

    asyncio.run(send_whatsapp_message(name, msg))

    input("\nPress Enter to exit...")
