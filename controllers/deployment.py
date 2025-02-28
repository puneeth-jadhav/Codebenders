import os
import re
import json
import docker
import socket
from bson import ObjectId
from typing import Any, Dict
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from controllers.base import BaseController
from database.models import DeployCredentials

# Import components from the DevOps agent
from typing_extensions import TypedDict
from utils.deploy_utils import broadcast_log
from langgraph.graph import StateGraph, START, END
from database.models import DeployProjectMetadata 
from http import HTTPStatus

load_dotenv(
    "/home/puneeth/Work/New_codebenders/rest_api_server/.env"
)

BASE_PATH = "/home/puneeth/Work/New_codebenders"
FRONTEND_GIT_CONTEXT = "./rest_api_server/2/frontend/flight-booking-app"
BACKEND_GIT_CONTEXT = "./rest_api_server/2/backend"
FRONTEND_BASE_PATH = "/home/puneeth/Work/New_codebenders/rest_api_server/2/frontend"
BACKEND_BASE_PATH = "/home/puneeth/Work/New_codebenders/rest_api_server/2"

# Enhanced OpenAI LLM configuration
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.2,
    openai_api_key=os.getenv("OPENAI_API_KEY"),
)

class DeploymentProjectController(BaseController):
    
    def get_metadata(self, project_id):
        """Retrieve deployment metadata for a specific project"""
        print("Invoked get metadta controller ")
        project_metadata = DeployProjectMetadata(project_id=project_id).get_metadata()

        if not project_metadata:
            return {"error": "No metadata found"}
        return project_metadata

    def update_metadata(self,project_id,metadata,section=None):
        """Update a specific metadata section (GitHub, Docker, AWS)"""
        project_metadata = DeployProjectMetadata(project_id)
        if section:
            if section == "github":
                success = project_metadata.update_github_metadata(metadata)
            elif section == "docker":
                success = project_metadata.update_docker_metadata(metadata)
            elif section == "aws":
                success = project_metadata.update_aws_metadata(metadata)
        else: #updating complete project metadata
            success = project_metadata.save_metadata(metadata)

        return {"message": "Update successful"} if success else {"error": "Update failed"}
    def save_metadata(self, project_id, metadata):
        """Save deployment metadata for a project"""
        project_metadata = DeployProjectMetadata(project_id=project_id)
        mongo_id = project_metadata.save_metadata(metadata)
        if not mongo_id:
            return {"success": False,"error": "Failed to save metadata"}, HTTPStatus.BAD_REQUEST
        else:
            return {"success": True ,"message": "Metadata saved"}
    
    def delete_metadata(self,project_id):
        """Delete deployment metadata of a project"""
        project_metadata = DeployProjectMetadata(project_id=project_id)
        result = project_metadata.delete_metadata()
        if result:
            return {"success": True, "message": "Metadata deleted successfully"}
        else:
            print(f"Deletion failed for project_id: {project_id}")  # Debug log
            return {"success": False, "error": "Failed to delete metadata"}
        
class DeployCredentialsController(BaseController):
    """Controller for managing deployment credentials."""

    def __init__(self):
        super().__init__()

    def create_credentials(
        self, project_id: int, project_name: str, credentials: dict
    ) -> bool:
        """Create and store deployment credentials using project_id."""
        deploy_cred = DeployCredentials(
            project_id=project_id, project_name=project_name
        )
        return deploy_cred.save_credentials(credentials)

    def get_credentials(self, project_id: int, cred_type: str = None) -> dict:
        """Retrieve credentials using project_id."""
        return DeployCredentials(
            project_id=project_id, project_name=""
        ).get_credentials(cred_type)

    def update_credentials(
        self, project_id: int, cred_type: str, cred_data: dict
    ) -> bool:
        """Update specific credential type using project_id."""
        return DeployCredentials(
            project_id=project_id, project_name=""
        ).update_specific_credentials(cred_type, cred_data)

    def delete_credentials(self, project_id: int) -> bool:
        """Delete credentials using project_id."""
        return DeployCredentials(
            project_id=project_id, project_name=""
        ).delete_credentials()


# Enhanced State to support conversational flow
class DeploymentState(TypedDict):
    containers: dict


