# adk-agent-apps

A multi agent apps project built with Google's Agent Development Kit (ADK).

## Project Structure

This project is organized as follows:

```
adk-agent-apps/
├── apps/                 # Parent folder containing all the apps
    └── app1              # Individual app folder
        ├── __init__.py   
        ├── agent.py      # Main agent logic
        ├── tools.py      # Custom tools used by the agent
        ├── utils.py      # Utility functions and helpers specific to this app
        └── sub_agents/   # folder containing the sub agents
        └── tests/        # Unit, integration, and load tests
    └── app2              # Individual app folder
        ├── __init__.py   
        ├── agent.py      # Main agent logic
        ├── tools.py      # Custom tools used by the agent
        ├── utils.py      # Utility functions and helpers specific to this app
        └── sub_agents/   # folder containing the sub agents
        └── tests/        # Unit, integration, and load tests
    └── server.py         # FastAPI Backend server hosting all the apps
    └── utils/           # Common Utility functions and helpers
├── notebooks/           # Jupyter notebooks for prototyping and evaluation
├── Makefile             # Makefile for common commands
├── GEMINI.md            # AI-assisted development guide
└── pyproject.toml       # Project dependencies and configuration
└── Dockerfile           # Dockerfile required for building the docker image
```

## Requirements

Before you begin, ensure you have:
- **uv**: Python package manager - [Install](https://docs.astral.sh/uv/getting-started/installation/)
- **Google Cloud SDK**: For GCP services - [Install](https://cloud.google.com/sdk/docs/install)
- **make**: Build automation tool - [Install](https://www.gnu.org/software/make/) (pre-installed on most Unix-based systems)


## Quick Start (Local Testing)

Install required packages and launch the local development environment:

```bash
make install && make playground
```

## Commands

| Command              | Description                                                                                 |
| -------------------- | ------------------------------------------------------------------------------------------- |
| `make install`       | Install all required dependencies using uv                                                  |
| `make playground`    | Launch local development environment with backend and frontend - leveraging `adk web` command.|
| `make local-backend` | Launch local development server |                                                                   |

For full command options and usage, refer to the [Makefile](Makefile).


## Usage

This template follows a "bring your own agent" approach - you focus on your business logic, and the template handles everything else (UI, infrastructure, deployment).

1. **Integrate:** Import your agent by adding your agent app folder containing the app code changes under the `apps` folder.
2. **Test:** Explore your agent functionality using the Streamlit playground with `make playground` and by deploying locally as a Fast API server using `make local-backend` command. The playground offers features like chat history, user feedback, and various input types, and automatically reloads your agent on code changes. You can use the 'adk_app_testing.ipynb' notebook to test your app.
3. **Deploy:** Once the agent app is tested locally, you need to push your app changes to the main branch by raising a pull request. Once the pull request is reviewed and merged, the app changes will get deployed automatically to the dev Cloud run service using Cloud Build.
4. **Monitor:** Track performance and gather insights using Cloud Logging and Tracing to iterate on your application.

The project includes a `GEMINI.md` file that provides context for AI tools like Gemini CLI when asking questions about your template.


## Deployment

### Local Environment

You can deploy your app locally using the following two options

1. **Using adk web:** You can deploy using adk web. Run the following `make playground` command which deploys the app using adk web. 

2. **Fast API server:** You can deploy the app locally as a Fast API server. Run the following `make local-backend` command to deploy the app locally as a Fast API server.


### Dev Environment

The app is deployed on Cloud Run in dev environment. The app changes should not be directly deployed to Cloud Run by the developer. The following process will be followed to deploy the app changes to Cloud Run

1. Developer should raise a pull request to merge their changes to the `main` branch. 
2. The pull request changes will get reviewed.
3. Once the changes are reviewed and approved, the pull request will be merged to the `main` branch.
4. Once the pull request is merged, the changes will be deployed to Cloud Run. 
