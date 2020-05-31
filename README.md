
# SatMaps

- [Project Structure](#project-structure)
- [Project Setup](#project-setup)
- [Project description](#proj-des)
- [To-Do](#to-do)
- [Licensing](#licensing)

<a name="project-structure"></a>
## 1. Project Structure
The following project structure is proposed (suggestions are welcome)

```
satmaps
  ├── SatMaps
  |   ├── Maps.py
  |   ├── TileMachine.py
  |   ├── TileDownloader.py
  |   ├── TileStitcher.py  
  ├── src  
  |   ├── main.py
  ├── data
  ├── notebook
```

N.B. Make sure you are inside the git project folder before running the above command.


<a name="project-setup"></a>
## 2. Project Setup

The project can be used in two ways:

### 2.1 PIP Wheel Install
Install using the wheel file provided using:

Step 1: ```pip install dist/"wheel package name"``` #Install using pip <br />

### 2.2 Conda Environment Install
To setup the virtual environment for this project do the following steps:

Step 1: ```cd jiomaps``` #Enter the project folder! <br />
Step 2: ```conda env create -f envs/jiomaps.yml``` #create the virtual environment from the yml file provided. <br />
Step 3: ```conda activate jiomaps``` #activate the virtual env.

<a name="proj-des"></a>
## 3. Project description
The downloader script is ```src/main.py``` <br />

      ```python src/main.py test_hyd --southwest=17.455242,78.364024 --northeast=17.455702,78.365357 --raster_path=test_hyd.tif```

* This is a sample command to check the download of a very small region of Hyderabad

<a name="to-do"></a>
## 4. To-Do

- [✔] Logo cropping
- [✔] Auto max zoom level
- [x] No image resolution
- [✔] Georeferencing issues
- [✔] TIF optimisation
- [✔] No tile downloaded handling

<a name="licensing"></a>
## 5. Licensing
Apache License 2.0
