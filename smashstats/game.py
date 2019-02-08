import cv2
import pkg_resources
import numpy as np
from .points import offset, scale_point

class Game():
    """
    Analyses a Smash gameplay frame and show game stats
    """

    def __init__(self, players):
        self.players = players
        self.stats = []

    def analyze(self):
        for player in self.players:
            player.analyze()
        self.stats.append([player.dictionary for player in self.players])

    def update_frame(self, frame):
        for player in self.players:
            player.update_frame(frame)


class Player():
    """
    A Player on the HUD
    """

    # Values with respect to 1080p
    SIZE = (325, 195)
    PERCENT_OFFSET = (290, 100)
    DIGIT_SIZE = (70, 80)
    ONES_OFFSET = (213, 47)

    def __init__(self, base_frame, percent_point):
        """
        Extracts the player frame from a base frame and a given percent point
        """
        self.height, _, _ = base_frame.shape
        self.dictionary = {}
        self.scale = self.height / 1080.0
        print(self.scale)
        self.basepoint = self._calculate_basepoint(percent_point)
        self.endpoint = offset(self.basepoint, self.SIZE, self.scale)
        self.init_templates()
        self.update_frame(base_frame)

    def init_templates(self):
        template_path = pkg_resources.resource_filename(__name__, 'templates/ultimate/{}/{}.png'.format(self.height, "{}"))
        print(template_path)
        self.number_template = [cv2.imread(template_path.format('0'), 0),
                                cv2.imread(template_path.format('1'), 0),
                                cv2.imread(template_path.format('2'), 0),
                                cv2.imread(template_path.format('3'), 0),
                                cv2.imread(template_path.format('4'), 0),
                                cv2.imread(template_path.format('5'), 0),
                                cv2.imread(template_path.format('6'), 0),
                                cv2.imread(template_path.format('7'), 0),
                                cv2.imread(template_path.format('8'), 0),
                                cv2.imread(template_path.format('9'), 0)]

    def update_frame(self, frame):
        cropped_frame = frame[self.basepoint[1]:self.endpoint[1], self.basepoint[0]:self.endpoint[0]]
        gray_frame = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2GRAY)
        _, threshold = cv2.threshold(gray_frame, 40, 255, cv2.THRESH_BINARY)
        self.frame = threshold

    def analyze(self):
        self.dictionary = {'percent': self.percent()}

    def identify_digit(self, frame, cutoff=.7):
        """
        Identify a single digit in a given frame
        """
        probability = []
        for x in range(0, 10):
            res = cv2.matchTemplate(frame, self.number_template[x], cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= cutoff)
            probability.append(len(list(zip(*loc[::-1]))))
        maximum = max(probability)
        if maximum != 0:
            return probability.index(max(probability))
        return None

    def _calculate_basepoint(self, percent_point):
        """
        Calculate the basepoint given a percent point
        """
        percent_offset = (-self.PERCENT_OFFSET[0], -self.PERCENT_OFFSET[1])
        return offset(percent_point, percent_offset, self.scale)

    def size(self):
        """
        Return the size of the underlying frame
        """
        return scale_point(self.SIZE, self.scale)

    def percent_offset(self):
        """
        Return the scaled offset of the percent sign
        """
        return scale_point(self.PERCENT_OFFSET, self.scale)

    def digit_size(self):
        """
        Return the scaled size of a percent digit
        """
        return scale_point(self.DIGIT_SIZE, self.scale)

    def ones_offset(self):
        """
        Return the scaled offset of the ones digit
        """
        return scale_point(self.ONES_OFFSET, self.scale)

    def tens_offset(self):
        """
        Return the scaled offset of the tens digit
        """
        tens_base = offset(self.ONES_OFFSET, (-(((self.DIGIT_SIZE[0] * 9) // 10) - int(5 * self.scale)), 0))
        return scale_point(tens_base, self.scale)

    def hundreds_offset(self):
        """
        Return the scaled offset of the tens digit
        """
        hundreds_base = offset(self.ONES_OFFSET, (-(((((self.DIGIT_SIZE[0] * 9) // 10)) - int(5 * self.scale)) * 2), 0))
        return scale_point(hundreds_base, self.scale)

    def percent(self):
        """
        Calculate the percent of the player
        """
        val = self.identify_digit(self.ones_frame())
        cv2.imshow('tens', self.tens_frame())
        if cv2.waitKey(1) & 0xFF == ord('q'):
            exit(0)
        ten = self.identify_digit(self.tens_frame())
        hundred = self.identify_digit(self.hundreds_frame())
        if val and ten:
            val = ten * 10 + val
            if hundred:
                val = hundred * 100 + val
        return val

    def ones_frame(self):
        ones_end = offset(self.ones_offset(), self.digit_size())
        return self.frame[self.ones_offset()[1]:ones_end[1], self.ones_offset()[0]:ones_end[0]]

    def tens_frame(self):
        tens_end = offset(self.tens_offset(), self.digit_size())
        tens_frame = self.frame[self.tens_offset()[1]:tens_end[1], self.tens_offset()[0]:tens_end[0]]
        return tens_frame

    def hundreds_frame(self):
        hundreds_end = offset(self.hundreds_offset(), self.digit_size())
        hundreds_frame = self.frame[self.hundreds_offset()[1]:hundreds_end[1], self.hundreds_offset()[0]:hundreds_end[0]]
        return hundreds_frame
