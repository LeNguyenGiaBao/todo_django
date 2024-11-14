from apps.todos.models import Todo
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken


class TodoAPITestCase(APITestCase):

    def setUp(self):
        """Set up initial test data"""
        self.user = User.objects.create_user(username="user1", password="password")
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)

        self.todo = Todo.objects.create(
            title="Sample Task",
            description="This is a test task",
            completed=False,
            user=self.user,
            created_by=self.user,
        )

    def authenticate(self):
        """Helper function to authenticate and set the JWT token in the header"""
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)

    def test_create_todo_authenticated(self):
        """Test creating a new todo item"""
        data = {
            "title": "New Task",
            "description": "This is a new task",
        }
        self.authenticate()
        response = self.client.post("/api/todos/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "New Task")

    def test_list_todos_authenticated(self):
        """Test listing all to-do items for an authenticated user"""
        self.authenticate()
        response = self.client.get("/api/todos/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("id", response.data[0])

    def test_retrieve_single_todo_authenticated(self):
        """Test retrieving a single todo item"""
        self.authenticate()
        response = self.client.get(f"/api/todos/{self.todo.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.todo.id))

    def test_update_todo_authenticated(self):
        """Test updating a todo item"""
        data = {
            "title": "Updated Task",
            "description": "This task has been updated.",
            "completed": True,
        }
        self.authenticate()
        response = self.client.put(f"/api/todos/{self.todo.id}/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated Task")
        self.assertEqual(response.data["completed"], True)

    def test_delete_todo_authenticated(self):
        """Test deleting a todo item (soft delete)"""
        self.authenticate()
        response = self.client.delete(f"/api/todos/{self.todo.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Verify that the task is soft deleted
        self.todo.refresh_from_db()
        self.assertTrue(self.todo.is_deleted)

    def test_mark_todo_done_authenticated(self):
        """Test marking a todo item as completed"""
        self.authenticate()
        data = {"completed": True}
        response = self.client.patch(f"/api/todos/{self.todo.id}/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["completed"], True)

    def test_access_denied_for_unauthenticated(self):
        """Test that unauthenticated users cannot access the API"""
        self.client.logout()  # Logout the user
        response = self.client.get("/api/todos/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_todo_unauthenticated(self):
        """Test creating a new todo item without authentication"""
        data = {
            "title": "New Task",
            "description": "This is a new task",
        }
        self.client.logout()  # Logout to simulate unauthenticated user
        response = self.client.post("/api/todos/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_todos_unauthenticated(self):
        """Test listing all todos for an unauthenticated user"""
        self.client.logout()
        response = self.client.get("/api/todos/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_single_todo_unauthenticated(self):
        """Test retrieving a single todo item without authentication"""
        self.client.logout()
        response = self.client.get(f"/api/todos/{self.todo.id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_todo_unauthenticated(self):
        """Test updating a todo item without authentication"""
        data = {
            "title": "Updated Task",
            "description": "This task has been updated.",
            "completed": True,
        }
        self.client.logout()
        response = self.client.put(f"/api/todos/{self.todo.id}/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_todo_unauthenticated(self):
        """Test deleting a todo item without authentication"""
        self.client.logout()
        response = self.client.delete(f"/api/todos/{self.todo.id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
