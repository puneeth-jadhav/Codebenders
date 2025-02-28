from typing import Dict, List
import json
from utils.llm_helper import LLMHelper


class ERDGenerator:
    """Service for generating and refining ERDs"""

    def __init__(self, model_name: str = None):
        self.llm = LLMHelper.get_llm(model_name) if model_name else LLMHelper.get_llm()

    @property
    def generation_prompt(self) -> str:
        return """
You are a database architect designing a comprehensive data model.

INPUT ANALYSIS:
1. Requirements Document: {requirements}
2. Selected Features: {features}
3. Database Type: {database_type}

DESIGN REQUIREMENTS:
1. Entity Design:
   - Create entities for all core features
   - Include standard fields:
     * Primary keys (uuid/id)
     * Audit fields (created_at, updated_at)
     * Status fields where needed
     * Soft delete capability
     * Version control if needed

2. Data Integrity:
   - Appropriate foreign keys
   - Required constraints
   - Unique constraints
   - Index considerations
   - Data validation rules

3. Relationships:
   - Clear cardinality definition
   - Proper relationship types
   - Junction tables for many-to-many
   - Relationship constraints

4. Schema Standards:
   - Consistent naming patterns
   - Appropriate data types
   - Field size optimization
   - Index naming conventions

5. Technical Considerations:
   - Performance optimization
   - Scalability requirements
   - Query patterns support
   - Data access patterns

Generate Mermaid ERD following this exact syntax:
```mermaid
erDiagram
    %% Entity definitions with full specifications
    ENTITY_NAME {{
        data_type id PK "primary key"
        data_type required_field "not null"
        data_type unique_field "unique,indexed"
        data_type fk_field FK "foreign key"
        data_type status_field "enum"
        timestamp created_at "not null"
        timestamp updated_at "not null"
        timestamp deleted_at "soft delete"
    }}

    %% Relationship definitions with cardinality
    ENTITY_A ||--|| ENTITY_B : "has_one"
    ENTITY_A ||--|{{ ENTITY_B : "has_many"
    ENTITY_A }}|--|{{ ENTITY_B : "many_to_many"
```

Return only valid Mermaid JS code without any additional text or explanations.
"""

    @property
    def refinement_prompt(self) -> str:
        return """
You are a database architect reviewing and enhancing an existing ERD.

INPUT ANALYSIS:
1. Requirements Document: {requirements}
2. Current ERD: {current_erd}
3. User Feedback: {feedback}
4. Selected Features: {features}

IMPROVEMENT REQUIREMENTS:
1. Data Integrity:
   - Primary key for each entity (uuid/id)
   - Appropriate foreign keys
   - Required constraints
   - Unique constraints
   - Index considerations

2. Relationships:
   - Validate all relationships
   - Ensure proper cardinality
   - Add missing relationships
   - Document relationship types clearly

3. Schema Completeness:
   - Support for all features
   - Audit fields (created_at, updated_at)
   - Status tracking where needed
   - Soft delete capability
   - Version control if required

4. Naming Conventions:
   - Consistent entity naming (singular/plural)
   - Clear attribute naming
   - Relationship naming
   - Index naming patterns

5. Data Types:
   - Appropriate size/scale
   - Performance considerations
   - Storage efficiency
   - Standard types across entities

6. Technical Considerations:
   - Indexing strategy
   - Partitioning needs
   - Archive strategy
   - Performance optimization

Generate improved Mermaid ERD following this exact syntax:
```mermaid
erDiagram
    %% Entities with complete attributes
    ENTITY_NAME {{
        data_type id PK "comment"
        data_type required_field "not null"
        data_type optional_field
        data_type fk_field FK "indexed"
        timestamp created_at
        timestamp updated_at
    }}

    %% Relationships with cardinality
    ENTITY_A ||--|{{ ENTITY_B : "relationship_label"
```

Return only valid Mermaid JS code without any additional text or explanations.
"""

    def generate_erd(
        self, requirements: str, features: List[Dict], tech_stack: Dict
    ) -> str:
        """Generate initial ERD"""
        messages = [
            {
                "role": "user",
                "content": self.generation_prompt.format(
                    requirements=requirements,
                    features=features,
                    database_type=tech_stack.get("components", {}).get(
                        "database", "Not specified"
                    ),
                ),
            }
        ]

        response = self.llm.invoke(messages)

        # Add theme configuration
        mermaid_code = """
%%{
init: {
    'theme': 'forest'
}
}%%
""" + response.content.replace(
            "```mermaid", ""
        ).replace(
            "```", ""
        )

        return mermaid_code

    def refine_erd(
        self, current_erd: str, feedback: str, requirements: str, features: List[Dict]
    ) -> str:
        """Refine ERD based on feedback"""
        messages = [
            {
                "role": "user",
                "content": self.refinement_prompt.format(
                    requirements=requirements,
                    current_erd=current_erd,
                    feedback=feedback,
                    features=features,
                ),
            }
        ]

        response = self.llm.invoke(messages)

        # Add theme configuration
        mermaid_code = """
%%{
init: {
    'theme': 'forest'
}
}%%
""" + response.content.replace(
            "```mermaid", ""
        ).replace(
            "```", ""
        )

        return mermaid_code
