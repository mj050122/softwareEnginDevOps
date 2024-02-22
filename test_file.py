import pytest
from app import app, DB_NAME as db
import sqlite3

@pytest.fixture
def client():
    try:
        # Establish connection to the SQLite database
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        # Fetch an existing user from the 'accounts' table
        cursor.execute("SELECT username, password FROM accounts LIMIT 1")
        user = cursor.fetchone()
        if user is None:
            raise Exception("No users found in the database.")
        cursor.close()
        conn.close()
        # Unpack the fetched user data
        username, password = user
        # Create a test client using Flask's test_client method
        with app.test_client() as client:
            yield client, username, password  # Pass the fetched user data to the test function
    except Exception as e:
        pytest.fail(f"Error setting up fixture: {e}")
    #cleaning up after tests
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM accounts WHERE username='new_user'")
    cursor.execute("DELETE FROM blocked_users WHERE username='invalid_username'")
    conn.commit()
    cursor.close()

def test_valid_login(client):
    # Unpack the fetched user data directly from the fixture
    client, username, password = client
    # Send a POST request with valid login credentials
    response = client.post('/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)
    # Check if the login was successful by verifying if the login page is not returned
    assert b'Login' not in response.data

def test_invalid_login(client):
    client, _, _ = client  # We don't need the username and password for an invalid login
    # Send a POST request with invalid login credentials
    response = client.post('/login', data=dict(
        username='invalid_username',
        password='invalid_password'
    ), follow_redirects=True)
    # Check if the login failed by verifying if the login page is returned
    assert b'Login' in response.data

def test_valid_registration(client):
    client, _, _ = client 
    # Send a POST request with valid registration data
    response = client.post('/register', data=dict(
        username='new_user',
        password='new_password',
        email='new_user@example.com'
    ), follow_redirects=True)
    assert b'You have successfully registered!' in response.data

def test_existing_registration(client):
    client, _, _ = client
    response = client.post('/register', data=dict(
        username='jeremyFitzgerald',  # An existing username
        password='new_password',
        email='new_user@example.com'
    ), follow_redirects=True)
    assert b'You have successfully registered!' not in response.data

def test_invalid_email(client):
    client, _, _ = client
    response = client.post('/register', data=dict(
        username='new_user',
        password='new_password',
        email='totallyinvalidemail.no'   
    ), follow_redirects=True)
    assert b'You have successfully registered!' not in response.data
