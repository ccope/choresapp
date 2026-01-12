"""Admin routes for managing people, tasks, and assignments."""
import os
from statistics import median
from typing import Any, Dict

from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy.sql import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError

from chores.models.choresdb import Assignments, People, Tasks, db

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# ============================================================================
# People Routes
# ============================================================================


@admin_bp.route("/people")
def list_people():
    """List all people."""
    people = db.session.execute(
        select(People).order_by(People.name)
    ).scalars().all()
    return render_template("admin/people/list.html", people=people)


@admin_bp.route("/people/new")
def new_person():
    """Show form to create a new person."""
    return render_template("admin/people/form.html", person=None)


@admin_bp.route("/people", methods=["POST"])
def create_person():
    """Create a new person."""
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    
    if not name or not email:
        flash("Name and email are required", "error")
        return redirect(url_for("admin.new_person"))
    
    try:
        person = People(name=name, email=email)
        db.session.add(person)
        db.session.commit()
        flash(f"Person '{name}' created successfully", "success")
        return redirect(url_for("admin.list_people"))
    except IntegrityError:
        db.session.rollback()
        flash(f"Person with name '{name}' or email '{email}' already exists", "error")
        return redirect(url_for("admin.new_person"))


@admin_bp.route("/people/<int:person_id>")
def view_person(person_id: int):
    """View details of a specific person."""
    person = db.session.execute(
        select(People)
        .options(selectinload(People.tasks).selectinload(Assignments.task))
        .where(People.id == person_id)
    ).scalar_one_or_none()
    
    if not person:
        flash("Person not found", "error")
        return redirect(url_for("admin.list_people"))
    
    return render_template("admin/people/detail.html", person=person)


@admin_bp.route("/people/<int:person_id>/edit")
def edit_person(person_id: int):
    """Show form to edit a person."""
    person = db.session.execute(
        select(People).where(People.id == person_id)
    ).scalar_one_or_none()
    
    if not person:
        flash("Person not found", "error")
        return redirect(url_for("admin.list_people"))
    
    return render_template("admin/people/form.html", person=person)


@admin_bp.route("/people/<int:person_id>/update", methods=["POST"])
def update_person(person_id: int):
    """Update a person."""
    person = db.session.execute(
        select(People).where(People.id == person_id)
    ).scalar_one_or_none()
    
    if not person:
        flash("Person not found", "error")
        return redirect(url_for("admin.list_people"))
    
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    
    if not name or not email:
        flash("Name and email are required", "error")
        return redirect(url_for("admin.edit_person", person_id=person_id))
    
    try:
        person.name = name
        person.email = email
        db.session.commit()
        flash(f"Person '{name}' updated successfully", "success")
        return redirect(url_for("admin.view_person", person_id=person_id))
    except IntegrityError:
        db.session.rollback()
        flash(f"Person with name '{name}' or email '{email}' already exists", "error")
        return redirect(url_for("admin.edit_person", person_id=person_id))


@admin_bp.route("/people/<int:person_id>/delete", methods=["POST"])
def delete_person(person_id: int):
    """Delete a person."""
    person = db.session.execute(
        select(People)
        .options(selectinload(People.tasks))
        .where(People.id == person_id)
    ).scalar_one_or_none()
    
    if not person:
        flash("Person not found", "error")
        return redirect(url_for("admin.list_people"))
    
    # Check if person has assignments
    if person.tasks:
        flash(
            f"Cannot delete '{person.name}' because they have {len(person.tasks)} assignment(s). "
            "Please remove all assignments first.",
            "error"
        )
        return redirect(url_for("admin.view_person", person_id=person_id))
    
    name = person.name
    db.session.delete(person)
    db.session.commit()
    flash(f"Person '{name}' deleted successfully", "success")
    return redirect(url_for("admin.list_people"))


# ============================================================================
# Tasks Routes
# ============================================================================


@admin_bp.route("/tasks")
def list_tasks():
    """List all tasks."""
    tasks = db.session.execute(
        select(Tasks).order_by(Tasks.name)
    ).scalars().all()
    return render_template("admin/tasks/list.html", tasks=tasks)


