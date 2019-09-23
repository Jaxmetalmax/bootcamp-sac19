import lxml.html
import requests as req
import sqlite3
import datetime

class GameTitle(object):
    def __init__(self,title="",price="",tags=None,platforms=None):
        self.title = title
        self.price = price
        self.tags = tags
        self.platforms = platforms

def scrap_titles():
    html = req.get ('https://store.steampowered.com/explore/new/')

    doc = lxml.html.fromstring(html.content)

    newReleases = doc.xpath('//div[@id="tab_newreleases_content"]')[0]

    titles = newReleases.xpath('.//div[@class="tab_item_name"]/text()')

    prices = newReleases.xpath('.//div[@class="discount_final_price"]/text()')
    

    tags = newReleases.xpath('.//div[@class="tab_item_top_tags"]')

    totalTags = []

    for tag in tags:
        totalTags.append(tag.text_content())

    totalTags = [tag.split(', ') for tag in totalTags]

    platforms_div = newReleases.xpath('.//div[@class="tab_item_details"]')

    totalPlatforms = []

    for game in platforms_div:
        namePlatform = game.xpath('.//span[contains(@class, "platform_img")]')
        platforms = [t.get('class').split(' ')[-1] for t in namePlatform]
        if 'hmd_separator' in platforms:
            platforms.remove('hmd_separator')
        totalPlatforms.append(platforms)

    titles_list = []

    for info in zip(titles,prices, totalTags, totalPlatforms):
        new_game = GameTitle()
        new_game.title = info[0]
        new_game.price = info[1]
        new_game.tags = info[2]
        new_game.platforms = info[3]
        titles_list.append(new_game)

    return titles_list

def update_game_list(game_list):
    
    if len(game_list) > 0:
        for game in game_list:

            connection = sqlite3.connect('games.db')
            cursor = connection.cursor()
            
            tags = ','.join(game.tags)
            platforms = ','.join(game.platforms)
            now = datetime.date.today().strftime("%Y-%m-%d")
            
            cursor.execute("INSERT INTO games (title,price,tags,platforms,date) VALUES (?,?,?,?,?)", (game.title, game.price, tags, platforms, now))

            connection.commit()
            cursor.close()

if __name__ == '__main__':
    game_list = scrap_titles()
    
    update_game_list(game_list)