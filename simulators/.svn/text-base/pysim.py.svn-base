"""
A Pure Python 2D Robot Simulator

(c) 2005, PyroRobotics.org. Licensed under the GNU GPL.
"""
import time, math, random
try:
    import Tkinter
except:
    print "Warning: Tkinter is not available for pysim"
    class Tkinter:
        Toplevel = object
try:
    import cPickle as pickle
except:
    import pickle
# try to share a tk interpreter, if one is available:
try:
    import pyrobot.system.share as share
except:
    # else, define a new one:
    share = None
PIOVER180 = math.pi / 180.0
PIOVER2   = math.pi /2
RESOLUTION = 7 # decimal places of accuracy in making comparisons

def normRad(x):
    """
    Compute angle in range radians(-180) to radians(180)
    """
    while (x > math.pi): 
        x -= 2 * math.pi
    while (x < -math.pi):
        x += 2 * math.pi
    return x

class Segment:
    def __init__(self, start, end, id = None, partOf = None):
        self.start = [round(v,RESOLUTION) for v in start]
        self.end = [round(v,RESOLUTION) for v in end]
        self.id = id
        self.partOf = partOf
        self.vertical = self.start[0] == self.end[0]
        if not self.vertical:
            self.slope = round((self.end[1] - self.start[1])/
                               (self.end[0] - self.start[0]), RESOLUTION)
            self.yintercept = round(self.start[1] -
                                    self.start[0] * self.slope, RESOLUTION)
    def length(self):
        return math.sqrt((self.start[0] - self.end[0])**2 +
                         (self.start[1] - self.end[1])**2)
    def angle(self):
        return math.atan2(self.end[1] - self.start[1],
                          self.end[0] - self.start[0])
    def parallel(self, other):
        if self.vertical:
            return other.vertical
        elif other.vertical:
            return 0
        else:
            return self.slope == other.slope
    # return the point at which two segments would intersect if they extended
    # far enough
    def intersection(self, other):
        if self.parallel(other):
            # the segments may intersect, but we don't care
            return None
        elif self.vertical:
            return other.intersection(self)
        elif other.vertical:
            return (other.start[0],
                    self.yintercept + other.start[0] * self.slope)
        else:
            # m1x + b1 = m2x + b2; so
            # (m1 - m2)x + b1 - b2 == 0
            # (m1 - m2)x = b2 - b1
            # x = (b2 - b1)/(m1 - m2)
            # figure intersect:
            # putting a round() around both of these next 2 computations caused problems:
            x = ((other.yintercept - self.yintercept) / (self.slope - other.slope))
            return (x, self.yintercept + x * self.slope)
    def in_bbox(self, point):
        return (((self.end[0]   <= round(point[0],RESOLUTION) <= self.start[0]) or
                 (self.start[0] <= round(point[0],RESOLUTION) <= self.end[0])) and
                ((self.end[1]   <= round(point[1],RESOLUTION) <= self.start[1]) or
                 (self.start[1] <= round(point[1],RESOLUTION) <= self.end[1])))
    # is a point collinear with this line segment?
    def on_line(self, point):
        if self.vertical:
            return round(point[0],RESOLUTION) == self.start[0]
        else:
            return (round(point[0] * self.slope +
                          self.yintercept,RESOLUTION) == round(point[1]),RESOLUTION)
    def intersects(self, other):
        if self.parallel(other):
            # they can "intersect" if they are collinear and overlap
            if not (self.in_bbox(other.start) or self.in_bbox(other.end)):
                return None
            elif self.vertical:
                if self.start[0] == other.start[0]:
                    return self.intersection(other)
                else:
                    return None
            else:
                if self.yintercept == other.yintercept:
                    return self.intersection(other)
                else:
                    return None
        else:
            i = self.intersection(other)
            if self.in_bbox(i) and other.in_bbox(i):
                return i
            else:
                return None

MAXRAYLENGTH = 1000.0 # some large measurement in meters

## Supported colors for Tkinter, lights, and cameras

