import os
import sys
import subprocess
import pyperclip
import wave
import json
import time
from concurrent.futures import ThreadPoolExecutor

# Настройки скорости
MAX_WORKERS = 20  # Количество одновременных потоков скачивания

def download_segment(args):
    url, index = args
    temp_file = f"seg_{index:04d}.ts"
    # Скачиваем только аудио часть сегмента для экономии времени
    cmd = [
        "ffmpeg", "-y", "-i", url, 
        "-vn", "-acodec", "copy", 
        "-loglevel", "error", temp_file
    ]
    subprocess.run(cmd)
    return temp_file

def fast_multithread_download(input_path, out_wav="temp_audio.wav"):
    print(f"🚀 Запуск многопоточной загрузки ({MAX_WORKERS} потоков)...")
    
    with open(input_path, 'r', encoding='utf-8') as f:
        links = [line.strip() for line in f if line.strip().startswith('http')]
    
    if not links:
        print("❌ Ссылки не найдены!")
        return None

    # Шаг 1: Параллельное скачивание сегментов
    print(f"📥 Скачиваю {len(links)} сегментов...")
    indexed_links = list(zip(links, range(len(links))))
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        temp_files = list(executor.map(download_segment, indexed_links))

    # Шаг 2: Создание списка для склейки
    concat_list = "list.txt"
    with open(concat_list, 'w') as f:
        for temp_file in temp_files:
            f.write(f"file '{temp_file}'\n")

    # Шаг 3: Мгновенная склейка и конвертация в WAV
    print("🧩 Склеиваю и оптимизирую для Vosk...")
    cmd_concat = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", 
        "-i", concat_list, "-ar", "16000", "-ac", "1", out_wav
    ]
    subprocess.run(cmd_concat, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Шаг 4: Очистка временных файлов
    print("🧹 Очистка...")
    for f in temp_files:
        if os.path.exists(f): os.remove(f)
    os.remove(concat_list)
    
    return out_wav

def transcribe_audio(audio_path, model_path):
    from vosk import Model, KaldiRecognizer
    if not os.path.exists(model_path): return
    
    model = Model(model_path)
    wf = wave.open(audio_path, "rb")
    rec = KaldiRecognizer(model, wf.getframerate())
    
    print("🧠 Распознавание началось...")
    results = []
    while True:
        data = wf.readframes(32000)
        if len(data) == 0: break
        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            if res['text']:
                print(f"🎤 {res['text']}")
                results.append(res['text'])
    
    final = json.loads(rec.FinalResult())
    if final['text']: results.append(final['text'])
    wf.close()
    
    full_text = " ".join(results)
    pyperclip.copy(full_text)
    print("\n✅ ГОТОВО! Текст в буфере.")

def main():
    if len(sys.argv) < 3: return
    
    input_file = sys.argv[1]
    model_folder = sys.argv[2]
    
    start_time = time.time()
    
    # Теперь скачивание пойдет в 20 раз быстрее
    wav_file = fast_multithread_download(input_file)
    
    if wav_file and os.path.exists(wav_file):
        transcribe_audio(wav_file, model_folder)
        os.remove(wav_file)
    
    print(f"\n⏱ Итоговое время: {int(time.time() - start_time)} сек.")

if __name__ == "__main__":
    main()