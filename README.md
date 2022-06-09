# ChoresApp

## Simple webapp to track whose turn it is to do chores

### Requirements:

- Current alembic.ini points to a sqlite3 database, but it should be portable to other DBs.
- Python 3.8+ (currently uses 3.10)

### Setup:

1. Install dependencies via poetry
1. Run `alembic upgrade head` to create the database in ./data/
1. Populate database using the admin.py CLI. You can also script the process, see batch_sample.py
1. Get credentials for your notification service of choice (currently AWS or Discord)
1. Configure environment variables in a .env file or how you prefer (see example in .env.sample)
1. Run main.py
