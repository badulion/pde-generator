import imageio.v2 as iio
import os
import matplotlib.pyplot as plt
import numpy as np

def animate_solution(u_array: np.ndarray, output_path: str = "equation.gif"):

    os.makedirs("tmp", exist_ok=True)
    for i in range(len(u_array)):
        plt.imshow(u_array[i], vmin=-1, vmax=1)
        plt.colorbar()
        plt.savefig(f"tmp/{i}.png")
        plt.close()

    with iio.get_writer('equation.gif', mode='I') as writer:
        file_list = [f"tmp/{i}.png" for i in range(len(u_array))]
        for filename in file_list:
            image = iio.imread(filename)
            writer.append_data(image)

    # cleanup
    tmp_files = os.listdir("tmp")
    for file in tmp_files:
        os.remove(os.path.join("tmp", file))
    os.removedirs("tmp")