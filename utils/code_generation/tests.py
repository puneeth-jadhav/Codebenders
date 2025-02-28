from .system_prompts import get_frontend_system_message
from .graphs import AnthropicGraph
from langchain_core.messages import HumanMessage

# Notes on base_path
# The base_path is the path where the project will be created for both the frontend and backend.
# Eg: base path = /home/user/Desktop
# This is the parameter we need to pass to the code generation function.
# Now in the function we need to create 2 new base paths one for the frontend and one for the backend.
# Eg: frontend_base_path = /home/user/Desktop/<project_id>/frontend and backend_base_path = /home/user/Desktop/<project_id>/backend
# Now this is what is seperately passed to the get_frontend_system_message and get_backend_system_message functions respectively.
# Also the same seperately passed to the graphs for the frontend and backend generation respectively.
# Eg:
# inputs = {
#     "messages": [
#         HumanMessage(
#             content=frontend_prompt
#         )
#     ],
#     "base_path": "/home/user/Desktop/<project_id>/frontend"
# }

system_message = get_frontend_system_message(complete_path='./2/frontend') # Here we need to put the base_path in complete_path

graph = AnthropicGraph(system_message=system_message, model_name='us.anthropic.claude-3-5-haiku-20241022-v1:0')

app = graph.generate_graph()

