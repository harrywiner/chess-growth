import pandas as pd
import requests

from dotenv import load_dotenv
load_dotenv()

from library import hello_world, fetch_all_games, filter_rapid, build_rating_frame
hello_world("Harry")


rapid_games = filter_rapid(fetch_all_games(os.environ.USERNAME))

df = build_rating_frame(rapid_games)
