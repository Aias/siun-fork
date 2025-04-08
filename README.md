**Note:** This repository has been forked from the original `minyuanye/SIUN`. The dependencies have been updated to be compatible with Python 3.12. These updates were almost entirely vibe-coded via Gemini 2.5 Pro, and I can't make any promises about similar results on machines besides my own.

The readme below has been slightly modified to reflect these updates.

---

# Scale-Iterative Upscaling Network for Image Deblurring

by Minyuan Ye, Dong Lyu and Gengsheng Chen<br>
pdf [[main](https://ieeexplore.ieee.org/document/8963625)][[backup](http://lab.zhuzhuguowang.cn:36900/croxline/Paper/Scale-Iterative%20Upscaling%20Network%20for%20Image%20Deblurring.pdf)]

### One real example

![/comparisions/images_in_paper/real_building1_comparision.png](../master/comparisons/images_in_paper/Real_building1_comparison.png)<br>
(a) Result of Nah et al. (b) Result of Tao et al. (c) Result of Zhang et al. (d) Our result.
<br>

### Results on benchmark datasets

![/comparisions/images_in_paper/benchmark_comparison.png](../master/comparisons/images_in_paper/benchmark_comparison.png)<br>
From top to bottom are blurry input, deblurring results of Nah et al., Tao et al., Zhang et al. and ours.<br>
<br>

### Results on real-world blurred images

![/comparisions/images_in_paper/real_comparison.png](../master/comparisons/images_in_paper/real_comparison.png)<br>
From top to bottom are images restored by Pan et al., Nah et al., Tao et al., Zhang et al. and ours. As space limits, the original blurry images are omitted here.
They can be viewed in Lai dataset with their names, from left to right: boy_statue, pietro, street4 and text1.
<br>

## Prerequisites

-   Python 3.9-3.12 (tested with 3.12)
-   `pip` (Python package installer)
-   (Optional, for managing Python versions) `pyenv`
-   Refer to `/code/requirements.txt` for Python package dependencies.

<br>
## Installation & Setup

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/minyuanye/SIUN.git
    cd SIUN
    ```

2.  **Set up Python Environment (using Python 3.12 recommended):**

    -   If using `pyenv`, set the local version:
        ```bash
        # Ensure Python 3.12.x is installed (e.g., pyenv install 3.12.7)
        pyenv local 3.12.7
        ```
    -   Create a virtual environment:
        ```bash
        python -m venv venv
        ```

3.  **Activate the Virtual Environment:**

    -   **Important:** You must activate the environment in _each new terminal session_ before running the script.

    ```bash
    source venv/bin/activate
    ```

    _(Your prompt should now show `(venv)`)_

4.  **Install Dependencies:**
    ```bash
    pip install --upgrade pip # Recommended
    pip install -r code/requirements.txt
    ```

## Basic usage

**Important:** Ensure your virtual environment is activated (`source venv/bin/activate`) in your current terminal session before running any commands.

You can always add `--gpu=<gpu_id>` to specify GPU ID (not required for CPU execution). The default ID is 0.

1.  **Deblur a single image:**

    ```bash
    python code/deblur.py --apply --file-path '</path/to/your/image.png>' --iter <N>
    ```

    -   Replace `</path/to/your/image.png>` with the actual path to your input image.
    -   Replace `<N>` with the desired number of iterations (e.g., `4`, `6`). Higher numbers take longer but may improve quality.
    -   The output will be saved in the _same directory_ as the input file, with `_deblur<N>` added to the filename (e.g., `image_deblur6.png`).
    -   **Note on Image Size:** The script internally pads images so their height and width are multiples of 256 pixels (based on the training patch size). For potentially better results and fewer padding artifacts, consider resizing your input image to dimensions that are already multiples of 256 (e.g., 1024x768, 512x512) before running the script.

2.  **Deblur all images in a folder:**

    ```bash
    python code/deblur.py --apply --dir-path '</path/to/your/directory/>' --iter <N>
    ```

    -   Replace `</path/to/your/directory/>` with the path to the folder containing images.
    -   Replace `<N>` with the desired number of iterations.
    -   Outputs will be saved in the _same directory_ as the input images with the `_deblur<N>` suffix.
    -   _(Note: The original `--result-dir` argument is no longer used with this modification)_

3.  **Testing the model (Original Method):**

    ```bash
    python code/deblur.py --test
    ```

    -   Note: This command is intended for the GOPRO dataset and requires setting `test_directory_path` in `code/src/config.py`. Using Item 2 above is generally recommended for testing on custom images.

4.  **Training a new model (Original Method):**
    ```bash
    python code/deblur.py --train
    ```
    -   Requires removing existing model files in `code/model/` and setting `train_directory_path` in `code/src/config.py` to the GOPRO training set.
    -   After training, run `python code/deblur.py --verify`.

## Advanced usage

Please refer to the source code. Most configuration parameters are listed in '/code/src/config.py'.

## Citation

If you use any part of our code, or SIUN is useful for your research, please consider citing:

```bibtex
@ARTICLE{8963625,
author={M. {Ye} and D. {Lyu} and G. {Chen}},
journal={IEEE Access},
title={Scale-Iterative Upscaling Network for Image Deblurring},
year={2020},
volume={8},
number={},
pages={18316-18325},
keywords={Blind deblurring;curriculum learning;scale-iterative;upscaling network},
doi={10.1109/ACCESS.2020.2967823},
ISSN={2169-3536},
month={},}
```