frontend_prompt = '''
You are a frontend developer agent with capabilities to create/edit files and execute terminal commands.

Input:
Problem Statement: ### [PROBLEM STATEMENT]  
Develop a responsive, user-friendly flight booking search interface that allows users to search for domestic and international flights with options for one-way, round-trip, and multi-city travel, while providing dynamic interaction elements and accessibility compliance.  

---

### 1. CONTEXT AND SCOPE  
- **Business Need**: Simplify the flight search process for users by providing an intuitive interface with advanced travel options and special fare benefits.  
- **Current System Context**: No existing system is specified; this is a new development effort.  
- **High-Level Goals**:  
  - Enable users to search for flights with customizable travel options.  
  - Provide a seamless, responsive, and accessible user experience.  
  - Support dynamic interactions such as date pickers, modals, and multi-city travel configurations.  
- **Scope Boundaries**:  
  - **In-Scope**: Flight search interface, dynamic travel options (one-way, round-trip, multi-city), date-picker, travelers/class modal, special fare selection, and responsive design.  
  - **Out-of-Scope**: Backend flight search engine, payment processing, and booking confirmation workflows.  

---

### 2. FUNCTIONAL REQUIREMENTS  

#### 2.1 Primary Functions (Must-Have)  
- **Core Features**:  
  - **Travel Options**: Allow users to select one-way (default), round-trip, or multi-city travel via radio buttons.  
  - **Travel Details Input**:  
    - "From" and "To" fields with placeholder text and a swap icon for reversing values.  
    - "Departure" and "Return" fields with an interactive calendar dropdown for date selection.  
    - "Travelers & Class" dropdown modal to select the number of travelers and travel class.  
  - **Multi-City Support**: Add additional "From," "To," and "Departure" fields dynamically for each leg of the journey.  
  - **Special Fares Section**: Display benefit cards (e.g., Student, Senior Citizen) with toggle checkboxes for selection.  
  - **Search Flights Button**: Full-width button to validate inputs and submit the form.  

- **User Workflows**:  
  1. Select travel type (one-way, round-trip, or multi-city).  
  2. Enter travel details (From, To, Departure, Return, Travelers & Class).  
  3. (Optional) Add special fare benefits.  
  4. Click "Search Flights" to validate inputs and proceed.  

- **Business Rules**:  
  - "Return" field is disabled for one-way travel and enabled for round-trip or multi-city.  
  - At least one "From," "To," and "Departure" field must be filled for form submission.  

- **Processing Logic**:  
  - Validate required fields on form submission.  
  - Highlight errors with red borders and error messages.  

- **Validation Rules**:  
  - "From" and "To" fields must not be empty.  
  - "Departure" date must be a valid future date.  
  - "Return" date (if applicable) must be after the "Departure" date.  

#### 2.2 Secondary Functions (Should-Have)  
- **Enhanced Capabilities**:  
  - Predefined buttons for quick traveler class selection (e.g., Economy, Business).  
  - Hover/active effects for interactive elements to improve usability.  
  - Responsive design for mobile, tablet, and desktop layouts.  

#### 2.3 Future Enhancements (Nice-to-Have)  
- Integration with backend APIs for real-time flight availability.  
- Save user preferences for frequent travelers.  
- Support for internationalization (multi-language support).  

---

### 3. DATA REQUIREMENTS  

#### 3.1 Data Models  
- **Key Entities**:  
  - Travel Details: From, To, Departure, Return, Travelers, Class.  
  - Special Fares: Benefit type (e.g., Student, Senior Citizen), selection state.  

- **Essential Fields**:  
  - From/To: City or airport name.  
  - Departure/Return: Date in "DD MMM'YY" format.  
  - Travelers: Count of adults, children, and infants.  
  - Class: Economy, Premium Economy, Business, First Class.  

- **Data Relationships**:  
  - Each travel leg (multi-city) is associated with a unique set of From, To, and Departure fields.  

- **Validation Rules**:  
  - Ensure valid city/airport names.  
  - Validate date formats and logical date ranges.  

#### 3.2 Data Operations  
- **Storage Requirements**: Temporary storage of form data until submission.  
- **Retention Policies**: No long-term data retention required.  
- **Backup Needs**: Not applicable.  
- **Access Patterns**: Data is user-input driven and does not require external data sources.  

---

### 4. INTERFACE REQUIREMENTS  

#### 4.1 User Interface  
- **Required Inputs**:  
  - Travel type, From, To, Departure, Return, Travelers, Class, Special Fares.  
- **Expected Outputs**:  
  - Form validation feedback (error messages, red borders).  
  - Updated field values based on user interaction.  
- **Error Scenarios**:  
  - Missing required fields.  
  - Invalid date ranges.  
- **Response Time Expectations**: Instant feedback for form validation and dynamic interactions.  

#### 4.2 System Interface  
- **Integration Points**: None specified for backend integration.  
- **External Systems**: None required.  
- **Data Exchange Formats**: Not applicable.  
- **API Requirements**: Not applicable.  
- **Communication Protocols**: Not applicable.  

---

### 5. NON-FUNCTIONAL REQUIREMENTS  

#### 5.1 Performance  
- **Response Time**: Dynamic elements (e.g., date-picker, modals) must respond within 200ms.  
- **Throughput**: Support up to 100 concurrent users.  
- **Concurrency**: Handle simultaneous interactions without lag.  

#### 5.2 Security  
- **Authentication**: Not required for this interface.  
- **Authorization**: Not applicable.  
- **Data Protection**: Ensure secure handling of user inputs.  
- **Compliance**: Adhere to WAI-ARIA accessibility standards.  

#### 5.3 Scalability  
- **Growth Expectations**: Interface should support additional travel options or fare categories in the future.  
- **Load Handling**: Maintain performance under increased user load.  
- **Geographic Distribution**: Ensure usability across regions.  

---

### 6. CONSTRAINTS AND DEPENDENCIES  
- **Technical Limitations**: Must use React.js or equivalent framework.  
- **Business Constraints**: Adhere to brand guidelines (e.g., orange theme).  
- **External Dependencies**: Date-picker plugin, icon library, CSS framework.  
- **Regulatory Requirements**: Accessibility compliance (WAI-ARIA).  
- **Resource Limitations**: Limited to front-end development scope.  

---

### 7. ACCEPTANCE CRITERIA  
- **Functional Acceptance Criteria**:  
  - All required fields and workflows function as specified.  
  - Form validation highlights errors appropriately.  
- **Performance Benchmarks**:  
  - Dynamic elements respond within 200ms.  
- **Quality Metrics**:  
  - Interface passes usability and accessibility tests.  
- **Test Scenarios**:  
  - Validate form submission with valid and invalid inputs.  
  - Test responsiveness across devices.  
- **Success Indicators**:  
  - Users can successfully search for flights with all travel options.  

---

### 8. RISKS AND CONSIDERATIONS  
- **Known Technical Challenges**: Ensuring cross-browser compatibility.  
- **Critical Decision Points**: Selection of date-picker and CSS framework.  
- **Potential Bottlenecks**: Performance under high user load.  
- **Edge Cases**:  
  - Invalid date ranges (e.g., return date before departure).  
  - Excessive multi-city legs added by users.  
- **Error Scenarios**: Missing required fields, invalid inputs, or unresponsive elements.  
Technology Stack: 
# Improved Technology Stack Structure
technology_stack: {
  # Core Framework
  framework: {
    name: "React",
    version: "20.18.0",
    language: "TypeScript",
    required: true
  },

  # Project Configuration
  project: {
    build_tool: {
      name: "Vite",
      version: "latest",
      template: "react-ts",
      required: true
    },
    package_manager: {
      name: "pnpm",
      version: "10.x",
      required: true
    }
  },

  # UI Components and Styling
  ui: {
    framework: {
      name: "Material UI",
      core: "@mui/material",
      version: "latest",
      required: true,
      dependencies: {
        peer: ["react", "react-dom"],
        required: ["@emotion/react", "@emotion/styled"]
      }
    },
    icons: {
      package: "@mui/icons-material",
      required: true
    },
    typography: {
      font: "Roboto",
      package: "@fontsource/roboto",
      required: true
    }
  },

  # Additional Tools
  utilities: {
    routing: {
      package: "react-router-dom",
      required: true
    },
    state_management: {
      package: "zustand",
      required: true
    },
    form_handling: {
      package: "react-hook-form",
      required: true
    },
    api_client: {
      package: "axios",
      required: true
    }
  },

  # Installation Commands
  setup: {
    project_creation: "pnpm create vite@latest <project-name> --template react-ts",
    install_dependencies: [
      "cd <project-name>",
      "pnpm install",
      "pnpm add @mui/material @emotion/react @emotion/styled",
      "pnpm add @mui/icons-material",
      "pnpm add @fontsource/roboto",
      "pnpm add react-router-dom zustand react-hook-form axios",
    ]
  }
}

APIs: 
Base URL: http://localhost:8000

APIs: [
  {
    path: "/users",
    method: "POST",
    description: "Create a new user",
    request: {
      body: {
        name: "string",
        email: "string",
        phone: "string"
      }
    },
    response: {
      success: {
        user_id: "number",
        name: "string",
        email: "string",
        phone: "string",
        created_at: "string"
      },
      error: {
        code: "number",
        message: "string"
      }
    }
  },
  {
    path: "/users/{user_id}",
    method: "GET",
    description: "Retrieve user details by ID",
    request: {
      params: {
        user_id: "number"
      }
    },
    response: {
      success: {
        user_id: "number",
        name: "string",
        email: "string",
        phone: "string"
      },
      error: {
        code: "number",
        message: "string"
      }
    }
  },
  {
    path: "/flights",
    method: "GET",
    description: "Retrieve available flights based on search criteria",
    request: {
      query: {
        departure_city: "string",
        arrival_city: "string",
        departure_date: "string",
        return_date?: "string",
        travel_class?: "string"
      }
    },
    response: {
      success: [
        {
          flight_id: "number",
          flight_number: "string",
          airline: "string",
          departure_city: "string",
          arrival_city: "string",
          departure_date: "string",
          return_date?: "string",
          travel_class: "string",
          available_seats: "number"
        }
      ],
      error: {
        code: "number",
        message: "string"
      }
    }
  },
  {
    path: "/flights/{flight_id}",
    method: "GET",
    description: "Retrieve flight details by ID",
    request: {
      params: {
        flight_id: "number"
      }
    },
    response: {
      success: {
        flight_id: "number",
        flight_number: "string",
        airline: "string",
        departure_city: "string",
        arrival_city: "string",
        departure_date: "string",
        return_date?: "string",
        travel_class: "string",
        available_seats: "number"
      },
      error: {
        code: "number",
        message: "string"
      }
    }
  },
  {
    path: "/bookings",
    method: "POST",
    description: "Create a new booking",
    request: {
      body: {
        user_id: "number",
        flight_id: "number",
        fare_id: "number",
        adults: "number",
        children: "number",
        infants: "number",
        booking_date: "string"
      }
    },
    response: {
      success: {
        booking_id: "number",
        user_id: "number",
        flight_id: "number",
        fare_id: "number",
        adults: "number",
        children: "number",
        infants: "number",
        booking_date: "string"
      },
      error: {
        code: "number",
        message: "string"
      }
    }
  },
  {
    path: "/bookings/{booking_id}",
    method: "GET",
    description: "Retrieve booking details by ID",
    request: {
      params: {
        booking_id: "number"
      }
    },
    response: {
      success: {
        booking_id: "number",
        user_id: "number",
        flight_id: "number",
        fare_id: "number",
        adults: "number",
        children: "number",
        infants: "number",
        booking_date: "string"
      },
      error: {
        code: "number",
        message: "string"
      }
    }
  },
  {
    path: "/fares",
    method: "GET",
    description: "Retrieve all available fare types",
    request: {},
    response: {
      success: [
        {
          fare_id: "number",
          fare_type: "string",
          description: "string"
        }
      ],
      error: {
        code: "number",
        message: "string"
      }
    }
  },
  {
    path: "/fares/{fare_id}",
    method: "GET",
    description: "Retrieve fare details by ID",
    request: {
      params: {
        fare_id: "number"
      }
    },
    response: {
      success: {
        fare_id: "number",
        fare_type: "string",
        description: "string"
      },
      error: {
        code: "number",
        message: "string"
      }
    }
  }
]
 at http://localhost:8000

Execution Process:

1. Project Initialization
COMMAND: Execute setup commands from technology_stack.setup
WAIT: Until project creation is complete
CHECK: Confirm project structure exists

2. Package Management
- Review problem statement requirements
- For each additional required package:
  COMMAND: Install using package manager from technology_stack
  WAIT: Until installation completes
  CHECK: Verify in package.json

3. Implementation
For each feature in problem statement:
- CREATE/EDIT appropriate files
- VERIFY imports are available
- TEST imports by running dev server
- IMPLEMENT API integration
- VERIFY API endpoints are reachable

Commands Format:
```bash
[exact command to run]
```

File Operations Format:
```file:[path/to/file]
[complete file content]
```

Rules:
- Wait for each command to complete before proceeding
- Verify file creation/modification success
- Check for import errors before moving forward
- Use exact package versions
- Ensure dev server can start
- Confirm API connectivity

Error Handling:
- If a command fails, display error and retry
- If package conflicts occur, resolve before continuing
- If imports fail, fix before proceeding

Begin with:
"I'll create and set up the project. Let me execute the commands step by step..."

For each action:
1. State what you're about to do
2. Show the command or file operation
3. Wait for confirmation
4. Verify success
5. Proceed to next step

Remember:
- Execute commands sequentially
- Verify each step's success
- Keep files organized
- Ensure working code
'''

# inputs = {
#     "messages": [
#         HumanMessage(
#             content=frontend_prompt
#         )
#     ],
#     "base_path": "./2/frontend"
# }

# result = app.invoke(inputs)
# print(result)