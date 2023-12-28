import os
import threading
import psutil


browsers = [
    'chrome.exe',
    'firefox.exe',
    'msedge.exe',
    'Safari.exe',
    'opera.exe',
    'iexplore.exe',
    'brave.exe',
    'vivaldi.exe',
    'browser.exe',
    'Maxthon.exe',
    'UCBrowser.exe',
    'avant.exe',
    'Slimjet.exe',
    'Epic.exe',
    'waterfox.exe',
    'palemoon.exe',
    'dragon.exe',
    'midori.exe']
games = [
    'steam.exe',
    'dota.exe',
    'csgo.exe',
    'gta.exe',
    'minecraft.exe',
    'cyberpunk.exe',
    'portal.exe',
    'fortnite.exe',
    'leagueoflegends.exe',
    'Discord.exe', 
    'Telegram.exe'
]

def close_browser():
    for process_name in browsers:
        for process in psutil.process_iter(['pid', 'name']):
            if process.info['name'] == process_name:
                try:
                    p = psutil.Process(process.info['pid'])
                    p.terminate()  # Отправить сигнал завершения процессу
                    # Или использовать p.kill() для принудительного завершения процесса
                    print(f"{process_name} успешно закрыто.")
                except Exception as e:
                    print(f"Ошибка при закрытии {process_name}: {e}")

def close_game():
    for process_name in games:
        for process in psutil.process_iter(['pid', 'name']):
            if process.info['name'] == process_name:
                try:
                    p = psutil.Process(process.info['pid'])
                    p.terminate()  # Отправить сигнал завершения процессу
                    # Или использовать p.kill() для принудительного завершения процесса
                    print(f"{process_name} успешно закрыто.")
                except Exception as e:
                    print(f"Ошибка при закрытии {process_name}: {e}")
    # for process_name in games:
    #     for process in psutil.process_iter(['pid', 'name']):
    #         if process.info['name'] == process_name:
    #             pid = process.info['pid']
    #             p = psutil.Process(pid)
    #             p.terminate()
    #             return


def start():
    timer.start()

def stop():
    timer.cancel()

timer = threading.Timer(5.0, close_game)
