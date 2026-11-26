"""
Smart Campus AI Decision Support & Automation System
Master Entrypoint & Runner (Root)
"""

import sys
from core.router import RequestPreprocessor, RequestRouter
from core.core_facade import CoreFacade
from ai_engines.engine_facade import AIEngineFacade
from presentation.cli_view import InteractiveCampusCLI


def main() -> None:
    """
    Initializes the strict 3-tier architecture and starts the chosen presentation interface.
    Accepts '--gui' CLI argument to directly open the visual campus map window.
    """
    # 1. Initialize Request Preprocessor & Router
    preprocessor = RequestPreprocessor()
    router = RequestRouter(preprocessor)

    # 2. Initialize Master Facade 2 (AI Engine Facade)
    ai_facade = AIEngineFacade()

    # 3. Initialize Master Facade 1 (Core Facade)
    core_facade = CoreFacade(router=router, ai_facade=ai_facade)

    # 4. Check for direct GUI mode flag
    if "--gui" in sys.argv:
        from presentation.gui_advanced import launch_gui
        print("[+] Starting Smart Campus AI Visual Navigation Window...")
        launch_gui(core_facade)
    else:
        # Default: Start Presentation Layer (CLI Form)
        cli = InteractiveCampusCLI(core_facade)
        cli.start()


if __name__ == "__main__":
    main()
