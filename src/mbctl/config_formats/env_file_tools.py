class EnvFileTools:
    @staticmethod
    def parse_env_file(content: str) -> dict:
        """Parses the content of an env file into a dictionary."""
        env_dict = {}
        lines = content.splitlines()
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#"):
                key, _, value = line.partition("=")
                env_dict[key.strip()] = value.strip()
        return env_dict

    @staticmethod
    def generate_env_file(env_dict: dict) -> str:
        """Generates the content of an env file from a dictionary."""
        lines = []
        for key, value in env_dict.items():
            lines.append(f"{key}={value}")
        return "\n".join(lines) + "\n"

    @staticmethod
    def write_env_file(env_dict: dict, file_path: str):
        """Writes the env dictionary to a file."""
        content = EnvFileTools.generate_env_file(env_dict)
        with open(file_path, "w") as f:
            f.write(content)