class DevOpsAgentController(BaseController):

    def scan_projects(self) -> dict:
        """Scans the directory for projects and classifies them as frontend or backend."""
        detected_projects = {}
        excluded_dirs = {".venv", "node_modules", "__pycache__", ".git"}
        frontend_folder_name = "flight-booking-app"
        backend_folder_name = "backend"
        folders_to_scan = [frontend_folder_name, backend_folder_name]
        # Construct absolute paths for scanning
        frontend_path = os.path.join(FRONTEND_BASE_PATH, frontend_folder_name)
        backend_path = os.path.join(BACKEND_BASE_PATH, backend_folder_name)
        folders_to_scan = [frontend_path, backend_path]
        for project in folders_to_scan:
            if os.path.isdir(project) and project not in excluded_dirs:
                files = [
                    os.path.join(dp, f)
                    for dp, _, filenames in os.walk(project)
                    for f in filenames
                    if not any(excl in dp for excl in excluded_dirs)
                ]

                # Project type detection
                if any(fname.endswith(("package.json")) for fname in files):
                    detected_projects["frontend"] = {"path": project, "files": files}
                    print(f"Detected frontend project: {project}")
                elif any(
                    fname.endswith(("requirements.txt", ".py")) for fname in files
                ):
                    detected_projects["backend"] = {"path": project, "files": files}
                    print(f"Detected backend project: {project}")

        if not detected_projects:
            print("⚠️ No valid project folders specified or no files found.")
            return {"error": "No valid project folders specified or no files found."}

        # print(f"✅ Detected Projects: {detected_projects}")
        return {"projects": detected_projects}
        
    def is_vite_project(self,package_json_path):

        if not os.path.exists(package_json_path):
            print(f"⚠️ package.json not found at {package_json_path}")
            return False

        with open(package_json_path, "r") as f:
            package_data = json.load(f)

        scripts = package_data.get("scripts", {})
        dependencies = package_data.get("dependencies", {})
        dev_dependencies = package_data.get("devDependencies", {})

        if "vite" in dev_dependencies or "vite" in scripts.values():
            return "vite"
        elif "react" in dependencies:
            return "react"
        else:
            return "unknown"
        
    def generate_dockerfile_with_openai(self, project_info: str) -> str:
        """
        Uses OpenAI to generate a Dockerfile for a project.
        project_info: JSON string with keys 'project_path', 'project_type', and optional 'port'
        """
        # Parse project info
        info = json.loads(project_info)
        project_path = info["project_path"]
        project_type = info["project_type"]
        port = info.get("port", 8000 if project_type == "backend" else 3000)
        server_file = "main.py" if project_type == "backend" else None
        broadcast_log(f"Generating Dockerfile for {project_path}")
        if project_type == "frontend":
            package_json_path = os.path.join(project_path, "package.json")
            frontend_type = self.is_vite_project(package_json_path)
            if frontend_type == "vite":
                prompt = f"""
                Your task is to generate a **valid Dockerfile** for a Vite-based frontend project named '{project_path}'.
                
                **Rules:**
                - The response must contain **only the Dockerfile content** (no explanations, no markdown formatting).
                - Use **Node.js 18 Alpine** as the base image.
                - Ensure the app starts using `npm run dev -- --host`.
                - Expose port **5173** (default Vite port).
                - The response must start with `FROM node:18-alpine` and contain only valid Docker instructions.

                **Example Output (Do NOT return in Markdown format, only the Dockerfile content):**
                    FROM node:18-alpine
                    WORKDIR /app
                    COPY package*.json ./
                    RUN npm install
                    COPY . .
                    EXPOSE 5173
                    ENV NODE_ENV=production
                    CMD ["npm", "run", "dev", "--", "--host"]
                """
            else:  # Default to React
                prompt = f"""
                Your task is to generate a **valid Dockerfile** for a React-based frontend project named '{project_path}'.
                
                **Rules:**
                - The response must contain **only the Dockerfile content** (no explanations, no markdown formatting).
                - Use **Node.js 18 Alpine** as the base image.
                - Ensure the app starts with `npm start`.
                - Expose port **3000** (default React app port).
                - The response must start with `FROM node:18-alpine` and contain only valid Docker instructions.

                **Example Output (Do NOT return in Markdown format, only the Dockerfile content):**
                    FROM node:18-alpine
                    WORKDIR /app
                    COPY package*.json ./
                    RUN npm install
                    COPY . .
                    EXPOSE 3000
                    CMD ["npm", "start"]
                """
        else:  # Backend
            server_file_path = os.path.join(project_path, server_file)
            file_content = self.read_file_content(server_file_path)

            if not file_content:
                print(
                    f"⚠️ Server file {server_file} not found. Using default entry point."
                )
                entry_point = "main"
                port = 8000
            else:
                entry_point = server_file.replace(".py", "")
                if "run(" in file_content:
                    port_match = re.search(r"run\(.*port\s*=\s*(\d+)", file_content)
                    if port_match:
                        port = int(port_match.group(1))

            prompt = f"""
            Your task is to generate a **valid Dockerfile** for a backend project named '{project_path}'.
            
            **Project Details:**
            - The backend application starts using the file `{server_file}`
            - Runs on port: {port}
            - Below is the full content of `{server_file}`:

            ```
            {file_content}
            ```

            **Rules:**
            - The response must contain **only the Dockerfile content** (no explanations, no markdown formatting).
            - Use **Python 3.10** as the base image.
            - Assume a valid `requirements.txt` file is already provided.
            - Ensure the application starts using `uvicorn {entry_point}:app --host 0.0.0.0 --port {port}` if FastAPI is detected.
            - If Flask is detected, start with `flask run --host=0.0.0.0 --port={port}`.
            - The response must start with `FROM python:3.10` and contain only valid Docker instructions.

            **Example Output (Do NOT return in Markdown format, only the Dockerfile content):**
            FROM python:3.10
            WORKDIR /app
            COPY requirements.txt .
            RUN pip install --no-cache-dir -r requirements.txt
            COPY . .
            EXPOSE {port}
            CMD ["uvicorn", "{entry_point}:app", "--host", "0.0.0.0", "--port", "{port}"]
            """

        response = llm.invoke(prompt)
        dockerfile_content = response.content.strip()

        # Save the Dockerfile
        dockerfile_path = os.path.join(project_path, "Dockerfile")
        with open(dockerfile_path, "w") as f:
            f.write(dockerfile_content + "\n")
        broadcast_log(f"Generated Dockerfile for {project_path}")
        return dockerfile_content
    
    def build_and_run_container(self, container_config: str) -> dict:
        """
        Builds and runs a Docker container based on provided configuration.
        container_config: JSON string with 'project_path', 'port', 'name' keys
        """
        config = json.loads(container_config)
        project_path = config["project_path"]
        # print("project path",project_path)
        port = config["port"]
        container_name = config["project_path"]
        client = docker.from_env()
        project_path = os.path.abspath(project_path)

        try:
            # Stop and remove any running container with the same name
            existing_containers = client.containers.list(
                all=True, filters={"name": container_name}
            )
            for container in existing_containers:
                broadcast_log(
                    f"\n🛑 Stopping and removing existing container {container_name}..."
                )
                container.stop()
                container.remove()

            # # Build image
            # print(f"🐳 Building Docker image for {project_path}...")
            # image, _ = client.images.build(path=project_path, tag=container_name)

            # print(f"🚀 Starting container '{container_name}' with port mapping {port}...\n")
            # # Run container
            # container = client.containers.run(
            #     image.id,
            #     detach=True,
            #     ports={f"{port}/tcp": port},
            #     name=container_name,
            # )

            return {
                "container_id": "N/A",
                "name": container_name,
                "port": port,
                "status": "Disabled the building and running the DOckerfile",
            }

        except Exception as e:
            return {"error": str(e)}

    def setup_github_actions(self, project_data: dict) -> str:
        """Creates GitHub Actions workflow for building Docker images and deploying to EC2 via Docker Hub."""

        if "project_path" not in project_data:
            raise ValueError("Missing required key 'project_path' in project_data")
        
        project_path = project_data["project_path"]
        project_name = os.path.basename(project_path)
        workflow_dir = os.path.join(BASE_PATH, ".github", "workflows")
        os.makedirs(workflow_dir, exist_ok=True)
        
        is_frontend = os.path.exists(os.path.join(project_path, "package.json"))
        port_mapping = "8000:8000" if not is_frontend else ("5173:5173" if self.is_vite_project(os.path.join(project_path, "package.json")) else "3000:3000")
        # print(project_path)
        # print(os.getcwd())
        context = ""
        if is_frontend:
            context= FRONTEND_GIT_CONTEXT
        else:
            context = BACKEND_GIT_CONTEXT
        # Fixed GitHub Actions Workflow
        workflow_content = f"""name: Build and Deploy {project_name}

on:
  push:
    branches:
      - main

jobs:
  build_and_push:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v2

      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{{{ secrets.DOCKER_HUB_USERNAME }}}}
          password: ${{{{ secrets.DOCKER_HUB_PASSWORD }}}}

      - name: Build and push Docker image
        uses: docker/build-push-action@v4
        with:
          context: {context}
          file: {context}/Dockerfile
          push: true
          tags: ${{{{ secrets.DOCKER_HUB_USERNAME }}}}/{project_name}:${{{{ github.sha }}}}

  deploy:
    needs: build_and_push
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to EC2
        uses: appleboy/ssh-action@master
        with:
          host: ${{{{ secrets.HOST }}}}
          username: ${{{{ secrets.USERNAME }}}}
          key: ${{{{ secrets.SSH_KEY }}}}
          script: |
            # Check if Docker is installed, install if not
            if ! command -v docker &> /dev/null; then
              echo "Docker not found. Installing Docker..."
              sudo apt update
              sudo apt install -y docker.io
              sudo systemctl start docker
              sudo systemctl enable docker
              sudo chmod 666 /var/run/docker.sock
            fi

            # Log in to Docker Hub
            echo "${{{{ secrets.DOCKER_HUB_PASSWORD }}}}" | docker login -u "${{{{ secrets.DOCKER_HUB_USERNAME }}}}" --password-stdin

            # Pull the latest image and run the container
            sudo docker pull ${{ secrets.DOCKER_HUB_USERNAME }}/{project_name}:${{ github.sha }}

            # Stop and remove existing container if running
            if [ "$(sudo docker ps -q -f name={project_name})" ]; then
              sudo docker stop {project_name}
              sudo docker rm {project_name}
            fi

            # Run the new container
            sudo docker run -d --restart always -p {port_mapping} --name {project_name} ${{{{ secrets.DOCKER_HUB_USERNAME }}}}/{project_name}:${{{{ github.sha }}}}
"""

        # Save workflow file
        workflow_filename = f"{project_name}-deploy.yml"
        workflow_path = os.path.join(workflow_dir, workflow_filename)
        with open(workflow_path, "w") as f:
            f.write(workflow_content)

        broadcast_log(f"Successfully Created CI/CD Pipeline for the {project_name}.")
        return workflow_content

    # ---- HELPER FUNCTIONS ----
    def read_file_content(self, file_path):
        """Reads the entire content of a given file and returns it."""
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        else:
            return None

    def is_port_in_use(self, port):
        """Check if a port is already in use."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("localhost", port)) == 0

    # ---- DIRECT DEPLOYMENT FUNCTION ----
    def run_deployment_workflow(self, state):
        """Execute the full deployment workflow."""
        scan_result = self.scan_projects()
        projects = scan_result["projects"]

        # Generate dockerfiles for each project
        for role, project_data in projects.items():
            project_info = {"project_path": project_data["path"], "project_type": role}
            self.generate_dockerfile_with_openai(
                json.dumps(project_info)
            )  # Use .invoke()

        # Setup CI/CD
        cicd_results = {}
        for role, project_data in projects.items():
            cicd_results[role] = self.setup_github_actions(
                {"project_path": project_data["path"]}
            )

        # # Build and run containers
        # container_results = {}
        # for role, project_data in projects.items():
        #     default_port = 3000 if role == "frontend" else 8000
        #     container_config = {
        #         "project_path": project_data["path"],
        #         "port": default_port,
        #         "name": f"{project_data['path']}-{role}",
        #     }
        #     container_results[role] = self.build_and_run_container(json.dumps(container_config))  # Use .invoke()

        return {
            "success": True,
            # "containers": container_results,
        }

    # ---- WORKFLOW CREATION ----
    def create_devops_agent(self):
        """Create the DevOps agent workflow graph."""
        builder = StateGraph(DeploymentState)
        # Add deployment node only
        builder.add_node("deployment_workflow", self.run_deployment_workflow)
        # Direct path from start to deployment and end
        builder.add_edge(START, "deployment_workflow")
        builder.add_edge("deployment_workflow", END)
        return builder.compile()

    # Initialize agent with empty state
    def get_initial_state(self):
        return DeploymentState(
            containers={},
        )