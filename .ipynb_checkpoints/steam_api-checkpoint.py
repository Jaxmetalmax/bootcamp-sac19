from bottle import Bottle, run, template, request
import sqlite3
import updategames
import datetime

app = Bottle()

@app.route('/games', method='GET')
def get_list_games():
    connection = sqlite3.connect('games.db')
    cursor = connection.cursor()
    cursor.execute("SELECT DISTINCT title FROM games")
    result = cursor.fetchall()
    list_games=[]

    for title in result:
        list_games.append(title[0])
        
    return {"games": list_games}

@app.route('/games/date/:date', method='GET')
def get_list_games(date):
    connection = sqlite3.connect('games.db')
    cursor = connection.cursor()
    cursor.execute(f"SELECT title, price FROM games WHERE date='{date}'")
    result = cursor.fetchall()
    list_games=[]
    
    for title in result:
        gameobj = {title[0]:title[1]}
        list_games.append(gameobj)
        
    return {date : list_games}

@app.route('/games/history', method='GET')
def get_game_history():
    data = request.json
    connection = sqlite3.connect('games.db')
    cursor = connection.cursor()

    title_game = data["title"]
    cursor.execute(f"SELECT price, date FROM games WHERE title='{title_game}'")
    result = cursor.fetchall()
    list_prices=[]
    for title in result:
        gameobj = {title[0]:title[1]}
        list_prices.append(gameobj)
    
    return {title_game: list_prices}

@app.route('/games/update/price', method='POST')
def update_game_price():
    data = request.json
    connection = sqlite3.connect('games.db')
    cursor = connection.cursor()

    title_game = data["title"]
    title_price = data["price"]
    title_date = data["date"]
    now = datetime.date.today().strftime("%Y-%m-%d")

    cursor.execute(f"UPDATE games SET price='{title_price}', date='{now}' WHERE title='{title_game}' AND date='{title_date}'")
    connection.commit()
    
    return {title_game: {"price":title_price, "date":now }}

@app.route('/games/update/list', method='GET')
def update_game_list():
    list_scrap = updategames.scrap_titles()
    updategames.update_game_list(list_scrap)

    connection = sqlite3.connect('games.db')
    
    now = datetime.date.today().strftime("%Y-%m-%d")

    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM games WHERE date='{now}'")
    result = cursor.fetchall()
    list_games=[]

    for title in result:
        list_games.append({title[0]: {"price": title[1], "tags":title[2], "platforms":title[3]}})
        
    return {now: list_games}

run(app, host='0.0.0.0', port=3000, reloader=True, debug=True)