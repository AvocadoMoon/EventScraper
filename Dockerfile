FROM ubuntu:latest
USER root

ENV GOOGLE_APPLICATION_CREDENTIALS=/app/config/adc.json
ENV CACHE_DB_PATH=/app/config

######################
## Install Packages ##
######################

RUN apt-get update && apt-get -y install cron
RUN apt-get -y install software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa && apt-get update
RUN apt-get -y install python3 && apt-get -y install python3-pip && apt-get -y install python3-poetry

################
## Cron Setup ##
################
# Copy hello-cron file to the cron.d directory
COPY ./docker/runBotCron /etc/cron.d/runBotCron
 
# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/runBotCron
 
# Create the log file to be able to run tail
RUN touch /var/log/cron.log
 
# Run the command on container startup
CMD cron && tail -f /var/log/cron.log


ADD src /app/src
COPY pyproject.toml /app
COPY README.md /app
RUN groupadd eventg
RUN useradd -m -g eventg eventscraper
RUN chown eventscraper:eventg -R /app

#################################
## Install Python Dependencies ##
#################################

USER eventscraper
WORKDIR /app
RUN poetry install

RUN mkdir /app/config
VOLUME /app/config


######################################
## Copy Entrypoint and Install GoSu ##
######################################

USER root
ADD ./docker/entrypoint.sh /app/entrypoint.sh
RUN chmod u=rx,g=r,o=r /app/entrypoint.sh
RUN set -eux; \
	apt-get update; \
	apt-get install -y gosu; \
	rm -rf /var/lib/apt/lists/*; \
# verify that the binary works
	gosu nobody true
ENTRYPOINT ["/app/entrypoint.sh"]