colorMap = {
    "aliceblue": (240, 248, 255),
    "antiquewhite": (250, 235, 215),
    "antiquewhite1": (255, 239, 219),
    "antiquewhite2": (238, 223, 204),
    "antiquewhite3": (205, 192, 176),
    "antiquewhite4": (139, 131, 120),
    "aquamarine": (127, 255, 212),
    "aquamarine1": (127, 255, 212),
    "aquamarine2": (118, 238, 198),
    "aquamarine3": (102, 205, 170),
    "aquamarine4": (69, 139, 116),
    "azure": (240, 255, 255),
    "azure1": (240, 255, 255),
    "azure2": (224, 238, 238),
    "azure3": (193, 205, 205),
    "azure4": (131, 139, 139),
    "beige": (245, 245, 220),
    "bisque": (255, 228, 196),
    "bisque1": (255, 228, 196),
    "bisque2": (238, 213, 183),
    "bisque3": (205, 183, 158),
    "bisque4": (139, 125, 107),
    "black": (0, 0, 0),
    "blanchedalmond": (255, 235, 205),
    "blue": (0, 0, 255),
    "blue1": (0, 0, 255),
    "blue2": (0, 0, 238),
    "blue3": (0, 0, 205),
    "blue4": (0, 0, 139),
    "blueviolet": (138, 43, 226),
    "brown": (165, 42, 42),
    "brown1": (255, 64, 64),
    "brown2": (238, 59, 59),
    "brown3": (205, 51, 51),
    "brown4": (139, 35, 35),
    "burlywood": (222, 184, 135),
    "burlywood1": (255, 211, 155),
    "burlywood2": (238, 197, 145),
    "burlywood3": (205, 170, 125),
    "burlywood4": (139, 115, 85),
    "cadetblue": (95, 158, 160),
    "cadetblue1": (152, 245, 255),
    "cadetblue2": (142, 229, 238),
    "cadetblue3": (122, 197, 205),
    "cadetblue4": (83, 134, 139),
    "chartreuse": (127, 255, 0),
    "chartreuse1": (127, 255, 0),
    "chartreuse2": (118, 238, 0),
    "chartreuse3": (102, 205, 0),
    "chartreuse4": (69, 139, 0),
    "chocolate": (210, 105, 30),
    "chocolate1": (255, 127, 36),
    "chocolate2": (238, 118, 33),
    "chocolate3": (205, 102, 29),
    "chocolate4": (139, 69, 19),
    "coral": (255, 127, 80),
    "coral1": (255, 114, 86),
    "coral2": (238, 106, 80),
    "coral3": (205, 91, 69),
    "coral4": (139, 62, 47),
    "cornflowerblue": (100, 149, 237),
    "cornsilk": (255, 248, 220),
    "cornsilk1": (255, 248, 220),
    "cornsilk2": (238, 232, 205),
    "cornsilk3": (205, 200, 177),
    "cornsilk4": (139, 136, 120),
    "cyan": (0, 255, 255),
    "cyan1": (0, 255, 255),
    "cyan2": (0, 238, 238),
    "cyan3": (0, 205, 205),
    "cyan4": (0, 139, 139),
    "darkblue": (0, 0, 139),
    "darkcyan": (0, 139, 139),
    "darkgoldenrod": (184, 134, 11),
    "darkgoldenrod1": (255, 185, 15),
    "darkgoldenrod2": (238, 173, 14),
    "darkgoldenrod3": (205, 149, 12),
    "darkgoldenrod4": (139, 101, 8),
    "darkgray": (169, 169, 169),
    "darkgreen": (0, 100, 0),
    "darkgrey": (169, 169, 169),
    "darkkhaki": (189, 183, 107),
    "darkmagenta": (139, 0, 139),
    "darkolivegreen": (85, 107, 47),
    "darkolivegreen1": (202, 255, 112),
    "darkolivegreen2": (188, 238, 104),
    "darkolivegreen3": (162, 205, 90),
    "darkolivegreen4": (110, 139, 61),
    "darkorange": (255, 140, 0),
    "darkorange1": (255, 127, 0),
    "darkorange2": (238, 118, 0),
    "darkorange3": (205, 102, 0),
    "darkorange4": (139, 69, 0),
    "darkorchid": (153, 50, 204),
    "darkorchid1": (191, 62, 255),
    "darkorchid2": (178, 58, 238),
    "darkorchid3": (154, 50, 205),
    "darkorchid4": (104, 34, 139),
    "darkred": (139, 0, 0),
    "darksalmon": (233, 150, 122),
    "darkseagreen": (143, 188, 143),
    "darkseagreen1": (193, 255, 193),
    "darkseagreen2": (180, 238, 180),
    "darkseagreen3": (155, 205, 155),
    "darkseagreen4": (105, 139, 105),
    "darkslateblue": (72, 61, 139),
    "darkslategray": (47, 79, 79),
    "darkslategray1": (151, 255, 255),
    "darkslategray2": (141, 238, 238),
    "darkslategray3": (121, 205, 205),
    "darkslategray4": (82, 139, 139),
    "darkslategrey": (47, 79, 79),
    "darkturquoise": (0, 206, 209),
    "darkviolet": (148, 0, 211),
    "deeppink": (255, 20, 147),
    "deeppink1": (255, 20, 147),
    "deeppink2": (238, 18, 137),
    "deeppink3": (205, 16, 118),
    "deeppink4": (139, 10, 80),
    "deepskyblue": (0, 191, 255),
    "deepskyblue1": (0, 191, 255),
    "deepskyblue2": (0, 178, 238),
    "deepskyblue3": (0, 154, 205),
    "deepskyblue4": (0, 104, 139),
    "dimgray": (105, 105, 105),
    "dimgrey": (105, 105, 105),
    "dodgerblue": (30, 144, 255),
    "dodgerblue1": (30, 144, 255),
    "dodgerblue2": (28, 134, 238),
    "dodgerblue3": (24, 116, 205),
    "dodgerblue4": (16, 78, 139),
    "firebrick": (178, 34, 34),
    "firebrick1": (255, 48, 48),
    "firebrick2": (238, 44, 44),
    "firebrick3": (205, 38, 38),
    "firebrick4": (139, 26, 26),
    "floralwhite": (255, 250, 240),
    "forestgreen": (34, 139, 34),
    "gainsboro": (220, 220, 220),
    "ghostwhite": (248, 248, 255),
    "gold": (255, 215, 0),
    "gold1": (255, 215, 0),
    "gold2": (238, 201, 0),
    "gold3": (205, 173, 0),
    "gold4": (139, 117, 0),
    "goldenrod": (218, 165, 32),
    "goldenrod1": (255, 193, 37),
    "goldenrod2": (238, 180, 34),
    "goldenrod3": (205, 155, 29),
    "goldenrod4": (139, 105, 20),
    "gray": (190, 190, 190),
    "gray0": (0, 0, 0),
    "gray1": (3, 3, 3),
    "gray2": (5, 5, 5),
    "gray3": (8, 8, 8),
    "gray4": (10, 10, 10),
    "gray5": (13, 13, 13),
    "gray6": (15, 15, 15),
    "gray7": (18, 18, 18),
    "gray8": (20, 20, 20),
    "gray9": (23, 23, 23),
    "gray10": (26, 26, 26),
    "gray11": (28, 28, 28),
    "gray12": (31, 31, 31),
    "gray13": (33, 33, 33),
    "gray14": (36, 36, 36),
    "gray15": (38, 38, 38),
    "gray16": (41, 41, 41),
    "gray17": (43, 43, 43),
    "gray18": (46, 46, 46),
    "gray19": (48, 48, 48),
    "gray20": (51, 51, 51),
    "gray21": (54, 54, 54),
    "gray22": (56, 56, 56),
    "gray23": (59, 59, 59),
    "gray24": (61, 61, 61),
    "gray25": (64, 64, 64),
    "gray26": (66, 66, 66),
    "gray27": (69, 69, 69),
    "gray28": (71, 71, 71),
    "gray29": (74, 74, 74),
    "gray30": (77, 77, 77),
    "gray31": (79, 79, 79),
    "gray32": (82, 82, 82),
    "gray33": (84, 84, 84),
    "gray34": (87, 87, 87),
    "gray35": (89, 89, 89),
    "gray36": (92, 92, 92),
    "gray37": (94, 94, 94),
    "gray38": (97, 97, 97),
    "gray39": (99, 99, 99),
    "gray40": (102, 102, 102),
    "gray41": (105, 105, 105),
    "gray42": (107, 107, 107),
    "gray43": (110, 110, 110),
    "gray44": (112, 112, 112),
    "gray45": (115, 115, 115),
    "gray46": (117, 117, 117),
    "gray47": (120, 120, 120),
    "gray48": (122, 122, 122),
    "gray49": (125, 125, 125),
    "gray50": (127, 127, 127),
    "gray51": (130, 130, 130),
    "gray52": (133, 133, 133),
    "gray53": (135, 135, 135),
    "gray54": (138, 138, 138),
    "gray55": (140, 140, 140),
    "gray56": (143, 143, 143),
    "gray57": (145, 145, 145),
    "gray58": (148, 148, 148),
    "gray59": (150, 150, 150),
    "gray60": (153, 153, 153),
    "gray61": (156, 156, 156),
    "gray62": (158, 158, 158),
    "gray63": (161, 161, 161),
    "gray64": (163, 163, 163),
    "gray65": (166, 166, 166),
    "gray66": (168, 168, 168),
    "gray67": (171, 171, 171),
    "gray68": (173, 173, 173),
    "gray69": (176, 176, 176),
    "gray70": (179, 179, 179),
    "gray71": (181, 181, 181),
    "gray72": (184, 184, 184),
    "gray73": (186, 186, 186),
    "gray74": (189, 189, 189),
    "gray75": (191, 191, 191),
    "gray76": (194, 194, 194),
    "gray77": (196, 196, 196),
    "gray78": (199, 199, 199),
    "gray79": (201, 201, 201),
    "gray80": (204, 204, 204),
    "gray81": (207, 207, 207),
    "gray82": (209, 209, 209),
    "gray83": (212, 212, 212),
    "gray84": (214, 214, 214),
    "gray85": (217, 217, 217),
    "gray86": (219, 219, 219),
    "gray87": (222, 222, 222),
    "gray88": (224, 224, 224),
    "gray89": (227, 227, 227),
    "gray90": (229, 229, 229),
    "gray91": (232, 232, 232),
    "gray92": (235, 235, 235),
    "gray93": (237, 237, 237),
    "gray94": (240, 240, 240),
    "gray95": (242, 242, 242),
    "gray96": (245, 245, 245),
    "gray97": (247, 247, 247),
    "gray98": (250, 250, 250),
    "gray99": (252, 252, 252),
    "gray100": (255, 255, 255),
    "green": (0, 255, 0),
    "green1": (0, 255, 0),
    "green2": (0, 238, 0),
    "green3": (0, 205, 0),
    "green4": (0, 139, 0),
    "greenyellow": (173, 255, 47),
    "grey": (190, 190, 190),
    "grey0": (0, 0, 0),
    "grey1": (3, 3, 3),
    "grey2": (5, 5, 5),
    "grey3": (8, 8, 8),
    "grey4": (10, 10, 10),
    "grey5": (13, 13, 13),
    "grey6": (15, 15, 15),
    "grey7": (18, 18, 18),
    "grey8": (20, 20, 20),
    "grey9": (23, 23, 23),
    "grey10": (26, 26, 26),
    "grey11": (28, 28, 28),
    "grey12": (31, 31, 31),
    "grey13": (33, 33, 33),
    "grey14": (36, 36, 36),
    "grey15": (38, 38, 38),
    "grey16": (41, 41, 41),
    "grey17": (43, 43, 43),
    "grey18": (46, 46, 46),
    "grey19": (48, 48, 48),
    "grey20": (51, 51, 51),
    "grey21": (54, 54, 54),
    "grey22": (56, 56, 56),
    "grey23": (59, 59, 59),
    "grey24": (61, 61, 61),
    "grey25": (64, 64, 64),
    "grey26": (66, 66, 66),
    "grey27": (69, 69, 69),
    "grey28": (71, 71, 71),
    "grey29": (74, 74, 74),
    "grey30": (77, 77, 77),
    "grey31": (79, 79, 79),
    "grey32": (82, 82, 82),
    "grey33": (84, 84, 84),
    "grey34": (87, 87, 87),
    "grey35": (89, 89, 89),
    "grey36": (92, 92, 92),
    "grey37": (94, 94, 94),
    "grey38": (97, 97, 97),
    "grey39": (99, 99, 99),
    "grey40": (102, 102, 102),
    "grey41": (105, 105, 105),
    "grey42": (107, 107, 107),
    "grey43": (110, 110, 110),
    "grey44": (112, 112, 112),
    "grey45": (115, 115, 115),
    "grey46": (117, 117, 117),
    "grey47": (120, 120, 120),
    "grey48": (122, 122, 122),
    "grey49": (125, 125, 125),
    "grey50": (127, 127, 127),
    "grey51": (130, 130, 130),
    "grey52": (133, 133, 133),
    "grey53": (135, 135, 135),
    "grey54": (138, 138, 138),
    "grey55": (140, 140, 140),
    "grey56": (143, 143, 143),
    "grey57": (145, 145, 145),
    "grey58": (148, 148, 148),
    "grey59": (150, 150, 150),
    "grey60": (153, 153, 153),
    "grey61": (156, 156, 156),
    "grey62": (158, 158, 158),
    "grey63": (161, 161, 161),
    "grey64": (163, 163, 163),
    "grey65": (166, 166, 166),
    "grey66": (168, 168, 168),
    "grey67": (171, 171, 171),
    "grey68": (173, 173, 173),
    "grey69": (176, 176, 176),
    "grey70": (179, 179, 179),
    "grey71": (181, 181, 181),
    "grey72": (184, 184, 184),
    "grey73": (186, 186, 186),
    "grey74": (189, 189, 189),
    "grey75": (191, 191, 191),
    "grey76": (194, 194, 194),
    "grey77": (196, 196, 196),
    "grey78": (199, 199, 199),
    "grey79": (201, 201, 201),
    "grey80": (204, 204, 204),
    "grey81": (207, 207, 207),
    "grey82": (209, 209, 209),
    "grey83": (212, 212, 212),
    "grey84": (214, 214, 214),
    "grey85": (217, 217, 217),
    "grey86": (219, 219, 219),
    "grey87": (222, 222, 222),
    "grey88": (224, 224, 224),
    "grey89": (227, 227, 227),
    "grey90": (229, 229, 229),
    "grey91": (232, 232, 232),
    "grey92": (235, 235, 235),
    "grey93": (237, 237, 237),
    "grey94": (240, 240, 240),
    "grey95": (242, 242, 242),
    "grey96": (245, 245, 245),
    "grey97": (247, 247, 247),
    "grey98": (250, 250, 250),
    "grey99": (252, 252, 252),
    "grey100": (255, 255, 255),
    "honeydew": (240, 255, 240),
    "honeydew1": (240, 255, 240),
    "honeydew2": (224, 238, 224),
    "honeydew3": (193, 205, 193),
    "honeydew4": (131, 139, 131),
    "hotpink": (255, 105, 180),
    "hotpink1": (255, 110, 180),
    "hotpink2": (238, 106, 167),
    "hotpink3": (205, 96, 144),
    "hotpink4": (139, 58, 98),
    "indianred": (205, 92, 92),
    "indianred1": (255, 106, 106),
    "indianred2": (238, 99, 99),
    "indianred3": (205, 85, 85),
    "indianred4": (139, 58, 58),
    "ivory": (255, 255, 240),
    "ivory1": (255, 255, 240),
    "ivory2": (238, 238, 224),
    "ivory3": (205, 205, 193),
    "ivory4": (139, 139, 131),
    "khaki": (240, 230, 140),
    "khaki1": (255, 246, 143),
    "khaki2": (238, 230, 133),
    "khaki3": (205, 198, 115),
    "khaki4": (139, 134, 78),
    "lavender": (230, 230, 250),
    "lavenderblush": (255, 240, 245),
    "lavenderblush1": (255, 240, 245),
    "lavenderblush2": (238, 224, 229),
    "lavenderblush3": (205, 193, 197),
    "lavenderblush4": (139, 131, 134),
    "lawngreen": (124, 252, 0),
    "lemonchiffon": (255, 250, 205),
    "lemonchiffon1": (255, 250, 205),
    "lemonchiffon2": (238, 233, 191),
    "lemonchiffon3": (205, 201, 165),
    "lemonchiffon4": (139, 137, 112),
    "lightblue": (173, 216, 230),
    "lightblue1": (191, 239, 255),
    "lightblue2": (178, 223, 238),
    "lightblue3": (154, 192, 205),
    "lightblue4": (104, 131, 139),
    "lightcoral": (240, 128, 128),
    "lightcyan": (224, 255, 255),
    "lightcyan1": (224, 255, 255),
    "lightcyan2": (209, 238, 238),
    "lightcyan3": (180, 205, 205),
    "lightcyan4": (122, 139, 139),
    "lightgoldenrod": (238, 221, 130),
    "lightgoldenrod1": (255, 236, 139),
    "lightgoldenrod2": (238, 220, 130),
    "lightgoldenrod3": (205, 190, 112),
    "lightgoldenrod4": (139, 129, 76),
    "lightgoldenrodyellow": (250, 250, 210),
    "lightgray": (211, 211, 211),
    "lightgreen": (144, 238, 144),
    "lightgrey": (211, 211, 211),
    "lightpink": (255, 182, 193),
    "lightpink1": (255, 174, 185),
    "lightpink2": (238, 162, 173),
    "lightpink3": (205, 140, 149),
    "lightpink4": (139, 95, 101),
    "lightsalmon": (255, 160, 122),
    "lightsalmon1": (255, 160, 122),
    "lightsalmon2": (238, 149, 114),
    "lightsalmon3": (205, 129, 98),
    "lightsalmon4": (139, 87, 66),
    "lightseagreen": (32, 178, 170),
    "lightskyblue": (135, 206, 250),
    "lightskyblue1": (176, 226, 255),
    "lightskyblue2": (164, 211, 238),
    "lightskyblue3": (141, 182, 205),
    "lightskyblue4": (96, 123, 139),
    "lightslateblue": (132, 112, 255),
    "lightslategray": (119, 136, 153),
    "lightslategrey": (119, 136, 153),
    "lightsteelblue": (176, 196, 222),
    "lightsteelblue1": (202, 225, 255),
    "lightsteelblue2": (188, 210, 238),
    "lightsteelblue3": (162, 181, 205),
    "lightsteelblue4": (110, 123, 139),
    "lightyellow": (255, 255, 224),
    "lightyellow1": (255, 255, 224),
    "lightyellow2": (238, 238, 209),
    "lightyellow3": (205, 205, 180),
    "lightyellow4": (139, 139, 122),
    "limegreen": (50, 205, 50),
    "linen": (250, 240, 230),
    "magenta": (255, 0, 255),
    "magenta1": (255, 0, 255),
    "magenta2": (238, 0, 238),
    "magenta3": (205, 0, 205),
    "magenta4": (139, 0, 139),
    "maroon": (176, 48, 96),
    "maroon1": (255, 52, 179),
    "maroon2": (238, 48, 167),
    "maroon3": (205, 41, 144),
    "maroon4": (139, 28, 98),
    "mediumaquamarine": (102, 205, 170),
    "mediumblue": (0, 0, 205),
    "mediumorchid": (186, 85, 211),
    "mediumorchid1": (224, 102, 255),
    "mediumorchid2": (209, 95, 238),
    "mediumorchid3": (180, 82, 205),
    "mediumorchid4": (122, 55, 139),
    "mediumpurple": (147, 112, 219),
    "mediumpurple1": (171, 130, 255),
    "mediumpurple2": (159, 121, 238),
    "mediumpurple3": (137, 104, 205),
    "mediumpurple4": (93, 71, 139),
    "mediumseagreen": (60, 179, 113),
    "mediumslateblue": (123, 104, 238),
    "mediumspringgreen": (0, 250, 154),
    "mediumturquoise": (72, 209, 204),
    "mediumvioletred": (199, 21, 133),
    "midnightblue": (25, 25, 112),
    "mintcream": (245, 255, 250),
    "mistyrose": (255, 228, 225),
    "mistyrose1": (255, 228, 225),
    "mistyrose2": (238, 213, 210),
    "mistyrose3": (205, 183, 181),
    "mistyrose4": (139, 125, 123),
    "moccasin": (255, 228, 181),
    "navajowhite": (255, 222, 173),
    "navajowhite1": (255, 222, 173),
    "navajowhite2": (238, 207, 161),
    "navajowhite3": (205, 179, 139),
    "navajowhite4": (139, 121, 94),
    "navy": (0, 0, 128),
    "navyblue": (0, 0, 128),
    "oldlace": (253, 245, 230),
    "olivedrab": (107, 142, 35),
    "olivedrab1": (192, 255, 62),
    "olivedrab2": (179, 238, 58),
    "olivedrab3": (154, 205, 50),
    "olivedrab4": (105, 139, 34),
    "orange": (255, 165, 0),
    "orange1": (255, 165, 0),
    "orange2": (238, 154, 0),
    "orange3": (205, 133, 0),
    "orange4": (139, 90, 0),
    "orangered": (255, 69, 0),
    "orangered1": (255, 69, 0),
    "orangered2": (238, 64, 0),
    "orangered3": (205, 55, 0),
    "orangered4": (139, 37, 0),
    "orchid": (218, 112, 214),
    "orchid1": (255, 131, 250),
    "orchid2": (238, 122, 233),
    "orchid3": (205, 105, 201),
    "orchid4": (139, 71, 137),
    "palegoldenrod": (238, 232, 170),
    "palegreen": (152, 251, 152),
    "palegreen1": (154, 255, 154),
    "palegreen2": (144, 238, 144),
    "palegreen3": (124, 205, 124),
    "palegreen4": (84, 139, 84),
    "paleturquoise": (175, 238, 238),
    "paleturquoise1": (187, 255, 255),
    "paleturquoise2": (174, 238, 238),
    "paleturquoise3": (150, 205, 205),
    "paleturquoise4": (102, 139, 139),
    "palevioletred": (219, 112, 147),
    "palevioletred1": (255, 130, 171),
    "palevioletred2": (238, 121, 159),
    "palevioletred3": (205, 104, 127),
    "palevioletred4": (139, 71, 93),
    "papayawhip": (255, 239, 213),
    "peachpuff": (255, 218, 185),
    "peachpuff1": (255, 218, 185),
    "peachpuff2": (238, 203, 173),
    "peachpuff3": (205, 175, 149),
    "peachpuff4": (139, 119, 101),
    "peru": (205, 133, 63),
    "pink": (255, 192, 203),
    "pink1": (255, 181, 197),
    "pink2": (238, 169, 184),
    "pink3": (205, 145, 158),
    "pink4": (139, 99, 108),
    "plum": (221, 160, 221),
    "plum1": (255, 187, 255),
    "plum2": (238, 174, 238),
    "plum3": (205, 150, 205),
    "plum4": (139, 102, 139),
    "powderblue": (176, 224, 230),
    "purple": (160, 32, 240),
    "purple1": (155, 48, 255),
    "purple2": (145, 44, 238),
    "purple3": (125, 38, 205),
    "purple4": (85, 26, 139),
    "red": (255, 0, 0),
    "red1": (255, 0, 0),
    "red2": (238, 0, 0),
    "red3": (205, 0, 0),
    "red4": (139, 0, 0),
    "rosybrown": (188, 143, 143),
    "rosybrown1": (255, 193, 193),
    "rosybrown2": (238, 180, 180),
    "rosybrown3": (205, 155, 155),
    "rosybrown4": (139, 105, 105),
    "royalblue": (65, 105, 225),
    "royalblue1": (72, 118, 255),
    "royalblue2": (67, 110, 238),
    "royalblue3": (58, 95, 205),
    "royalblue4": (39, 64, 139),
    "saddlebrown": (139, 69, 19),
    "salmon": (250, 128, 114),
    "salmon1": (255, 140, 105),
    "salmon2": (238, 130, 98),
    "salmon3": (205, 112, 84),
    "salmon4": (139, 76, 57),
    "sandybrown": (244, 164, 96),
    "seagreen": (46, 139, 87),
    "seagreen1": (84, 255, 159),
    "seagreen2": (78, 238, 148),
    "seagreen3": (67, 205, 128),
    "seagreen4": (46, 139, 87),
    "seashell": (255, 245, 238),
    "seashell1": (255, 245, 238),
    "seashell2": (238, 229, 222),
    "seashell3": (205, 197, 191),
    "seashell4": (139, 134, 130),
    "sienna": (160, 82, 45),
    "sienna1": (255, 130, 71),
    "sienna2": (238, 121, 66),
    "sienna3": (205, 104, 57),
    "sienna4": (139, 71, 38),
    "skyblue": (135, 206, 235),
    "skyblue1": (135, 206, 255),
    "skyblue2": (126, 192, 238),
    "skyblue3": (108, 166, 205),
    "skyblue4": (74, 112, 139),
    "slateblue": (106, 90, 205),
    "slateblue1": (131, 111, 255),
    "slateblue2": (122, 103, 238),
    "slateblue3": (105, 89, 205),
    "slateblue4": (71, 60, 139),
    "slategray": (112, 128, 144),
    "slategray1": (198, 226, 255),
    "slategray2": (185, 211, 238),
    "slategray3": (159, 182, 205),
    "slategray4": (108, 123, 139),
    "slategrey": (112, 128, 144),
    "snow": (255, 250, 250),
    "snow1": (255, 250, 250),
    "snow2": (238, 233, 233),
    "snow3": (205, 201, 201),
    "snow4": (139, 137, 137),
    "springgreen": (0, 255, 127),
    "springgreen1": (0, 255, 127),
    "springgreen2": (0, 238, 118),
    "springgreen3": (0, 205, 102),
    "springgreen4": (0, 139, 69),
    "steelblue": (70, 130, 180),
    "steelblue1": (99, 184, 255),
    "steelblue2": (92, 172, 238),
    "steelblue3": (79, 148, 205),
    "steelblue4": (54, 100, 139),
    "tan": (210, 180, 140),
    "tan1": (255, 165, 79),
    "tan2": (238, 154, 73),
    "tan3": (205, 133, 63),
    "tan4": (139, 90, 43),
    "thistle": (216, 191, 216),
    "thistle1": (255, 225, 255),
    "thistle2": (238, 210, 238),
    "thistle3": (205, 181, 205),
    "thistle4": (139, 123, 139),
    "tomato": (255, 99, 71),
    "tomato12": (55, 99, 71),
    "tomato2": (238, 92, 66),
    "tomato3": (205, 79, 57),
    "tomato4": (139, 54, 38),
    "turquoise": (64, 224, 208),
    "turquoise1": (0, 245, 255),
    "turquoise2": (0, 229, 238),
    "turquoise3": (0, 197, 205),
    "turquoise4": (0, 134, 139),
    "violet": (238, 130, 238),
    "violetred": (208, 32, 144),
    "violetred1": (255, 62, 150),
    "violetred2": (238, 58, 140),
    "violetred3": (205, 50, 120),
    "violetred4": (139, 34, 82),
    "wheat": (245, 222, 179),
    "wheat1": (255, 231, 186),
    "wheat2": (238, 216, 174),
    "wheat3": (205, 186, 150),
    "wheat4": (139, 126, 102),
    "white": (255, 255, 255),
    "whitesmoke": (245, 245, 245),
    "yellow": (255, 255, 0),
    "yellow1": (255, 255, 0),
    "yellow2": (238, 238, 0),
    "yellow3": (205, 205, 0),
    "yellow4": (139, 139, 0),
    "yellowgreen": (154, 205, 50),
}
colorCode   = {}
colorUnCode = {}
colorNames  = colorMap.keys()
colorNames.sort()
code = 1
for n in colorNames:
    colorCode[n] = code
    colorUnCode[code] = colorMap[n]
    code += 1

