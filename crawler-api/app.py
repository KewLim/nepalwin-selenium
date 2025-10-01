from fastapi import FastAPI
from typing import Optional
from scripts.crawler_depo import crawler_depo_api
from scripts.crawler_phone import crawler_phone_api
from scripts.add_deposit import add_deposit_api
from scripts.add_player import add_player_api

app = FastAPI()

@app.post("/crawler/deposit")
def crawler_deposit(website_choice: str = "1", start_date: str = None, end_date: str = None):
    """
    Crawl deposit transactions
    Args:
        website_choice: "1" for NepalWin, "2" for 95np
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    try:
        result = crawler_depo_api(website_choice, start_date, end_date)
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/crawler/phone")
def crawler_phone(website_choice: str = "1", start_date: str = None, end_date: str = None):
    """
    Crawl phone numbers
    Args:
        website_choice: "1" for NepalWin, "2" for 95np
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    try:
        result = crawler_phone_api(website_choice, start_date, end_date)
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/add/deposit")
def add_deposit(website_choice: str = "1", start_order_ids_config: dict = None):
    """
    Add deposits from transaction history
    Args:
        website_choice: "1" for NepalWin, "2" for 95np
        start_order_ids_config: Configuration for start order IDs per gateway
    """
    try:
        result = add_deposit_api(website_choice, start_order_ids_config)
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/add/player")
def add_player(website_choice: str = "1"):
    """
    Add players from phone number file
    Args:
        website_choice: "1" for NepalWin, "2" for 95np
    """
    try:
        result = add_player_api(website_choice)
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}