@admin_bp.route("/tasks/new")
def new_task():
    """Show form to create a new task."""
    return render_template("admin/tasks/form.html", task=None)


@admin_bp.route("/tasks", methods=["POST"])
def create_task():
    """Create a new task."""
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    
    if not name:
        flash("Task name is required", "error")
        return redirect(url_for("admin.new_task"))
    
    try:
        task = Tasks(name=name, description=description)
        db.session.add(task)
        db.session.commit()
        flash(f"Task '{name}' created successfully", "success")
        return redirect(url_for("admin.list_tasks"))
    except IntegrityError:
        db.session.rollback()
        flash(f"Task with name '{name}' already exists", "error")
        return redirect(url_for("admin.new_task"))


@admin_bp.route("/tasks/<int:task_id>")
def view_task(task_id: int):
    """View details of a specific task."""
    task = db.session.execute(
        select(Tasks)
        .options(selectinload(Tasks.people).selectinload(Assignments.person))
        .where(Tasks.id == task_id)
    ).scalar_one_or_none()
    
    if not task:
        flash("Task not found", "error")
        return redirect(url_for("admin.list_tasks"))
    
    return render_template("admin/tasks/detail.html", task=task)


@admin_bp.route("/tasks/<int:task_id>/edit")
def edit_task(task_id: int):
    """Show form to edit a task."""
    task = db.session.execute(
        select(Tasks).where(Tasks.id == task_id)
    ).scalar_one_or_none()
    
    if not task:
        flash("Task not found", "error")
        return redirect(url_for("admin.list_tasks"))
    
    return render_template("admin/tasks/form.html", task=task)


@admin_bp.route("/tasks/<int:task_id>/update", methods=["POST"])
def update_task(task_id: int):
    """Update a task."""
    task = db.session.execute(
        select(Tasks).where(Tasks.id == task_id)
    ).scalar_one_or_none()
    
    if not task:
        flash("Task not found", "error")
        return redirect(url_for("admin.list_tasks"))
    
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    
    if not name:
        flash("Task name is required", "error")
        return redirect(url_for("admin.edit_task", task_id=task_id))
    
    try:
        task.name = name
        task.description = description
        db.session.commit()
        flash(f"Task '{name}' updated successfully", "success")
        return redirect(url_for("admin.view_task", task_id=task_id))
    except IntegrityError:
        db.session.rollback()
        flash(f"Task with name '{name}' already exists", "error")
        return redirect(url_for("admin.edit_task", task_id=task_id))


@admin_bp.route("/tasks/<int:task_id>/delete", methods=["POST"])
def delete_task(task_id: int):
    """Delete a task."""
    task = db.session.execute(
        select(Tasks)
        .options(selectinload(Tasks.people))
        .where(Tasks.id == task_id)
    ).scalar_one_or_none()
    
    if not task:
        flash("Task not found", "error")
        return redirect(url_for("admin.list_tasks"))
    
    # Check if task has assignments
    if task.people:
        flash(
            f"Cannot delete '{task.name}' because it has {len(task.people)} assignment(s). "
            "Please remove all assignments first.",
            "error"
        )
        return redirect(url_for("admin.view_task", task_id=task_id))
    
    name = task.name
    db.session.delete(task)
    db.session.commit()
    flash(f"Task '{name}' deleted successfully", "success")
    return redirect(url_for("admin.list_tasks"))


# ============================================================================
# Assignments Routes
# ============================================================================


@admin_bp.route("/assignments")
def list_assignments():
    """List all assignments."""
    assignments = db.session.execute(
        select(Assignments)
        .options(
            selectinload(Assignments.person),
            selectinload(Assignments.task)
        )
        .order_by(Assignments.task_id, Assignments.counter)
    ).scalars().all()
    return render_template("admin/assignments/list.html", assignments=assignments)


