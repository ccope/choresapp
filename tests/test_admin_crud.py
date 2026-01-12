"""Comprehensive tests for admin CRUD operations."""
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from chores.models.choresdb import Base, People, Tasks, Assignments
from chores.web import app


@pytest.fixture
def test_engine():
    """Create a test database engine."""
    engine = create_engine("sqlite:///:memory:", echo=True, future=True)
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def test_session(test_engine):
    """Create a test database session."""
    session = Session(test_engine)
    yield session
    session.close()


@pytest.fixture
def client(test_engine):
    """Create a Flask test client."""
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret-key"
    
    # Override the session to use our test database
    with app.test_client() as client:
        with client.application.app_context():
            from flask_sqlalchemy_session import flask_scoped_session
            from sqlalchemy.orm import sessionmaker
            SessionFactory = sessionmaker(autoflush=False, bind=test_engine)
            flask_scoped_session(SessionFactory, app)
        yield client


class TestPeopleCRUD:
    """Test CRUD operations for People."""
    
    def test_add_person(self, client, test_session):
        """Test adding a new person."""
        response = client.post("/admin/people", data={
            "name": "John Doe",
            "email": "john@example.com"
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b"John Doe" in response.data or b"created successfully" in response.data
        
        # Verify in database
        person = test_session.query(People).filter_by(name="John Doe").first()
        assert person is not None
        assert person.email == "john@example.com"
    
    def test_add_person_duplicate_name(self, client, test_session):
        """Test adding a person with duplicate name."""
        # Add first person
        person = People(name="Jane Doe", email="jane@example.com")
        test_session.add(person)
        test_session.commit()
        
        # Try to add duplicate
        response = client.post("/admin/people", data={
            "name": "Jane Doe",
            "email": "jane2@example.com"
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b"already exists" in response.data
    
    def test_add_person_duplicate_email(self, client, test_session):
        """Test adding a person with duplicate email."""
        # Add first person
        person = People(name="Bob Smith", email="bob@example.com")
        test_session.add(person)
        test_session.commit()
        
        # Try to add duplicate email
        response = client.post("/admin/people", data={
            "name": "Bob Jones",
            "email": "bob@example.com"
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b"already exists" in response.data
    
    def test_add_person_empty_fields(self, client):
        """Test adding a person with empty fields."""
        response = client.post("/admin/people", data={
            "name": "",
            "email": ""
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b"required" in response.data
    
    def test_list_people(self, client, test_session):
        """Test listing all people."""
        # Add test people
        person1 = People(name="Alice", email="alice@example.com")
        person2 = People(name="Bob", email="bob@example.com")
        test_session.add_all([person1, person2])
        test_session.commit()
        
        response = client.get("/admin/people")
        assert response.status_code == 200
        assert b"Alice" in response.data
        assert b"Bob" in response.data
    
    def test_view_person(self, client, test_session):
        """Test viewing a person's details."""
        person = People(name="Charlie", email="charlie@example.com")
        test_session.add(person)
        test_session.commit()
        
        response = client.get(f"/admin/people/{person.id}")
        assert response.status_code == 200
        assert b"Charlie" in response.data
        assert b"charlie@example.com" in response.data
    
    def test_update_person(self, client, test_session):
        """Test updating a person."""
        person = People(name="David", email="david@example.com")
        test_session.add(person)
        test_session.commit()
        
        response = client.post(f"/admin/people/{person.id}/update", data={
            "name": "David Smith",
            "email": "david.smith@example.com"
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify update
        test_session.refresh(person)
        assert person.name == "David Smith"
        assert person.email == "david.smith@example.com"
    
    def test_delete_person_without_assignments(self, client, test_session):
        """Test deleting a person without assignments."""
        person = People(name="Eve", email="eve@example.com")
        test_session.add(person)
        test_session.commit()
        person_id = person.id
        
        response = client.post(f"/admin/people/{person_id}/delete", follow_redirects=True)
        assert response.status_code == 200
        
        # Verify deletion
        person = test_session.query(People).filter_by(id=person_id).first()
        assert person is None
    
    def test_delete_person_with_assignments(self, client, test_session):
        """Test deleting a person who has assignments (should fail)."""
        # Create person, task, and assignment
        person = People(name="Frank", email="frank@example.com")
        task = Tasks(name="Clean Kitchen", description="Clean the kitchen")
        test_session.add_all([person, task])
        test_session.commit()
        
        assignment = Assignments(people_id=person.id, task_id=task.id, counter=0)
        test_session.add(assignment)
        test_session.commit()
        
        # Try to delete person
        response = client.post(f"/admin/people/{person.id}/delete", follow_redirects=True)
        assert response.status_code == 200
        assert b"Cannot delete" in response.data or b"assignment" in response.data
        
        # Verify person still exists
        person = test_session.query(People).filter_by(id=person.id).first()
        assert person is not None


class TestTasksCRUD:
    """Test CRUD operations for Tasks."""
    
    def test_add_task(self, client, test_session):
        """Test adding a new task."""
        response = client.post("/admin/tasks", data={
            "name": "Vacuum Living Room",
            "description": "Vacuum the entire living room"
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify in database
        task = test_session.query(Tasks).filter_by(name="Vacuum Living Room").first()
        assert task is not None
        assert task.description == "Vacuum the entire living room"
    
    def test_add_task_duplicate_name(self, client, test_session):
        """Test adding a task with duplicate name."""
        task = Tasks(name="Mop Floor", description="Mop the floor")
        test_session.add(task)
        test_session.commit()
        
        response = client.post("/admin/tasks", data={
            "name": "Mop Floor",
            "description": "Different description"
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b"already exists" in response.data
    
    def test_add_task_empty_name(self, client):
        """Test adding a task with empty name."""
        response = client.post("/admin/tasks", data={
            "name": "",
            "description": "Some description"
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b"required" in response.data
    
    def test_add_task_without_description(self, client, test_session):
        """Test adding a task without description."""
        response = client.post("/admin/tasks", data={
            "name": "Simple Task",
            "description": ""
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify in database
        task = test_session.query(Tasks).filter_by(name="Simple Task").first()
        assert task is not None
        assert task.description == ""
    
    def test_list_tasks(self, client, test_session):
        """Test listing all tasks."""
        task1 = Tasks(name="Task 1", description="Description 1")
        task2 = Tasks(name="Task 2", description="Description 2")
        test_session.add_all([task1, task2])
        test_session.commit()
        
        response = client.get("/admin/tasks")
        assert response.status_code == 200
        assert b"Task 1" in response.data
        assert b"Task 2" in response.data
    
    def test_view_task(self, client, test_session):
        """Test viewing a task's details."""
        task = Tasks(name="View Test Task", description="Test description")
        test_session.add(task)
        test_session.commit()
        
        response = client.get(f"/admin/tasks/{task.id}")
        assert response.status_code == 200
        assert b"View Test Task" in response.data
        assert b"Test description" in response.data
    
    def test_update_task(self, client, test_session):
        """Test updating a task."""
        task = Tasks(name="Old Task Name", description="Old description")
        test_session.add(task)
        test_session.commit()
        
        response = client.post(f"/admin/tasks/{task.id}/update", data={
            "name": "New Task Name",
            "description": "New description"
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify update
        test_session.refresh(task)
        assert task.name == "New Task Name"
        assert task.description == "New description"
    
    def test_delete_task_without_assignments(self, client, test_session):
        """Test deleting a task without assignments."""
        task = Tasks(name="Delete Me", description="To be deleted")
        test_session.add(task)
        test_session.commit()
        task_id = task.id
        
        response = client.post(f"/admin/tasks/{task_id}/delete", follow_redirects=True)
        assert response.status_code == 200
        
        # Verify deletion
        task = test_session.query(Tasks).filter_by(id=task_id).first()
        assert task is None
    
    def test_delete_task_with_assignments(self, client, test_session):
        """Test deleting a task with assignments (should fail)."""
        person = People(name="George", email="george@example.com")
        task = Tasks(name="Important Task", description="Can't delete")
        test_session.add_all([person, task])
        test_session.commit()
        
        assignment = Assignments(people_id=person.id, task_id=task.id, counter=0)
        test_session.add(assignment)
        test_session.commit()
        
        # Try to delete task
        response = client.post(f"/admin/tasks/{task.id}/delete", follow_redirects=True)
        assert response.status_code == 200
        assert b"Cannot delete" in response.data or b"assignment" in response.data
        
        # Verify task still exists
        task = test_session.query(Tasks).filter_by(id=task.id).first()
        assert task is not None


class TestAssignmentsCRUD:
    """Test CRUD operations for Assignments."""
    
    def test_create_assignment(self, client, test_session):
        """Test creating a new assignment."""
        person = People(name="Helen", email="helen@example.com")
        task = Tasks(name="Water Plants", description="Water all plants")
        test_session.add_all([person, task])
        test_session.commit()
        
        response = client.post("/admin/assignments", data={
            "person_id": str(person.id),
            "task_id": str(task.id)
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify in database
        assignment = test_session.query(Assignments).filter_by(
            people_id=person.id, task_id=task.id
        ).first()
        assert assignment is not None
        assert assignment.counter == 0
    
    def test_create_assignment_with_existing_assignees(self, client, test_session):
        """Test creating assignment when task already has assignees."""
        person1 = People(name="Ian", email="ian@example.com")
        person2 = People(name="Jack", email="jack@example.com")
        task = Tasks(name="Feed Cat", description="Feed the cat")
        test_session.add_all([person1, person2, task])
        test_session.commit()
        
        # Create first assignment with counter = 5
        assignment1 = Assignments(people_id=person1.id, task_id=task.id, counter=5)
        test_session.add(assignment1)
        test_session.commit()
        
        # Create second assignment - should get median counter
        response = client.post("/admin/assignments", data={
            "person_id": str(person2.id),
            "task_id": str(task.id)
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify counter is set to median
        assignment2 = test_session.query(Assignments).filter_by(
            people_id=person2.id, task_id=task.id
        ).first()
        assert assignment2 is not None
        assert assignment2.counter == 5  # Median of [5]
    
    def test_create_duplicate_assignment(self, client, test_session):
        """Test creating a duplicate assignment."""
        person = People(name="Kate", email="kate@example.com")
        task = Tasks(name="Take Trash", description="Take out trash")
        test_session.add_all([person, task])
        test_session.commit()
        
        assignment = Assignments(people_id=person.id, task_id=task.id, counter=0)
        test_session.add(assignment)
        test_session.commit()
        
        # Try to create duplicate
        response = client.post("/admin/assignments", data={
            "person_id": str(person.id),
            "task_id": str(task.id)
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b"already assigned" in response.data
    
    def test_create_assignment_invalid_person(self, client, test_session):
        """Test creating assignment with invalid person ID."""
        task = Tasks(name="Some Task", description="Description")
        test_session.add(task)
        test_session.commit()
        
        response = client.post("/admin/assignments", data={
            "person_id": "9999",
            "task_id": str(task.id)
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b"not found" in response.data
    
    def test_create_assignment_invalid_task(self, client, test_session):
        """Test creating assignment with invalid task ID."""
        person = People(name="Leo", email="leo@example.com")
        test_session.add(person)
        test_session.commit()
        
        response = client.post("/admin/assignments", data={
            "person_id": str(person.id),
            "task_id": "9999"
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b"not found" in response.data
    
    def test_list_assignments(self, client, test_session):
        """Test listing all assignments."""
        person = People(name="Mary", email="mary@example.com")
        task = Tasks(name="Clean Bathroom", description="Clean bathroom")
        test_session.add_all([person, task])
        test_session.commit()
        
        assignment = Assignments(people_id=person.id, task_id=task.id, counter=3)
        test_session.add(assignment)
        test_session.commit()
        
        response = client.get("/admin/assignments")
        assert response.status_code == 200
        assert b"Mary" in response.data
        assert b"Clean Bathroom" in response.data
    
    def test_view_assignment(self, client, test_session):
        """Test viewing an assignment's details."""
        person = People(name="Nancy", email="nancy@example.com")
        task = Tasks(name="Wash Dishes", description="Wash all dishes")
        test_session.add_all([person, task])
        test_session.commit()
        
        assignment = Assignments(people_id=person.id, task_id=task.id, counter=7)
        test_session.add(assignment)
        test_session.commit()
        
        response = client.get(f"/admin/assignments/{task.id}/{person.id}")
        assert response.status_code == 200
        assert b"Nancy" in response.data
        assert b"Wash Dishes" in response.data
        assert b"7" in response.data
    
    def test_delete_assignment(self, client, test_session):
        """Test deleting an assignment."""
        person = People(name="Oscar", email="oscar@example.com")
        task = Tasks(name="Fold Laundry", description="Fold clean laundry")
        test_session.add_all([person, task])
        test_session.commit()
        
        assignment = Assignments(people_id=person.id, task_id=task.id, counter=2)
        test_session.add(assignment)
        test_session.commit()
        
        response = client.post(f"/admin/assignments/{task.id}/{person.id}/delete", follow_redirects=True)
        assert response.status_code == 200
        
        # Verify deletion
        assignment = test_session.query(Assignments).filter_by(
            people_id=person.id, task_id=task.id
        ).first()
        assert assignment is None
    
    def test_delete_assignment_allows_person_deletion(self, client, test_session):
        """Test that deleting assignment allows person to be deleted."""
        person = People(name="Paul", email="paul@example.com")
        task = Tasks(name="Some Chore", description="Do something")
        test_session.add_all([person, task])
        test_session.commit()
        
        assignment = Assignments(people_id=person.id, task_id=task.id, counter=0)
        test_session.add(assignment)
        test_session.commit()
        
        # Delete assignment
        response = client.post(f"/admin/assignments/{task.id}/{person.id}/delete", follow_redirects=True)
        assert response.status_code == 200
        
        # Now delete person should work
        response = client.post(f"/admin/people/{person.id}/delete", follow_redirects=True)
        assert response.status_code == 200
        
        # Verify person is deleted
        person = test_session.query(People).filter_by(id=person.id).first()
        assert person is None


class TestAdminDashboard:
    """Test admin dashboard."""
    
    def test_admin_index(self, client, test_session):
        """Test admin dashboard displays correct counts."""
        person = People(name="Quinn", email="quinn@example.com")
        task = Tasks(name="Task A", description="Description")
        test_session.add_all([person, task])
        test_session.commit()
        
        assignment = Assignments(people_id=person.id, task_id=task.id, counter=0)
        test_session.add(assignment)
        test_session.commit()
        
        response = client.get("/admin/")
        assert response.status_code == 200
        assert b"1" in response.data  # Should show counts
