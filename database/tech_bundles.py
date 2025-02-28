TECH_STACKS = [
    {
        "name": "FastAPI + React + MySQL + AWS",
        "description": "A modern, AWS-ready stack combining React's robust UI capabilities with FastAPI's high-performance Python backend. Utilizes MySQL for reliable data storage and AWS services for scalability, making it ideal for cloud-native applications requiring high performance and reliability.",
        "best_for": [
            "High-performance APIs",
            "Cloud-native applications",
            "Scalable enterprise solutions",
        ],
        "components": {
            "frontend": "React",
            "backend": "FastAPI",
            "database": "MySQL",
            "cloud_platform": "AWS",
            "containerization": "Docker",
            "version_control": "Git",
            "api": "REST",
            "package_manager": "pnpm",
            "language_frontend": "TypeScript",
            "language_backend": "Python",
            "build_tool": "Vite",
            "orm": "SQLAlchemy",
        },
        "details": {
            "frontend": {
                "framework": {
                    "name": "React",
                    "version": "18.2.0",
                    "language": "TypeScript",
                    "required": "true",
                },
                "project": {
                    "build_tool": {
                        "name": "Vite",
                        "version": "5.1.0",
                        "template": "react-ts",
                        "required": "true",
                    },
                    "package_manager": {
                        "name": "pnpm",
                        "version": "10.4.1",
                        "required": "true",
                    },
                },
                "dependencies": {
                    "core": ["react", "react-dom", "@types/react", "@types/react-dom"],
                    "routing": {"package": "react-router-dom", "version": "6.20.0"},
                    "state_management": {
                        "package": "redux-toolkit",
                        "version": "2.0.1",
                    },
                    "api_client": {"package": "axios", "version": "1.6.2"},
                },
            },
            "backend": {
                "framework": {
                    "name": "FastAPI",
                    "version": "0.115.8",
                    "language": "Python",
                    "python_version": "3.11",
                    "required": "true",
                },
                "dependencies": {
                    "core": [
                        "fastapi==0.115.8",
                        "uvicorn==0.28.0",
                        "python-dotenv==1.0.0",
                        "pydantic==2.5.1",
                    ],
                    "dev": ["black==23.11.0", "pytest==7.4.3", "pylint==3.0.2"],
                },
            },
            "database": {
                "type": "MySQL",
                "version": "8.0",
                "orm": {"name": "SQLAlchemy", "version": "2.0.23"},
                "dependencies": [
                    "mysql-connector-python==8.2.0",
                    "sqlalchemy==2.0.23",
                    "alembic==1.12.1",
                ],
                "connection": {
                    "host": "localhost",
                    "port": 3306,
                    "url_format": "mysql+mysqlconnector://user:password@localhost:3306/dbname",
                },
            },
            "cloud_platform": {
                "provider": "AWS",
                "services": {
                    "compute": {"name": "EC2", "type": "t3a.medium"},
                    "database": {"name": "RDS", "engine": "MySQL"},
                    "storage": {"name": "S3", "type": "Standard"},
                    "networking": {
                        "name": "VPC",
                        "components": ["subnet", "security_groups", "route_tables"],
                    },
                },
            },
            "containerization": {
                "platform": {"name": "Docker", "version": "24.0.7", "required": "true"},
                "configurations": {
                    "files": ["Dockerfile", "docker-compose.yml", ".dockerignore"],
                    "services": ["frontend", "backend", "database"],
                },
            },
            "version_control": {
                "system": {"name": "Git", "version": "2.42.0"},
                "configuration": {
                    "files": [".gitignore", ".git-credentials", "README.md"],
                    "branches": {
                        "main": "main",
                        "development": "dev",
                        "feature_prefix": "feature/",
                    },
                },
            },
            "api_layer": {
                "type": "REST",
                "specifications": {"format": "OpenAPI/Swagger", "version": "3.0.0"},
                "security": {
                    "authentication": "JWT",
                    "authorization": "Role-based (RBAC)",
                },
                "endpoints": {"base_url": "/api/v1", "documentation": "/docs"},
            },
            "setup": {
                "prerequisites": [
                    "Node.js >= 18",
                    "pnpm >= 10.4",
                    "Python >= 3.11",
                    "Docker >= 24.0",
                    "Git >= 2.42",
                    "MySQL >= 8.0",
                ],
                "commands": {
                    "frontend": [
                        "pnpm create vite@latest frontend -- --template react-ts",
                        "cd frontend",
                        "pnpm install",
                        "pnpm add react-router-dom @reduxjs/toolkit react-redux axios",
                        "pnpm dev",
                    ],
                    "backend": [
                        "python -m venv venv",
                        "source venv/bin/activate",
                        "pip install -r requirements.txt",
                        "uvicorn main:app --reload",
                    ],
                    "docker": ["docker-compose build", "docker-compose up"],
                },
            },
        },
    },
    {
        "name": "Next.js + Django + PostgreSQL + Vercel",
        "description": "An enterprise-grade solution merging Next.js's powerful SSR capabilities with Django's battle-tested backend framework. Features PostgreSQL for complex data relationships and Vercel's edge network, perfect for large-scale applications requiring SEO optimization and robust security features.",
        "best_for": [
            "SEO-critical applications",
            "Enterprise-grade security",
            "Complex data relationships",
        ],
        "components": {
            "frontend": "Next.js",
            "backend": "Django",
            "database": "PostgreSQL",
            "cloud_platform": "Vercel",
            "containerization": "Docker",
            "version_control": "Git",
            "api": "REST",
            "package_manager": "pnpm",
            "language_frontend": "TypeScript",
            "language_backend": "Python",
            "build_tool": "Turbopack",
            "orm": "Django ORM",
        },
        "details": {
            "frontend": {
                "framework": {
                    "name": "Next.js",
                    "version": "14.0.3",
                    "language": "TypeScript",
                    "required": "true",
                },
                "project": {
                    "build_tool": {
                        "name": "Turbopack",
                        "version": "latest",
                        "template": "next-ts",
                        "required": "true",
                    },
                    "package_manager": {
                        "name": "pnpm",
                        "version": "10.4.1",
                        "required": "true",
                    },
                },
                "dependencies": {
                    "core": [
                        "next",
                        "react",
                        "react-dom",
                        "@types/react",
                        "@types/react-dom",
                    ],
                    "ui": {
                        "package": "tailwindcss",
                        "components": "shadcn/ui",
                        "version": "3.3.5",
                    },
                    "state_management": {"package": "jotai", "version": "2.6.0"},
                    "form_handling": {
                        "package": "react-hook-form",
                        "validation": "zod",
                        "version": "7.48.2",
                    },
                    "api_client": {"package": "tanstack-query", "version": "5.8.4"},
                },
            },
            "backend": {
                "framework": {
                    "name": "Django",
                    "version": "4.2.7",
                    "language": "Python",
                    "python_version": "3.11",
                    "required": "true",
                },
                "dependencies": {
                    "core": [
                        "django==4.2.7",
                        "djangorestframework==3.14.0",
                        "django-cors-headers==4.3.0",
                        "dj-rest-auth==5.0.1",
                        "django-environ==0.11.2",
                    ],
                    "dev": [
                        "black==23.11.0",
                        "pytest-django==4.7.0",
                        "django-debug-toolbar==4.2.0",
                    ],
                },
            },
            "database": {
                "type": "PostgreSQL",
                "version": "15.0",
                "orm": {"name": "Django ORM", "version": "4.2.7"},
                "dependencies": [
                    "psycopg2-binary==2.9.9",
                    "django-postgres-extra==2.0.8",
                ],
                "connection": {
                    "host": "localhost",
                    "port": 5432,
                    "url_format": "postgresql://user:password@localhost:5432/dbname",
                },
            },
            "cloud_platform": {
                "provider": "Vercel",
                "services": {
                    "frontend": {
                        "name": "Vercel Edge Network",
                        "features": ["SSR", "ISR", "Edge Functions"],
                    },
                    "backend": {"name": "Railway", "type": "Container Deployment"},
                    "database": {
                        "name": "Railway PostgreSQL",
                        "type": "Managed Database",
                    },
                },
            },
            "containerization": {
                "platform": {"name": "Docker", "version": "24.0.7", "required": "true"},
                "configurations": {
                    "files": ["Dockerfile", "docker-compose.yml", ".dockerignore"],
                    "services": ["frontend", "backend", "database"],
                },
            },
            "version_control": {
                "system": {"name": "Git", "version": "2.42.0"},
                "configuration": {
                    "files": [".gitignore", ".git-credentials", "README.md"],
                    "branches": {
                        "main": "main",
                        "development": "dev",
                        "feature_prefix": "feature/",
                    },
                },
            },
            "api_layer": {
                "type": "REST",
                "specifications": {"format": "OpenAPI/Swagger", "version": "3.0.0"},
                "security": {
                    "authentication": "JWT",
                    "authorization": "Role-based (RBAC)",
                },
                "endpoints": {"base_url": "/api/v1", "documentation": "/docs"},
            },
            "setup": {
                "prerequisites": [
                    "Node.js >= 18",
                    "pnpm >= 10.4",
                    "Python >= 3.11",
                    "Docker >= 24.0",
                    "Git >= 2.42",
                    "PostgreSQL >= 15.0",
                ],
                "commands": {
                    "frontend": [
                        "pnpm create next-app --typescript",
                        "cd frontend",
                        "pnpm install",
                        "pnpm add jotai @tanstack/react-query react-hook-form zod",
                        "pnpm dev",
                    ],
                    "backend": [
                        "python -m venv venv",
                        "source venv/bin/activate",
                        "pip install -r requirements.txt",
                        "python manage.py runserver",
                    ],
                    "docker": ["docker-compose build", "docker-compose up"],
                },
            },
        },
    },
    {
        "name": "Vue + NestJS + MongoDB + DigitalOcean",
        "description": "A lightweight, TypeScript-first stack combining Vue 3's reactivity with NestJS's structured backend approach. Uses MongoDB for flexible data storage and DigitalOcean for simplified deployment, suited for agile startups and microservices architectures requiring quick iteration.",
        "best_for": [
            "Rapid development",
            "Microservices architecture",
            "Agile startups",
        ],
        "components": {
            "frontend": "Vue",
            "backend": "NestJS",
            "database": "MongoDB",
            "cloud_platform": "DigitalOcean",
            "containerization": "Docker",
            "version_control": "Git",
            "api": "REST",
            "package_manager": "pnpm",
            "language_frontend": "TypeScript",
            "language_backend": "TypeScript",
            "build_tool": "Vite",
            "orm": "Mongoose",
        },
        "details": {
            "frontend": {
                "framework": {
                    "name": "Vue",
                    "version": "3.3.9",
                    "language": "TypeScript",
                    "required": "true",
                },
                "project": {
                    "build_tool": {
                        "name": "Vite",
                        "version": "5.0.0",
                        "template": "vue-ts",
                        "required": "true",
                    },
                    "package_manager": {
                        "name": "pnpm",
                        "version": "10.4.1",
                        "required": "true",
                    },
                },
                "dependencies": {
                    "core": ["vue", "vue-router", "pinia"],
                    "ui": {
                        "package": "primevue",
                        "version": "3.42.0",
                        "components": "prime-components",
                        "icons": "@heroicons/vue",
                    },
                    "state_management": {"package": "pinia", "version": "2.1.7"},
                    "form_handling": {
                        "package": "vee-validate",
                        "validation": "yup",
                        "version": "4.11.8",
                    },
                    "api_client": {"package": "axios", "version": "1.6.2"},
                },
            },
            "backend": {
                "framework": {
                    "name": "NestJS",
                    "version": "10.2.1",
                    "language": "TypeScript",
                    "node_version": "18.x",
                    "required": "true",
                },
                "dependencies": {
                    "core": [
                        "@nestjs/core",
                        "@nestjs/common",
                        "@nestjs/platform-express",
                        "@nestjs/mongoose",
                        "class-validator",
                        "class-transformer",
                    ],
                    "dev": [
                        "@types/node",
                        "@types/express",
                        "typescript",
                        "ts-node",
                        "prettier",
                    ],
                },
            },
            "database": {
                "type": "MongoDB",
                "version": "6.0",
                "orm": {"name": "Mongoose", "version": "7.6.5"},
                "dependencies": ["mongoose", "@types/mongoose"],
                "connection": {
                    "host": "localhost",
                    "port": 27017,
                    "url_format": "mongodb://user:password@localhost:27017/dbname",
                },
            },
            "cloud_platform": {
                "provider": "DigitalOcean",
                "services": {
                    "compute": {"name": "App Platform", "type": "Basic"},
                    "database": {"name": "MongoDB", "type": "Managed Database"},
                    "storage": {"name": "Spaces", "type": "Object Storage"},
                },
            },
            "containerization": {
                "platform": {"name": "Docker", "version": "24.0.7", "required": "true"},
                "configurations": {
                    "files": ["Dockerfile", "docker-compose.yml", ".dockerignore"],
                    "services": ["frontend", "backend", "database"],
                },
            },
            "version_control": {
                "system": {"name": "Git", "version": "2.42.0"},
                "configuration": {
                    "files": [".gitignore", ".git-credentials", "README.md"],
                    "branches": {
                        "main": "main",
                        "development": "dev",
                        "feature_prefix": "feature/",
                    },
                },
            },
            "api_layer": {
                "type": "REST",
                "specifications": {"format": "OpenAPI/Swagger", "version": "3.0.0"},
                "security": {
                    "authentication": "JWT",
                    "authorization": "Role-based (RBAC)",
                },
                "endpoints": {"base_url": "/api/v1", "documentation": "/docs"},
            },
            "setup": {
                "prerequisites": [
                    "Node.js >= 18",
                    "pnpm >= 10.4",
                    "Docker >= 24.0",
                    "Git >= 2.42",
                    "MongoDB >= 6.0",
                ],
                "commands": {
                    "frontend": [
                        "pnpm create vite frontend -- --template vue-ts",
                        "cd frontend",
                        "pnpm install",
                        "pnpm add vue-router pinia primevue axios vee-validate yup",
                        "pnpm dev",
                    ],
                    "backend": [
                        "pnpm add -g @nestjs/cli",
                        "nest new backend",
                        "cd backend",
                        "pnpm install",
                        "pnpm start:dev",
                    ],
                    "docker": ["docker-compose build", "docker-compose up"],
                },
            },
        },
    },
]
