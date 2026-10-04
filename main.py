import re
import sys
import os
import wave
import json
import subprocess
import pyperclip
from vosk import Model, KaldiRecognizer

def extract_audio_from_video(video_path, out_wav="temp_audio.wav"):
    print("🎞 Извлекаю звук из видео...")
    if os.path.exists(out_wav):
        try:
            os.remove(out_wav)
        except OSError:
            pass # Файл может быть занят другим процессом

    command = [
    "ffmpeg", 
    "-err_detect", "ignore_err", # Игнорировать мелкие ошибки в потоке
    "-i", video_path,
    "-ar", "16000",
    "-ac", "1",
    "-f", "wav",
    out_wav,
    "-y"
]
    
    # Убираем перенаправление в DEVNULL, чтобы видеть ошибки ffmpeg, если они есть
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Ошибка ffmpeg: {result.stderr}")
        sys.exit(1)
        
    return out_wav

def capitalize_names(text):
    """Делает имена с заглавной буквы"""
    common_names = {
        # Мужские имена
        'rachel', 'michael', 'john', 'david', 'james', 'william', 'robert', 
        'richard', 'thomas', 'charles', 'daniel', 'matthew', 'anthony', 'mark',
        'donald', 'steven', 'paul', 'andrew', 'joshua', 'kenneth', 'kevin',
        'brian', 'george', 'timothy', 'ronald', 'edward', 'jason', 'jeffrey',
        'ryan', 'jacob', 'gary', 'nicholas', 'eric', 'stephen', 'jonathan',
        'larry', 'justin', 'scott', 'brandon', 'benjamin', 'samuel', 'gregory',
        'alexander', 'patrick', 'frank', 'raymond', 'jack', 'dennis', 'jerry',
        'tyler', 'aaron', 'jose', 'henry', 'douglas', 'adam', 'peter', 'nathan',
        'zachary', 'walter', 'kyle', 'harold', 'carl', 'jeremy', 'keith',
        'roger', 'gerald', 'ethan', 'arthur', 'terry', 'christian', 'sean',
        'lawrence', 'austin', 'joe', 'noah', 'jesse', 'albert', 'bryan',
        'billy', 'bruce', 'jordan', 'dylan', 'alan', 'gabe', 'logan', 'juan',
        'wayne', 'ralph', 'roy', 'eugene', 'randy', 'vincent', 'russell',
        'louis', 'philip', 'bobby', 'johnny', 'bradley',
        
        # Женские имена
        'sarah', 'emma', 'emily', 'sophia', 'ava', 'isabella', 'mia', 'abigail',
        'charlotte', 'harper', 'evelyn', 'amelia', 'elizabeth', 'sofia', 'madison',
        'alexis', 'grace', 'chloe', 'ella', 'avery', 'scarlett', 'victoria',
        'ria', 'zoe', 'hannah', 'addison', 'lily', 'natalie', 'lillian', 'lucy',
        'audrey', 'leah', 'samantha', 'anna', 'allison', 'savannah', 'camila',
        'claire', 'penelope', 'aria', 'riley', 'layla', 'nora', 'brooklyn',
        'alice', 'makayla', 'luna', 'kaylee', 'katherine', 'haley', 'eleanor',
        'keira', 'clara', 'jasmine', 'melanie', 'kylie', 'kayla', 'autumn',
        'eva', 'naomi', 'aurora', 'brooklyn', 'julia', 'stella', 'maya',
        'katelyn', 'khloe', 'paisley', 'annabelle', 'serenity', 'peyton',
        'mackenzie', 'bella', 'eva', 'skylar', 'gianna', 'alexandra', 'jade',
        'isabelle', 'maria', 'corinne', 'jennifer', 'rebecca', 'stephanie',
        'nicole', 'kristen', 'danielle', 'tiffany', 'cassandra', 'catherine',
        'christina', 'lauren', 'amanda', 'kelsey', 'whitney', 'heather',
        'melissa', 'rachel', 'vanessa', 'sandra', 'nancy', 'karen', 'betty',
        'helen', 'donna', 'carol', 'ruth', 'sharon', 'michelle', 'laura',
        'sarah', 'kimberly', 'deborah', 'jessica', 'shirley', 'cynthia',
        'angela', 'barbara', 'emily', 'kathy', 'amy', 'brenda', 'anna',
        'rebecca', 'virginia', 'kathleen', 'pamela', 'martha', 'debra',
        'amanda', 'stephanie', 'carolyn', 'christine', 'marie', 'janet',
        'catherine', 'frances', 'ann', 'joyce', 'diane', 'julie', 'alice',
        'heather', 'teresa', 'doris', 'gloria', 'evelyn', 'jean', 'cheryl',
        'mildred', 'katherine', 'joan', 'ashley', 'judith', 'rose', 'janice',
        'kelly', 'nicole', 'judy', 'christina', 'kathy', 'theresa', 'beverly',
        'denise', 'tammy', 'irene', 'jane', 'lori', 'rachel', 'marilyn',
        'andrea', 'kathryn', 'louise', 'sara', 'anne', 'jacqueline', 'wanda',
        'bonnie', 'julia', 'ruby', 'lois', 'tina', 'phyllis', 'norma',
        'paula', 'diana', 'annie', 'lillian', 'emily', 'robin', 'peggy',
        'crystal', 'gladys', 'rita', 'dawn', 'connie', 'florence', 'tracy',
        'edna', 'tiffany', 'carmen', 'rosa', 'cindy', 'grace', 'wendy',
        'victoria', 'edith', 'kim', 'sherry', 'sylvia', 'josephine', 'thelma',
        'shannon', 'sheila', 'ethel', 'ellen', 'elaine', 'marjorie', 'carrie',
        'charlotte', 'monica', 'esther', 'pauline', 'emma', 'juanita', 'anita',
        'rhonda', 'hazel', 'amber', 'eva', 'debbie', 'april', 'leslie',
        'clara', 'lucille', 'jamie', 'joanne', 'eleanor', 'valerie', 'danielle',
        'megan', 'alicia', 'suzanne', 'michele', 'gail', 'bertha', 'darlene',
        'veronica', 'jill', 'erin', 'geraldine', 'lauren', 'cathy', 'joann',
        'lorraine', 'lynn', 'sally', 'regina', 'erica', 'beatrice', 'dolores',
        'bernice', 'audrey', 'yvonne', 'annette', 'june', 'samantha', 'marion',
        'dana', 'stacy', 'ana', 'renee', 'ida', 'vivian', 'roberta', 'holly',
        'brittany', 'melanie', 'loretta', 'yolanda', 'jeanette', 'laurie',
        'katie', 'kristen', 'vanessa', 'alma', 'sue', 'elsie', 'beth',
        'jeanne', 'rosemary', 'patty', 'arlene', 'mabel', 'marsha'
    }
    
    words = text.split()
    for i, word in enumerate(words):
        # Если слово в нижнем регистре и есть в списке имен - делаем заглавной
        if word.lower() in common_names and word.islower():
            words[i] = word.capitalize()
    
    return ' '.join(words)

