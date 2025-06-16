from cx_Freeze import setup

# Dependencies are automatically detected, but they might need fine-tuning.
build_exe_options = {
    "include_files": ["config.txt", "PasswordsDatabase.db", "databases", "static", "templates"],
    "packages": ["flask", "encodings"]
}

setup(
    name="site_web_tournois",
    version="1.0",
    description="Site web réalisé en python afin de gérer des tournois sportifs.",
    options={"build_exe": build_exe_options},
    executables=[{"script": "app.py", "base": "console"}],
)