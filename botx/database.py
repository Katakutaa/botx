import json
import os
from datetime import datetime

DB_FILE = "orders.json"

def load_db():
    if not os.path.exists(DB_FILE):
        return {"orders": {}, "counter": 0}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def create_order(user_id, username, file_id, bet_soni, kategoriya, narx, muddat):
    db = load_db()
    db["counter"] += 1
    order_id = f"{db['counter']:04d}"
    
    db["orders"][order_id] = {
        "id": order_id,
        "user_id": user_id,
        "username": username or "Noma'lum",
        "file_id": file_id,
        "bet_soni": bet_soni,
        "kategoriya": kategoriya,
        "narx": narx,
        "muddat": muddat,
        "status": "kutilmoqda",  # kutilmoqda | tasdiqlandi | rad_etildi | bajarildi
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "result_file_id": None,
    }
    save_db(db)
    return order_id

def get_order(order_id):
    db = load_db()
    return db["orders"].get(order_id)

def update_order_status(order_id, status):
    db = load_db()
    if order_id in db["orders"]:
        db["orders"][order_id]["status"] = status
        save_db(db)
        return True
    return False

def set_result_file(order_id, file_id):
    db = load_db()
    if order_id in db["orders"]:
        db["orders"][order_id]["result_file_id"] = file_id
        db["orders"][order_id]["status"] = "bajarildi"
        save_db(db)
        return True
    return False

def get_all_orders():
    db = load_db()
    return db["orders"]

def get_user_orders(user_id):
    db = load_db()
    return {k: v for k, v in db["orders"].items() if v["user_id"] == user_id}