def smart_format_text(text_lines):
    """Умное форматирование с сохранением структуры по строкам"""
    formatted_lines = []
    
    for line in text_lines:
        line = line.strip()
        if not line:
            continue
            
        # Исправляем имена
        line = capitalize_names(line)
            
        # Заглавная буква в начале строки
        if line and line[0].isalpha():
            line = line[0].upper() + line[1:]
        
        # Добавляем точку в конец, если нет пунктуации
        if line and line[-1].isalnum():
            line += '.'
            
        formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)

def transcribe_audio(audio_path, model_path):
    print("🧠 Загружаю модель...")
    model = Model(model_path)

    wf = wave.open(audio_path, "rb")
    if wf.getnchannels() != 1:
        print("⚠️ Аудио не моно. ffmpeg должен был это исправить.")
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)

    print("🎧 Распознаю речь...\n")
    subtitles = []

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            if "text" in result and result["text"].strip():
                text = result["text"].strip()
                subtitles.append(text)
                print(text)

    final = json.loads(rec.FinalResult())
    if "text" in final and final["text"].strip():
        subtitles.append(final["text"].strip())
        print(final["text"].strip())

    wf.close()

    # Форматируем текст с сохранением структуры строк
    print("\n🔤 Форматирую текст...")
    all_text = smart_format_text(subtitles)
    
    pyperclip.copy(all_text)
    print("\n✅ Отформатированный текст скопирован в буфер обмена.")
    print("\n=== Форматированный текст ===\n")
    print(all_text)

def main():
    if len(sys.argv) < 3:
        print("Использование: python transcribe_mp4_vosk.py video.mp4 vosk-model-small-ru-0.22")
        sys.exit(1)

    video_path = sys.argv[1]
    model_path = sys.argv[2]

    if not os.path.exists(video_path):
        print("❌ Видео не найдено:", video_path)
        sys.exit(1)
    if not os.path.exists(model_path):
        print("❌ Модель не найдена:", model_path)
        sys.exit(1)

    wav_path = extract_audio_from_video(video_path)
    transcribe_audio(wav_path, model_path)
    os.remove(wav_path)

if __name__ == "__main__":
    main()