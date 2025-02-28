class Urls:
    url_prefix = "/restapi"

    def __init__(self):
        for k, v in self.urls_map.items():
            self.__setattr__(k, v % self.url_prefix)


class Fonts:
    CHOICES = [
        "Inter",
        "Roboto",
        "Open Sans",
        "Lato",
        "Montserrat",
        "Poppins",
        "Source Sans Pro",
        "Ubuntu",
        "Nunito",
        "Raleway",
    ]


class CustomDatabaseConfig:
    DB_TYPE = "mysql"
    DB_HOST = "100.27.172.95"
    DB_PORT = 3306
    DB_USER = "dangles"
    DB_PASSWORD = "dangles@123"
    DB_NAME = "flight_booking"

    @classmethod
    def to_dict(cls) -> dict:
        return {
            "DB_TYPE": cls.DB_TYPE,
            "DB_HOST": cls.DB_HOST,
            "DB_PORT": cls.DB_PORT,
            "DB_USER": cls.DB_USER,
            "DB_PASSWORD": cls.DB_PASSWORD,
            "DB_NAME": cls.DB_NAME,
        }

    @classmethod
    def to_env_string(cls) -> str:
        return f"""
DB_TYPE={cls.DB_TYPE}
DB_HOST={cls.DB_HOST}
DB_PORT={cls.DB_PORT}
DB_USER={cls.DB_USER}
DB_PASSWORD={cls.DB_PASSWORD}
DB_NAME={cls.DB_NAME}
"""


class UrlsV1(Urls):
    url_prefix = "/restapi/v1"

    urls_map = dict(
        **{
            "codegen": r"%s/codegen/(\d+)",
            "data_models": r"%s/data_models",
            "data_model": r"%s/data_models/(\d+)",
            "deployments": r"%s/deployments",
            "deployment": r"%s/deployments/(\d+)",
            "projects": r"%s/projects",
            "project": r"%s/projects/(\d+)",
            "features": r"%s/projects/(\d+)/features",
            "feature": r"%s/projects/(\d+)/features/(\d+)",
            "tech_bundles": r"%s/tech-bundles",
            "project_tech_bundle": r"%s/projects/(\d+)/tech-bundle",
            "epic": r"%s/projects/(\d+)/epics(?:/(\d+))?",
            "epic_generation": r"%s/projects/(\d+)/features/(\d+)/epic",
            "story_generation": r"%s/projects/(\d+)/epics/(\d+)/stories/generate",
            "story": r"%s/projects/(\d+)/epics/(\d+)/stories(?:/(\d+))?",
            "erd": r"%s/projects/(\d+)/erd",
            "theme": r"%s/projects/(\d+)/theme",
            "prompts": r"%s/projects/(\d+)/prompts",
            "deployment_agent": r"%s/projects/(\d+)/deployment",
            "deployment_metadata": r"%s/projects/(\d+)/deployment-metadata",  # GET,PUT request.
            "deployment_credentails": r"%s/projects/(\d+)/deployment-credentials",
            "github_api": r"%s/projects/(\d+)/github(?:/([^/]+))?(?:/([^/]+))?",
            "ws_logs": r"%s/ws/logs",
            "files": r"%s/files/(\d+)",
            "execute": r"%s/execute/(\d+)",
            "test_credentials": r"%s/projects/(\d+)/test-credentials",
            "testingaide_sync": r"%s/projects/(\d+)/testingaide/sync",
        }
    )


urls_v1 = UrlsV1()
