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

- create admin pages
  - create CRUD routes for people
  - create CRUD routes for tasks
  - create CRUD routes for assigning people to tasks
  - write tests for adding people, tasks, and assignments
  - write tests for removing a person who has been assigned to a task
- password-protect the admin routes
- make reusable logic to identify who's turn is next for a given task
- add vacation mode
  - save the number of times each task has been done in the vacation record
  - when vacation is over, for each task type, get the delta of the count of task completions since the vacation record was created, and add that delta to the person's count
  - create CRUD routes to view/add/remove vacations for people
  - add new html page for vacations, and add navigation link from the homepage to the new page
  - write tests for vacation mode, including when the user has had new task types assigned or unassigned whiel on vacation
- Create scheduled auto-nag function for different tasks based on apscheduler
- create admin pages for auto-nag
  - list/add/remove auto-nag schedules

## Back Burner

- store discord user handles in the db and @ people in the channel
- create notification abstraction for email + discord methods
- add bot functionality?
- add preferred contact methods to the user model?
- #fix redirect
- #make calendar
- update task descriptions
- add "next time it's (name)'s turn!" to messages for scheduled tasks
