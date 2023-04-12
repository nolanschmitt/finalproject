import requests
import json
import sqlite3
import pickle
import os
from bs4 import BeautifulSoup

def create_database():
    conn = sqlite3.connect("ncaa_teams.db")
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS team_wins_losses
                      (id INTEGER PRIMARY KEY, school TEXT, name TEXT, wins INTEGER, losses INTEGER)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS team_conf_wins_losses
                      (id INTEGER PRIMARY KEY, school TEXT, name TEXT, confWins INTEGER, confLosses INTEGER)''')

    conn.commit()
    return conn

def get_all_teams(api_key, conn, offset=0, limit=25):
    url = f"https://api.sportsdata.io/v3/cbb/scores/json/teams?key={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        teams = json.loads(response.content.decode('utf-8'))
        cursor = conn.cursor()

        for team in teams[offset:offset+limit]:
            try:
                cursor.execute("INSERT INTO team_wins_losses (id, school, name, wins, losses) VALUES (?, ?, ?, ?, ?)",
                                (team['TeamID'], team['School'], team['Name'], team['Wins'], team['Losses']))
            except sqlite3.IntegrityError:
                pass  # Ignore duplicate entries

            try:
                cursor.execute("INSERT INTO team_conf_wins_losses (id, school, name, confWins, confLosses) VALUES (?, ?, ?, ?, ?)",
                                (team['TeamID'], team['School'], team['Name'], team['ConferenceWins'], team['ConferenceLosses']))
            except sqlite3.IntegrityError:
                pass  # Ignore duplicate entries

        conn.commit()
    else:
        print(f"Error fetching teams data. Status code: {response.status_code}")


def second():
    conn=  sqlite3.connect('ncaa_teams.db')
    c = conn.cursor()



    c.execute(''' CREATE TABLE IF NOT EXISTS ncaa_teams
                (team_name TEXT, games_played INTEGER,
                three_points INTEGER, rpg REAL
                )  ''')


    items_stored = 0
    url = 'https://basketball.realgm.com/ncaa/team-stats'

    response = requests.get(url)
    #print(response.content)

    soup = BeautifulSoup(response.content, 'html.parser')

    table = soup.find('table', {'class': 'tablesaw'})
    rows = table.find_all('tr')[1:]  # Skip the header row

    for row in rows:
        data = row.find_all('td')
        team_name = data[1].text.strip()
        points_per_game = int(round(float(data[4].text.strip())))
        games_played = int(data[2].text.strip())
        three_points = int(round(float(data[8].text.strip())))
        rpg = int(round(float(data[16].text.strip())))


        c.execute('''SELECT * FROM ncaa_teams WHERE team_name = ?''',
                (team_name,))
        if  c.fetchone():
            continue
            # Insert the data into the database
        c.execute('''INSERT INTO ncaa_teams VALUES (?,?,?,?)''',
                    ( team_name, games_played,
                    three_points, rpg))
        items_stored += 1

        if items_stored == 25:
            break



    conn.commit()

    conn.close()


def main():
    api_key = "a25c9131b52644ae85644b62f0de7566"  # Replace with your actual API key
    conn = create_database()

    counter_file = 'counter.pkl'

    if os.path.exists(counter_file):
        with open(counter_file, 'rb') as f:
            counter = pickle.load(f)
    else:
        counter = 0
    counter = counter%4
    offset = counter * 25
    get_all_teams(api_key, conn, offset=offset, limit=25)
    second()
    counter += 1

    with open(counter_file, 'wb') as f:
        pickle.dump(counter, f)

    conn.close()

if __name__ == "__main__":
    main()
