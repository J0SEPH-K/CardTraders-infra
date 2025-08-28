import os
from datetime import datetime, timezone
from pymongo import MongoClient, ReturnDocument

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "cardtraders")


def next_seq(db, name: str) -> int:
    res = db["counters"].find_one_and_update(
        {"_id": name},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return int(res.get("seq") or 1)


def main():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]

    # Optional cleanup: delete existing dummy buyer data if in uploadedCards
    # db["uploadedCards"].delete_many({})

    doc = {
        "id": next_seq(db, "uploadedCards"),
        "category": "pokemon",
        "card_name": "Pikachu (Illustration Rare)",
        "rarity": "Illustration Rare",
        "language": "en",
        "set": "SVP Black Star Promos",
        "card_num": "SVP 085",
        "createdAt": datetime.now(timezone.utc),
    }

    db["uploadedCards"].insert_one(doc)
    print("Inserted:", doc)


if __name__ == "__main__":
    main()