## Support functions

def sgn(v):
    if v >= 0: return +1
    else:      return -1

class Simulator:
    def __init__(self, (width, height), (offset_x, offset_y), scale, run=1):
        self.robots = []
        self.robotsByName = {}
        self.lights = []
        self.trail = []
        self.needToMove = [] # list of robots that need to move (see step)
        self.maxTrailSize = 10 # 5 * 60 * 10 # 5 minutes (one timeslice = 1/10 sec)
        self.trailStart = 0
        self.world = []
        self.time = 0.0
        self.timeslice = 100 # in milliseconds
        self.scale = scale
        self.offset_x = offset_x
        self.offset_y = offset_y
        self._width, self._height = width, height
        self.lightAboveWalls = 0
        # connections to pyrobot:
        self.ports = []
        self.assoc = {}
        self.done = 0
        self.quit = 0
        self.properties = ["stall", "x", "y", "th", "thr", "energy"]
        self.supportedFeatures = ["range-sensor", "continuous-movement", "odometry"]
        self.stepCount = 0
        self.display = {"wireframe": 0}
        self.running = 0
        self.stop = 0 # use to stop the sim
    def resetPaths(self): pass
    def resetPath(self, pos): pass
    def update_idletasks(self): pass
    def mainloop(self):
        """ Simulates what TkSimulator does. """
        self.running = 1
        while not self.done:
            self.step()
            time.sleep(self.timeslice/1000.0) # to run in real time
        self.running = 0
    def destroy(self):
        self.done = 1 # stop processing requests, if handling
        self.quit = 1 # stop accept/bind toplevel
    def __getitem__(self, name):
        if name in self.robotsByName:
            return self.robotsByName[name]
        else:
            return None
    def remove(self, thing):
        pass
    def update(self):
        pass

    def addWall(self, x1, y1, x2, y2, color="black"):
        seg = Segment((x1, y1), (x2, y2), len(self.world) + 1, "wall")
        seg.color = color
        seg.type = "wall"
        self.world.append(seg)

    def addShape(self, name, *args, **nargs):
        # addShape("box", x, y, x, y, color)
        # addShape("polygon", points, fill = "black", outline = "purple")
        # addshape("line", (x1, y1), (x2, y2), fill = "purple", width?)
        # addshape("oval", (x1, y1), (x2, y2), fill = "purple", outline="yellow")
        if len(nargs) == 0:
            temp = list(args)
            temp.insert(0, name)
            self.shapes.append(temp)
        else:
            self.shapes.append( (name, args, nargs) )
        self.redraw()

    def addBox(self, ulx, uly, lrx, lry, color="white", wallcolor="black"):
        self.addWall( ulx, uly, ulx, lry, wallcolor)
        self.addWall( ulx, uly, lrx, uly, wallcolor)
        self.addWall( ulx, lry, lrx, lry, wallcolor)
        self.addWall( lrx, uly, lrx, lry, wallcolor)

    def addLight(self, x, y, brightness, color="yellow"):
        self.lights.append(Light(x, y, brightness, color))
        self.redraw()

    def refillLights(self, brightness):
        """
        Set all the lights to the given brightness.
        """
        for light in self.lights:
            if light.type != "fixed": continue
            light.brightness = brightness
        self.redraw()

    def resetLights(self, brightness, width, height):
        """
        Randomly relocate all lights in the environment within the
        bounding box defined by the given width and height.  Make sure
        that they are not too close to the edge of the bounding box.
        """
        for light in self.lights:
            if light.type != "fixed": continue
            light.x = 0.5 + random.random() * (width-1)
            light.y = 0.5 + random.random() * (height-1)
            light.brightness = brightness
        self.redraw()

    def resetLightPositions(self, coords):
        """
        Relocate lights in the environment to the given list of 
        coordinates.
        """
        for i in range(len(self.lights)):
            light = self.lights[i]
            if light.type != "fixed": continue
            light.x = coords[i][0]
            light.y = coords[i][1]
        self.redraw()

    def redraw(self): pass

    def addRobot(self, port, r):
        self.robots.append(r)
        self.robotsByName[r.name] = r
        self.trail.append([None] * self.maxTrailSize)
        r.simulator = self
        r._xya = r._gx, r._gy, r._ga # save original position for later reset
        r._port = port
        if port != None:
            self.assoc[port] = r
            self.ports.append(port)

    def scale_x(self, x): return self.offset_x + (x * self.scale)
    def scale_y(self, y): return self.offset_y - (y * self.scale)

    def addTrail(self, pos, index, robot):
        self.trail[pos][index] = robot._gx, robot._gy, robot._ga
        
    def step(self, run = 1):
        """
        Advance the world by timeslice milliseconds.
        """
        # might want to randomize this order so the same ones
        # don't always move first:
        self.needToMove = []
        self.time += (self.timeslice / 1000.0)
        i = 0
        for r in self.robots:
            r.ovx, r.ovy, r.ova = r.vx, r.vy, r.va
            resetVelocities = 0
            if r.stall:
                resetVelocities = 1
                ovx, r.ovx = r.ovx, r.ovx/5.0
                ovy, r.ovy = r.ovy, r.ovy/5.0
                ova, r.ova = r.ova, r.ova/5.0
            r.step(self.timeslice)
            if r.type != "puck" and resetVelocities:
                r.vx = ovx
                r.vy = ovy
                r.va = ova
            self.addTrail(i, self.stepCount % self.maxTrailSize, r)
            i += 1
        for r in self.needToMove:
            r.step(self.timeslice, movePucks = 0)
        if self.stepCount > self.maxTrailSize:
            self.trailStart = ((self.stepCount + 1) % self.maxTrailSize)
        self.stepCount += 1
    def drawLine(self, x1, y1, x2, y2, fill, tag, **args):
        pass
    def drawOval(self, x1, y1, x2, y2, **args):
        pass
    def castRay(self, robot, x1, y1, a, maxRange = MAXRAYLENGTH,
                ignoreRobot = "self",
                rayType = "range"):
        # ignoreRobot: all, self, other; 
        hits = []
        x2, y2 = math.sin(a) * maxRange + x1, math.cos(a) * maxRange + y1
        seg = Segment((x1, y1), (x2, y2))
        # go down list of walls, and see if it hit anything:
        # check if it is not a light ray, or if it is, and not above walls:
        if (rayType != "light") or (rayType == "light" and not self.lightAboveWalls):
            for w in self.world:
                retval = w.intersects(seg)
                if retval:
                    dist = Segment(retval, (x1, y1)).length()
                    if dist <= maxRange:
                        hits.append( (dist, retval, w) ) # distance, hit, obj
        # go down list of robots, and see if you hit one:
        if ignoreRobot != "all":
            for r in self.robots:
                # don't hit your own bounding box if ignoreRobot == "self":
                if r.name == robot.name and ignoreRobot == "self": continue
                # don't hit other's bounding box if ignoreRobot == "other":
                if r.name != robot.name and ignoreRobot == "other": continue
                a90 = r._ga + PIOVER2
                cos_a90 = math.cos(a90)
                sin_a90 = math.sin(a90)
                segments = []
                if r.boundingBox != []:
                    xys = map(lambda x, y: (r._gx + x * cos_a90 - y * sin_a90,
                                            r._gy + x * sin_a90 + y * cos_a90),
                              r.boundingBox[0], r.boundingBox[1])
                    # for each of the bounding box segments:
                    for i in range(len(xys)):
                        w = Segment( xys[i], xys[i - 1]) # using the previous one completes the polygon
                        w.color = r.color
                        w.type = r.type
                        w.robot = r
                        segments.append(w)
                if r.boundingSeg != []:
                    # bounding segments
                    xys = map(lambda x, y: (r._gx + x * cos_a90 - y * sin_a90,
                                            r._gy + x * sin_a90 + y * cos_a90),
                              r.boundingSeg[0], r.boundingSeg[1])
                    # for each of the bounding segments:
                    for i in range(0, len(xys), 2):
                        w = Segment( xys[i], xys[i + 1]) # assume that they come in pairs
                        w.color = r.color
                        w.type = r.type
                        w.robot = r
                        segments.append(w)
                for s in r.additionalSegments(r._gx, r._gy, cos_a90, sin_a90,
                                              color = r.color, type = r.type, robot = r):
                    segments.append(s)
                for w in segments:
                    retval = w.intersects(seg)
                    if retval:
                        dist = Segment(retval, (x1, y1)).length()
                        if dist <= maxRange:
                            hits.append( (dist, retval, w) ) # distance,hit,obj
        if len(hits) == 0:
            return (None, None, None)
        else:
            return min(hits)

    def process(self, request, sockname, pickleIt = 1):
        """
        Process does all of the work.
        request  - a string message
        sockname - (IPNUMBER (str), SOCKETNUM (int)) from client
        """
        retval = 'error'
        if request == 'reset':
            self.reset()
            retval = "ok"
        elif request.count('connectionNum'):
            connectionNum, port = request.split(":")
            retval = self.ports.index( int(port) )
        elif request == 'end' or request == 'exit':
            retval = "ok"
            self.done = 1
        elif request == 'quit':
            retval = "ok"
            self.done = 1
            self.quit = 1
        elif request == "disconnect":
            retval = "ok"
        elif request == 'properties':
            retval = self.properties
        elif request == 'supportedFeatures':
            retval = self.supportedFeatures
        elif request == 'builtinDevices':
            retval = self.assoc[sockname[1]].builtinDevices
        elif request == 'forward':
            self.assoc[sockname[1]].move(0.3, 0.0)
            retval = "ok"
        elif request == 'left':
            self.assoc[sockname[1]].move(0.0, 0.3)
            retval = "ok"
        elif request == 'right':
            self.assoc[sockname[1]].move(0.0, -0.3)
            retval = "ok"
        elif request == 'back':
            self.assoc[sockname[1]].move(-0.3, 0.0)
            retval = "ok"
        elif request == 'name':
            retval = self.assoc[sockname[1]].name
        elif request == 'x':
            retval = self.assoc[sockname[1]].x
        elif request == 'energy':
            retval = self.assoc[sockname[1]].energy
        elif request == 'y':
            retval = self.assoc[sockname[1]].y
        elif request == 'stall':
            retval = self.assoc[sockname[1]].stall
        elif request == 'radius':
            retval = self.assoc[sockname[1]].radius
        elif request == 'thr':
            retval = self.assoc[sockname[1]].a
        elif request == 'th':
            retval = self.assoc[sockname[1]].a / PIOVER180
        elif len(request) > 1 and request[0] == '!': # eval
            try:
                retval = str(eval(request[1:]))
            except Exception, msg:
                try:
                    exec request[1:]
                    retval = "ok"
                except:
                    retval = "error: %s" % msg
        else:
            # assume a package
            message = request.split("_")
            if message[0] == "m": # "m_t_r" move:translate:rotate
                t, r = 0, 0
                try: t, r = float(message[1]), float(message[2])
                except: pass
                retval = self.assoc[sockname[1]].move(t, r)
            elif message[0] == "l": # "l_string" say text
                el, strng = None, None
                try:
                    el, strng = message
                except: pass
                strng = strng.replace("~-", "_")
                self.assoc[sockname[1]].say(strng)
                self.redraw()
                retval = "ok"
            elif message[0] == "a": # "a_name_x_y_th" simulation placement
                simulation, name, x, y, thr = None, None, None, None, None
                try:
                    simulation, name, x, y, thr = message
                    x = float(x)
                    y = float(y)
                    thr = float(thr)
                except: pass
                if name in self.robotsByName:
                    r = self.robotsByName[name]
                    r.setPose(x, y, thr, 1)#handofgod
                    r.localize(0, 0, 0)
                    return "ok"
                elif name.isdigit():
                    pos = int(name)
                    r = self.robots[pos]
                    r.setPose(x, y, thr, 1)#handofgod
                    r.localize(0, 0, 0)
                    return "ok"
                return "error: no such robot position '%s'" % name
            elif message[0] == "b": # "b_x_y_th" localize
                localization, x, y, thr = None, None, None, None
                try:
                    localization, x, y, thr = message
                    x = float(x)
                    y = float(y)
                    thr = float(thr)
                except: pass
                retval = self.assoc[sockname[1]].localize(x, y, thr)
            elif message[0] == "c": # "c_name" getpose
                simulation, name = None, None
                try:
                    simulation, name = message
                except: pass
                if name in self.robotsByName:
                    r = self.robotsByName[name]
                    retval = (r._gx, r._gy, r._ga)
                elif name.isdigit():
                    pos = int(name)
                    r = self.robots[pos]
                    retval = (r._gx, r._gy, r._ga)
            elif message[0] == "f": # "f_i_v" rgb[i][v]
                index, pos = 0, 0
                try:
                    index, pos = int(message[1]), int(message[2])
                except: pass
                device = self.assoc[sockname[1]].getIndex("light", index)
                if device:
                    retval = device.rgb[pos]
            elif message[0] == "h": # "h_v" bulb:value
                val = None
                try:
                    val = float(message[1])
                except: pass
                self.assoc[sockname[1]].bulb.brightness = val
                self.redraw()
                retval = "ok"
            elif message[0] == "i": # "i_name_index_property_val"
                try:
                    code, dtype, index, property, val = message
                    index = int(index)
                    device = self.assoc[sockname[1]].getIndex(dtype, index)
                    oldval = device.__dict__[property]
                    if type(oldval) == str:
                        device.__dict__[property] = val
                    elif type(oldval) == int:
                        device.__dict__[property] = int(val)
                    elif type(oldval) == float:
                        device.__dict__[property] = float(val)
                    retval = "ok"
                except: pass
            elif message[0] == "j": # "j_index_p_t_z" ptz[index].setPose(p, t, z)
                code, index, p, t, z = [None] * 5
                try:
                    code, index, p, t, z = message
                    index = int(index)
                except: pass
                device = self.assoc[sockname[1]].getIndex("ptz", index)
                if device:
                    if p == "None": p = None
                    else:          p = float(p)
                    if t == "None": t = None
                    else:          t = float(t)
                    if z == "None": z = None
                    else:          z = float(z)
                    retval = device.setPose(p, t, z)
            elif message[0] == "k": # "k_index" ptz[index].getPose()
                try:
                    code, index = message
                    index = int(index)
                except: pass
                device = self.assoc[sockname[1]].getIndex("ptz", index)
                if device:
                    retval = device.getPose()
            elif message[0] == "t": # "t_v" translate:value
                val = 0
                try:
                    val = float(message[1])
                except: pass
                retval = self.assoc[sockname[1]].translate(val)
            elif message[0] == "v": # "v_v" global step scalar:value
                val = 0
                try:
                    val = float(message[1])
                except: pass                
                self.assoc[sockname[1]].stepScalar = val
                retval = "ok"
            elif message[0] == "o": # "o_v" rotate:value
                val = 0
                try:
                    val = float(message[1])
                except: pass
                retval = self.assoc[sockname[1]].rotate(val)
            elif message[0] == "d": # "d_sonar" display:keyword
                val = 0
                try:
                    val = message[1]
                except: pass
                retval = self.assoc[sockname[1]].display[val] = 1
            elif message[0] == "e": # "e_amt" eat:keyword
                val = 0
                if message[1] == "all":
                    val = -1.0 # code for "eat all light; returns 1.0"
                else:
                    try:
                        val = float(message[1])
                    except: pass
                retval = self.assoc[sockname[1]].eat(val)
            elif message[0] == "x": # "x_expression" expression
                try:
                    retval = eval(message[1])
                except: pass
            elif message[0] == "z": # "z_gripper_0_command" command
                dtype, index, command = None, None, None
                try:
                    dtype = message[1]
                    index = int(message[2])
                    command = message[3]
                except: pass
                device = self.assoc[sockname[1]].getIndex(dtype, index)
                if device:
                    retval = device.__class__.__dict__[command](device)
            elif message[0] == "g": # "g_sonar_0" geometry_sensor_id
                index = 0
                for d in self.assoc[sockname[1]].devices:
                    if d.type == message[1]:
                        if int(message[2]) == index:
                            if message[1] in ["sonar", "light", "directional", "bulb", "ir", "bumper"]:
                                retval = d.geometry, d.arc, d.maxRange
                            elif message[1] == "camera":
                                retval = d.width, d.height
                        index += 1
            elif message[0] == "r": # "r_sonar_0" groups_sensor_id
                index = 0
                for d in self.assoc[sockname[1]].devices:
                    if d.type == message[1]:
                        if int(message[2]) == index:
                            if message[1] in ["sonar", "light", "directional", "ir", "bumper"]:
                                retval = d.groups
                        index += 1
            elif message[0] == "s": # "s_sonar_0" subscribe
                if message[1] in self.assoc[sockname[1]].display and self.assoc[sockname[1]].display[message[1]] != -1:
                    self.assoc[sockname[1]].display[message[1]] = 1
                self.properties.append("%s_%s" % (message[1], message[2]))
                self.assoc[sockname[1]].subscribed = 1
                retval = "ok"
            elif message[0] in ["sonar", "light", "directional", 
                                "camera", "gripper", "ir", "bumper"]: # sonar_0, light_0...
                index = 0
                for d in self.assoc[sockname[1]].devices:
                    if d.type == message[0]:
                        try:    i = int(message[1])
                        except: i = -1
                        if i == index:
                            retval = d.scan
                        index += 1
        if pickleIt:
            return pickle.dumps(retval)
        else:
            return retval

