import os
import pandas as pd
# import open3d as o3d
from PIL import Image
from PIL.ImageOps import flip


def visualize2d(frame: pd.DataFrame, min_color:float, max_color: float, flip_img: bool = False) -> Image:
    # maybe: shift pixel grid to positive axis
    x_min = frame.min()['px']
    y_min = frame.min()['py']
    if x_min < 0:
        frame['px'] -= x_min
    if y_min < 0:
        frame['py'] -= y_min

    # normalize color to [0, 255]
    frame['color'] -= min_color
    frame['color'] /= max_color
    frame['color'] *= 255

    width = int(frame.max()['px'] + 1)
    height = int(frame.max()['py'] + 1)
    c_max = frame.max()['color']

    img = Image.new(mode='L', size=(width, height), color=0)
    for row in frame.itertuples():
        img.putpixel((int(row.px), int(row.py)), int(row.color))
    if flip_img:
        img = flip(img)
    return img


def visualize3d(frame: pd.DataFrame):
    intermediate_path = './point_cloud.png'
    pc_data = frame.loc[:, ['x', 'y', 'z']].drop_duplicates().to_numpy()

    # point_cloud = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(pc_data))
    # visualizer = o3d.visualization.Visualizer()
    # visualizer.create_window()
    # visualizer.add_geometry(point_cloud)
    # visualizer.poll_events()
    # visualizer.update_renderer()
    # visualizer.capture_screen_image(intermediate_path)
    # visualizer.destroy_window()
    #
    # img = Image.open(intermediate_path)
    # os.remove(intermediate_path)
    img = None
    return img


