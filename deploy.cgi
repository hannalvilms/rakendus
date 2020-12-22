#!/bin/bash
# -*- coding: utf-8 -*-

# Deploys app from version control, runs tests and if tests pass, runs new version of the app. If tests fail or any other error, sends email.

# Write some HTTP headers to make Nginx happy
echo -e "Content-Type: text/html\n"
DIRECTORY="$PWD"
VCS_URL=https://github.com/hannalvilms/rakendus.git
OUTPUT=''

# Variables
OUTPUT=''

log() {
        # Output immediately (for terminal and web)
        echo -e $1

        # Collect OUTPUT (for sending email later)
        OUTPUT+="$1"$'\n'
}

cmd() {
        log "Doing '$@'"

        # Run the command and capture its output and exit code
        COMMAND_OUTPUT=`$@ 2>&1`
        COMMAND_EXIT_CODE=$?

        # Add command output to OUTPUT
        OUTPUT+=$COMMAND_OUTPUT$'\n'

        # Send the command output to stdout too
        echo -e $COMMAND_OUTPUT$'\n'

        if [[ $COMMAND_EXIT_CODE -ne 0 ]]; then

                log "The previous command returned non-zero exit code. Aborting."

                # Send email to me
                mail -s 'message subject' -aFrom:a@rakendus.icu hannaliisavilms@gmail.com <<< $OUTPUT

                # Stop the script
                exit $?
        fi
}
# Update project

log "Updating the project"

# Change potentially changed files (only tracked ones) back to the state they were originally in Github
cmd "git reset --hard"

# Pull the new commits from Github
cmd "git pull origin main"

# Restores database from dump
cmd 'refresh_mongodb.sh'

# Make the deploy executable
#cmd 'chmod +x deploy'

# Go to app folder
cd techworld/app

# Install dependencies
cmd 'npm i'

# Run tests
cmd 'npm run test'

# Go back to project root folder
cd ..

# Build image
TIMESTAMP=`date +%Y-%m-%d_%H-%M-%S`
cmd "docker build -t my-app ."

# Tag
log "1"
cmd "docker tag my-app:latest 239370337321.dkr.ecr.us-east-2.amazonaws.com/my-app:$TIMESTAMP"

log "2"
# Push the docker to aws
cmd "docker push 239370337321.dkr.ecr.us-east-2.amazonaws.com/my-app:$TIMESTAMP"

log "3"
# Run container
cmd "docker run 239370337321.dkr.ecr.us-east-2.amazonaws.com/my-app:$TIMESTAMP"