class TkSimulator(Tkinter.Toplevel, Simulator):
    def __init__(self, dimensions, offsets, scale, root = None, run = 1):
        if root == None:
            if share and share.gui:
                root = share.gui
            else:
                root = Tkinter.Tk()
                root.withdraw()
        Tkinter.Toplevel.__init__(self, root)
        Simulator.__init__(self, dimensions, offsets, scale)
        self.root = root
        self.tkfont = None
        self.wm_title("Pyrobot Simulator")
        self.protocol('WM_DELETE_WINDOW',self.destroy)
        self.frame = Tkinter.Frame(self)
        self.frame.pack(side = 'bottom', expand = "yes", anchor = "n",
                        fill = 'both')
        self.canvas = Tkinter.Canvas(self.frame, bg="white", width=self._width, height=self._height)
        self.canvas.pack(expand="yes", fill="both", side="top", anchor="n")
        self.addMouseBindings()
        self.mBar = Tkinter.Frame(self, relief=Tkinter.RAISED, borderwidth=2)
        self.mBar.pack(fill=Tkinter.X)
        self.lastEventRobot = None
        self.menuButtons = {}
        menu = [
            ('File', [['Reset', self.reset],
                      ['Display world details', self.printDetails],
                      ['Exit', self.destroy]]),
            ('View',[
            ['wireframe', lambda: self.simToggle("wireframe")],
            ['trail', lambda: self.toggle("trail")],                     
            ['body', lambda: self.toggle("body")],                 
            ['boundingBox', lambda: self.toggle("boundingBox")],
            ['gripper', lambda: self.toggle("gripper")],
            ['camera', lambda: self.toggle("camera")],
            ['sonar', lambda: self.toggle("sonar")],
            ['ir', lambda: self.toggle("ir")],
            ['bumper', lambda: self.toggle("bumper")],
            ['light', lambda: self.toggle("light")],                     
            ['lightBlocked', lambda: self.toggle("lightBlocked")],
            ['speech', lambda: self.toggle("speech")],
            ]
             ),
            ('Options', [['lights visible above walls',
                          lambda: self.toggleOption("lightAboveWalls")]]),
            ]
        for entry in menu:
            self.mBar.tk_menuBar(self.makeMenu(self.mBar, entry[0], entry[1]))
        self.shapes = []
        if run:
            self.running = 1
            self.after(100, self.step)
        else:
            self.running = 0
    def toggleOption(self, key):
        if key == "lightAboveWalls":
            self.lightAboveWalls = not self.lightAboveWalls
        else:
            raise AttributeError, "invalid key: '%s'" % key
        self.redraw()
    def simToggle(self, key):
        self.display[key] = not self.display[key]
        self.redraw()
    def toggle(self, key):
        for r in self.robots:
            if r.subscribed == 0: continue
            if r.display[key] == 1:
                r.display[key] = 0
            else:
                r.display[key] = 1
            r._last_pose = (-1, -1, -1)
        self.redraw()
    def reset(self):
        for r in self.robots:
            r._gx, r._gy, r._ga = r._xya
            r.energy = 10000.0
        for l in self.lights:
            l.x, l.y, l.brightness = l._xyb
        self.redraw()
    def makeMenu(self, bar, name, commands):
        """ Assumes self.menuButtons exists """
        menu = Tkinter.Menubutton(bar,text=name,underline=0)
        self.menuButtons[name] = menu
        menu.pack(side=Tkinter.LEFT,padx="2m")
        menu.filemenu = Tkinter.Menu(menu)
        for cmd in commands:
            if cmd:
                menu.filemenu.add_command(label=cmd[0],command=cmd[1])
            else:
                menu.filemenu.add_separator()
        menu['menu'] = menu.filemenu
        return menu
    def destroy(self):
        if not self.running:
            self.withdraw()
        self.done = 1 # stop processing requests, if handling
        self.quit = 1 # stop accept/bind toplevel
        self.root.quit() # kill the gui
    def dispatch_event(self, event, type):
        if self.lastEventRobot:
            return self.lastEventRobot.mouse_event(event, type, self.lastEventRobot)
        # else let's get a robot
        widget = event.widget
        x = widget.canvasx(event.x)
        y = widget.canvasy(event.y)
        d = 5 # overlap, in canvas units
        items = widget.find_overlapping(x-d, y-d, x+d, y+d)
        for item in items:
            tags = self.canvas.gettags(item)
            for tag in tags:
                if "robot-" in tag:
                    robot = self.robotsByName[tag[6:]]
                    self.lastEventRobot = robot
                    return robot.mouse_event(event, type, robot)
    def addMouseBindings(self):
        self.canvas.bind("<B1-Motion>", func=lambda event=self:self.dispatch_event(event, "motion"))
        self.canvas.bind("<Button-1>",  func=lambda event=self:self.dispatch_event(event, "down"))
        self.canvas.bind("<ButtonRelease-1>", func=lambda event=self:self.dispatch_event(event, "up"))
        self.canvas.bind("<Control-B1-Motion>", func=lambda event=self:self.dispatch_event(event, "control-motion"))
        self.canvas.bind("<Control-Button-1>", func=lambda event=self:self.dispatch_event(event, "control-down"))
        self.canvas.bind("<Control-ButtonRelease-1>", func=lambda event=self:self.dispatch_event(event, "control-up"))
        self.canvas.bind("<ButtonRelease-2>", self.click_b2_up)
        self.canvas.bind("<ButtonRelease-3>", self.click_b3_up)
        self.canvas.bind("<Button-2>", self.click_b2_down)
        self.canvas.bind("<Button-3>", self.click_b3_down)
        self.canvas.bind("<B2-Motion>", self.click_b2_move)
        self.canvas.bind("<B3-Motion>", self.click_b3_move)
    def click_b2_down(self, event):
        self.click_start = event.x, event.y
    def click_b3_down(self, event):
        self.click_start = event.x, event.y
        self.click_b3_move(event)
    def click_b2_up(self, event):
        self.click_stop = event.x, event.y
        if self.click_stop == self.click_start:
            # center on this position:
            center = self.canvas.winfo_width()/2, self.canvas.winfo_height()/2
            x_diff = self.click_start[0] - self.click_stop[0]
            y_diff = self.click_start[1] - self.click_stop[1]
            self.offset_x -= (self.click_stop[0] - center[0])
            self.offset_y -= (self.click_stop[1] - center[1])
        else: # move this much
            x_diff = self.click_start[0] - self.click_stop[0]
            y_diff = self.click_start[1] - self.click_stop[1]
            self.offset_x -= x_diff
            self.offset_y -= y_diff
        self.redraw()
    def click_b3_up(self, event):
        """
        Button handler for B3 for scaling window
        """
        stop = event.x, event.y
        center = self.canvas.winfo_width()/2, self.canvas.winfo_height()/2
        radius_stop = Segment(center, stop).length()
        radius_start = Segment(center, self.click_start).length()
        self.scale *= radius_stop/radius_start
        self.offset_x = (radius_stop/radius_start) * self.offset_x + (1 - (radius_stop/radius_start)) * center[0]
        self.offset_y = (radius_stop/radius_start) * self.offset_y + (1 - (radius_stop/radius_start)) * center[1]
        self.redraw()
    def click_b2_move(self, event):
        self.remove('arrow')
        self.click_stop = event.x, event.y
        x1, y1 = self.click_start
        x2, y2 = self.click_stop
        self.canvas.create_line(x1, y1, x2, y2, tag="arrow", fill="purple")
    def click_b3_move(self, event):
        self.remove('arrow')
        stop = event.x, event.y
        center = self.canvas.winfo_width()/2, self.canvas.winfo_height()/2
        radius = Segment(center, stop).length()
        self.canvas.create_oval(center[0] - radius, center[1] - radius,
                                center[0] + radius, center[1] + radius,
                                tag="arrow", outline="purple")
    def resetPath(self, num):
        for point in range(len(self.trail[num])):
            self.trail[num][point] = None
    def resetPaths(self):
        for t in range(len(self.trail)):
            self.resetPath(t)
    def redraw(self):
        self.remove('all')
        for shape in self.shapes:
            if shape[0] == "box":
                name, ulx, uly, lrx, lry, fill = shape
                outline = "black"
                if self.display["wireframe"]:
                    if fill != "white":
                        outline = fill
                    else:
                        outline = "black"
                    fill = ""
                self.canvas.create_rectangle(self.scale_x(ulx), self.scale_y(uly),
                                             self.scale_x(lrx), self.scale_y(lry),
                                             tag="line", fill=fill, outline=outline)
            elif shape[0] == "polygon":
                name, points, nargs = shape
                xys = [(self.scale_x(x), self.scale_y(y)) for (x, y) in points]
                self.canvas.create_polygon(xys, tag="line", **nargs)
            elif shape[0] == "line":
                name, ((x1, y1), (x2, y2)), nargs = shape
                x1, y1, x2, y2 = self.scale_x(x1), self.scale_y(y1), self.scale_x(x2), self.scale_y(y2)
                self.canvas.create_line(x1, y1, x2, y2, tag="line", **nargs)
            elif shape[0] == "oval":
                name, ((x1, y1), (x2, y2)), nargs = shape
                x1, y1, x2, y2 = self.scale_x(x1), self.scale_y(y1), self.scale_x(x2), self.scale_y(y2)
                self.canvas.create_oval(x1, y1, x2, y2, tag="line", **nargs)
        if not self.display["wireframe"]:
            for segment in self.world:
                (x1, y1), (x2, y2) = segment.start, segment.end
                id = self.drawLine(x1, y1, x2, y2, fill="black", tag="line")
                segment.id = id
        for light in self.lights:
            if light.type != "fixed": continue 
            x, y, brightness, color = light.x, light.y, light.brightness, light.color
            self.drawOval((x - brightness), (y - brightness),
                          (x + brightness), (y + brightness),
                          tag="line", fill=color, outline="orange")
        i = 0
        for path in self.trail:
            if self.robots[i].subscribed and self.robots[i].display["trail"] == 1:
                if path[self.trailStart] != None:
                    lastX, lastY, lastA = path[self.trailStart]
                    #lastX, lastY = self.scale_x(lastX), self.scale_y(lastY)
                    color = self.robots[i].colorParts["trail"]
                    for p in range(self.trailStart, self.trailStart + self.maxTrailSize):
                        xya = path[p % self.maxTrailSize]
                        if xya == None: break
                        x, y = xya[0], xya[1]
                        self.drawLine(lastX, lastY, x, y, fill=color, tag="trail")
                        lastX, lastY = x, y
            i += 1
        for robot in self.robots:
            robot._last_pose = (-1, -1, -1)
        if not self.running:
            self.step(run=0)
    def printDetails(self):
        print "Window: size=(%d,%d), offset=(%d,%d), scale=%f" % (self.winfo_width(), self.winfo_height(), self.offset_x, self.offset_y, self.scale)
        for robot in self.robots:
            print "   %s: pose = (%.2f, %.2f, %.2f)" % (robot.name, robot._gx, robot._gy, robot._ga % (2 * math.pi))
        
    def addBox(self, ulx, uly, lrx, lry, color="white", wallcolor="black"):
        Simulator.addBox(self, ulx, uly, lrx, lry, color, wallcolor)
        self.shapes.append( ("box", ulx, uly, lrx, lry, color) )
        self.redraw()
    def addWall(self, x1, y1, x2, y2, color="black"):
        seg = Segment((x1, y1), (x2, y2), partOf="wall")
        seg.color = color
        seg.type = "wall"
        id = self.drawLine(x1, y1, x2, y2, fill=color, tag="line")
        seg.id = id
        self.world.append( seg )
    def drawText(self, x, y, text, fill="black", tag="robot", **args):
        #print 'called drawText with "%s"' % text
        fontPixelHeight = 15
        if not self.tkfont:
            import tkFont
            self.font = tkFont.Font(size = -fontPixelHeight) # -n is n pixels tall
            self.tkfont = tkFont.Font(self.canvas, font=self.font)
            self.tkfont.height = self.tkfont.metrics("linespace")
            self.actual = self.font.actual() # but let's get actual
        # sizes are all in pixels
        lines = text.split("\n")
        width = 0
        for line in lines:
            w = self.tkfont.measure(line) + 10 # width of text
            if w > width:
                width = w 
        height = (abs(self.actual["size"]) * len(lines) * 1.25) + fontPixelHeight
        between = 30
        above   = 40
        roundness = 2
        xp, yp = self.scale_x(x), self.scale_y(y)
        points = [(xp, yp),
                  (xp + between, yp - above),
                  (xp + between, yp - above - 10 + roundness),
                  (xp + between + roundness, yp - above - 10),
                  (xp + between + width - roundness, yp - above - 10),
                  (xp + between + width, yp - above - 10 + roundness),
                  (xp + between + width, yp - above - 10 + height - roundness),
                  (xp + between + width - roundness, yp - above - 10 + height),
                  (xp + between + roundness, yp - above - 10 + height),
                  (xp + between, yp - above - 10 + height - roundness),
                  (xp + between, yp - above + 10),
                  ]
        self.canvas.create_polygon(points, tag=(tag,"top"), fill="white", outline="black")
        self.canvas.create_text(self.scale_x(x) + between + 5, self.scale_y(y) - above, text=text, font=self.font, tag=(tag,"top"), fill=fill, anchor="nw", **args)
    def drawLine(self, x1, y1, x2, y2, fill="", tag="robot", **args):
        return self.canvas.create_line(self.scale_x(x1), self.scale_y(y1), self.scale_x(x2), self.scale_y(y2), tag=tag, fill=fill, **args)
    def drawOval(self, x1, y1, x2, y2, **args):
        return self.canvas.create_oval(self.scale_x(x1), self.scale_y(y1),
                                       self.scale_x(x2), self.scale_y(y2),
                                       **args)
    def drawPolygon(self, points, fill="", outline="black", tag="robot", **args):
        xy = map(lambda pt: (self.scale_x(pt[0]), self.scale_y(pt[1])), points)
        if self.display["wireframe"]:
            if fill != "white":
                outline = fill
            else:
                outline = "black"
            fill = ""
        return self.canvas.create_polygon(xy, tag=tag, fill=fill, outline=outline)
    def remove(self, thing):
        self.canvas.delete(thing)
    def step(self, run = 1):
        self.remove("robot")
        Simulator.step(self, run)
        if run and not self.stop:
            self.running = 1
            self.after(self.timeslice, self.step)
        else:
            self.running = 0
    def addTrail(self, pos, index, robot):
        Simulator.addTrail(self, pos, index, robot)
        if robot.display["trail"] == 1:
            xya = self.trail[pos][(index - 1) % self.maxTrailSize]
            if xya != None:
                self.drawLine(xya[0], xya[1], robot._gx, robot._gy, robot.color, "trail")
    def update(self):
        self.update_idletasks()

