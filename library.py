import re
from typing import List
from chess import pgn
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime, timedelta
import pandas as pd
import requests
import io
import pytz

def hello_world(name):
    print("Hello ", name)
    
"""
Network Functions
"""

def fetch_recent_games():
    parsed_games = []
    for i in range(8):
        games_res = requests.get(f"https://api.chess.com/pub/player/{os.environ.USERNAME}/games/2022/0{i}/pgn").text
        [parsed_games.append(pgn.read_game(io.StringIO(g))) for g in games_res.split("\n\n\n")]


def fetch_all_games(username):
    """
    Fetches and parses all games since starting the account
    """
    player_joined = requests.get(f"https://api.chess.com/pub/player/{username}").json()["joined"]
    date_joined = datetime.fromtimestamp(player_joined)
    month = date_joined.month
    year = date_joined.year

    now = datetime.now()

    parsed_games = []
    while datetime(year, month, 1) - now <= timedelta(0,1,0):
        month_text = f"0{month}" if month < 10 else f"{month}"
        games_res = requests.get(f"https://api.chess.com/pub/player/{username}/games/{year}/{month_text}/pgn").text
        [parsed_games.append(pgn.read_game(io.StringIO(g))) for g in games_res.split("\n\n\n")]
        month += 1
        if month > 12:
            month -= 12
            year += 1
    
    return clean_games(parsed_games)
"""
Chess Functions
"""
def is_rapid(time_control: str) -> bool:
    match = re.match("\d+", time_control)
    if not match: raise "Invalid Time Control"
    return int(match.group(0)) >= 600

assert is_rapid("600")
assert not is_rapid("100")

def is_live(event: str) -> bool:
    return event == "Live Chess"

def filter_rapid(games):
    return list(filter(lambda g: is_rapid(g.headers["TimeControl"]) and is_live(g.headers["Event"]), games))
    

"""
Datetime Functions
"""

def parse_date(date: str) -> int:
    return datetime.strptime(date, "%Y.%m.%d").replace(tzinfo=pytz.UTC).timestamp()

"""
Util Functions
"""
def clean_games(games):
    return list(filter(lambda g: g is not None and "TimeControl" in g.headers.keys(), games))

"""
Data Functions
"""
def build_rating_frame(games, username):
    rating_times = [[int(g.headers["WhiteElo"] if g.headers["White"] == username else g.headers["BlackElo"]), 
                     parse_date(g.headers["UTCDate"])] 
                    for g in games]
    return pd.DataFrame(rating_times, columns=["Rating", "Date"])


def build_rating_list(games, username):
    """
    @returns List[DateUTC,Rating]
    """
    return [[parse_date(g.headers["UTCDate"]),
             int(g.headers["WhiteElo"] if g.headers["White"] == username else g.headers["BlackElo"])] 
                    for g in games]
    
