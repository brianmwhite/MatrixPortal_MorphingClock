
import adafruit_fancyled.adafruit_fancyled as fancy

start_color_hex = 0x000714
end_color_hex = 0x0000FF
number_of_colors = 100

start_color = fancy.unpack(start_color_hex)
end_color = fancy.unpack(end_color_hex)

gradient = [(0.0, start_color),(1.0, end_color)]
palette = fancy.expand_gradient(gradient, number_of_colors)

np = []
# np.append(start_color.pack())

for i in range(1,number_of_colors-1):
    color = fancy.CRGB(palette[i][0], palette[i][1], palette[i][2])
    np.append(color.pack())

np.append(end_color.pack())

print(np)