class SimRobot:
    def __init__(self, name, x, y, a, boundingBox = [], color = "red"):
        if " " in name:
            name = name.replace(" ", "_")
        self.name = name
        self.type = "robot"
        # set them here manually: (afterwards, use setPose)
        self.proposePosition = 0 # used to check for obstacles before moving
        self.stepScalar = 1.0 # normally = 1.0
        self._gx = x
        self._gy = y
        self._ga = a
        self.subscribed = 0
        self.x, self.y, self.a = (0.0, 0.0, 0.0) # localize
        self.boundingBox = boundingBox # ((x1, x2), (y1, y2)) NOTE: Xs then Ys of bounding box
        self.boundingSeg = []
        if boundingBox != []:
            self.radius = max(max(map(abs, boundingBox[0])), max(map(abs, boundingBox[1]))) # meters
        else:
            self.radius = 0.0
        self.builtinDevices = ["speech"]
        self.color = color
        self.colorParts = {"ir": "pink", "sonar": "gray", "bumper": "black", "trail": color}
        self.devices = []
        self.simulator = None # will be set when added to simulator
        self.vx, self.vy, self.va = (0.0, 0.0, 0.0) # meters / second, rads / second
        self.friction = 1.0
        # -1: don't automatically turn display on when subscribing:
        self.display = {"body": 1, "boundingBox": 0, "gripper": -1, "camera": 0, "sonar": 0,
                        "light": -1, "lightBlocked": 0, "trail": -1, "ir": -1, "bumper": 1,
                        "speech": 1}
        self.stall = 0
        self.energy = 10000.0
        self.maxEnergyCostPerStep = 1.0
        # FIXME: add some noise to movement
        #self.noiseTranslate = 0.01 # percent of translational noise 
        #self.noiseRotate    = 0.01 # percent of translational noise 
        self._mouse = 0 # mouse down?
        self._mouse_xy = (0, 0) # last mouse click
        self._last_pose = (-1, -1, -1) # last robot pose drawn
        self.bulb = None
        self.gripper = None
        self.sayText = ""

    def additionalSegments(self, x, y, cos_a90, sin_a90, **dict):
        # dynamic segments
        retval = []
        if self.gripper:
            g = self.gripper
            x1, x2, x3, x4 = g.pose[0], g.pose[0] + g.armLength, g.pose[0], g.pose[0] + g.armLength
            y1, y2, y3, y4 = g.armPosition, g.armPosition, -g.armPosition,  -g.armPosition
            if g.robot.proposePosition and g.velocity != 0.0:
                armPosition, velocity = g.moveWhere()
                y1, y2, y3, y4 = armPosition, armPosition, -armPosition,  -armPosition
            xys = map(lambda nx, ny: (x + nx * cos_a90 - ny * sin_a90,
                                      y + nx * sin_a90 + ny * cos_a90),
                      (x1, x2, x3, x4), (y1, y2, y3, y4))
            w = [Segment(xys[0], xys[1], partOf="gripper"),
                 Segment(xys[2], xys[3], partOf="gripper")]
            for s in w:
                for key in dict:
                    s.__dict__[key] = dict[key]
                retval.append(s)
        return retval
    
    def addBoundingSeg(self, boundingSeg):
        if self.boundingSeg == []:
            self.boundingSeg = boundingSeg
        else:
            self.boundingSeg[0].extend(boundingSeg[0])
            self.boundingSeg[1].extend(boundingSeg[1])
        segradius = max(max(map(abs, boundingSeg[0])), max(map(abs, boundingSeg[1]))) # meters
        self.radius = max(self.radius, segradius)
        
    def localize(self, x = 0, y = 0, th = 0):
        self.x, self.y, self.a = (x, y, th)

    def say(self, text):
        self.sayText = text

    def setPose(self, x = None, y = None, a = None, handOfGod = 0):
        if x != None: # we never send just x; always comes with y
            if self._mouse != 1 and not handOfGod: # if the mouse isn't down:
                # first, figure out how much we moved in the global coords:
                a90 = -self._ga
                cos_a90 = math.cos(a90)
                sin_a90 = math.sin(a90)
                dx =  (x - self._gx) * cos_a90 - (y - self._gy) * sin_a90
                dy =  (x - self._gx) * sin_a90 + (y - self._gy) * cos_a90
                # then, move that much in the local coords:
                local90 = -self.a
                cos_local90 = math.cos(local90)
                sin_local90 = math.sin(local90)
                a90 = -self.a
                self.y += dx * cos_local90 - dy * sin_local90
                self.x += dx * sin_local90 + dy * cos_local90 
                # noise: --------------------------------------------------------------
                # FIXME: should be based on the total distance moved:
                # dist = Segment((x, y), (self._gx, self._gy)).length()
                # but distributed over x and y components, gaussian?
                # Velocity should maybe play a role, too
            # just update the global position
            self._gx = x
            self._gy = y
        if a != None:
            # if our angle changes, update localized position:
            if self._mouse != 1 and not handOfGod: # if mouse isn't down
                diff = a - self._ga
                self.a += diff 
                self.a = self.a % (2 * math.pi) # keep in the positive range
            # just update the global position
            self._ga = a % (2 * math.pi) # keep in the positive range
            # noise: --------------------------------------------------------------
            # FIXME: add gaussian(noiseRotate)
    def move(self, vx, va):
        self.vx = vx
        self.va = va
        return "ok"

    def rotate(self, va):
        self.va = va
        return "ok"

    def translate(self, vx):
        self.vx = vx
        return "ok"

    def getPose(self):
        """ Returns global coordinates. """
        return (self._gx, self._gy, self._ga)
    
    def getIndex(self, dtype, i):
        index = 0
        for d in self.devices:
            if d.type == dtype:
                if i == index:
                    return d
                index += 1
        return None

    def updateDevices(self):
        # measure and draw the new device data:
        if self.subscribed == 0: return
        # do some computations and save for speed
        a90 = self._ga + PIOVER2
        cos_a90 = math.cos(a90)
        sin_a90 = math.sin(a90)
        for d in self.devices:
            if not d.active: continue
            if d.type == "sonar" or d.type == "ir" or d.type == "bumper":
                i = 0
                for x, y, a in d.geometry:
                    ga = (self._ga + a)
                    gx = self._gx + (x * cos_a90 - y * sin_a90)
                    gy = self._gy + (x * sin_a90 + y * cos_a90)
                    dist, hit, obj = self.simulator.castRay(self, gx, gy, -ga, d.maxRange)
                    if hit:
                        self.drawRay(d.type, gx, gy, hit[0], hit[1], self.colorParts[d.type])
                    else:
                        hx, hy = math.sin(-ga) * d.maxRange, math.cos(-ga) * d.maxRange
                        dist = d.maxRange
                        self.drawRay(d.type, gx, gy, gx + hx, gy + hy, self.colorParts[d.type])
                    if d.type == "bumper":
                        if dist < d.maxRange: d.scan[i] = 1
                        else:                 d.scan[i] = 0
                    else: 
                        d.scan[i] = dist
                    i += 1
            elif d.type == "bulb":
                pass # nothing to update... it is not a sensor
            elif d.type == "directional": # directional light sensor
                # for each light sensor:
                i = 0
                for (d_x, d_y, d_a) in d.geometry:
                    # compute total light on sensor, falling off as square of distance
                    # position of light sensor in global coords:
                    gx = self._gx + (d_x * cos_a90 - d_y * sin_a90)
                    gy = self._gy + (d_x * sin_a90 + d_y * cos_a90)
                    ga = self._ga + d_a
                    sum = 0.0
                    rgb = [0, 0, 0]
                    for light in self.simulator.lights: # for each light source:
                        # these can be type == "fixed" and type == "bulb"
                        if light.type == "fixed": 
                            x, y, brightness, light_rgb = light.x, light.y, light.brightness, light.rgb
                        else: # get position from robot:
                            if light.robot == self: continue # don't read the bulb if it is on self
                            ogx, ogy, oga, brightness = (light.robot._gx,
                                                         light.robot._gy,
                                                         light.robot._ga,
                                                         light.brightness)
                            oa90 = oga + PIOVER2
                            x = ogx + (light.x * math.cos(oa90) - light.y * math.sin(oa90))
                            y = ogy + (light.x * math.sin(oa90) + light.y * math.cos(oa90))
                        seg = Segment((x,y), (gx, gy))
                        a = -seg.angle() + PIOVER2
                        # see if line between sensor and light is blocked by any boundaries (ignore other bb)
                        dist,hit,obj = self.simulator.castRay(self, x, y, a, seg.length() - .1,
                                                               ignoreRobot = "other", rayType = "light")
                        # compute distance of segment; value is sqrt of that?
                        if not hit: # no hit means it has a clear shot:
                            # is the light source within the arc of the sensor
                            dx = x - gx
                            dy = y - gy
                            angle = math.atan2(dy, dx) - (ga + PIOVER2)
                            angle = normRad(angle)
                            if -math.pi/3 < angle < math.pi/3:
                                self.drawRay("light", x, y, gx, gy, "orange")
                                intensity = (1.0 / (seg.length() * seg.length()))
                                sum += min(intensity, 1.0) * math.cos(angle*1.5) * brightness * 1000.0
                                for c in [0, 1, 2]:
                                    rgb[c] += light_rgb[c] * (1.0/ seg.length())
                            else: 
                                self.drawRay("lightBlocked", x, y, gx, gy, "blue")
                        else:
                            self.drawRay("lightBlocked", x, y, hit[0], hit[1], "purple")
                            print "hit!"
                    d.scan[i] = min(sum, d.maxRange)
                    i += 1
            elif d.type == "light":
                # for each light sensor:
                i = 0
                for (d_x, d_y, d_a) in d.geometry:
                    # compute total light on sensor, falling off as square of distance
                    # position of light sensor in global coords:
                    gx = self._gx + (d_x * cos_a90 - d_y * sin_a90)
                    gy = self._gy + (d_x * sin_a90 + d_y * cos_a90)
                    sum = 0.0
                    rgb = [0, 0, 0]
                    for light in self.simulator.lights: # for each light source:
                        # these can be type == "fixed" and type == "bulb"
                        if light.type == "fixed": 
                            x, y, brightness, light_rgb = light.x, light.y, light.brightness, light.rgb
                        else: # get position from robot:
                            if light.robot == self: continue # don't read the bulb if it is on self
                            ogx, ogy, oga, brightness, color = (light.robot._gx,
                                                                light.robot._gy,
                                                                light.robot._ga,
                                                                light.brightness, light.robot.color)
                            oa90 = oga + PIOVER2
                            x = ogx + (light.x * math.cos(oa90) - light.y * math.sin(oa90))
                            y = ogy + (light.x * math.sin(oa90) + light.y * math.cos(oa90))
                            light_rgb = colorMap[color]
                        seg = Segment((x,y), (gx, gy))
                        a = -seg.angle() + PIOVER2
                        # see if line between sensor and light is blocked by any boundaries (ignore other bb)
                        dist,hit,obj = self.simulator.castRay(self, x, y, a, seg.length() - .1,
                                                               ignoreRobot = "other", rayType = "light")
                        # compute distance of segment; value is sqrt of that?
                        if not hit: # no hit means it has a clear shot:
                            self.drawRay("light", x, y, gx, gy, "orange")
                            intensity = (1.0 / (seg.length() * seg.length())) 
                            sum += min(intensity, 1.0) * brightness * 1000.0
                            for c in [0, 1, 2]:
                                rgb[c] += light_rgb[c] * (1.0/ seg.length())
                        else:
                            self.drawRay("lightBlocked", x, y, hit[0], hit[1], "purple")
                    d.scan[i] = min(sum, d.maxRange)
                    for c in [0, 1, 2]:
                        d.rgb[i][c] = min(int(rgb[c]), 255)
                    i += 1
            elif d.type == "gripper":
                # cast a ray in two places, set scan = 1 if it is "broken"
                x = d.pose[0] + .07 # first beam distance from center of robot
                y = d.armPosition # distance between arms
                d.scan = [0] * (2 + 3) # two beams, 3 sensors (no lift)
                d.objs = []
                for i in range(2): # two beams
                    gx = self._gx + (x * cos_a90 - y * sin_a90)
                    gy = self._gy + (x * sin_a90 + y * cos_a90)
                    ogx = self._gx + (x * cos_a90 + y * sin_a90)
                    ogy = self._gy + (x * sin_a90 - y * cos_a90)
                    dist,hit,obj = self.simulator.castRay(self, gx, gy, -self._ga + PIOVER2, 2 * y,
                                                          rayType = "breakBeam")
                    if hit: 
                        d.scan[i] = 1
                        d.objs.append(obj) # for gripping
                        if self.display["gripper"] == 1: # breaker beams
                            self.drawRay("gripper", gx, gy, ogx, ogy, "orange")
                    elif self.display["gripper"] == 1:
                        self.drawRay("gripper", gx, gy, ogx, ogy, "purple")
                    x += .07  # distance between beams
                d.scan[2] = d.isClosed()
                d.scan[3] = d.isOpened()
                d.scan[4] = d.isMoving()
            elif d.type == "ptz": pass
            elif d.type == "camera":
                x, y = self._gx, self._gy # camera location
                stepAngle = d.zoom / float(d.width - 1)
                a = d.startAngle
                d.scan = []
                for i in range(d.width):
                    # FIX: move camera to d.pose; currently assumes robot center
                    ga = (self._ga + a) 
                    dist,hit,obj = self.simulator.castRay(self, x, y, -ga,
                                                           ignoreRobot="self",
                                                           rayType = "camera")
                    if obj != None:
                        if i in [0, d.width - 1]:
                            self.drawRay("camera", x, y, hit[0], hit[1], "purple")
                        dist = (10 - dist)/10.0 # 10 meter range
                        if obj.type == "wall":
                            height = int(min(max((dist ** 2) * d.height/2.0, 1), d.height/2))
                        else:
                            height = int(min(max((dist ** 2) * d.height/4.0, 1), d.height/4))
                        d.scan.append((colorCode[obj.color], height))
                    else:
                        d.scan.append((None, None))
                    a -= stepAngle
            else:
                raise AttributeError, "unknown type of device: '%s'" % d.type

    def eat(self, amt):
        for light in self.simulator.lights:
            if light != "fixed": continue
            dist = Segment((self._gx, self._gy), (light.x, light.y)).length()
            radius = max(light.brightness, self.radius)
            if amt == -1:
                if light.brightness > 0 and dist <= radius:
                    light.brightness = 0
                    self.simulator.redraw()
                    return 1.0
            elif dist <= radius and amt/1000.0 <= light.brightness:
                light.brightness -= amt/1000.0
                self.energy += amt
                self.simulator.redraw()
                return amt
        return 0.0

    def step(self, timeslice = 100, movePucks = 1):
        """
        Move the robot self.velocity amount, if not blocked.
        """
        if self._mouse: return # don't do any of this if mouse is down
        self.proposePosition = 1
        gvx = self.ovx * self.stepScalar
        gvy = self.ovy * self.stepScalar
        vx = gvx * math.sin(-self._ga) + gvy * math.cos(-self._ga)
        vy = gvx * math.cos(-self._ga) - gvy * math.sin(-self._ga)
        va = self.ova
        # proposed positions:
        p_x = self._gx + vx * (timeslice / 1000.0) # miliseconds
        p_y = self._gy + vy * (timeslice / 1000.0) # miliseconds
        p_a = self._ga + va * (timeslice / 1000.0) # miliseconds
        pushedAPuck = 0
        # for each of the robot's bounding box segments:
        a90 = p_a + PIOVER2
        cos_a90 = math.cos(a90)
        sin_a90 = math.sin(a90)
        if self.subscribed or self.type == "puck":
            if vx != 0 or vy != 0 or va != 0:
                self.energy -= self.maxEnergyCostPerStep
            # let's check if that movement would be ok:
            segments = []
            if self.boundingBox != []:
                xys = map(lambda x, y: (p_x + x * cos_a90 - y * sin_a90,
                                        p_y + x * sin_a90 + y * cos_a90),
                          self.boundingBox[0], self.boundingBox[1])
                for i in range(len(xys)):
                    bb = Segment( xys[i], xys[i - 1])
                    segments.append(bb)
            if self.boundingSeg != []:
                xys = map(lambda x, y: (p_x + x * cos_a90 - y * sin_a90,
                                        p_y + x * sin_a90 + y * cos_a90),
                          self.boundingSeg[0], self.boundingSeg[1])
                for i in range(0, len(xys), 2):
                    bb = Segment( xys[i], xys[i + 1])
                    segments.append(bb)
            for s in self.additionalSegments(p_x, p_y, cos_a90, sin_a90):
                segments.append(s)
            for bb in segments:
                # check each segment of the robot's bounding segs for wall obstacles:
                for w in self.simulator.world:
                    if bb.intersects(w):
                        self.proposePosition = 0
                        if self.gripper and self.gripper.velocity != 0:
                            self.gripper.state = "stop"
                            self.gripper.velocity = 0
                        if self.ovx != 0 or self.ovy != 0 or self.ova != 0:
                            self.stall = 1
                        self.updateDevices()
                        self.draw()
                        return
                # check each segment of the robot's bounding box for other robots:
                for r in self.simulator.robots:
                    if r.name == self.name: continue # don't compare with your own!
                    r_a90 = r._ga + PIOVER2
                    cos_r_a90 = math.cos(r_a90)
                    sin_r_a90 = math.sin(r_a90)
                    r_segments = []
                    if r.boundingBox != []:
                        r_xys = map(lambda x, y: (r._gx + x * cos_r_a90 - y * sin_r_a90,
                                                  r._gy + x * sin_r_a90 + y * cos_r_a90),
                                    r.boundingBox[0], r.boundingBox[1])
                        for j in range(len(r_xys)):
                            r_seg = Segment(r_xys[j], r_xys[j - 1])
                            r_segments.append(r_seg)
                    if r.boundingSeg != []:
                        r_xys = map(lambda x, y: (r._gx + x * cos_r_a90 - y * sin_r_a90,
                                                  r._gy + x * sin_r_a90 + y * cos_r_a90),
                                    r.boundingSeg[0], r.boundingSeg[1])
                        for j in range(0, len(r_xys), 2):
                            r_seg = Segment(r_xys[j], r_xys[j + 1])
                            r_segments.append(r_seg)
                    for s in r.additionalSegments(r._gx, r._gy, cos_r_a90, sin_r_a90):
                        r_segments.append(s)
                    for r_seg in r_segments:
                        bbintersect = bb.intersects(r_seg)
                        if r.type == "puck": # other robot is a puck
                            if bbintersect:
                                # transfer some energy to puck
                                if movePucks:
                                    r._ga = self._ga + ((random.random() - .5) * 0.4) # send in random direction, 22 degree
                                    r.vx = self.vx * 0.9 # knock it away
                                    if r not in self.simulator.needToMove:
                                        self.simulator.needToMove.append(r)
                                    if self.type == "puck":
                                        self.vx = self.vx * 0.9 # loose some
                                pushedAPuck = 1
                        elif bbintersect:
                            if self.type == "puck":
                                self.vx = 0.0
                                self.vy = 0.0
                            self.proposePosition = 0
                            if self.gripper and self.gripper.velocity != 0:
                                self.gripper.state = "stop"
                                self.gripper.velocity = 0
                            if self.ovx != 0 or self.ovy != 0 or self.ova != 0:
                                self.stall = 1
                            self.updateDevices()
                            self.draw()
                            return
        if pushedAPuck:
            # can't move this yet!
            if movePucks and r not in self.simulator.needToMove:
                self.simulator.needToMove.append( self )
            else:
                if self.gripper and self.gripper.velocity != 0:
                    self.gripper.state = "stop"
                    self.gripper.velocity = 0
                if self.ovx != 0 or self.ovy != 0 or self.ova != 0:
                    self.stall = 1
                self.updateDevices()
                self.draw()
            return
        self.proposePosition = 0
        # ok! move the robot, if it wanted to move
        if self.gripper and self.gripper.velocity != 0:
            # handle moving paddles
            d = self.gripper
            d.armPosition, d.velocity = d.moveWhere()
            if d.armPosition == d.openPosition:
                if d.storage != [] and d.state == "deploy":
                    x = d.pose[0] + d.armLength/2
                    y = 0
                    rx, ry = (p_x + x * cos_a90 - y * sin_a90,
                              p_y + x * sin_a90 + y * cos_a90)
                    r = d.storage.pop()
                    r.setPose(rx, ry, 0.0)
                    d.state = "open"
        if self.friction != 1.0:
            if r.type == "puck":
                self.vx *= self.friction
                self.vy *= self.friction
                if 0.0 < self.vx < 0.1: self.vx = 0.0
                if 0.0 < self.vy < 0.1: self.vy = 0.0
                if 0.0 > self.vx > -0.1: self.vx = 0.0
                if 0.0 > self.vy > -0.1: self.vy = 0.0
            else:
                self.ovx *= self.friction
                self.ovy *= self.friction
                if 0.0 < self.ovx < 0.1: self.ovx = 0.0
                if 0.0 < self.ovy < 0.1: self.ovy = 0.0
                if 0.0 > self.ovx > -0.1: self.ovx = 0.0
                if 0.0 > self.ovy > -0.1: self.ovy = 0.0
        self.stall = 0
        self.setPose(p_x, p_y, p_a)
        self.updateDevices()
        self.draw()
    def draw(self): pass
    def drawRay(self, dtype, x1, y1, x2, y2, color):
        if self.display[dtype] == 1:
            self.simulator.drawLine(x1, y1, x2, y2, color, "robot")
    def addDevice(self, dev):
        self.devices.append(dev)
        if dev.type not in self.builtinDevices:
            self.builtinDevices.append(dev.type)
        if dev.type == "bulb":
            self.simulator.lights.append( dev )
            dev.robot = self
            self.bulb = dev
        elif dev.type == "camera":
            dev.robot = self
        elif dev.type == "gripper":
            dev.robot = self
            self.gripper = dev

