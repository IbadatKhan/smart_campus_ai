"""
Smart Campus AI Decision Support & Automation System
Master Entrypoint & Runner (Root)
"""

from core.router import RequestPreprocessor, RequestRouter
from core.core_facade import CoreFacade
from ai_engines.engine_facade import AIEngineFacade
from presentation.cli_view import InteractiveCampusCLI


def main():
    """Initializes 3-tier architecture and starts presentation controller."""
    # 1. Initialize Request Preprocessor & Router
    preprocessor = RequestPreprocessor()
    router = RequestRouter(preprocessor)

    # 2. Initialize Master Facade 2 (AI Engine Facade with Day-1 stubs)
    ai_facade = AIEngineFacade()

    # 3. Initialize Master Facade 1 (Core Facade)
    core_facade = CoreFacade(router=router, ai_facade=ai_facade)

    # 4. Start Presentation Layer (CLI Form)
    cli = InteractiveCampusCLI(core_facade)
    cli.start()


if __name__ == "__main__":
    main()
