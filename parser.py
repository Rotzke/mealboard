#!/usr/bin/python3.6
"""Recipes parser for MealBord website."""
import yaml
import base64
import logging
from io import BytesIO

import requests
from bs4 import BeautifulSoup


URL = 'http://mealboard.macminicolo.net/mealboard'
requests = requests.Session()
payload = {'username': '',  # Add credentials here
           'pin': ''}
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)


def stars(soup):
    """Convert stars png to rating points."""
    rating = 0
    for i in soup.findAll('img'):
        if i['src'] == 'star_filled_webview.png':
            rating += 1
        elif i['src'] == 'star_half_filled_webview.png':
            rating += 0.5
    return rating


def img_base64(url):
    """Convert image file into base64 string."""
    return base64.b64encode(BytesIO(requests.get(url).content).read()
                            ).decode('utf-8')


def parse_recipes():
    """Writing all recipes to YAML file."""
    requests.post('{}/loginsubmit.jsp'.format(URL), data=payload)
    recipes = []
    r = requests.get('{}/recipelist.jsp?RECIPE_NAME=NEW%20RECIPE'.format(URL))
    soup = [i.text for i in
            BeautifulSoup(r.text, 'lxml').findAll('td')[2:]][0:1]
    for num, i in enumerate(soup):
        dictey = {}
        d = requests.get('{}/recipeview.jsp?RECIPE_NAME={}'.format(URL, i))
        dish_soup = BeautifulSoup(d.text, 'lxml')
        try:
            dictey['name'] = dish_soup.find('div', {'class': 'name'}).text
        except AttributeError:
            dictey['name'] = ''
        try:
            dictey['servings'] =\
                dish_soup.find('div', {'class':
                                       'info'
                                       }
                               ).findAll('div')[0].text.strip().split(': ')[1]
        except AttributeError:
            dictey['servings'] = ''
        try:
            dictey['source'] = dish_soup.find('div', {'class': 'source'}).text
        except AttributeError:
            dictey['source'] = ''
        try:
            dictey['prep_time'] =\
                dish_soup.find('div', {'class':
                                       'info'
                                       }
                               ).findAll('div')[1].text.strip().split(': ')[1]
        except AttributeError:
            dictey['prep_time'] = ''
        try:
            dictey['cook_time'] =\
                dish_soup.find('div', {'class':
                                       'cookingTimeBox'
                                       }).text.strip().split(': ')[1]
        except AttributeError:
            dictey['cook_time'] = ''
        try:
            dictey['photo'] =\
                img_base64(dish_soup.find('div',
                                          {'class': 'photo'}).img['src'])
        except AttributeError:
            dictey['photo'] = ''
        try:
            dictey['ingredients'] =\
                '\n'.join([i.strip()
                           for i in dish_soup.find('div',
                                                   {'class':
                                                    'ingredientsBox'
                                                    }
                                                   ).text.strip().split('\n')
                           if i != '']).encode('ascii',
                                               errors='ignore').decode('utf-8')
        except AttributeError:
            dictey['ingredients'] = ''
        try:
            dictey['directions'] =\
                '\n'.join([str(i).strip()
                          for i in dish_soup.find('div',
                                                  {'class':
                                                   'preparationBox'
                                                   }
                                                  ).contents
                           if str(i) != '<br/>']
                          ).encode('ascii',
                                   errors='ignore').decode('utf-8')
        except AttributeError:
            dictey['directions'] = ''
        try:
            dictey['notes'] =\
                dish_soup.find('div',
                               {'class':
                                'description'
                                }
                               ).text.\
                strip().encode('ascii', errors='ignore'
                               ).decode('utf-8').\
                replace('\n', '').replace('\r', '')
        except AttributeError:
            dictey['notes'] = ''
        rating = stars(dish_soup.find('div', {'class': 'rating'}))
        if rating > 0:
            dictey['rating'] = str(int(rating))
        recipes.append(dictey)
        logging.info(num+1)
    with open('data.yml', 'w') as outfile:
        yaml.dump(recipes, outfile, default_style='|')


if __name__ == '__main__':
    parse_recipes()
