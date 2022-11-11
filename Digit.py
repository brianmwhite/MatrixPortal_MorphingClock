from adafruit_display_shapes.line import Line
from adafruit_display_shapes.rect import Rect
import time


class Digit:
    sA = 0
    sB = 1
    sC = 2
    sD = 3
    sE = 4
    sF = 5
    sG = 6
    segHeight = 6
    segWidth = segHeight
    height = 31
    width = 63
    animSpeed = 0.03

    # digitBits = bytes(
    #     [
    #         0xFC,  #   B11111100, // 0 ABCDEF--
    #         0x60,  #   B01100000, // 1 -BC-----
    #         0xDA,  #   B11011010, // 2 AB-DE-G-
    #         0xF2,  #   B11110010, // 3 ABCD--G-
    #         0x66,  #   B01100110, // 4 -BC--FG-
    #         0xB6,  #   B10110110, // 5 A-CD-FG-
    #         0xBE,  #   B10111110, // 6 A-CDEFG-
    #         0xE0,  #   B11100000, // 7 ABC-----
    #         0xFE,  #   B11111110, // 8 ABCDEFG-
    #         0xF6,  #   B11110110, // 9 ABCD_FG-
    #     ]
    # )

    digitBits = [
        "11111100",  # 0 ABCDEF--
        "01100000",  # 1 -BC-----
        "11011010",  # 2 AB-DE-G-
        "11110010",  # 3 ABCD--G-
        "01100110",  # 4 -BC--FG-
        "10110110",  # 5 A-CD-FG-
        "10111110",  # 6 A-CDEFG-
        "11100000",  # 7 ABC-----
        "11111110",  # 8 ABCDEFG-
        "11110110",  # 9 ABCD_FG-
    ]

    black = 0

    def __init__(self, d, value, xo, yo, color):
        self.display = d
        self.value = value
        self.xOffset = xo
        self.yOffset = yo
        self.color = color
        pass

    def Value(self):
        return self.value

    def drawPixel(self, x, y, c):
        self.display.append(
            Rect(
                self.xOffset + x,
                self.height - (y + self.yOffset),
                1,
                1,
                outline=c,
                stroke=1,
            )
        )

    def drawLine(self, x, y, x2, y2, c):
        self.display.append(
            Line(
                self.xOffset + x,
                self.height - (y + self.yOffset),
                self.xOffset + x2,
                self.height - (y2 + self.yOffset),
                c,
            )
        )

    def drawFillRect(self, x, y, w, h, c):
        self.display.append(
            Rect(
                self.xOffset + x,
                self.height - (y + self.yOffset),
                w,
                h,
                fill=c,
                stroke=0,
            )
        )

    def DrawColon(self, c):
        #   // Colon is drawn to the left of this digit
        self.drawFillRect(-3, self.segHeight - 1, 2, 2, c)
        self.drawFillRect(-3, self.segHeight + 1 + 3, 2, 2, c)

    def drawSeg(self, seg):
        if seg == self.sA:
            self.drawLine(
                1,
                self.segHeight * 2 + 2,
                self.segWidth,
                self.segHeight * 2 + 2,
                self.color,
            )
        elif seg == self.sB:
            self.drawLine(
                self.segWidth + 1,
                self.segHeight * 2 + 1,
                self.segWidth + 1,
                self.segHeight + 2,
                self.color,
            )
        elif seg == self.sC:
            self.drawLine(
                self.segWidth + 1, 1, self.segWidth + 1, self.segHeight, self.color
            )
        elif seg == self.sD:
            self.drawLine(1, 0, self.segWidth, 0, self.color)
        elif seg == self.sE:
            self.drawLine(0, 1, 0, self.segHeight, self.color)
        elif seg == self.sF:
            self.drawLine(0, self.segHeight * 2 + 1, 0, self.segHeight + 2, self.color)
        elif seg == self.sG:
            self.drawLine(
                1, self.segHeight + 1, self.segWidth, self.segHeight + 1, self.color
            )

    def Draw(self, value):
        pattern = self.digitBits[value]
        if pattern[0] == "1":
            self.drawSeg(self.sA)
        if pattern[1] == "1":
            self.drawSeg(self.sB)
        if pattern[2] == "1":
            self.drawSeg(self.sC)
        if pattern[3] == "1":
            self.drawSeg(self.sD)
        if pattern[4] == "1":
            self.drawSeg(self.sE)
        if pattern[5] == "1":
            self.drawSeg(self.sF)
        if pattern[6] == "1":
            self.drawSeg(self.sG)
        self.value = value

    def Morph2(self):
        #   // TWO
        for i in range(self.segWidth + 1):
            if i < self.segWidth:
                self.drawPixel(self.segWidth - i, self.segHeight * 2 + 2, self.color)
                self.drawPixel(self.segWidth - i, self.segHeight + 1, self.color)
                self.drawPixel(self.segWidth - i, 0, self.color)

            self.drawLine(
                self.segWidth + 1 - i,
                1,
                self.segWidth + 1 - i,
                self.segHeight,
                self.black,
            )
            self.drawLine(
                self.segWidth - i, 1, self.segWidth - i, self.segHeight, self.color
            )
            time.sleep(self.animSpeed)

    def Morph3(self):
        #   // THREE
        for i in range(self.segWidth + 1):
            self.drawLine(0 + i, 1, 0 + i, self.segHeight, self.black)
            self.drawLine(1 + i, 1, 1 + i, self.segHeight, self.color)
            time.sleep(self.animSpeed)

    def Morph4(self):
        #   // FOUR
        for i in range(self.segWidth):
            self.drawPixel(
                self.segWidth - i, self.segHeight * 2 + 2, self.black
            )  # // Erase A
            self.drawPixel(0, self.segHeight * 2 + 1 - i, self.color)  # // Draw as F
            self.drawPixel(1 + i, 0, self.black)  # // Erase D
            time.sleep(self.animSpeed)