class TkRobot(SimRobot):
    def __init__(self, *args, **kwargs):
        SimRobot.__init__(self, *args, **kwargs)
	self._mouse_offset_from_center = 0, 0
    def mouse_event(self, event, command, robot):
        x, y = event.x, event.y
        if command[:8] == "control-":
            self._mouse_xy = x, y
            cx, cy = self.simulator.scale_x(robot._gx), self.simulator.scale_y(robot._gy)
            if command == "control-up":
                self.simulator.remove('arrow')
                a = Segment((cx, cy), (x, y)).angle()
                robot.setPose(a = (-a - PIOVER2) % (2 * math.pi))
                self._mouse = 0
                self.simulator.lastEventRobot = None
                self.simulator.redraw()
            elif command in ["control-down", "control-motion"]:
                self._mouse = 1
                self.simulator.remove('arrow')
                self.simulator.canvas.create_line(cx, cy, x, y, tag="arrow", fill="purple")
        else:
            if command == "up":
                x -= self.simulator.offset_x
                y -= self.simulator.offset_y
                x, y = map(lambda v: float(v) / self.simulator.scale, (x, -y))
                robot.setPose(x - self._mouse_offset_from_center[0],
                              y - self._mouse_offset_from_center[1])
                self._mouse = 0
                self.simulator.lastEventRobot = None
                self.simulator.redraw()
            elif command == "down":
                self._mouse = 1
                self._mouse_xy = x, y
                cx = x - self.simulator.offset_x
                cy = y - self.simulator.offset_y
                cx, cy = map(lambda v: float(v) / self.simulator.scale, (cx, -cy))
                self._mouse_offset_from_center = cx - self._gx, cy - self._gy
                self.simulator.canvas.move("robot-%s" % robot.name, x - self._mouse_xy[0], y - self._mouse_xy[1])
            elif command == "motion":
                self._mouse = 1
                self.simulator.canvas.move("robot-%s" % robot.name, x - self._mouse_xy[0], y - self._mouse_xy[1])
                self._mouse_xy = x, y
                # now move it so others will see it it correct place as you drag it:
                x -= self.simulator.offset_x
                y -= self.simulator.offset_y
                x, y = map(lambda v: float(v) / self.simulator.scale, (x, -y))
                robot.setPose(x, y)
        return "break"
