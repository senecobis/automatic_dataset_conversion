import os
from PIL import Image
import tqdm 



folder_path = '/data/storage/pellerito/MoonLanding/Malapert_crater/Cam2/image_left'
new_folder_path = '/data/storage/pellerito/MoonLanding/Malapert_crater/Cam2/image_left_png'

for file_name in tqdm.tqdm(os.listdir(folder_path)):
    if file_name.endswith('.ppm'):
        ppm_path = os.path.join(folder_path, file_name)
        png_path = os.path.join(new_folder_path, os.path.splitext(file_name)[0] + '.png')

        image = Image.open(ppm_path)
        image.save(png_path, 'PNG')

