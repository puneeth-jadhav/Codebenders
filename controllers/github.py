import base64
from datetime import datetime
from nacl import encoding, public 
from dotenv import load_dotenv
from controllers.base import BaseController
import os
import json
import requests


load_dotenv("/home/puneeth/Work/New_codebenders/rest_api_server/.env")

# GitHub API Configuration
GITHUB_OWNER = "puneeth-jadhav"
GITHUB_REPO = "Codebenders"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") 
BRANCH_NAME = "main"


class GitHubController(BaseController):
    def test_github_credentials(self, username, token):
        """
        Test if the provided GitHub credentials are valid by making an API call to the user endpoint.
        
        Parameters:
        username (str): GitHub username
        token (str): GitHub personal access token
        
        Returns:
        dict: Result of the test with success status and additional information
        """
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        
        # First, test authentication by accessing user data
        user_url = f"https://api.github.com/users/{username}"
        user_response = requests.get(user_url, headers=headers)
        
        if user_response.status_code != 200:
            return {
                "success": False,
                "message": "Invalid credentials or user not found",
                "status_code": user_response.status_code,
                "details": user_response.json() if user_response.text else "No details available",
                "status": "failed"
            }
        
        # Next, test if the token has sufficient permissions to access repositories
        repos_url = "https://api.github.com/user/repos?per_page=1"
        repos_response = requests.get(repos_url, headers=headers)
        
        # Check rate limits as well (useful information to return)
        rate_limit_url = "https://api.github.com/rate_limit"
        rate_limit_response = requests.get(rate_limit_url, headers=headers)
        rate_limit_data = rate_limit_response.json() if rate_limit_response.status_code == 200 else {}
        
        repo_access = repos_response.status_code == 200
        
        # Get the authenticated user data (may be different from the provided username if using a token)
        auth_user_url = "https://api.github.com/user"
        auth_user_response = requests.get(auth_user_url, headers=headers)
        auth_user_data = auth_user_response.json() if auth_user_response.status_code == 200 else {}
        
        # Construct the result
        user_data = user_response.json()
        result = {
            "success": True,
            "message": "GitHub credentials are valid",
            "user": {
                "login": user_data.get("login"),
                "name": user_data.get("name"),
                "id": user_data.get("id"),
                "avatar_url": user_data.get("avatar_url"),
                "html_url": user_data.get("html_url"),
                "public_repos": user_data.get("public_repos"),
                "authenticated_as": auth_user_data.get("login") if auth_user_response.status_code == 200 else None
            },
            "permissions": {
                "repository_access": repo_access,
                "scopes": auth_user_response.headers.get("X-OAuth-Scopes", "").split(", ") if auth_user_response.status_code == 200 else []
            },
            "rate_limit": rate_limit_data.get("rate", {})
        }
        
        return result

    def fetch_actions(self):
        url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/actions/runs"
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            self.set_status(500)
            self.write({"error": "Failed to fetch GitHub deployments"})
            return

        deployments = response.json().get("workflow_runs", [])
        formatted_deployments = [
            {
                "id": run["id"],
                "name": run["name"],
                "display_title": run["display_title"],
                "workflow": run["workflow_id"],
                "version": run.get("head_branch", "main"),
                "target": run["event"],
                "timestamp": run["created_at"],
                "status": run["conclusion"] or "in_progress",
                "url": run["html_url"],
            }
            for run in deployments
        ]

        return formatted_deployments

    def push_code_github(self, data):
        # Step 1: Get latest commit SHA
        #print(data)
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_message = data.get(
            "message", f"Deployed using Codebenders via API at {current_time}"
        )
        print(commit_message)

        ref_url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/git/ref/heads/{BRANCH_NAME}"
        headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
        }

        # Step 1: Check if the repository exists
        repo_url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}"
        repo_response = requests.get(repo_url, headers=headers)

        if repo_response.status_code == 404:  # Repo doesn't exist, create it
            create_repo_url = f"https://api.github.com/user/repos"
            create_repo_data = {
                "name": GITHUB_REPO,
                "private": False,  # Change to True if you want a private repo
                "description": "Auto-created repo via API",
                "auto_init": True,  # Initializes the repo with a README
            }
            create_repo_response = requests.post(create_repo_url, headers=headers, json=create_repo_data)

            if create_repo_response.status_code not in [201, 202]:
                return {"error": "Failed to create repository", "status": "failed"}
            
        
        # Step 2: Check if branch exists or create it
        ref_url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/git/ref/heads/{BRANCH_NAME}"
        ref_response = requests.get(ref_url, headers=headers)
        ref_data = ref_response.json()

        if ref_response.status_code == 404:  # Branch not found, create it
            default_branch_ref_url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/git/ref/heads/main"
            default_branch_response = requests.get(default_branch_ref_url, headers=headers)
            default_branch_data = default_branch_response.json()

            if "object" not in default_branch_data:
                return {"error": "Failed to fetch default branch SHA", "status": "failed"}

            latest_commit_sha = default_branch_data["object"]["sha"]

            # Create new branch from main
            create_branch_url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/git/refs"
            branch_data = {"ref": f"refs/heads/{BRANCH_NAME}", "sha": latest_commit_sha}
            create_branch_response = requests.post(create_branch_url, headers=headers, json=branch_data)

            if create_branch_response.status_code != 201:
                return {"error": "Failed to create new branch", "status": "failed"}
        elif "object" in ref_data:
            latest_commit_sha = ref_data["object"]["sha"]
        else:
            return {"error": "Failed to fetch branch reference", "status": "failed"}


        # Step 3: Get the tree SHA of the latest commit
        commit_url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/git/commits/{latest_commit_sha}"
        commit_response = requests.get(commit_url, headers=headers)
        commit_data = commit_response.json()

        if "tree" not in commit_data:
            return {"error": "Failed to fetch commit tree", "status": "failed"}

        base_tree_sha = commit_data["tree"]["sha"]


        # Step 4: Get the existing repository tree
        tree_url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/git/trees/{base_tree_sha}?recursive=1"
        tree_response = requests.get(tree_url, headers=headers)
        tree_data = tree_response.json()

        if "tree" not in tree_data:
            return {"error": "Failed to fetch repository tree", "status": "failed"}
        def get_all_files(base_path):
            """ Get all files recursively from the base path. """
            file_list = []
            for root, _, files in os.walk(base_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    repo_path = os.path.relpath(file_path, base_path)  # Get relative path
                    file_list.append(repo_path)
            return file_list
        # Step 4: Get all files in CWD
        cwd = os.getcwd()
        files_to_push = get_all_files(cwd)

        print(f"Files detected: {files_to_push}")

        new_blobs = []
        for file in files_to_push:
            with open(file, "rb") as f:
                content = f.read()

            # Handle binary files properly
            try:
                content_str = content.decode("utf-8")
                encoding = "utf-8"
            except UnicodeDecodeError:
                content_str = base64.b64encode(content).decode("utf-8")
                encoding = "base64"  # Use base64 for binary files

            blob_url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/git/blobs"
            blob_data = {
                "content": content_str,
                "encoding": encoding
            }
            blob_response = requests.post(blob_url, headers=headers, json=blob_data)
            blob_json = blob_response.json()

            if "sha" in blob_json:
                new_blobs.append({
                    "path": file,
                    "mode": "100644",  # Regular file mode
                    "type": "blob",
                    "sha": blob_json["sha"]
                })

        if not new_blobs:
            return {"error": "Failed to upload new files", "status": "failed"}

        # Step 6: Create a new tree with the selected files
        new_tree_data = {"base_tree": base_tree_sha, "tree": new_blobs}
        new_tree_url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/git/trees"
        new_tree_response = requests.post(new_tree_url, headers=headers, json=new_tree_data)
        new_tree_data = new_tree_response.json()

        if "sha" not in new_tree_data:
            return {"error": "Failed to create new tree", "status": "failed"}

        new_tree_sha = new_tree_data["sha"]

        # Step 7: Create a new commit
        new_commit_data = {
            "message": commit_message,
            "tree": new_tree_sha,
            "parents": [latest_commit_sha],
        }
        new_commit_url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/git/commits"
        new_commit_response = requests.post(new_commit_url, headers=headers, json=new_commit_data)
        new_commit_data = new_commit_response.json()

        print(new_commit_data)
        if "sha" not in new_commit_data:
            return {"error": "Failed to create new commit", "status": "failed"}

        new_commit_sha = new_commit_data["sha"]


         # Step 8: Update the branch reference to point to the new commit
        update_ref_url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/git/refs/heads/{BRANCH_NAME}"
        update_ref_data = {"sha": new_commit_sha, "force": True}
        update_ref_response = requests.patch(update_ref_url, headers=headers, json=update_ref_data)

        if update_ref_response.status_code != 200:
            return {"error": "Failed to update branch reference", "status": "failed"}

        return {
            "success": True,
            "message": "Selected folders pushed successfully",
            "commit_url": new_commit_data["html_url"],
        }

    def encrypt_secret(self, public_key, secret_value):
        """
        Encrypt a secret value using the repository's public key
        """
        public_key_decoded = public.PublicKey(
            public_key["key"].encode("utf-8"), encoding.Base64Encoder()
        )
        sealed_box = public.SealedBox(public_key_decoded)
        encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
        return base64.b64encode(encrypted).decode("utf-8")
    
    def create_or_update_secret(self, secret_name, secret_value):
        """
        Create or update a repository secret
        """
        # First get the public key
        public_key_data, error = self.get_public_key()
        if error:
            return error
        
        # Encrypt the secret value
        encrypted_value = self.encrypt_secret(public_key_data, secret_value)
        
        # Create or update the secret
        url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/actions/secrets/{secret_name}"
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        
        data = {
            "encrypted_value": encrypted_value,
            "key_id": public_key_data["key_id"]
        }
        
        response = requests.put(url, headers=headers, json=data)
        
        if response.status_code not in [201, 204]:
            return {
                "error": f"Failed to create/update secret: {response.status_code}",
                "details": response.json(),
                "status": "failed"
            }
        
        return {
            "success": True,
            "message": f"Secret '{secret_name}' created/updated successfully",
            "status": "success"
        }

    def fetch_repo_secrets(self):
        """
        Fetch all repository secrets (names only, not values as GitHub doesn't expose secret values)
        """
        url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/actions/secrets"
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            return {
                "error": f"Failed to fetch repository secrets: {response.status_code}",
                "details": response.json(),
                "status": "failed"
            }
        
        secrets_data = response.json()
        # Note: This only returns secret names and metadata, not the actual values
        return {
            "total_count": secrets_data.get("total_count", 0),
            "secrets": [
                {
                    "name": secret["name"],
                    "created_at": secret["created_at"],
                    "updated_at": secret["updated_at"]
                }
                for secret in secrets_data.get("secrets", [])
            ]
        }
    
    def get_public_key(self):
        """
        Get the repository's public key needed for encrypting secrets
        """
        url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/actions/secrets/public-key"
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            return None, {
                "error": f"Failed to get public key: {response.status_code}",
                "details": response.json()
            }
        
        return response.json(), None
    
    def delete_secret(self, secret_name):
        """
        Delete a repository secret
        """
        url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/actions/secrets/{secret_name}"
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        
        response = requests.delete(url, headers=headers)
        
        if response.status_code != 204:
            return {
                "error": f"Failed to delete secret: {response.status_code}",
                "details": response.json() if response.text else "No details available",
                "status": "failed"
            }
        
        return {
            "success": True,
            "message": f"Secret '{secret_name}' deleted successfully",
            "status": "success"
        }