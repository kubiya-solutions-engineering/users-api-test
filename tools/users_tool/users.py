from kubiya_sdk.tools import Arg
from .base import UserApiTool
from kubiya_sdk.tools.registry import tool_registry

get_all_users = UserApiTool(
    name="get_all_users",
    description="Retrieve all users from the database",
    content="""
import requests
from typing import Dict, List, Any

def get_users() -> Dict[str, Any]:
    try:
        response = requests.get("http://users-api.users-api.svc.cluster.local:80/users")
        response.raise_for_status()
        users = response.json()
        return {
            "status": "success",
            "message": f"Successfully retrieved {len(users)} users",
            "data": users
        }
    except requests.exceptions.RequestException as e:
        error_msg = f"Failed to retrieve users: {str(e)}"
        print(error_msg)
        return {
            "status": "error",
            "message": error_msg,
            "data": None
        }

result = get_users()
print(f"Status: {result['status']}")
print(f"Message: {result['message']}")
if result['data']:
    print("Users:")
    for user in result['data']:
        print(f"- ID: {user.get('id')}, Name: {user.get('name')}, Email: {user.get('email')}")
    """,
    args=[],
)

get_user = UserApiTool(
    name="get_user",
    description="Retrieve a specific user by ID or email",
    content="""
import requests

identifier = args[0]  # Can be either ID or email

def get_user_details(identifier):
    try:
        # If identifier contains @, treat as email
        if '@' in identifier:
            response = requests.get(
                "http://users-api.users-api.svc.cluster.local:80/users",
                params={"email": identifier}
            )
            response.raise_for_status()
            users = response.json()
            
            if not users:
                return {
                    "status": "error",
                    "message": f"No user found with email {identifier}",
                    "data": None
                }
            return {
                "status": "success",
                "message": f"Successfully retrieved user with email {identifier}",
                "data": users[0]
            }
        else:
            # Treat as ID
            response = requests.get(
                f"http://users-api.users-api.svc.cluster.local:80/users/{identifier}"
            )
            response.raise_for_status()
            return {
                "status": "success",
                "message": f"Successfully retrieved user with ID {identifier}",
                "data": response.json()
            }
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "message": f"Failed to retrieve user {identifier}: {str(e)}",
            "data": None
        }

result = get_user_details(identifier)
print(f"Status: {result['status']}")
print(f"Message: {result['message']}")
if result['data']:
    user = result['data']
    print(f"User Details:")
    print(f"- ID: {user.get('id')}")
    print(f"- Name: {user.get('name')}")
    print(f"- Email: {user.get('email')}")
    """,
    args=[
        Arg(name="identifier", type="str", description="ID or email of the user to retrieve", required=True),
    ],
)

create_user = UserApiTool(
    name="create_user",
    description="Create a new user",
    content="""
import requests

# Get name and email from args list
name = args[0]
email = args[1]

def create_new_user(name, email):
    try:
        response = requests.post(
            "http://users-api.users-api.svc.cluster.local:80/users",
            json={"name": name, "email": email}
        )
        response.raise_for_status()
        result = {
            "status": "success",
            "message": f"Successfully created new user: {name}",
            "data": response.json()
        }
    except requests.exceptions.RequestException as e:
        result = {
            "status": "error",
            "message": f"Failed to create user: {str(e)}",
            "data": None
        }
    return result

result = create_new_user(name, email)
print(f"Status: {result['status']}")
print(f"Message: {result['message']}")
if result['data']:
    user = result['data']
    print(f"Created User Details:")
    print(f"- ID: {user.get('id')}")
    print(f"- Name: {user.get('name')}")
    print(f"- Email: {user.get('email')}")
    """,
    args=[
        Arg(name="name", type="str", description="Name of the user", required=True),
        Arg(name="email", type="str", description="Email of the user", required=True),
    ],
)

update_user = UserApiTool(
    name="update_user",
    description="Update an existing user by ID or email",
    content="""
import requests

# Get arguments from args list
identifier = args[0]  # Can be either ID or email
new_name = args[1]
new_email = args[2]

def get_user_by_email(email):
    try:
        response = requests.get(
            "http://users-api.users-api.svc.cluster.local:80/users",
            params={"email": email}
        )
        response.raise_for_status()
        users = response.json()
        return users[0] if users else None
    except requests.exceptions.RequestException:
        return None

def update_user_details(identifier, new_name=None, new_email=None):
    try:
        # Check if identifier is an email
        user_id = identifier
        if '@' in identifier:
            user = get_user_by_email(identifier)
            if not user:
                return {
                    "status": "error",
                    "message": f"No user found with email {identifier}",
                    "data": None
                }
            user_id = user['id']
            
        params = {}
        if new_name:
            params["name"] = new_name
        if new_email:
            params["email"] = new_email
            
        response = requests.put(
            f"http://users-api.users-api.svc.cluster.local:80/users/{user_id}",
            params=params
        )
        response.raise_for_status()
        user = response.json()

        updated_fields = []
        if new_name:
            updated_fields.append("name")
        if new_email:
            updated_fields.append("email")

        result = {
            "status": "success",
            "message": f"Successfully updated user {identifier} ({', '.join(updated_fields)})",
            "data": user
        }
    except requests.exceptions.RequestException as e:
        result = {
            "status": "error",
            "message": f"Failed to update user {identifier}: {str(e)}",
            "data": None
        }

    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    if result['data']:
        user = result['data']
        print(f"Updated User Details:")
        print(f"- ID: {user.get('id')}")
        print(f"- Name: {user.get('name')}")
        print(f"- Email: {user.get('email')}")

update_user_details(identifier, new_name, new_email)
    """,
    args=[
        Arg(name="identifier", type="str", description="ID or email of the user to update", required=True),
        Arg(name="new_name", type="str", description="New name for the user", required=False),
        Arg(name="new_email", type="str", description="New email for the user", required=False),
    ],
)

delete_user = UserApiTool(
    name="delete_user",
    description="Delete a user by ID or email",
    content="""
import requests

# Get identifier from args list
identifier = args[0]  # Can be either ID or email

def get_user_by_email(email):
    try:
        response = requests.get(
            "http://users-api.users-api.svc.cluster.local:80/users",
            params={"email": email}
        )
        response.raise_for_status()
        users = response.json()
        return users[0] if users else None
    except requests.exceptions.RequestException:
        return None

def delete_user_by_identifier(identifier):
    try:
        # Check if identifier is an email
        user_id = identifier
        if '@' in identifier:
            user = get_user_by_email(identifier)
            if not user:
                return {
                    "status": "error",
                    "message": f"No user found with email {identifier}",
                    "data": None
                }
            user_id = user['id']

        response = requests.delete(f"http://users-api.users-api.svc.cluster.local:80/users/{user_id}")
        response.raise_for_status()
        result = {
            "status": "success",
            "message": f"Successfully deleted user {identifier}",
            "data": response.json()
        }
    except requests.exceptions.RequestException as e:
        result = {
            "status": "error",
            "message": f"Failed to delete user {identifier}: {str(e)}",
            "data": None
        }

    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    if result['data']:
        print("Deletion confirmed")

delete_user_by_identifier(identifier)
    """,
    args=[
        Arg(name="identifier", type="str", description="ID or email of the user to delete", required=True),
    ],
)

# Register the tools
tool_registry.register("users", get_all_users)
tool_registry.register("users", get_user)
tool_registry.register("users", create_user)
tool_registry.register("users", update_user)
tool_registry.register("users", delete_user)