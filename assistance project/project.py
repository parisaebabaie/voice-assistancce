import os
import speech_recognition
import pyttsx3
import webbrowser
import wikipedia
from langdetect import detect
from rich.console import Console
from dotenv import load_dotenv
from googletrans import Translator
from bidi.algorithm import get_display
import arabic_reshaper
 
# تابع برای اصلاح متن فارسی
def process_farsi_text(text):
    reshaped_text = arabic_reshaper.reshape(text)  # اتصال حروف
    return get_display(reshaped_text)  # راست‌چین کردن متن
 

load_dotenv('.env')
console = Console()
translator = Translator()

def speak(text, lang='en'):
    """Convert text to speech with language support"""
    engine = pyttsx3.init()
    
    # Set Persian voice if available
    
    engine.say(text)
    engine.runAndWait()

def search_web(query, lang='en'):
    """Open web browser with search results"""
    if lang == 'fa':
        url = f"https://www.google.com/search?q={query}&hl=fa"
    else:
        url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)
    return f"نتایج جستجو برای {query} در مرورگر باز شد" if lang == 'fa' else f"I've opened a web search for {query}"

def get_wikipedia_answer(query, lang='en'):
    """Get summary from Wikipedia"""
    try:
        wikipedia.set_lang(lang)
        summary = wikipedia.summary(query, sentences=2)
        return process_farsi_text(summary)
    except wikipedia.exceptions.DisambiguationError as e:
        if lang == 'fa':
            return process_farsi_text((f"چندین نتیجه یافت شد. لطفا دقیق‌تر بگویید. گزینه‌ها شامل: {', '.join(e.options[:3])}..."))
        return f"Multiple results found. Can you be more specific? Options include: {', '.join(e.options[:3])}..."
    except wikipedia.exceptions.PageError:
        return "متاسفانه اطلاعاتی درباره این موضوع پیدا نکردم" if lang == 'fa' else "Sorry, I couldn't find information on that topic."
    except:
        return "خطا در ارتباط با ویکی‌پدیا" if lang == 'fa' else "Error connecting to Wikipedia"

def detect_language(text):
    """Detect if text is in Persian"""
    try:
        # Simple detection for common Persian words
        persian_chars = set('آابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی')
        if any(char in persian_chars for char in text):
            return 'fa'
        return 'en'
    except:
        return 'en'

def handle_command(text):
    """Process recognized text and return response"""
    lang = detect_language(text)
    text = text.lower()
    
    # Persian commands
    if lang == 'fa':
        if "باز کردن یوتیوب" in text or "یوتیوب" in text:
            webbrowser.open("https://youtube.com")
            return "در حال باز کردن یوتیوب"
        
        elif "باز کردن آپارات" in text or "آپارات" in text:
            webbrowser.open("https://aparat.com")
            return "در حال باز کردن آپارات"
        
        elif "باز کردن گوگل" in text or "گوگل" in text:
            webbrowser.open("https://google.com")
            return "در حال باز کردن گوگل"
        
        elif "هوا" in text or "هوا چطوره" in text or "آب و هوا" in text:
            webbrowser.open("https://www.accuweather.com/fa/ir/isfahan/208194/weather-forecast/208194")
            return "در حال نمایش آب و هوای اصفهان"
        
        elif "ویکی پدیا" in text or "دانشنامه" in text:
            query = text.replace("ویکی پدیا", "").replace("دانشنامه", "").strip()
            return process_farsi_text(get_wikipedia_answer(query, 'fa'))
        
        elif "جستجو کن" in text or "سرچ کن" in text or "درباره" in text:
            query = text.replace("جستجو کن", "").replace("سرچ کن", "").replace("درباره", "").strip()
            return search_web(query, 'fa')
        
        elif "خروج" in text or "تمام" in text:
            return "خدانگهدار"
        
        else:
            return f"گفتید: {text}. چگونه می‌توانم کمک کنم؟"
    
    # English commands (kept as fallback)
    else:
        if "open youtube" in text:
            webbrowser.open("https://youtube.com")
            return "Opening YouTube"

        elif "open aparat" in text:
            webbrowser.open("https://aparat.com")
            return "Opening Aparat"
        
        elif "open google" in text:
            webbrowser.open("https://google.com")
            return "Opening Google"
        
        elif "weather" in text or "how is the weather" in text:
            webbrowser.open("https://www.accuweather.com/en/ir/isfahan/208194/weather-forecast/208194")
            return "Opening weather in Isfahan"
        
        elif "wikipedia" in text:
            query = text.replace("wikipedia", "").strip()
            return get_wikipedia_answer(query)
        
        elif "search for" in text or "what is" in text or "who is" in text:
            query = text.replace("search for", "").replace("what is", "").replace("who is", "").strip()
            return search_web(query)
        
        elif "exit" in text or "quit" in text:
            return "Goodbye!"
        
        else:
            return f"I heard you say: {text}. How can I help with that?"

