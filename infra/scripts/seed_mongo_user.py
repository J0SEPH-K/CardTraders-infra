#!/usr/bin/env python3
"""
Seed a test user into MongoDB Atlas.

- Database: cardtraders
- Collection: users

This script will:
- Connect using MONGODB_URI (mongodb+srv://...)
- Upsert a user document for email test@cardtraders.app
- Hash the password Test1234! with bcrypt
- Include the requested fields and sensible defaults

Usage:
  export MONGODB_URI="mongodb+srv://<user>:<pass>@<cluster>/?retryWrites=true&w=majority"
  python3 infra/scripts/seed_mongo_user.py \
    --pfp-url "https://example.com/pfp/test-user.png" \
    --phone "010-0000-0000" \
    --address "서울특별시 어딘가 123" \
    --premade "안녕하세요" --premade "구매 가능합니다"

Notes:
- For pfp, prefer storing a URL to an object storage (e.g., S3/Cloudinary) instead of binary in Mongo; GridFS is an option for large binaries, but a CDN URL is typically better for mobile apps.
- For messages, prefer separate collections (conversations, messages). Here we store an empty list or lightweight conversation metadata for demonstration.
"""

from __future__ import annotations
import os
import sys
import argparse
import uuid
from datetime import datetime, timezone

from pymongo import MongoClient, ASCENDING
import bcrypt
from bson import ObjectId


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Seed a test user into MongoDB")
    p.add_argument("--email", default="test@cardtraders.app", help="User email")
    p.add_argument("--password", default="Test1234!", help="Plaintext password to hash")
    p.add_argument("--username", default="test-user", help="Username")
    p.add_argument("--phone", dest="phone_num", default="010-0000-0000", help="Phone number")
    p.add_argument("--address", default="서울특별시 어딘가 123", help="Address")
    p.add_argument("--pfp-url", default=None, help="Profile image URL (recommended)")
    p.add_argument("--notification", action="store_true", default=True, help="Enable notifications")
    p.add_argument("--no-notification", dest="notification", action="store_false", help="Disable notifications")
    p.add_argument("--starred", action="append", default=[], help="Add a starred uploadedCards item id (ObjectId string). Can be used multiple times.")
    p.add_argument("--blocked", action="append", default=[], help="Add a blocked userId. Can be used multiple times.")
    p.add_argument("--premade", action="append", default=["안녕하세요", "구매 가능합니다"], help="Premade message string. Can be used multiple times.")
    p.add_argument("--signup-date", default=datetime.now().strftime("%Y/%m/%d"), help="Signup date in YYYY/MM/DD format")
    p.add_argument("--user-id", default=None, help="Force a userId (otherwise generated)")
    return p.parse_args()


def get_client() -> MongoClient:
    uri = os.environ.get("MONGODB_URI") or os.environ.get("MONGO_URI")
    if not uri:
        print("ERROR: Please set MONGODB_URI env var.", file=sys.stderr)
        sys.exit(1)
    return MongoClient(uri)


def ensure_indexes(users):
    # Ensure unique email index
    users.create_index([("email", ASCENDING)], name="uniq_email", unique=True)
    users.create_index([("userId", ASCENDING)], name="idx_userId", unique=True)


def main():
    args = parse_args()
    client = get_client()
    db = client["cardtraders"]
    users = db["users"]

    ensure_indexes(users)

    # Prepare fields
    now = datetime.now(timezone.utc)
    user_id = args.user_id or f"usr_{uuid.uuid4().hex[:12]}"

    # Hash password
    pw_hash = bcrypt.hashpw(args.password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")

    # Prepare starred_item as ObjectIds if possible
    starred: list[ObjectId] = []
    for s in args.starred:
        try:
            starred.append(ObjectId(s))
        except Exception:
            print(f"WARN: skipping invalid ObjectId in --starred: {s}")

    doc = {
        "userId": user_id,
        "username": args.username,
        "email": args.email.lower(),
        "password": pw_hash,  # bcrypt hash
        "phone_num": args.phone_num,
        "address": args.address,
        "signup_date": args.signup_date,  # string YYYY/MM/DD
        "suggested_num": 0,
        "starred_item": starred,  # list of ObjectId referencing 'uploadedCards'
        # Messages: recommend storing conversations/messages in separate collections.
        # For now, store lightweight conversation metadata.
        "messages": [],
        "premade_messages": args.premade,
        "notification": bool(args.notification),
        "blocked_users": list(args.blocked),  # list of userId strings
        # pfp recommendation: store URL to CDN; if not provided, keep None.
        "pfp": {
            "url": args.pfp_url,
            "storage": "url" if args.pfp_url else None,
        },
        "createdAt": now,
        "updatedAt": now,
    }

    # Upsert on email
    res = users.update_one({"email": doc["email"]}, {"$set": doc, "$setOnInsert": {"userId": user_id}}, upsert=True)

    if res.upserted_id:
        print(f"Inserted user with _id={res.upserted_id} email={doc['email']} userId={user_id}")
    else:
        print(f"Updated user email={doc['email']} userId={user_id}")

    print("Done.")


if __name__ == "__main__":
    main()
