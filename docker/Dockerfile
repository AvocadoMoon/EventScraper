FROM ubuntu:latest

ENV GOOGLE_APPLICATION_CREDENTIALS=/app/config/adc.json
ENV CACHE_DB_PATH=/app/config
USER root

RUN useradd -m eventscraper

ADD /app/src

RUN chown eventscraper -R /app

RUN apt-get update && apt-get -y install cron
RUN apt-get -y install python && apt-get -y install pipx

# Copy hello-cron file to the cron.d directory
COPY runBotCron /etc/cron.d/runBotCron
 
# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/runBotCron
 
# Create the log file to be able to run tail
RUN touch /var/log/cron.log
 
# Run the command on container startup
CMD cron && tail -f /var/log/cron.log


USER eventscraper

COPY ../src /app/src
COPY ../pyproject.toml /app
COPY entrypoint.sh /app

RUN pipx install poetry

WORKDIR /app
RUN poetry init

RUN mkdir /app/config
VOLUME /app/config


ENTRYPOINT ["/app/entrypoint.sh"]