def main():
    console.rule(process_farsi_text('[bold yellow] دستیار صوتی فارسی و انگلیسی'))
    recognizer = speech_recognition.Recognizer()
    print(process_farsi_text('زبان خود را انتخاب کنید: (fa/en)\n'))
    lan = input()

    if lan == 'fa':
        while True:
            with console.status(status=process_farsi_text('در حال گوش دادن...'), spinner='point') as progress_bar:
                try:
                    with speech_recognition.Microphone() as mic:
                        recognizer.adjust_for_ambient_noise(mic, duration=0.2)
                        console.print(process_farsi_text("[yellow]در حال گوش دادن...[/yellow]"))
                        audio = recognizer.listen(mic)
                        
                        # Try Persian first, then English
                        try:
                            text = recognizer.recognize_google(audio, language='fa-IR').lower()
                        except:
                            text = recognizer.recognize_google(audio).lower()
                        
                        console.print(process_farsi_text('[bold]متن تشخیص داده شده:[/bold]'), text)

                        progress_bar.update(status=process_farsi_text('در حال پردازش...'), spinner='line')
                        response = process_farsi_text(handle_command(text))
                        
                        console.print(process_farsi_text('[bold]پاسخ:[/bold]'),response)

                        if "خدانگهدار" in response or "goodbye" in response.lower():
                            progress_bar.stop()
                            console.rule(process_farsi_text('[bold yellow]با تشکر از استفاده شما از دستیار صوتی'))
                            break

                        progress_bar.stop()
                        continue_listening = input(process_farsi_text("آیا می‌خواهید ادامه دهید؟\n (y/n)")).lower()
                        
                        if continue_listening != 'y':
                            console.rule(process_farsi_text('[bold yellow]با تشکر از استفاده شما از دستیار صوتی'))
                            break

                except speech_recognition.UnknownValueError:
                    progress_bar.stop()
                    console.print(process_farsi_text("[red]متاسفانه متوجه نشدم[/red]"))
                    retry = input(process_farsi_text("آیا می‌خواهید دوباره تلاش کنید؟\n (y/n) ")).lower()
                    
                    if retry != 'y':
                        console.rule(process_farsi_text('[bold yellow]با تشکر از استفاده شما از دستیار صوتی'))
                        break
    else:
        while True:
            with console.status(status='Listening...', spinner='point') as progress_bar:
                try:
                    with speech_recognition.Microphone() as mic:
                        recognizer.adjust_for_ambient_noise(mic, duration=0.1)
                        audio = recognizer.listen(mic)
                        text = recognizer.recognize_google(audio_data=audio).lower()
                        console.print(f'[bold]Recognized text[/bold]: {text}')

                        progress_bar.update(status='Processing...', spinner='line')
                        response = handle_command(text)
                        
                        console.print(f'[bold]Response[/bold]: {response}')
                        speak(response)

                        if "goodbye" in response.lower():
                            progress_bar.stop()
                            console.rule('[bold yellow]Thank you for using the Voice Assistant Demo')
                            break

                        progress_bar.stop()
                        continue_listening = input("Would you like to ask something else? (y/n) ").lower()
                        
                        if continue_listening != 'y':
                            console.rule('[bold yellow]Thank you for using the Voice Assistant Demo')
                            break

                except speech_recognition.UnknownValueError:
                    progress_bar.stop()
                    console.print("[red]Sorry, I didn't understand that.[/red]")
                    retry = input("Would you like to try again? (y/n) ").lower()
                    
                    if retry != 'y':
                        console.rule('[bold yellow]Thank you for using the Voice Assistant Demo')
                        break


if __name__ == '__main__':
    main()