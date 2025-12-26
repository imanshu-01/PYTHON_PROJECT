import asyncio
import pyautogui
import platform
import time
from datetime import datetime
from typing import List, Optional
import json
import os

# Optional Text-to-Speech
try:
    import pyttsx3
    tts_engine = pyttsx3.init()
    tts_engine.setProperty("rate", 150)
    tts_engine.setProperty("volume", 0.8)a 
except ImportError:
    tts_engine = None

# Configuration
CONFIG_FILE = "whatsapp_config.json"
DEFAULT_WAIT_TIMES = {
    "app_load": 15,
    "search_wait": 4,
    "contact_select": 5,
    "message_send": 2
}

class WhatsAppAutomation:
    def __init__(self, config_file: str = CONFIG_FILE):
        self.config_file = config_file
        self.config = self.load_config()
        self.wait_times = {**DEFAULT_WAIT_TIMES, **self.config.get("wait_times", {})}
        
    def load_config(self):
        """Load configuration from JSON file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"⚠️ Config file {self.config_file} is corrupted. Using defaults.")
                return {}
        return {}
    
    def save_config(self):
        """Save configuration to JSON file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

async def speak(text):
    """Text-to-speech output"""
    if tts_engine:
        tts_engine.stop()
        tts_engine.say(text)
        tts_engine.runAndWait()

def get_multi_line_input():
    """
    Get multi-line message input from user
    Returns up to 30 lines of text
    """
    print("\n" + "="*50)
    print("Enter your message (20-30 lines max).")
    print("Type 'END' on a new line to finish, or press Ctrl+Z then Enter.")
    print("="*50)
    
    lines = []
    try:
        for i in range(30):
            line = input(f"Line {i+1}: ")
            if line.upper() == "END":
                break
            lines.append(line)
            
            # Optional: Add automatic stop at 30 lines
            if i >= 29:
                print("📝 Maximum 30 lines reached.")
                break
    except EOFError:
        # Handle Ctrl+Z or Ctrl+D
        pass
    
    return "\n".join(lines)

def get_contacts():
    """
    Get multiple contacts from user
    """
    print("\n" + "="*50)
    print("Enter contact names (separated by commas):")
    print("Example: John Doe, Jane Smith, Bob Johnson")
    print("="*50)
    
    contacts_input = input("Contacts: ").strip()
    if not contacts_input:
        return []
    
    # Split by comma and clean up
    contacts = [c.strip() for c in contacts_input.split(",") if c.strip()]
    return contacts

def format_message_for_display(message: str, max_lines: int = 10) -> str:
    """
    Format message for preview display
    """
    lines = message.split('\n')
    total_lines = len(lines)
    
    if total_lines <= max_lines:
        return message
    
    preview = '\n'.join(lines[:max_lines])
    return f"{preview}\n...\n[{total_lines - max_lines} more lines]"

def simulate_typing_with_pauses(message: str, interval: float = 0.04):
    """
    Simulate realistic typing with strategic pauses
    """
    words = message.split(' ')
    for i, word in enumerate(words):
        # Type word
        pyautogui.typewrite(word, interval=interval)
        
        # Add space unless it's the last word
        if i < len(words) - 1:
            pyautogui.press('space')
        
        # Occasionally pause (simulates thinking)
        if i % 10 == 9:  # Pause after every 10 words
            time.sleep(0.5)
        
        # Pause slightly longer at punctuation
        if word and word[-1] in '.!?':
            time.sleep(0.2)

async def open_whatsapp():
    """
    Open WhatsApp application
    """
    print("🚀 Opening Start Menu...")
    pyautogui.press("win")
    await asyncio.sleep(2)

    print("🔍 Searching WhatsApp...")
    pyautogui.typewrite("WhatsApp", interval=0.1)
    await asyncio.sleep(3)

    print("📱 Launching WhatsApp...")
    pyautogui.press("enter")
    
    # Wait for WhatsApp to load
    print("⏳ Waiting for WhatsApp to load...")
    for i in range(DEFAULT_WAIT_TIMES['app_load']):
        print(f"  {i+1}/{DEFAULT_WAIT_TIMES['app_load']}", end='\r')
        await asyncio.sleep(1)
    print("\n✅ WhatsApp loaded!")