class Puck(SimRobot):
    def __init__(self, *args, **kwargs):
        SimRobot.__init__(self, *args, **kwargs)
        self.radius = 0.05
        self.friction = 0.90
        self.type = "puck"

class TkPuck(TkRobot):
    def __init__(self, *args, **kwargs):
        TkRobot.__init__(self, *args, **kwargs)
        self.radius = 0.05
        self.friction = 0.90
        self.type = "puck"
    def draw(self):
        """
        Draws the body of the robot. Not very efficient.
        """
        self.simulator.canvas.tkraise("top")
        if  self._last_pose == (self._gx, self._gy, self._ga): return # hasn't moved
        self._last_pose = (self._gx, self._gy, self._ga)
        self.simulator.remove("robot-%s" % self.name)
        if self.display["body"] == 1:
            x1, y1, x2, y2 = (self._gx - self.radius), (self._gy - self.radius), (self._gx + self.radius), (self._gy + self.radius)
            self.simulator.drawOval(x1, y1, x2, y2, fill=self.color, tag="robot-%s" % self.name, outline="black")
        if self.display["boundingBox"] == 1 and self.boundingBox != []:
            # Body Polygon, by x and y lists:
            a90 = self._ga + PIOVER2 # angle is 90 degrees off for graphics
            cos_a90 = math.cos(a90)
            sin_a90 = math.sin(a90)
            xy = map(lambda x, y: (self._gx + x * cos_a90 - y * sin_a90,
                                   self._gy + x * sin_a90 + y * cos_a90),
                     self.boundingBox[0], self.boundingBox[1])
            self.simulator.drawPolygon(xy, tag="robot-%s" % self.name, fill="", outline="purple")

Pioneer = SimRobot

class TkPioneer(TkRobot):
    def __init__(self, *args, **kwargs):
        TkRobot.__init__(self, *args, **kwargs)
        self.radius = 0.4

    def draw(self):
        """
        Draws the body of the robot. Not very efficient.
        """
        self.simulator.canvas.tkraise("top")
        if self._last_pose == (self._gx, self._gy, self._ga) and (
            (self.gripper == None) or (self.gripper and self.gripper.velocity == 0)): 
            if self.display["speech"] == 1:
                if self.sayText != "":
                    # center of robot: 
                    x, y = self._gx, self._gy
                    # FIXME: remove old text
                    # self.simulator.remove("robot-%s" % self.name)
                    self.simulator.drawText(x, y, self.sayText, tag="robot") # -%s" % self.name)
            return # hasn't moved
        self._last_pose = (self._gx, self._gy, self._ga)
        self.simulator.remove("robot-%s" % self.name)
        # Body Polygon, by x and y lists:
        sx = [.225, .15, -.15, -.225, -.225, -.15, .15, .225]
        sy = [.08, .175, .175, .08, -.08, -.175, -.175, -.08]
        s_x = self.simulator.scale_x
        s_y = self.simulator.scale_y
        a90 = self._ga + PIOVER2 # angle is 90 degrees off for graphics
        cos_a90 = math.cos(a90)
        sin_a90 = math.sin(a90)
        if self.display["body"] == 1:
            xy = map(lambda x, y: (self._gx + x * cos_a90 - y * sin_a90,
                                   self._gy + x * sin_a90 + y * cos_a90),
                     sx, sy)
            self.simulator.drawPolygon(xy, fill=self.color, tag="robot-%s" % self.name, outline="black")
            bx = [ .14, .06, .06, .14] # front camera
            by = [-.06, -.06, .06, .06]
            xy = map(lambda x, y: (self._gx + x * cos_a90 - y * sin_a90,
                                   self._gy + x * sin_a90 + y * cos_a90),
                     bx, by)
            self.simulator.drawPolygon(xy, tag="robot-%s" % self.name, fill="black")
            if self.bulb:
                x = (self._gx + self.bulb.x * cos_a90 - self.bulb.y * sin_a90)
                y = (self._gy + self.bulb.x * sin_a90 + self.bulb.y * cos_a90)
                radius = .05
                self.simulator.drawOval(x - radius, y - radius, x + radius, y + radius,
                                        tag="robot-%s" % self.name, fill=self.color, outline="black")
            if self.gripper:
                # draw grippers:
                # base:
                xy = [(self._gx + x * cos_a90 - y * sin_a90,
                       self._gy + x * sin_a90 + y * cos_a90) for (x,y) in
                      ((self.gripper.pose[0], self.gripper.openPosition),
                       (self.gripper.pose[0], -self.gripper.openPosition))]
                self.simulator.drawLine(xy[0][0], xy[0][1], xy[1][0], xy[1][1],
                                        tag="robot-%s" % self.name, fill="black")
                # left arm:
                xs = []
                ys = []
                xs.append(self.gripper.pose[0]);     ys.append(self.gripper.armPosition + 0.01)
                xs.append(self.gripper.pose[0] + self.gripper.armLength); ys.append(self.gripper.armPosition + 0.01)
                xs.append(self.gripper.pose[0] + self.gripper.armLength); ys.append(self.gripper.armPosition - 0.01)
                xs.append(self.gripper.pose[0]);     ys.append(self.gripper.armPosition - 0.01)
                xy = map(lambda x, y: (self._gx + x * cos_a90 - y * sin_a90,
                                       self._gy + x * sin_a90 + y * cos_a90),
                         xs, ys)
                self.simulator.drawPolygon(xy, tag="robot-%s" % self.name, fill="black", outline="black")
                # right arm:
                xs = []
                ys = []
                xs.append(self.gripper.pose[0]);     ys.append(-self.gripper.armPosition + 0.01)
                xs.append(self.gripper.pose[0] + self.gripper.armLength); ys.append(-self.gripper.armPosition + 0.01)
                xs.append(self.gripper.pose[0] + self.gripper.armLength); ys.append(-self.gripper.armPosition - 0.01)
                xs.append(self.gripper.pose[0]);     ys.append(-self.gripper.armPosition - 0.01)
                xy = map(lambda x, y: (self._gx + x * cos_a90 - y * sin_a90,
                                       self._gy + x * sin_a90 + y * cos_a90),
                         xs, ys)
                self.simulator.drawPolygon(xy, tag="robot-%s" % self.name, fill="black", outline="black")
        if self.display["boundingBox"] == 1:
            if self.boundingBox != []:
                xy = map(lambda x, y: (self._gx + x * cos_a90 - y * sin_a90,
                                       self._gy + x * sin_a90 + y * cos_a90),
                         self.boundingBox[0], self.boundingBox[1])
                self.simulator.drawPolygon(xy, tag="robot-%s" % self.name, fill="", outline="purple")
            if self.boundingSeg != []:
                xy = map(lambda x, y: (self._gx + x * cos_a90 - y * sin_a90,
                                       self._gy + x * sin_a90 + y * cos_a90),
                         self.boundingSeg[0], self.boundingSeg[1])
                for i in range(0, len(xy), 2):
                    self.simulator.drawLine(xy[i][0], xy[i][1],
                                            xy[i + 1][0], xy[i + 1][1],
                                            tag="robot-%s" % self.name, fill="purple")
            additionalSegments = self.additionalSegments(self._gx, self._gy, cos_a90, sin_a90)
            if additionalSegments != []:
                for s in additionalSegments:
                    self.simulator.drawLine(s.start[0], s.start[1], s.end[0], s.end[1],
                                            tag="robot-%s" % self.name, fill="purple")
        if self.display["speech"] == 1:
            if self.sayText != "":
                # center of robot: 
                x, y = self._gx, self._gy
                self.simulator.drawText(x, y, self.sayText, tag="robot") # % self.name)

class TkBlimp(TkRobot):
    def __init__(self, *args, **kwargs):
        TkRobot.__init__(self, *args, **kwargs)
        self.radius = 0.44 # meters
        self.color = "purple"

    def draw(self):
        self.simulator.canvas.tkraise("top")
        if self._last_pose == (self._gx, self._gy, self._ga): return
        self._last_pose = (self._gx, self._gy, self._ga)
        a90 = self._ga + PIOVER2 # angle is 90 degrees off for graphics
        cos_a90 = math.cos(a90)
        sin_a90 = math.sin(a90)
        self.simulator.remove("robot-%s" % self.name)
        self.simulator.drawOval(self._gx - self.radius, self._gy - self.radius,
                                self._gx + self.radius, self._gy + self.radius,
                                tag="robot-%s" % self.name, fill=self.color, outline="blue")
        x = (self._gx + self.radius * cos_a90 - 0 * sin_a90)
        y = (self._gy + self.radius * sin_a90 + 0 * cos_a90)
        self.simulator.drawLine(self._gx, self._gy, x, y,
                                tag="robot-%s" % self.name, fill="blue", width=3)

class RangeSensor:
    def __init__(self, name, geometry, arc, maxRange, noise = 0.0):
        self.type = name
        self.active = 1
        # geometry = (x, y, a) origin in meters and radians
        self.geometry = geometry
        self.arc = arc
        self.maxRange = maxRange
        self.noise = noise
        self.groups = {}
        self.scan = [0] * len(geometry) # for data
class Light:
    def __init__(self, x, y, brightness, color="yellow"):
        self.active = 1
        self.x = x
        self.y = y
        self.brightness = brightness
        self.color = color
        self._xyb = x, y, brightness # original settings for reset
        self.rgb = colorMap[color]
        self.type = "fixed"
class BulbDevice(Light):
    """
    Bulb will have color of robot.
    """
    def __init__(self, x, y):
        Light.__init__(self, x, y, 1.0)
        self.type = "bulb"
        self.active = 1
        self.geometry = (0, 0, 0)

class LightSensor:
    def __init__(self, geometry, noise = 0.0):
        self.type = "light"
        self.active = 1
        self.geometry = geometry
        self.arc = None
        self.maxRange = 1000.0
        self.noise = noise
        self.groups = {}
        self.scan = [0] * len(geometry) # for data
        self.rgb = [[0,0,0] for g in geometry]

class DirectionalLightSensor:
    def __init__(self, geometry, arc, noise = 0.0):
        # geometry (x, y, a) where a is direction (in radians) relative to robot
        self.type = "directional"
        self.active = 1
        self.geometry = geometry
        self.arc = arc
        self.maxRange = 1000.0 # in mm
        self.noise = noise
        self.groups = {}
        self.scan = [0] * len(geometry) # for data

class Gripper:
    def __init__(self):
        self.type = "gripper"
        self.active = 1
        self.scan = []
        self.objs = []
        self.armLength  = 0.200 # length of the paddles
        self.velocity   = 0.0   # moving?
        self.openPosition  = 0.12
        self.closePosition = 0.0
        self.pose = (0.225, 0, 0) # position of gripper on robot
        self.state = "open"
        self.armPosition   = self.openPosition
        self.breakBeam = []
        self.storage = []
    def close(self):
        self.state = "close"
        self.velocity = -0.01
        return "ok"
    def deploy(self):
        self.state = "deploy"
        self.velocity = 0.01
        return "ok"
    def store(self):
        self.state = "store"
        self.velocity = -0.01
        for segment in self.objs:
            segment.robot.setPose(-1000.0, -1000.0, 0.0)
            if segment.robot not in self.storage:
                self.storage.append( segment.robot )
    def open(self):
        self.state = "open"
        self.velocity = 0.01
        return "ok"
    def stop(self):
        self.state = "stop"
        self.velocity = 0.0
        return "ok"
    def moveWhere(self):
        armPosition = self.armPosition
        velocity = self.velocity
        if velocity > 0: # opening +
            armPosition += velocity
            if armPosition >= self.openPosition:
                armPosition = self.openPosition
                velocity = 0.0
        elif velocity < 0: # closing - 
            armPosition += velocity
            if armPosition <= self.closePosition:
                armPosition = self.closePosition
                velocity = 0.0
        return armPosition, velocity
    def isClosed(self):
        return self.velocity == 0 and self.armPosition == self.closePosition
    def isOpened(self):
        return self.velocity == 0 and self.armPosition == self.openPosition
    def isMoving(self):
        return self.velocity != 0

class PTZ:
    def __init__(self, camera):
        self.type = "ptz"
        self.camera = camera
        self.active = 1
    def setPose(self, p = None, t = None, z = None):
        if p != None:
            self.camera.pan = p * PIOVER180
        if z != None:
            self.camera.zoom = z * PIOVER180
        self.camera.startAngle = self.camera.pan + self.camera.zoom/2
        self.camera.stopAngle = self.camera.pan - self.camera.zoom/2
        return "ok"
    def getPose(self):
        return self.camera.pan / PIOVER180, 0, self.camera.zoom / PIOVER180

class Camera:
    def __init__(self, width, height, pan, zoom, x, y, thr):
        self.type = "camera"
        self.active = 1
        self.scan = []
        self.width = width
        self.height = height
        self.pan = pan * PIOVER180
        self.tilt = 0
        self.zoom = zoom * PIOVER180
        self.startAngle = self.pan + self.zoom/2
        self.stopAngle = self.pan - self.zoom/2
        self.pose = (x, y, thr)
        self.color = [[0,0,0] for i in range(self.width)]
        self.range = [0 for i in range(self.width)]

class PioneerFrontSonars(RangeSensor):
    def __init__(self):
        RangeSensor.__init__(self,
            "sonar", geometry = (( 0.10, 0.175, 90 * PIOVER180),
                                 ( 0.17, 0.15, 65 * PIOVER180),
                                 ( 0.20, 0.11, 40 * PIOVER180),
                                 ( 0.225, 0.05, 15 * PIOVER180),
                                 ( 0.225,-0.05,-15 * PIOVER180),
                                 ( 0.20,-0.11,-40 * PIOVER180),
                                 ( 0.17,-0.15,-65 * PIOVER180),
                                 ( 0.10,-0.175,-90 * PIOVER180)),
            arc = 5 * PIOVER180, maxRange = 8.0, noise = 0.0)
        self.groups = {'all': range(8),
                       'front': (3, 4),
                       'front-left' : (1,2,3),
                       'front-right' : (4, 5, 6),
                       'front-all' : (1,2, 3, 4, 5, 6),
                       'left' : (0,), 
                       'right' : (7,), 
                       'left-front' : (1,2), 
                       'right-front' : (5,6, ),
                       'left-back' : [],
                       'right-back' : [],
                       'back-right' : [],
                       'back-left' : [], 
                       'back' : [],
                       'back-all' : []}
        
