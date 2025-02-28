import io
import requests
import tornado.web
import tornado.ioloop
import json
from tornado.httpclient import AsyncHTTPClient
import paramiko
from handlers.v1.base import BaseHandler
from controllers.github import GitHubController

class ConnectionTestHandler(BaseHandler):
    def _get_controller_class(self):
        return GitHubController

    async def test_docker_connection(self, username, password, docker_host="https://hub.docker.com/v2"):
        """
        Test Docker Hub connection using username and password (or Personal Access Token).

        Args:
            username (str): Docker Hub username.
            password (str): Docker Hub password or Personal Access Token.
            docker_host (str): Docker Hub API endpoint.

        Returns:
            dict: Connection status and authentication details.
        """
        try:
            print(f"Testing Docker connection for user: {username} at {docker_host}")

            # Docker Hub authentication endpoint
            url = f"{docker_host}/users/login/"

            # JSON payload for authentication
            auth_data = json.dumps({"username": username, "password": password})

            # Send POST request to Docker Hub API
            response = requests.post(url, data=auth_data, headers={"Content-Type": "application/json"})
            # Check response status
            if response.status_code == 200:
                token = response.json().get("token")
                return {"status": "success", "message": "Docker Hub authentication successful", "token": token}
            else:
                return {
                    "status": "failed",
                    "message": f"Docker Hub authentication failed with status code: {response.status_code}",
                    "details": response.json() if response.content else None
                }

        except requests.RequestException as e:
            return {"status": "error", "message": f"Error testing Docker connection: {str(e)}"}

    async def test_aws_ssh_connection(self, ssh_token, ip_address, username="ec2-user"):
        """
        Test AWS SSH connection using key-based authentication.

        Args:
            ssh_token (str): SSH private key as a string.
            ip_address (str): AWS instance IP address.
            username (str): SSH username (default: ec2-user).

        Returns:
            dict: Connection status and details.
        """
        try:
            print(f"Testing SSH connection to {username}@{ip_address}")

            # Convert SSH token (private key string) into an in-memory file
            private_key_file = io.StringIO(ssh_token)

            # Load the private key using paramiko
            private_key = paramiko.RSAKey.from_private_key(private_key_file)

            # Initialize SSH client
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Connect to AWS instance
            ssh_client.connect(ip_address, username=username, pkey=private_key, timeout=10)

            # Close connection after successful authentication
            ssh_client.close()

            return {"status": "success", "message": "AWS SSH connection successful"}

        except paramiko.AuthenticationException:
            return {"status": "failed", "message": "Authentication failed: Invalid SSH key or username."}
        except paramiko.SSHException as e:
            return {"status": "failed", "message": f"SSH connection error: {str(e)}"}
        except Exception as e:
            return {"status": "error", "message": f"Error testing AWS SSH connection: {str(e)}"}

    async def post(self,project_id):
        try:
            # Parse request body
            data = json.loads(self.request.body)
            service = data.get("service", "").lower()

            if service == "docker":
                username = data.get("username")
                password = data.get("password")

                if not username or not password:
                    self.set_status(400)
                    self.write({"error": "Username and password required for DockerHub"})
                    return

                result = await self.test_docker_connection(username, password)
                self.write(result)

            elif service == "aws":
                ssh_key = data.get("ssh_key")
                ip_address = data.get("ip_address")
                username = data.get("username", "ubuntu")

                if not ssh_key or not ip_address:
                    self.set_status(400)
                    self.write({"error": "SSH key path and IP address required for AWS Ec2"})
                    return

                result = await self.test_aws_ssh_connection(ssh_key, ip_address, username)
                self.write(result)

            elif service == "github":
                username = data.get("username")
                token = data.get("token")
                if not username or not token:
                    self.set_status(400)
                    self.write({"error": "Username and Token required for Github"})
                    return

                result = self.controller.test_github_credentials(username,token)

                self.write(result)

        except json.JSONDecodeError:
            self.set_status(400)
            self.write({"error": "Invalid JSON body"})
        except Exception as e:
            self.set_status(500)
            self.write({"error": f"Server error: {str(e)}"})