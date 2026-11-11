"""Development entry point: `python app.py` starts the API on PORT (default 5001)."""
import logging
import os

from api import create_app

app = create_app()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # threaded=True   -> handle requests concurrently.
    # use_reloader=False -> the auto-reloader restarts the app on every file
    #   save (yours or the editor's) and its half-killed processes are what
    #   kept wedging the server. Restart manually after editing the code.
    app.run(port=int(os.environ.get("PORT", 5001)), threaded=True,
            debug=False, use_reloader=False)
