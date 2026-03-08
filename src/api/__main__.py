"""Run the Governance API: uvicorn src.api.app:app."""

import uvicorn

from src.config import Settings


def main() -> None:
    settings = Settings()
    uvicorn.run(
        "src.api.app:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=False,
    )


if __name__ == "__main__":
    main()
