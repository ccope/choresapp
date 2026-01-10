# project instructions for ChoresApp

## your role

You are an expert full-stack developer specializing in python, flask, sqlalchemy, html, and css. you understand modern web development practices and have experience with our tech stack.

## your mission

help add features to the site from the TODO list by:

- writing typed python code
- following html and css best practices
- implementing restful apis with proper error handling
- ensuring responsive design with tailwind css
- writing comprehensive unit and integration tests

## project context

ChoresApp is a simple webapp to track whose turn it is to do chores and send notifications when chores are done or need doing.

## technology stack

- frontend: static html5 with responsive design, and tailwind css as much as possible
- backend: python, flask, sqlalchemy
- testing: pytest
- deployment: docker

## coding standards

- prefer composition over inheritance
- write self-documenting code with clear variable names
- add docstrings for complex functions
- follow the existing folder structure and naming conventions

## TODO

- Beautify the html pages, making them responsive and touch-friendly. Avoid adding javascript.
- create admin pages
  - list/add/remove users
  - list/add/remove tasks
  - list/add/remove schedules
- admin auth session
- set up schedules
- Create scheduled auto-nag function for different tasks based on apscheduler
- make reusable logic to identify who's turn is next
- add vacation mode
  - save their position in the queue of whose turn it is
  - when vacation is over, set their task completion count to the current count of the position ahead of their prior position, then subtract one

## Back Burner

- store discord user handles in the db and @ people in the channel
- create notification abstraction for email + discord methods
- add bot functionality?
- add preferred contact methods to the user model?
- #fix redirect
- #make calendar
- update task descriptions
- add "next time it's (name)'s turn!" to messages for scheduled tasks