async def send_to_contact(contact_name: str, message: str, is_first: bool = True):
    """
    Send message to a single contact
    """
    try:
        if not is_first:
            # After first contact, we're already in WhatsApp
            print(f"\n🔍 Searching for next contact: {contact_name}")
            pyautogui.hotkey("ctrl", "f")
            await asyncio.sleep(1)
        else:
            # First contact needs to open search
            print(f"\n🔍 Opening search for: {contact_name}")
            pyautogui.hotkey("ctrl", "f")
            await asyncio.sleep(2)
        
        # Clear search if needed
        pyautogui.hotkey("ctrl", "a")
        pyautogui.press("backspace")
        await asyncio.sleep(0.5)
        
        # Type contact name
        print(f"👤 Typing contact name: {contact_name}")
        pyautogui.typewrite(contact_name, interval=0.08)
        await asyncio.sleep(DEFAULT_WAIT_TIMES['search_wait'])
        
        # Select contact
        print("⬇ Selecting contact...")
        pyautogui.press("down")
        await asyncio.sleep(0.5)
        pyautogui.press("enter")
        await asyncio.sleep(DEFAULT_WAIT_TIMES['contact_select'])
        
        # Focus message box
        print("⌨️ Focusing message box...")
        pyautogui.hotkey("ctrl", "l")
        await asyncio.sleep(1)
        
        # Type and send message
        print("✍️ Typing message...")
        
        # Option 1: Fast typing
        # pyautogui.typewrite(message, interval=0.01)
        
        # Option 2: Realistic typing with pauses
        simulate_typing_with_pauses(message, interval=0.03)
        
        await asyncio.sleep(1)
        
        # Send message
        print("📤 Sending message...")
        pyautogui.press("enter")
        await asyncio.sleep(DEFAULT_WAIT_TIMES['message_send'])
        
        print(f"✅ Message sent to {contact_name}")
        return True
        
    except Exception as e:
        print(f"❌ Error sending to {contact_name}: {e}")
        return False

async def send_whatsapp_messages(contacts: List[str], message: str):
    """
    Send WhatsApp message to multiple contacts using keyboard automation
    """
    
    if platform.system() != "Windows":
        print("❌ This script works only on Windows")
        await speak("This script works only on Windows")
        return
    
    if not contacts:
        print("❌ No contacts provided")
        await speak("No contacts provided")
        return
    
    if not message:
        print("❌ No message provided")
        await speak("No message provided")
        return
    
    automation = WhatsAppAutomation()
    successful_sends = 0
    
    try:
        print("\n" + "="*50)
        print(f"📱 Starting WhatsApp Automation")
        print(f"👥 Contacts: {len(contacts)}")
        print(f"📝 Message lines: {len(message.split('\\n'))}")
        print("="*50)
        
        # Open WhatsApp only once
        await open_whatsapp()
        
        # Send to each contact
        for i, contact in enumerate(contacts):
            print(f"\n{'='*40}")
            print(f"Contact {i+1}/{len(contacts)}: {contact}")
            print(f"{'='*40}")
            
            success = await send_to_contact(contact, message, is_first=(i==0))
            if success:
                successful_sends += 1
            
            # Add delay between contacts (except for the last one)
            if i < len(contacts) - 1:
                print(f"⏳ Waiting before next contact...")
                await asyncio.sleep(2)
        
        # Summary
        print("\n" + "="*50)
        print("📊 SUMMARY")
        print("="*50)
        print(f"✅ Successfully sent: {successful_sends}/{len(contacts)}")
        print(f"❌ Failed: {len(contacts) - successful_sends}")
        
        if successful_sends > 0:
            await speak(f"Messages sent successfully to {successful_sends} contacts")
        
    except Exception as e:
        print(f"❌ Critical error occurred: {e}")
        await speak("A critical error occurred")
        
        # Take screenshot for debugging
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"error_{timestamp}.png"
        try:
            pyautogui.screenshot(filename)
            print(f"📸 Screenshot saved as {filename}")
        except:
            print("⚠️ Could not save screenshot")