@admin_bp.route("/assignments/new")
def new_assignment():
    """Show form to create a new assignment."""
    people = db.session.execute(
        select(People).order_by(People.name)
    ).scalars().all()
    tasks = db.session.execute(
        select(Tasks).order_by(Tasks.name)
    ).scalars().all()
    return render_template("admin/assignments/form.html", people=people, tasks=tasks)


@admin_bp.route("/assignments", methods=["POST"])
def create_assignment():
    """Create a new assignment."""
    person_id = request.form.get("person_id", "").strip()
    task_id = request.form.get("task_id", "").strip()
    
    if not person_id or not task_id:
        flash("Person and task are required", "error")
        return redirect(url_for("admin.new_assignment"))
    
    try:
        person_id = int(person_id)
        task_id = int(task_id)
    except ValueError:
        flash("Invalid person or task ID", "error")
        return redirect(url_for("admin.new_assignment"))
    
    # Check if person and task exist
    person = db.session.execute(
        select(People).where(People.id == person_id)
    ).scalar_one_or_none()
    task = db.session.execute(
        select(Tasks).where(Tasks.id == task_id)
    ).scalar_one_or_none()
    
    if not person or not task:
        flash("Person or task not found", "error")
        return redirect(url_for("admin.new_assignment"))
    
    # Check if assignment already exists
    existing = db.session.execute(
        select(Assignments).where(
            Assignments.people_id == person_id,
            Assignments.task_id == task_id
        )
    ).scalar_one_or_none()
    
    if existing:
        flash(f"'{person.name}' is already assigned to '{task.name}'", "error")
        return redirect(url_for("admin.new_assignment"))
    
    # Create assignment with counter set to median of existing assignees
    existing_assignments = db.session.execute(
        select(Assignments).where(Assignments.task_id == task_id)
    ).scalars().all()
    
    counter = 0
    if existing_assignments:
        counter = int(median([a.counter for a in existing_assignments]))
    
    assignment = Assignments(people_id=person_id, task_id=task_id, counter=counter)
    db.session.add(assignment)
    db.session.commit()
    flash(f"'{person.name}' assigned to '{task.name}' successfully", "success")
    return redirect(url_for("admin.list_assignments"))


@admin_bp.route("/assignments/<int:task_id>/<int:people_id>")
def view_assignment(task_id: int, people_id: int):
    """View details of a specific assignment."""
    assignment = db.session.execute(
        select(Assignments)
        .options(
            selectinload(Assignments.person),
            selectinload(Assignments.task)
        )
        .where(
            Assignments.task_id == task_id,
            Assignments.people_id == people_id
        )
    ).scalar_one_or_none()
    
    if not assignment:
        flash("Assignment not found", "error")
        return redirect(url_for("admin.list_assignments"))
    
    return render_template("admin/assignments/detail.html", assignment=assignment)


@admin_bp.route("/assignments/<int:task_id>/<int:people_id>/delete", methods=["POST"])
def delete_assignment(task_id: int, people_id: int):
    """Delete an assignment."""
    assignment = db.session.execute(
        select(Assignments)
        .options(
            selectinload(Assignments.person),
            selectinload(Assignments.task)
        )
        .where(
            Assignments.task_id == task_id,
            Assignments.people_id == people_id
        )
    ).scalar_one_or_none()
    
    if not assignment:
        flash("Assignment not found", "error")
        return redirect(url_for("admin.list_assignments"))
    
    person_name = assignment.person.name
    task_name = assignment.task.name
    db.session.delete(assignment)
    db.session.commit()
    flash(f"'{person_name}' unassigned from '{task_name}' successfully", "success")
    return redirect(url_for("admin.list_assignments"))


@admin_bp.route("/")
def index():
    """Admin home page."""
    people_count = db.session.execute(select(func.count(People.id))).scalar()
    tasks_count = db.session.execute(select(func.count(Tasks.id))).scalar()
    assignments_count = db.session.execute(select(func.count(Assignments.task_id))).scalar()
    
    return render_template(
        "admin/index.html",
        people_count=people_count,
        tasks_count=tasks_count,
        assignments_count=assignments_count
    )
