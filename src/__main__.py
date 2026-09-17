from src.parser import Parser
from src.config import Config
from src.render import Render 
from pathlib import Path

def main():
    # Parse the config file properly, and pass all the data to Config class.
    path: Path = Path(__file__).parent.parent / "config" / "config.json"
    parse = Parser(path).parse_config()

    config = Config(**parse)

    rendering = Render(config).display()


if __name__ == "__main__":
    main()
