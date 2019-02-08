"""
Management of the top level video
"""
import logging
import cv2
import pkg_resources
import numpy as np
from .points import remove_neighbors, offset
from .game import Game, Player

class Video():
    """
    Manages the video to be processed
    """

    def __init__(self, path, cluster_size=10, show_video=False):
        self.logger = logging.getLogger(__name__)
        self.path = path
        self.cluster_size = cluster_size
        self.show_video = show_video
        self.capture = cv2.VideoCapture(path)
        self.games = []
        self.fps = self.capture.get(cv2.CAP_PROP_FPS)
        self.height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.game_in_progress = False
        self.frame = None

    def _next_frame(self):
        """
        Advance self.frame to the next frame in the capture
        """
        ret, self.frame = self.capture.read()
        if not ret:
            self.logger.warning('Failed to read frame')
        if self.show_video:
            cv2.imshow('frame', self.frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                exit(0)
        return ret

    def analyze(self):
        """
        Pull statistics from the game video
        """
        self.logger.info('Analysing game footage: %s', self.path)
        while not self.game_in_progress:
            self.start_game()
        while self.game_in_progress:
            self.analyze_game()

    def start_game(self):
        """
        Look for players in the frame to "start" a game
        """
        player_count = 0
        confirmed_count = 0
        while confirmed_count < 15:
            new = self._next_frame()
            if new:
                percents = self._find_percents()
                if percents:
                    self.logger.debug("%d players found, confirming %d/15", len(percents), confirmed_count)
                    if player_count == len(percents):
                        confirmed_count += 1
                    else:
                        confirmed_count = 0
                    player_count = len(percents)
        self.games.append(Game([Player(self.frame, point) for point in percents]))
        self.game_in_progress = True
        self.logger.info("Starting game with %d players", player_count)

    def analyze_game(self):
        new = self._next_frame()
        if new:
            self.games[-1].update_frame(self.frame)
            self.games[-1].analyze()
            self.logger.info(self.games[-1].stats[-1])
        for x in range(0, self.cluster_size):
            self._next_frame()

    @property
    def percent_template(self):
        """
        Returns the percent sign for the image size
        """
        percent_path = pkg_resources.resource_filename(__name__, 'templates/ultimate/{}/percent.png'.format(self.height))
        img = cv2.imread(percent_path, 0)
        return img

    def _find_percents(self, cutoff=0.6):
        """
        Returns the top left corner of any percent signs found
        """
        self.logger.debug('Attempting to find percents')
        # Only process the bottom 4th of a frame
        cropped_frame = self.frame[(self.height * 3) // 4:self.height, 0:self.width]
        cropped_offset = (0, (self.height * 3) // 4)
        gray_frame = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2GRAY)
        _, threshold = cv2.threshold(gray_frame, 20, 255, cv2.THRESH_BINARY)
        # Scale the template and attempt a match
        percent_template = self.percent_template
        res = cv2.matchTemplate(threshold, percent_template, cv2.TM_CCOEFF_NORMED)
        # Select all points where match value is above threshold
        loc = np.where(res >= cutoff)
        # Remove near points
        cropped_points = remove_neighbors(list(zip(*loc[::-1])))
        # Return points relative to their original location
        percent_points = [offset(point, cropped_offset) for point in cropped_points]
        return percent_points
