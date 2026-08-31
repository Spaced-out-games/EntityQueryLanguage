from config import LANGUAGE_NAME, AUTHOR, VERSION, DESCRIPTION


def show_project_identity() -> None:
    print(f"Welcome to {LANGUAGE_NAME} Version {VERSION}")
    print(DESCRIPTION)
    print(f"Designed by: {AUTHOR}")


if __name__ == "__main__":
    show_project_identity()
