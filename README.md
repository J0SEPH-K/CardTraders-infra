# CardTraders Infra

## Seeding a test user into MongoDB

This repo includes a helper script to upsert a test user into your MongoDB Atlas cluster.

- Database: `cardtraders`
- Collection: `users`
- Default user: `test@cardtraders.app` with password `Test1234!` (the script hashes it with bcrypt)

### 1) Prerequisites
- Python 3.10+
- Packages: `pymongo`, `bcrypt`

Install them (in a venv is recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pymongo bcrypt
```

### 2) Set MongoDB connection string

```bash
export MONGODB_URI="mongodb+srv://<user>:<pass>@<cluster>/?retryWrites=true&w=majority"
```

### 3) Run the seed script

```bash
python3 infra/scripts/seed_mongo_user.py \
  --pfp-url "https://example.com/pfp/test-user.png" \
  --phone "010-0000-0000" \
  --address "서울특별시 어딘가 123" \
  --premade "안녕하세요" --premade "구매 가능합니다"
```

By default, it will upsert the user with email `test@cardtraders.app` and generate a `userId`. You can override fields with flags (see `--help`).

### Data model notes
- pfp: store an HTTPS URL to an image hosted on a CDN (S3, Cloudinary, etc.). GridFS is possible but usually unnecessary for profile icons.
- password: stored as a bcrypt hash.
- starred_item: list of ObjectId referencing documents in the `uploadedCards` collection.
- messages: recommend separate collections:
  - `conversations`: { conversationId, members: [userId], lastMessageAt, lastMessage }
  - `messages`: { conversationId, fromUserId, toUserId, body, attachments, createdAt, readAt }
  The user doc can optionally hold light-weight derived fields like `inbox_unread_count`.
- premade_messages: list of strings users can reuse when chatting.
- blocked_users: list of userId strings to hide or block DM creation.

- DB schema under `infra/db/schema.sql`
- CI templates under `infra/github/workflows`
- Dev helper scripts under `infra/scripts`
