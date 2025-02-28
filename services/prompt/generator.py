from typing import Dict, List, Optional
from database.models import Project
from constants import CustomDatabaseConfig
from utils.llm_helper import LLMHelper
import json


class PromptGenerator:
    """Service for generating and managing code generation prompts"""

    def __init__(self, model_name: str = None):
        """Initialize with optional specific model"""
        self.llm = LLMHelper.get_llm(model_name) if model_name else LLMHelper.get_llm()

    async def generate_api_specification(
        self,
        requirement_document: str,
        selected_features: List[Dict],
        erd: str,
        host: str = "http://localhost:8000",
    ) -> List[Dict]:
        """
        Generate API specification using LLM.
        Returns the actual API list, not just the prompt.
        """
        system_message = """
You are an expert Backend API Architect tasked with designing a comprehensive RESTful API specification that:
1. Aligns with the selected features
2. Follows the data model from ERD
3. Implements all required functionality
4. Maintains data relationships
5. Follows REST best practices
"""

        human_message = f"""
CONTEXT:
1. Requirements Document: {requirement_document}
2. Selected Features: {selected_features}
3. Entity-Relationship Diagram: {erd}
4. Base URL: {host}

DESIGN REQUIREMENTS:

1. API Structure:
   - RESTful endpoint naming
   - Proper HTTP methods
   - Clear resource hierarchies
   - Consistent URL patterns
   - Relationship-based routing

2. Feature Coverage:
   - Implement all selected features
   - Support ERD relationships
   - Include necessary CRUD operations
   - Handle data validations
   - Support filtering/sorting where needed

3. Data Handling:
   - Follow ERD data types
   - Maintain relationships
   - Include validation rules
   - Handle nested resources
   - Support pagination

4. Authentication/Authorization:
   - Secure sensitive endpoints
   - Role-based access
   - Token handling
   - Permission checks

Generate API specification in this exact format:
[
  {{
    "path": "/resource-path",
    "method": "HTTP_METHOD",
    "auth": boolean,
    "description": "Purpose and usage",
    "request": {{
      "headers": {{
        "field": "type and description"
      }},
      "params": {{
        "field": "type and description" // Include only if needed
      }},
      "query": {{
        "field": "type and description" // Include only if needed
      }},
      "body": {{
        "field": "type and rules" // Include only if needed
      }}
    }},
    "response": {{
      "success": {{
        "field": "type and description"
      }},
      "error": {{
        "field": "type and description"
      }}
    }},
    "relationships": [
      "Related endpoints or resources"
    ]
  }}
]

RULES:
1. Every endpoint must:
   - Relate to ERD entities
   - Support selected features
   - Follow REST conventions
   - Include auth requirements
   - Handle relationships

2. Data types must:
   - Match ERD definitions
   - Use consistent formats
   - Include validations
   - Handle nulls properly

3. Responses must:
   - Be complete but concise
   - Include error cases
   - Handle relationships
   - Support pagination
   - Follow consistent structure

Return only the API specification array without additional text.
"""
        # Create messages for LLM
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": human_message},
        ]

        # Get response from LLM
        response = self.llm.invoke(messages)

        # Parse the JSON response into a list of API specifications
        try:
            apis = json.loads(
                response.content.replace("```json", "").replace("```", "")
            )
            if not isinstance(apis, list):
                raise ValueError("API specification must be a list")
            return apis
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse API specification: {str(e)}")

    def generate_backend_prompt(
        project: Project,
        requirement_document: str,
        selected_features: List[Dict],
        tech_stack: Dict,
        erd: str,
        apis: List[Dict],
    ) -> str:
        print(project)
        """Generate backend implementation prompt"""
        system_message = """
You are a backend developer agent who:
1. Creates production-ready implementations
2. Implements secure database connections using provided configurations
3. Follows exact framework versions and patterns
4. Follows best practices and conventions
5. Maintains code quality and consistency
6. Ensures proper error handling
7. Implements security best practices
"""

        human_message = f"""
CONTEXT:
1. Project Requirements: {requirement_document}
2. Selected Features: {selected_features}
3. Technical Stack: {tech_stack}
4. Database: {CustomDatabaseConfig.to_env_string()}
5. API Specifications: {apis}
6. Database Schema: {erd}

IMPLEMENTATION WORKFLOW:

1. Project Initialization
```bash
# Project setup commands based on tech_stack
```

2. Database Configuration
```env
{CustomDatabaseConfig.to_env_string()}
```

3. Feature Implementation
For each feature in selected_features:
   - Database models from erd
   - API routes from apis
   - Business logic
   - Error handling
   - Tests

Generate implementation in this structure:

1. Project Structure:
```
project_root/
  └─ src/
     ├─ models/      # From erd
     ├─ routes/      # From apis
     ├─ controllers/ # Business logic
     ├─ middleware/  # Auth, validation
     ├─ config/      # Environment setup
     └─ utils/       # Helper functions
```

2. Implementation Format:
```file:path/to/file.ext
Complete, working code with:
- Proper imports
- Error handling
- Database operations
- Input validation
- Auth checks
```

3. Configuration:
```env
# All required environment variables
```

4. Commands:
```bash
# Installation and setup commands
```

IMPLEMENTATION RULES:

1. Database Integration:
   - Use provided database configuration
   - Implement models
   - Follow ERD relationships
   - Use proper indexing
   - Implement transactions

2. Code Structure:
   - Follow tech_stack conventions
   - Use types/interfaces where applicable
   - Implement proper error handling
   - Include input validation
   - Add authentication middleware
   - Follow coding standards

3. Database Operations:
   - Follow erd schema
   - Implement proper relations
   - Include transactions where needed
   - Add data validation
   - Handle errors properly

4. API Implementation:
   - Follow apis specification
   - Implement all endpoints
   - Include proper status codes
   - Handle all error cases
   - Add response formatting

5. Security:
   - Implement authentication
   - Add input sanitization
   - Include rate limiting
   - Handle sensitive data
   - Add request validation

Return implementation in the specified format without additional explanation.
"""
        return f"{system_message}\n\n{human_message}"

    def generate_frontend_prompt(
        self,
        requirement_document: str,
        selected_features: List[Dict],
        tech_stack: Dict,
        theme: Dict,
        apis: List[Dict],
    ) -> str:
        """Generate frontend implementation prompt"""
        system_message = """
You are a frontend developer agent who:
1. Creates production-ready UI implementations following exact technical specifications
2. Strictly adheres to provided tech stack tools and versions
3. Implements consistent theming and styling across components
4. Ensures proper API and state management integration
5. Maintains clean, typed, and documented code
"""

        human_message = f"""
CONTEXT:
1. Project Requirements: {requirement_document}
2. Selected Features: {selected_features}
3. Technical Stack: {tech_stack}
4. API Specifications: {apis}
5. Theme Configuration: {theme}

THEME DETAILS:
- Primary Color: {theme["primary_color"]}
- Background Color: {theme["background_color"]}
- Text Color: {theme["text_color"]}
- Font Family: {theme["font"]}
- Logo URL: {theme["logo_url"]}

IMPLEMENTATION WORKFLOW:

1. Project Setup
```bash
# Project initialization based on tech_stack
```

2. Feature Implementation
For each feature in selected_features:
   - Component structure
   - API integration from apis
   - State management
   - Error handling
   - UI/UX implementation
   - Tests

Generate implementation in this structure:

1. Implementation Format:
```file:path/to/file.ext
Complete, working code with:
- Proper imports
- TypeScript types
- Error handling
- Loading states
- API integration
- Responsive design
```

2. Configuration:
```env
# Environment variables
```

3. Commands:
```bash
# Setup and development commands
```

IMPLEMENTATION RULES:

1. Code Structure:
   - Follow tech_stack best practices
   - Use TypeScript
   - Implement proper error boundaries
   - Add loading states
   - Follow component hierarchy
   - Use proper naming conventions

2. Tech Stack Compliance:
   - Use only specified libraries and versions
   - Follow framework-specific patterns
   - Implement specified state management
   - Use designated form handling
   - Follow testing framework conventions

3. Theme Integration:
   - Use theme variables consistently
   - Implement responsive design
   - Include logo where appropriate
   - Follow accessibility guidelines
   - Maintain styling consistency

4. API Integration:
   - Follow apis specification
   - Implement error handling
   - Add loading states
   - Handle offline scenarios
   - Type API responses

5. Feature Implementation:
   - Follow selected_features requirements
   - Create reusable components
   - Implement responsive design
   - Add accessibility features
   - Include proper documentation

6. Component Structure:
   - Follow atomic design principles
   - Implement prop validation
   - Add loading skeletons
   - Include error boundaries
   - Document component usage

7. State Management:
   - Use appropriate state solutions
   - Implement proper caching
   - Handle side effects
   - Manage form state
   - Handle user sessions

Generate implementation starting with:
1. Theme configuration
2. Project setup
3. Feature implementation

Return only the implementation code without additional explanations.
"""
        return f"{system_message}\n\n{human_message}"