class PioneerBackSonars(RangeSensor):
    def __init__(self):
        RangeSensor.__init__(self,
            "sonar", geometry = (( -0.10,-0.175,-90 * PIOVER180),
                                 ( -0.17,-0.15, (180 + 65) * PIOVER180),
                                 ( -0.20,-0.11, (180 + 40) * PIOVER180),
                                 ( -0.225,-0.05,(180 + 15) * PIOVER180),
                                 ( -0.225, 0.05,(180 - 15) * PIOVER180),
                                 ( -0.20, 0.11, (180 - 40) * PIOVER180),
                                 ( -0.17, 0.15, (180 - 65) * PIOVER180),
                                 ( -0.10, 0.175,(180 - 90) * PIOVER180)),
            arc = 5 * PIOVER180, maxRange = 8.0, noise = 0.0)
        self.groups = {'all': range(8),
                       'front': [],
                       'front-left' : [],
                       'front-right' : [],
                       'front-all' : [],
                       'left' : (7, ), 
                       'right' : (0, ), 
                       'left-front' : [], 
                       'right-front' : [],
                       'left-back' : (7, ),
                       'right-back' : (0, ),
                       'back-right' : (1, 2, 3),
                       'back-left' : (4, 5, 6), 
                       'back' : (3, 4),
                       'back-all' : ( 1, 2, 3, 4, 5, 6)}

class Pioneer16Sonars(RangeSensor):
    def __init__(self):
        RangeSensor.__init__(self,
            "sonar", geometry = (( 0.10, 0.175, 90 * PIOVER180),
                                 ( 0.17, 0.15, 65 * PIOVER180),
                                 ( 0.20, 0.11, 40 * PIOVER180),
                                 ( 0.225, 0.05, 15 * PIOVER180),
                                 ( 0.225,-0.05,-15 * PIOVER180),
                                 ( 0.20,-0.11,-40 * PIOVER180),
                                 ( 0.17,-0.15,-65 * PIOVER180),
                                 ( 0.10,-0.175,-90 * PIOVER180),
                                 ( -0.10,-0.175,-90 * PIOVER180),
                                 ( -0.17,-0.15, (180 + 65) * PIOVER180),
                                 ( -0.20,-0.11, (180 + 40) * PIOVER180),
                                 ( -0.225,-0.05,(180 + 15) * PIOVER180),
                                 ( -0.225, 0.05,(180 - 15) * PIOVER180),
                                 ( -0.20, 0.11, (180 - 40) * PIOVER180),
                                 ( -0.17, 0.15, (180 - 65) * PIOVER180),
                                 ( -0.10, 0.175,(180 - 90) * PIOVER180)),
            arc = 5 * PIOVER180, maxRange = 8.0, noise = 0.0)
        self.groups = {'all': range(16),
                       'front': (3, 4),
                       'front-left' : (1,2,3),
                       'front-right' : (4, 5, 6),
                       'front-all' : (1,2, 3, 4, 5, 6),
                       'left' : (0, 15), 
                       'right' : (7, 8), 
                       'left-front' : (0,), 
                       'right-front' : (7, ),
                       'left-back' : (15, ),
                       'right-back' : (8, ),
                       'back-right' : (9, 10, 11),
                       'back-left' : (12, 13, 14), 
                       'back' : (11, 12),
                       'back-all' : ( 9, 10, 11, 12, 13, 14)}

class Pioneer4Sonars(RangeSensor):
    def __init__(self):
        RangeSensor.__init__(self, "sonar",
             geometry = (( 0.225, 0.05, 15 * PIOVER180),
                         ( 0.225,-0.05,-15 * PIOVER180),
                         ( -0.225,-0.05,(180 + 15) * PIOVER180),
                         ( -0.225, 0.05,(180 - 15) * PIOVER180),
                         ), arc = 5 * PIOVER180, maxRange = 8.0, noise = 0.0)
        self.groups = {'all': range(4),
                       'front': (0, 1),
                       'front-left' : (0,),
                       'front-right' : (1,),
                       'front-all' : (0,1),
                       'left' : [], 
                       'right' : [], 
                       'left-front' : [], 
                       'right-front' : [],
                       'left-back' : [],
                       'right-back' : [],
                       'back-right' : (2,),
                       'back-left' : (3,), 
                       'back' : (2, 3),
                       'back-all' : ( 2, 3)}
        
class PioneerFrontLightSensors(LightSensor):
    def __init__(self):
        # make sure outside of bb!
        LightSensor.__init__(self, ((.225,  .175, 0), (.225, -.175, 0)),
                             noise=0.0) 
        self.groups = {"front-all": (0, 1),
                       "all": (0, 1),
                       "front": (0, 1),
                       "front-left": (0, ),
                       "front-right": (1, ),
                       'left' : (0,), 
                       'right' : (1,), 
                       'left-front' : (0,), 
                       'right-front' : (1, ),
                       'left-back' : [],
                       'right-back' : [],
                       'back-right' : [],
                       'back-left' : [], 
                       'back' : [],
                       'back-all' : []}

class Pioneer4FrontLightSensors(LightSensor):
    def __init__(self):
        # make sure outside of bb!
        LightSensor.__init__(self, (
            (.225,  .175, 0),
            (.225,  .0875, 0),
            (.225, -.0875, 0),
            (.225, -.175, 0),
            ),
                             noise=0.0) 
        self.groups = {"front-all": (0, 1, 2, 3),
                       "all": (0, 1, 2, 3),
                       "front": (1, 2),
                       "front-left": (0, ),
                       "front-right": (3, ),
                       'left' : (0, 1), 
                       'right' : (2, 3), 
                       'left-front' : (0,), 
                       'right-front' : (3, ),
                       'left-back' : [],
                       'right-back' : [],
                       'back-right' : [],
                       'back-left' : [], 
                       'back' : [],
                       'back-all' : []}

class PioneerFrontDirectionalLightSensors(DirectionalLightSensor):
    def __init__(self):
        # make sure outside of bb!
        DirectionalLightSensor.__init__(self, ((.225,  .175, -30 * PIOVER180), 
                                               (.225, -.175, 30 * PIOVER180)),
                                        120 * PIOVER180,
                                        noise=0.0) 
        self.groups = {"front-all": (0, 1),
                       "all": (0, 1),
                       "front": (0, 1),
                       "front-left": (0, ),
                       "front-right": (1, ),
                       'left' : (0,), 
                       'right' : (1,), 
                       'left-front' : (0,), 
                       'right-front' : (1, ),
                       'left-back' : [],
                       'right-back' : [],
                       'back-right' : [],
                       'back-left' : [], 
                       'back' : [],
                       'back-all' : []}

class TkMyro(TkRobot):
    def __init__(self, *args, **kwargs):
        TkRobot.__init__(self, *args, **kwargs)
        self.radius = 0.25

    def draw(self):
        """
        Draws the body of the robot. Not very efficient.
        """
        self.simulator.canvas.tkraise("top")
        if self._last_pose == (self._gx, self._gy, self._ga) and (
            (self.gripper == None) or (self.gripper and self.gripper.velocity == 0)): return # hasn't moved
        self._last_pose = (self._gx, self._gy, self._ga)
        self.simulator.remove("robot-%s" % self.name)
        # Body Polygon, by x and y lists:
        sx = [ .20, .20,-.10,-.10]
        sy = [ .15,-.15,-.15, .15] 
        s_x = self.simulator.scale_x
        s_y = self.simulator.scale_y
        a90 = self._ga + PIOVER2 # angle is 90 degrees off for graphics
        cos_a90 = math.cos(a90)
        sin_a90 = math.sin(a90)
        if self.display["body"] == 1:
            xy = map(lambda x, y: (self._gx + x * cos_a90 - y * sin_a90,
                                   self._gy + x * sin_a90 + y * cos_a90),
                     sx, sy)
            self.simulator.drawPolygon(xy, fill=self.color, tag="robot-%s" % self.name, outline="black")
            # --------------------------------------------------------------------------
            # Parts: wheel, wheel, battery
            bx = [[ .10, .10, -.10, -.10], 
                  [ .10, .10, -.10, -.10], 
                  [.05, .05, -.10, -.10], 
                  [.16, .17, .18, .17], 
                  [.16, .17, .18, .17]]
            by = [[ .18, .16, .16, .18], 
                  [ -.18, -.16, -.16, -.18], 
                  [.14, -.14, -.14, .14], 
                  [.13, .135, .115, .11], 
                  [-.13, -.135, -.115, -.11]]
            colors = ["black", "black", "gray", "yellow", "yellow"]
            for i in range(len(bx)):
                xy = map(lambda x, y: (self._gx + x * cos_a90 - y * sin_a90,
                                       self._gy + x * sin_a90 + y * cos_a90),
                         bx[i], by[i])
                self.simulator.drawPolygon(xy, tag="robot-%s" % self.name, fill=colors[i])
            # --------------------------------------------------------------------------
            if self.bulb:
                x = (self._gx + self.bulb.x * cos_a90 - self.bulb.y * sin_a90)
                y = (self._gy + self.bulb.x * sin_a90 + self.bulb.y * cos_a90)
                radius = .04
                self.simulator.drawOval(x - radius, y - radius, x + radius, y + radius,
                                        tag="robot-%s" % self.name, fill=self.color, outline="black")
            if self.gripper:
                # draw grippers:
                # base:
                xy = [(self._gx + x * cos_a90 - y * sin_a90,
                       self._gy + x * sin_a90 + y * cos_a90) for (x,y) in
                      ((self.gripper.pose[0], self.gripper.openPosition),
                       (self.gripper.pose[0], -self.gripper.openPosition))]
                self.simulator.drawLine(xy[0][0], xy[0][1], xy[1][0], xy[1][1],
                                        tag="robot-%s" % self.name, fill="black")
                # left arm:
                xs = []
                ys = []
                xs.append(self.gripper.pose[0]);     ys.append(self.gripper.armPosition + 0.01)
                xs.append(self.gripper.pose[0] + self.gripper.armLength); ys.append(self.gripper.armPosition + 0.01)
                xs.append(self.gripper.pose[0] + self.gripper.armLength); ys.append(self.gripper.armPosition - 0.01)
                xs.append(self.gripper.pose[0]);     ys.append(self.gripper.armPosition - 0.01)
                xy = map(lambda x, y: (self._gx + x * cos_a90 - y * sin_a90,
                                       self._gy + x * sin_a90 + y * cos_a90),
                         xs, ys)
                self.simulator.drawPolygon(xy, tag="robot-%s" % self.name, fill="black", outline="black")
                # right arm:
                xs = []
                ys = []
                xs.append(self.gripper.pose[0]);     ys.append(-self.gripper.armPosition + 0.01)
                xs.append(self.gripper.pose[0] + self.gripper.armLength); ys.append(-self.gripper.armPosition + 0.01)
                xs.append(self.gripper.pose[0] + self.gripper.armLength); ys.append(-self.gripper.armPosition - 0.01)
                xs.append(self.gripper.pose[0]);     ys.append(-self.gripper.armPosition - 0.01)
                xy = map(lambda x, y: (self._gx + x * cos_a90 - y * sin_a90,
                                       self._gy + x * sin_a90 + y * cos_a90),
                         xs, ys)
                self.simulator.drawPolygon(xy, tag="robot-%s" % self.name, fill="black", outline="black")
        if self.display["boundingBox"] == 1:
            if self.boundingBox != []:
                xy = map(lambda x, y: (self._gx + x * cos_a90 - y * sin_a90,
                                       self._gy + x * sin_a90 + y * cos_a90),
                         self.boundingBox[0], self.boundingBox[1])
                self.simulator.drawPolygon(xy, tag="robot-%s" % self.name, fill="", outline="purple")
            if self.boundingSeg != []:
                xy = map(lambda x, y: (self._gx + x * cos_a90 - y * sin_a90,
                                       self._gy + x * sin_a90 + y * cos_a90),
                         self.boundingSeg[0], self.boundingSeg[1])
                for i in range(0, len(xy), 2):
                    self.simulator.drawLine(xy[i][0], xy[i][1],
                                            xy[i + 1][0], xy[i + 1][1],
                                            tag="robot-%s" % self.name, fill="purple")
            additionalSegments = self.additionalSegments(self._gx, self._gy, cos_a90, sin_a90)
            if additionalSegments != []:
                for s in additionalSegments:
                    self.simulator.drawLine(s.start[0], s.start[1], s.end[0], s.end[1],
                                            tag="robot-%s" % self.name, fill="purple")

class MyroIR(RangeSensor):
    def __init__(self):
        RangeSensor.__init__(self,
                             "ir", geometry = (( 0.175, 0.13, 45 * PIOVER180),
                                               ( 0.175,-0.13,-45 * PIOVER180)),
                             arc = 5 * PIOVER180, maxRange = 0.5, noise = 0.0)
        self.groups = {'all': range(2),
                       'front': (0, 1),
                       'front-left' : (0, ),
                       'front-right' : (1, ),
                       'front-all' : (0, 1,),
                       'left' : (0,), 
                       'right' : (1,), 
                       'left-front' : (0, ), 
                       'right-front' : (1, ),
                       'left-back' : [],
                       'right-back' : [],
                       'back-right' : [],
                       'back-left' : [], 
                       'back' : [],
                       'back-all' : []}
class MyroBumper(RangeSensor):
    def __init__(self):
        RangeSensor.__init__(self,
                             "bumper", geometry = (( 0.20, 0.0, 80 * PIOVER180),
                                                   ( 0.20, 0.0,-80 * PIOVER180)),
                             arc = 5 * PIOVER180, maxRange = 0.20, noise = 0.0)
        self.groups = {'all': range(2),
                       'front': (0, 1),
                       'front-left' : (0, ),
                       'front-right' : (1, ),
                       'front-all' : (0, 1,),
                       'left' : (0,), 
                       'right' : (1,), 
                       'left-front' : (0, ), 
                       'right-front' : (1, ),
                       'left-back' : [],
                       'right-back' : [],
                       'back-right' : [],
                       'back-left' : [], 
                       'back' : [],
                       'back-all' : []}
        
class MyroLightSensors(LightSensor):
    def __init__(self):
        LightSensor.__init__(self, ((.18, .13, 0), (.18, -.13, 0)),
                             noise=0.0) 
        self.groups = {"front-all": (0, 1),
                       "all": (0, 1),
                       "front": (0, 1),
                       "front-left": (0, ),
                       "front-right": (1, ),
                       'left' : (0,), 
                       'right' : (1,), 
                       'left-front' : (0,), 
                       'right-front' : (1, ),
                       'left-back' : [],
                       'right-back' : [],
                       'back-right' : [],
                       'back-left' : [], 
                       'back' : [],
                       'back-all' : []}
