
import imageio
import os
import graphics

# this just makes a gif from the images in <project_directory>/gif

path = graphics.path
files = os.listdir(path)

with imageio.get_writer('example.gif', mode='I') as writer:
    for file in files:
        image = imageio.imread(path + file)
        writer.append_data(image)