async def schedule_messages(contacts: List[str], message: str, delay_minutes: int = 0):
    """
    Schedule messages to be sent after a delay
    """
    if delay_minutes > 0:
        print(f"⏰ Scheduling messages to be sent in {delay_minutes} minutes...")
        await asyncio.sleep(delay_minutes * 60)
    
    await send_whatsapp_messages(contacts, message)

def advanced_options():
    """
    Display and handle advanced options
    """
    print("\n" + "="*50)
    print("🛠️  ADVANCED OPTIONS")
    print("="*50)
    print("1. Schedule messages")
    print("2. Add message templates")
    print("3. Configure wait times")
    print("4. Test automation")
    print("5. Exit to main")
    
    choice = input("\nSelect option (1-5): ").strip()
    
    if choice == "1":
        try:
            delay = int(input("Enter delay in minutes: "))
            return {"schedule_delay": delay}
        except ValueError:
            print("⚠️ Invalid input. Using default (send now).")
    elif choice == "2":
        templates = {
            "1": "Hello! This is an automated message.",
            "2": "Reminder: Meeting tomorrow at 10 AM.",
            "3": "Please check your email for updates."
        }
        print("\nAvailable templates:")
        for key, value in templates.items():
            print(f"{key}. {value[:50]}...")
        
        template_choice = input("\nSelect template (1-3) or press Enter to skip: ")
        if template_choice in templates:
            return {"message_template": templates[template_choice]}
    
    return {}

async def main():
    """
    Main function with enhanced interface
    """
    print("🤖 ADVANCED WHATSAPP AUTOMATION")
    print("="*50)
    
    # Create automation instance
    automation = WhatsAppAutomation()
    
    # Get contacts
    contacts = get_contacts()
    if not contacts:
        print("❌ No contacts entered. Exiting.")
        return
    
    # Message input options
    print("\n" + "="*50)
    print("📝 MESSAGE INPUT OPTIONS")
    print("="*50)
    print("1. Type multi-line message")
    print("2. Use pre-written message")
    print("3. Load from file")
    
    msg_choice = input("\nSelect option (1-3): ").strip()
    
    if msg_choice == "1":
        message = get_multi_line_input()
    elif msg_choice == "2":
        # Pre-written message (20-30 lines example)
        message = """Hello!

This is an automated message with multiple lines.

Line 1: Start of message
Line 2: please read carefully
Line 3: Update on recent changes
Line 4: urgent notice
Line 5: Follow-up instructions
Line 6: Meeting schedule
Line 7: Project updates
Line 8: Team announcements
Line 9: Policy changes
Line 10: System updates
Line 11: Performance review
Line 12: Training schedule
Line 13: Holiday calendar
Line 14: Budget updates
Line 15: Security reminders
Line 16: Compliance notes
Line 17: Quality standards
Line 18: Best practices
Line 19: Innovation ideas
Line 20: Future plans

Thank you for your attention!
Best regards,
Automation System"""
    elif msg_choice == "3":
        filename = input("Enter filename: ").strip()
        try:
            with open(filename, 'r') as f:
                message = f.read()
        except FileNotFoundError:
            print(f"❌ File {filename} not found. Using default message.")
            message = "Default automated message."
    else:
        print("⚠️ Invalid choice. Using default message.")
        message = "Default automated message."
    
    # Preview message
    print("\n" + "="*50)
    print("📋 MESSAGE PREVIEW")
    print("="*50)
    print(format_message_for_display(message))
    print(f"\nTotal lines: {len(message.split('\\n'))}")
    print(f"Total characters: {len(message)}")
    
    confirm = input("\nProceed with sending? (y/n): ").lower()
    if confirm != 'y':
        print("❌ Message sending cancelled.")
        return
    
    # Advanced options
    advanced_config = advanced_options()
    
    # Send messages
    if advanced_config.get("schedule_delay"):
        await schedule_messages(
            contacts, 
            message, 
            advanced_config["schedule_delay"]
        )
    else:
        await send_whatsapp_messages(contacts, message)
    
    print("\n" + "="*50)
    print("🎉 Automation completed!")
    print("="*50)

if __name__ == "__main__":
    # Safety feature - fail-safe
    pyautogui.FAILSAFE = True
    print("⚠️  Move mouse to top-left corner to abort automation")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n❌ Automation interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
    
    input("\nPress Enter to exit...")