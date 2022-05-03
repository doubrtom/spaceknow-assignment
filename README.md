# Installation

Requirements:
- `pipenv`: https://pipenv.pypa.io/en/latest/

1. Copy .env.example into .env
2. Edit .env and insert your credentials
3. Run `pipenv shell` to create virtualenv and load .env file
4. Run `pipenv install` to install all package


# Usage

Application is written like CLI tool, to see supported commands run:
`python -m sk_client --help`

Then you can run commands e.g.:
`python -m sk_client credits`


# Run analysis

To run analysis over assignment area:
`python -m sk_client main assignment_parking`

Analysis is interactive, you have to select scenes and zoom level.
