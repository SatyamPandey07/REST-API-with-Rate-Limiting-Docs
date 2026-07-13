import json
import os

def main():
    collection = {
        "info": {
            "name": "TaskFlow API",
            "description": "Postman collection for TaskFlow API - A versioned, rate-limited REST API.",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": [
            {
                "name": "Auth",
                "item": [
                    {
                        "name": "Register User",
                        "request": {
                            "method": "POST",
                            "header": [
                                {
                                    "key": "Content-Type",
                                    "value": "application/json",
                                    "type": "text"
                                }
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps({
                                    "email": "user@example.com",
                                    "password": "securePassword123"
                                }, indent=2)
                            },
                            "url": {
                                "raw": "{{baseUrl}}/auth/register",
                                "host": ["{{baseUrl}}"],
                                "path": ["auth", "register"]
                            },
                            "description": "Registers a new user account. Pass email and password in request body."
                        },
                        "response": []
                    },
                    {
                        "name": "Login User",
                        "request": {
                            "method": "POST",
                            "header": [
                                {
                                    "key": "Content-Type",
                                    "value": "application/x-www-form-urlencoded",
                                    "type": "text"
                                }
                            ],
                            "body": {
                                "mode": "urlencoded",
                                "urlencoded": [
                                    {
                                        "key": "username",
                                        "value": "user@example.com",
                                        "type": "text"
                                    },
                                    {
                                        "key": "password",
                                        "value": "securePassword123",
                                        "type": "text"
                                    }
                                ]
                            },
                            "url": {
                                "raw": "{{baseUrl}}/auth/login",
                                "host": ["{{baseUrl}}"],
                                "path": ["auth", "login"]
                            },
                            "description": "Authenticates user credentials and returns a JWT access token."
                        },
                        "response": []
                    }
                ]
            },
            {
                "name": "Health",
                "item": [
                    {
                        "name": "Uptime Health Check",
                        "request": {
                            "method": "GET",
                            "header": [],
                            "url": {
                                "raw": "{{baseUrl}}/health",
                                "host": ["{{baseUrl}}"],
                                "path": ["health"]
                            },
                            "description": "Unauthenticated endpoint verifying API status and database connectivity."
                        },
                        "response": []
                    }
                ]
            },
            {
                "name": "Projects",
                "item": [
                    {
                        "name": "Create Project",
                        "request": {
                            "auth": {
                                "type": "bearer",
                                "bearer": [
                                    {
                                        "key": "token",
                                        "value": "{{access_token}}",
                                        "type": "string"
                                    }
                                ]
                            },
                            "method": "POST",
                            "header": [
                                {
                                    "key": "Content-Type",
                                    "value": "application/json",
                                    "type": "text"
                                }
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps({
                                    "name": "Acme Website Redesign",
                                    "description": "Redesign corporate homepage with modern aesthetics"
                                }, indent=2)
                            },
                            "url": {
                                "raw": "{{baseUrl}}/projects/",
                                "host": ["{{baseUrl}}"],
                                "path": ["projects", ""]
                            },
                            "description": "Creates a new project scoped to the authenticated user."
                        },
                        "response": []
                    },
                    {
                        "name": "Get Projects (Paginated)",
                        "request": {
                            "auth": {
                                "type": "bearer",
                                "bearer": [
                                    {
                                        "key": "token",
                                        "value": "{{access_token}}",
                                        "type": "string"
                                    }
                                ]
                            },
                            "method": "GET",
                            "header": [],
                            "url": {
                                "raw": "{{baseUrl}}/projects/?page=1&page_size=20",
                                "host": ["{{baseUrl}}"],
                                "path": ["projects", ""],
                                "query": [
                                    {"key": "page", "value": "1"},
                                    {"key": "page_size", "value": "20"}
                                ]
                            },
                            "description": "Retrieves a paginated list of projects owned by the authenticated user."
                        },
                        "response": []
                    },
                    {
                        "name": "Get Project by ID",
                        "request": {
                            "auth": {
                                "type": "bearer",
                                "bearer": [
                                    {
                                        "key": "token",
                                        "value": "{{access_token}}",
                                        "type": "string"
                                    }
                                ]
                            },
                            "method": "GET",
                            "header": [],
                            "url": {
                                "raw": "{{baseUrl}}/projects/:id",
                                "host": ["{{baseUrl}}"],
                                "path": ["projects", ":id"],
                                "variable": [
                                    {"key": "id", "value": "12", "description": "Database ID of target project"}
                                ]
                            },
                            "description": "Retrieves details of a project and its nested tasks."
                        },
                        "response": []
                    },
                    {
                        "name": "Update Project",
                        "request": {
                            "auth": {
                                "type": "bearer",
                                "bearer": [
                                    {
                                        "key": "token",
                                        "value": "{{access_token}}",
                                        "type": "string"
                                    }
                                ]
                            },
                            "method": "PUT",
                            "header": [
                                {
                                    "key": "Content-Type",
                                    "value": "application/json",
                                    "type": "text"
                                }
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps({
                                    "name": "Acme Website Redesign v2",
                                    "description": "Updated scope including mobile layout"
                                }, indent=2)
                            },
                            "url": {
                                "raw": "{{baseUrl}}/projects/:id",
                                "host": ["{{baseUrl}}"],
                                "path": ["projects", ":id"],
                                "variable": [
                                    {"key": "id", "value": "12"}
                                ]
                            },
                            "description": "Updates an existing project's name and description."
                        },
                        "response": []
                    },
                    {
                        "name": "Delete Project",
                        "request": {
                            "auth": {
                                "type": "bearer",
                                "bearer": [
                                    {
                                        "key": "token",
                                        "value": "{{access_token}}",
                                        "type": "string"
                                    }
                                ]
                            },
                            "method": "DELETE",
                            "header": [],
                            "url": {
                                "raw": "{{baseUrl}}/projects/:id",
                                "host": ["{{baseUrl}}"],
                                "path": ["projects", ":id"],
                                "variable": [
                                    {"key": "id", "value": "12"}
                                ]
                            },
                            "description": "Deletes the project and all cascaded tasks."
                        },
                        "response": []
                    }
                ]
            },
            {
                "name": "Tasks",
                "item": [
                    {
                        "name": "Create Task",
                        "request": {
                            "auth": {
                                "type": "bearer",
                                "bearer": [
                                    {
                                        "key": "token",
                                        "value": "{{access_token}}",
                                        "type": "string"
                                    }
                                ]
                            },
                            "method": "POST",
                            "header": [
                                {
                                    "key": "Content-Type",
                                    "value": "application/json",
                                    "type": "text"
                                }
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps({
                                    "title": "Implement JWT Auth",
                                    "description": "Complete endpoint decoration",
                                    "status": "Todo",
                                    "project_id": 12
                                }, indent=2)
                            },
                            "url": {
                                "raw": "{{baseUrl}}/tasks/",
                                "host": ["{{baseUrl}}"],
                                "path": ["tasks", ""]
                            },
                            "description": "Creates a task under a project owned by the user."
                        },
                        "response": []
                    },
                    {
                        "name": "Get Tasks (Filtered & Paginated)",
                        "request": {
                            "auth": {
                                "type": "bearer",
                                "bearer": [
                                    {
                                        "key": "token",
                                        "value": "{{access_token}}",
                                        "type": "string"
                                    }
                                ]
                            },
                            "method": "GET",
                            "header": [],
                            "url": {
                                "raw": "{{baseUrl}}/tasks/?page=1&page_size=20&status=Todo&project_id=12",
                                "host": ["{{baseUrl}}"],
                                "path": ["tasks", ""],
                                "query": [
                                    {"key": "page", "value": "1"},
                                    {"key": "page_size", "value": "20"},
                                    {"key": "status", "value": "Todo"},
                                    {"key": "project_id", "value": "12"}
                                ]
                            },
                            "description": "Retrieves the authenticated user's tasks. Supports status and project filters."
                        },
                        "response": []
                    },
                    {
                        "name": "Get Task by ID",
                        "request": {
                            "auth": {
                                "type": "bearer",
                                "bearer": [
                                    {
                                        "key": "token",
                                        "value": "{{access_token}}",
                                        "type": "string"
                                    }
                                ]
                            },
                            "method": "GET",
                            "header": [],
                            "url": {
                                "raw": "{{baseUrl}}/tasks/:id",
                                "host": ["{{baseUrl}}"],
                                "path": ["tasks", ":id"],
                                "variable": [
                                    {"key": "id", "value": "45"}
                                ]
                            },
                            "description": "Retrieves properties of a single task owned by the user."
                        },
                        "response": []
                    },
                    {
                        "name": "Update Task",
                        "request": {
                            "auth": {
                                "type": "bearer",
                                "bearer": [
                                    {
                                        "key": "token",
                                        "value": "{{access_token}}",
                                        "type": "string"
                                    }
                                ]
                            },
                            "method": "PUT",
                            "header": [
                                {
                                    "key": "Content-Type",
                                    "value": "application/json",
                                    "type": "text"
                                }
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps({
                                    "title": "Refactor JWT Auth",
                                    "status": "InProgress"
                                }, indent=2)
                            },
                            "url": {
                                "raw": "{{baseUrl}}/tasks/:id",
                                "host": ["{{baseUrl}}"],
                                "path": ["tasks", ":id"],
                                "variable": [
                                    {"key": "id", "value": "45"}
                                ]
                            },
                            "description": "Updates an existing task's properties."
                        },
                        "response": []
                    },
                    {
                        "name": "Delete Task",
                        "request": {
                            "auth": {
                                "type": "bearer",
                                "bearer": [
                                    {
                                        "key": "token",
                                        "value": "{{access_token}}",
                                        "type": "string"
                                    }
                                ]
                            },
                            "method": "DELETE",
                            "header": [],
                            "url": {
                                "raw": "{{baseUrl}}/tasks/:id",
                                "host": ["{{baseUrl}}"],
                                "path": ["tasks", ":id"],
                                "variable": [
                                    {"key": "id", "value": "45"}
                                ]
                            },
                            "description": "Deletes the task."
                        },
                        "response": []
                    }
                ]
            }
        ],
        "variable": [
            {
                "key": "baseUrl",
                "value": "http://localhost:8000/api/v1",
                "type": "string"
            },
            {
                "key": "access_token",
                "value": "your_access_token_here",
                "type": "string"
            }
        ]
    }

    # Ensure directories exist
    os.makedirs("docs", exist_ok=True)
    with open("docs/postman_collection.json", "w") as f:
        json.dump(collection, f, indent=2)
    print("Postman collection written successfully to docs/postman_collection.json")

if __name__ == "__main__":
    main()
