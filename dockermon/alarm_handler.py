""" Docker's alarm service.

This module implements an alarm service for monitoring whether containers
are running or not.

Todo:
    * integrate with the dojot's alarm manager.
    * align the alarms' status when the service starts.
"""
import docker
import logging
import threading


class AlarmHandler:
    """Handler for monitoring the status of the docker's containers.
    """

    def __init__(self):
        """Initializes the logger, docker client, and the background thread
        for the monitoring loop.
        """
        self.__logger = logging.getLogger('docker-monitor.alarms')
        self.__client = docker.from_env()
        self.__thread = threading.Thread(target=self.run, args=())
        self.__thread.daemon = True
        self.__thread.start()

    def run(self):
        """Infinite loop for monitoring the status of the docker's containers.

        It listen on for the the following docker container's events: die, stop, start, pause, and unpause.
        """
        # TODO Align the alarms

        while True:
            try:
                for event in self.__client.events(filters={'Type': 'container'}, decode=True):

                    if event['Action'] == 'die' \
                            or event['Action'] == 'stop' \
                            or event['Action'] == 'start' \
                            or event['Action'] == 'pause' \
                            or event['Action'] == 'unpause':

                        alarm = {'namespace': 'dojot.docker.container',
                                 'domain': 'docker container status change',
                                 'eventTimestamp': event['time']}

                        # Container went down
                        if event['Action'] == 'die' or event['Action'] == 'stop':
                            alarm['description'] = 'container went down'
                            alarm['severity'] = 'Major'
                            alarm['primarySubject'] = {'container': event['Actor']['Attributes']['name'],
                                                       'image': event['Actor']['Attributes']['image']}

                        # Container went up
                        elif event['Action'] == 'start':
                            alarm['description'] = 'container went up'
                            alarm['severity'] = 'Clear'
                            alarm['primarySubject'] = {'container': event['Actor']['Attributes']['name'],
                                                       'image': event['Actor']['Attributes']['image']}

                        # Processes were paused
                        elif event['Action'] == 'pause':
                            alarm['description'] = 'container processes were paused'
                            alarm['severity'] = 'Major'
                            alarm['primarySubject'] = {'container': event['Actor']['Attributes']['name'],
                                                       'image': event['Actor']['Attributes']['image']}

                        # Processes were unpaused
                        elif event['Action'] == 'unpause':
                            alarm['description'] = 'container processes were unpaused'
                            alarm['severity'] = 'Clear'
                            alarm['primarySubject'] = {'container': event['Actor']['Attributes']['name'],
                                                       'image': event['Actor']['Attributes']['image']}

                        # TODO integrate with dojot's alarm api
                        self.__logger.debug(alarm)
            except docker.errors.APIError:
                self.__logger.error('Communication with docker socket failed.')


# Alarm handler
handler = AlarmHandler()
