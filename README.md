# cpsc449-p5

Professor Kenytt Avery

CPSC 449, Web Back-end Development

Due: Nov. 6, 2020

## Introduction
An API featuring three microservices.

## Requirements
- python 3

To run the APIs, the user must obtain the following modules:

- flask
- flask_api
- flask_basic_auth
- os
- pugsql
- requests
- sys
- werkzeug.security
- foreman
- httpie

## Usage
To run the API:

1. Navigate to the project repository.
2. Using foreman, run `foreman start --formation gateway=1,users=3,timelines=3`. The gateway should be on port 5000 for development.
3. Using a second terminal emulator window, navigate to the same project repository and run `FLASK_APP=users_api flask init`. This should create the sqlite database: MBS.db
4. Begin making HTTP Requests to the API.

## Collaborators
Brandon Xue, Jacob Rapmund
