# Promise Tracker

## Onboarding Guide
Create a virtual environment with your tool of choice with python 3.11. Other python versions may work; we just have been primarily developing using python 3.11.

`conda create -n promisetracker python=3.11`

Active your virtual environment such that we may install dependencies inside it.

`conda activate promisetracker`

Navigate to the `<project root>/backend/` directory and run `pip install -e .` to editably install the package which you can import under the `ptracker` namespace.

Next you will need to configure your environment variables. Copy the `sample.env` file to `.env` in the same top-level project directory. Changes to the top-level `.env` will not be tracked via git (per `.gitignore` settings); this is by design to ensure we avoid commiting api and database keys. Update the `.env` file to have all the right secrets to ensure functionality.

Load the environment variables, such as by running:
`set -o allexport && source .env && set +o allexport` from the project root directory.

Finally, boot up the backend! This may seed the database depending on if tables are missing / empty. From the backend directory, run `source startup.sh`. You should find the server boots up on `http://localhost:8000/` according to the startup logs; refer to `http://localhost:8000/docs` for the list of available routes currently supported by the app.

The backend is booted with reloading for local development mode (controllable via the `environment` config); make your backend changes, save the file, and you should see the updates occur live in the app if the backend is running.
