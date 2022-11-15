# digit morphing code ported from https://www.instructables.com/Morphing-Digital-Clock/
# https://github.com/hwiguna/HariFun_166_Morphing_Clock

# some code started from https://github.com/adafruit/Adafruit_Learning_System_Guides/blob/main/Metro_Matrix_Clock/code.py
# SPDX-FileCopyrightText: 2020 John Park for Adafruit Industries
# SPDX-License-Identifier: MIT

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

    #    -- A --
    #   |       |
    #   F       B
    #   |       |
    #    -- G --
    #   |       |
    #   E       C
    #   |       |
    #    -- D --

    black = 0

    def __init__(self, d, b, value, xo, yo, color):
        self.display = d
        self.bitmap = b
        self.value = value
        self.xOffset = xo
        self.yOffset = yo
        self.color = color
        pass

    def Value(self):
        return self.value

    def drawPixel(self, x, y, c):
        self.bitmap[self.xOffset + x, self.height - (y + self.yOffset)] = c

    def drawLine(self, x, y, x2, y2, c):
        step = 1

        x = self.xOffset + x
        y = self.height - (y + self.yOffset)
        x2 = self.xOffset + x2
        y2 = self.height - (y2 + self.yOffset)

        if x == x2:
            if y2 < y:
                step = -1
            for point in range(y, y2 + 1, step):
                self.bitmap[x, point] = c
        elif y == y2:
            if x2 < x:
                step = -1
            for point in range(x, x2 + 1, step):
                self.bitmap[point, y] = c

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
        pass

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
                self.segWidth + 1, 1, self.segWidth + 1, self.segHeight + 2, self.color
            )
        elif seg == self.sD:
            self.drawLine(1, 0, self.segWidth, 0, self.color)
        elif seg == self.sE:
            self.drawLine(0, 1, 0, self.segHeight + 2, self.color)
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
                self.segHeight + 2,
                self.black,
            )
            self.drawLine(
                self.segWidth - i, 1, self.segWidth - i, self.segHeight + 2, self.color
            )
            time.sleep(self.animSpeed)

    def Morph3(self):
        #   // THREE
        for i in range(self.segWidth + 1):
            self.drawLine(0 + i, 1, 0 + i, self.segHeight + 2, self.black)
            self.drawLine(1 + i, 1, 1 + i, self.segHeight + 2, self.color)
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

    def Morph5(self):
        #   // FIVE
        for i in range(self.segWidth):
            self.drawPixel(self.segWidth + 1, self.segHeight + 2 + i, self.black)
            # // Erase B
            self.drawPixel(self.segWidth - i, self.segHeight * 2 + 2, self.color)
            # // Draw as A
            self.drawPixel(self.segWidth - i, 0, self.color)
            # // Draw D
            time.sleep(self.animSpeed)

    def Morph6(self):
        #   // SIX
        for i in range(self.segWidth + 1):
            # // Move C right to left
            self.drawLine(
                self.segWidth - i, 1, self.segWidth - i, self.segHeight + 2, self.color
            )
            if i > 0:
                self.drawLine(
                    self.segWidth - i + 1,
                    1,
                    self.segWidth - i + 1,
                    self.segHeight + 2,
                    self.black,
                )
            time.sleep(self.animSpeed)

    def Morph7(self):
        #   // SEVEN
        for i in range(self.segWidth + 2):
            # // Move E left to right
            self.drawLine(0 + i - 1, 1, 0 + i - 1, self.segHeight + 2, self.black)
            self.drawLine(0 + i, 1, 0 + i, self.segHeight + 2, self.color)

            # // Move F left to right
            self.drawLine(
                0 + i - 1,
                self.segHeight * 2 + 1,
                0 + i - 1,
                self.segHeight + 2,
                self.black,
            )
            self.drawLine(
                0 + i, self.segHeight * 2 + 1, 0 + i, self.segHeight + 2, self.color
            )

            # // Erase D and G gradually
            self.drawPixel(1 + i, 0, self.black)  # // D
            self.drawPixel(1 + i, self.segHeight + 1, self.black)  # // G
            time.sleep(self.animSpeed)

    def Morph8(self):
        # // EIGHT
        for i in range(self.segWidth + 1):
            # // Move B right to left
            self.drawLine(
                self.segWidth - i,
                self.segHeight * 2 + 1,
                self.segWidth - i,
                self.segHeight + 2,
                self.color,
            )
            if i > 0:
                self.drawLine(
                    self.segWidth - i + 1,
                    self.segHeight * 2 + 1,
                    self.segWidth - i + 1,
                    self.segHeight + 2,
                    self.black,
                )

            # // Move C right to left
            self.drawLine(
                self.segWidth - i, 1, self.segWidth - i, self.segHeight + 2, self.color
            )
            if i > 0:
                self.drawLine(
                    self.segWidth - i + 1,
                    1,
                    self.segWidth - i + 1,
                    self.segHeight + 2,
                    self.black,
                )

            # // Gradually draw D and G
            if i < self.segWidth:
                self.drawPixel(self.segWidth - i, 0, self.color)  # // D
                self.drawPixel(
                    self.segWidth - i, self.segHeight + 1, self.color
                )  # // G

            time.sleep(self.animSpeed)

    def Morph9(self):
        # // NINE
        for i in range(self.segWidth + 2):
            # // Move E left to right
            self.drawLine(0 + i - 1, 1, 0 + i - 1, self.segHeight + 2, self.black)
            self.drawLine(0 + i, 1, 0 + i, self.segHeight + 2, self.color)
            time.sleep(self.animSpeed)

    def Morph0(self):
        # // ZERO
        for i in range(self.segWidth + 1):
            if self.value == 1:  # // If 1 to 0, slide B to F and E to C
                # // slide B to F
                self.drawLine(
                    self.segWidth - i,
                    self.segHeight * 2 + 1,
                    self.segWidth - i,
                    self.segHeight + 2,
                    self.color,
                )
                if i > 0:
                    self.drawLine(
                        self.segWidth - i + 1,
                        self.segHeight * 2 + 1,
                        self.segWidth - i + 1,
                        self.segHeight + 2,
                        self.black,
                    )

                # // slide E to C
                self.drawLine(
                    self.segWidth - i,
                    1,
                    self.segWidth - i,
                    self.segHeight + 2,
                    self.color,
                )
                if i > 0:
                    self.drawLine(
                        self.segWidth - i + 1,
                        1,
                        self.segWidth - i + 1,
                        self.segHeight + 2,
                        self.black,
                    )

                if i < self.segWidth:
                    self.drawPixel(
                        self.segWidth - i, self.segHeight * 2 + 2, self.color
                    )  # // Draw A
                if i < self.segWidth:
                    self.drawPixel(self.segWidth - i, 0, self.color)  # // Draw D

            if self.value == 2:  # // If 2 to 0, slide B to F and Flow G to C
                # // slide B to F
                self.drawLine(
                    self.segWidth - i,
                    self.segHeight * 2 + 1,
                    self.segWidth - i,
                    self.segHeight + 2,
                    self.color,
                )
                if i > 0:
                    self.drawLine(
                        self.segWidth - i + 1,
                        self.segHeight * 2 + 1,
                        self.segWidth - i + 1,
                        self.segHeight + 2,
                        self.black,
                    )

                self.drawPixel(
                    1 + i, self.segHeight + 1, self.black
                )  # // Erase G left to right
                if i < self.segWidth:
                    self.drawPixel(
                        self.segWidth + 1, self.segHeight - i, self.color
                    )  # // Draw C

            if self.value == 3:  # // B to F, C to E
                # // slide B to F
                self.drawLine(
                    self.segWidth - i,
                    self.segHeight * 2 + 1,
                    self.segWidth - i,
                    self.segHeight + 2,
                    self.color,
                )
                if i > 0:
                    self.drawLine(
                        self.segWidth - i + 1,
                        self.segHeight * 2 + 1,
                        self.segWidth - i + 1,
                        self.segHeight + 2,
                        self.black,
                    )

                # // Move C to E
                self.drawLine(
                    self.segWidth - i,
                    1,
                    self.segWidth - i,
                    self.segHeight + 2,
                    self.color,
                )
                if i > 0:
                    self.drawLine(
                        self.segWidth - i + 1,
                        1,
                        self.segWidth - i + 1,
                        self.segHeight + 2,
                        self.black,
                    )

                # // Erase G from right to left
                self.drawPixel(
                    self.segWidth - i, self.segHeight + 1, self.black
                )  # // G

            if self.value == 4:  # // If 4 to 0, we also need to slide F to B
                pass

            if self.value == 5:  # // If 5 to 0, we also need to slide F to B
                if i < self.segWidth:
                    if i > 0:
                        self.drawLine(
                            1 + i,
                            self.segHeight * 2 + 1,
                            1 + i,
                            self.segHeight + 2,
                            self.black,
                        )
                    self.drawLine(
                        2 + i,
                        self.segHeight * 2 + 1,
                        2 + i,
                        self.segHeight + 2,
                        self.color,
                    )

            if self.value == 5 or self.value == 9:  #  // If 9 or 5 to 0, Flow G into E
                if i < self.segWidth:
                    self.drawPixel(self.segWidth - i, self.segHeight + 1, self.black)
                if i < self.segWidth:
                    self.drawPixel(0, self.segHeight - i, self.color)

            time.sleep(self.animSpeed)

    def Morph1(self):
        # // Zero or two to One
        for i in range(self.segWidth + 2):
            # // Move E left to right
            self.drawLine(0 + i - 1, 1, 0 + i - 1, self.segHeight + 2, self.black)
            self.drawLine(0 + i, 1, 0 + i, self.segHeight + 2, self.color)

            # // Move F left to right
            self.drawLine(
                0 + i - 1,
                self.segHeight * 2 + 1,
                0 + i - 1,
                self.segHeight + 2,
                self.black,
            )
            self.drawLine(
                0 + i, self.segHeight * 2 + 1, 0 + i, self.segHeight + 2, self.color
            )

            # // Gradually Erase A, G, D
            self.drawPixel(1 + i, self.segHeight * 2 + 2, self.black)  # // A
            self.drawPixel(1 + i, 0, self.black)  # // D
            self.drawPixel(1 + i, self.segHeight + 1, self.black)  # // G

            time.sleep(self.animSpeed)

    def Morph(self, newValue):
        if newValue == 2:
            self.Morph2()
        elif newValue == 3:
            self.Morph3()
        elif newValue == 4:
            self.Morph4()
        elif newValue == 5:
            self.Morph5()
        elif newValue == 6:
            self.Morph6()
        elif newValue == 7:
            self.Morph7()
        elif newValue == 8:
            self.Morph8()
        elif newValue == 9:
            self.Morph9()
        elif newValue == 0:
            self.Morph0()
        elif newValue == 1:
            self.Morph1()
        self.value = newValue
