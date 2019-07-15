import requests
import pickle
import time
import urllib
import os
from bs4 import BeautifulSoup


SPORT_PHOTO = {
    'football': 'photo-171276448_456239850',
    'basketbol': 'photo-171276448_456239851',
    'tennis': 'photo-171276448_456239849'
}


def get_time(event):
    event.replace('мин.', 'м.')
    if event.find('м.') != -1:
        return event[:event.find('м.') + 2], event[event.find('м.') + 2:].strip()
    else:
        return event[:event.find('ч.') + 2], event[event.find('ч.') + 2:].strip()


def get_bets(sport):
    bets = []
    if sport == 'tennis':
        url = "https://www.betonsuccess.ru/stavki-na-sport/vse/20/tennis/"
    elif sport == 'football':
        url = "https://www.betonsuccess.ru/stavki-na-sport/vse/19/futbol/"
    elif sport == 'basketbol':
        url = "https://www.betonsuccess.ru/stavki-na-sport/vse/3/basketbol/"
    elif sport == 'hokkej':
        url = 'https://www.betonsuccess.ru/stavki-na-sport/vse/8/hokkej/'

    else:
        print('No such sport: {}'.format(sport))
        return None

    r = urllib.request.urlopen(url)
    r.encoding = 'utf-8'
    soup = BeautifulSoup(r, features="html.parser")
    items = soup.find_all(class_='pick_item')
    for item in items:
        bet = {}
        bet['location'] = item.find(class_='location').text
        bet['event'] = item.find(class_='event_main').text
        bet['outcome'] = item.find(class_='outcome tte').text
        bet['stake'] = item.find_all(class_='stake')[1].text
        bet['odds'] = item.find_all(class_='odds')[1].text
        bet['comment'] = item.find(class_='comment').find('div').text

        bets.append(bet)

    if bets:
        return bets


def get_bet_id(bet):
    if bet:
        return get_time(bet['location'])[1]
    else:
        return 'void'


def post(msg, img):
    print(msg)
    url = 'https://api.vk.com/method/wall.post?message={}&access_token={}&v=5.100&owner_id=-171276448&attachments={}'.format(msg, '6ff13f867ab5517c2d621cad0b5667b1605571b150d4b47e2b4f5f9bca240eb0da5db4cabec960cfba3b2', img)
    requests.get(url)


def post_bet(b, sport):
    final_msg = ''
    
    if time.time() % 86400 > 74399:
        final_msg += "Последняя ставка на сегодня. Поздравляем тех, кто поднял с нами) \n"
        
    if time.time() % 86400 < 33800:
        final_msg += "Доброе утро! Начинаем работать, удачи всем. \n"
        
    if sport == 'football':
        final_msg += '!!! ФУТБОЛ !!! \n'
    elif sport == 'tennis':
        final_msg += '!!! ТЕННИС !!! \n'
    elif sport == 'basketbol':
        final_msg += '!!! БАСКЕТБОЛЛ !!! \n'

    final_msg += 'КФ: {}\n Событие: {}\n Турнир: {}\n Ставка: {}\n ' \
                 'Ставка сыграет через {}'.format(b['odds'],
                                                  b['event'],
                                                  get_time(b['location'])[1],
                                                  b['outcome'],
                                                  get_time(b['location'])[0])
    print(final_msg)
    post(final_msg, SPORT_PHOTO[sport])


if not(os.path.exists('data.pickle')):
    with open('data.pickle', 'wb') as file:
        pickle.dump(['void'], file)



j = 0
while True:
    
    if time.time() % 86400 > 75600 or time.time() % 86400 < 32400:
        print('Good night...')
        time.sleep(43200)
    
    
    football_bets = get_bets('football')
    print('Football bets parsed...')
    tennis_bets = get_bets('tennis')
    print('Tennis bets parsed...')
    bskt_bets = get_bets('basketbol')
    print('Basketball bets parsed...')

    with open('data.pickle', 'rb') as file:
        posted_bets = pickle.load(file)

        if j % 5 == 0 or j % 5 == 1 or j % 5 == 2:
            for b in football_bets:
                if not(get_bet_id(b) in posted_bets):
                    post_bet(b, 'football')
                    posted_bets.append(get_bet_id(b))
                    break

        elif j % 5 == 3:
            for b in tennis_bets:
                if not(get_bet_id(b) in posted_bets):
                    post_bet(b, 'tennis')
                    posted_bets.append(get_bet_id(b))
                    break

        else:
            for b in bskt_bets:
                if not(get_bet_id(b) in posted_bets):
                    post_bet(b, 'basketbol')
                    posted_bets.append(get_bet_id(b))
                    break

    with open('data.pickle', 'wb') as file:
        pickle.dump(posted_bets, file)

    j += 1
    time.sleep(1200)
