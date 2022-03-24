# ChoresApp
## Simple webapp to track whose turn it is to do chores

### Requirements:

* Current alembic.ini points to a sqlite3 database, but it should be portable to other DBs.
* Python 3.8+ (curerntly uses 3.10)

### Setup:

1. Install dependencies via poetry
1. `alembic init choresdb`
1. Populate database using the admin.py CLI. You can also import from it fairly easily to automate the process.
1. Get credentials for your notification service of choice (GMail is currently non-functional)
1. Configure your environment variables (see example in .env.sample)
1. Run main.py
