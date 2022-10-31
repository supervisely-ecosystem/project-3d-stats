<div align="center" markdown>

<img src="https://github.com/supervisely-ecosystem/project-3d-stats/releases/download/v0.0.0/poster_3d_stats.png"/>

# Project 3D statistics

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#How-to-Use">How to use</a> •
  <a href="#Screenshot">Screenshot</a>
</p>

[![](https://img.shields.io/badge/supervisely-ecosystem-brightgreen)](https://ecosystem.supervise.ly/apps/supervisely-ecosystem/project-3d-stats)
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/project-3d-stats)
[![views](https://app.supervise.ly/img/badges/views/supervisely-ecosystem/project-3d-stats)](https://supervise.ly)
[![runs](https://app.supervise.ly/img/badges/runs/supervisely-ecosystem/project-3d-stats.png)](https://supervise.ly)

</div>

# Overview

Application generates report with detailed general and per pointcloud statistics for all classes in pointcloud and episodes project.

# How to use

1. Run application from the context menu of pointcloud/episodes project
2. Open app
3. **Step 1** shows the information about selected dataset with links to project / dataset. Click `DOWNLOAD PROJECT AND CALCULATE STATS` button and wait until all tables are displayed.
4. Look at the statistics from the tables at **Steps 2-5**, get the information you need
5. Stop the app manually

# Some columns of Tables

### 1. **POINTCLOUDS** table
- **RELATED IMAGES COUNT** - Photocontext images count of pointcloud (see in Labeling tool from **LINK** column)
- **TAGS** - Tags of pointcloud (objects tags not included). 
- **SIZE X/Y/Z** - Pointcloud width, length and height (difference between max point coordinate value along the axis and min point coordinate value). 
- **MIN/MAX X/Y/Z** - Min or max point coordinate value along the axis X, Y or Z.

### 2. **CLASSES** table
- **POINTCLOUDS COUNT** - Number of pointclouds containing at least one figure of class.
- **AVERAGE SIZE X/Y/Z** - Average width, length and height of class figures.
- **POSITION X/Y/Z MIN/MAX** - Min or max coordinate value of class figures center along the axis X, Y or Z.

### 3. **LABELS** table
- **VOLUME** - Figure volume (width * length * height).
- **POINTS INSIDE** - Number of points of pointcloud inside the figure.
- **SIZE X/Y/Z** - Figure width, length and height.
- **POSITION X/Y/Z** - Center of figure coordinates.
- **ROTATION DX/DY/DZ** - Rotation around the axis X,Y or Z [-pi; +pi] 

### 4. **DATASETS** table
- **AVERAGE SIZE X/Y/Z** - Average point cloud width, length and height in the dataset (average difference between max point coordinate value along the axis and min point coordinate value).
- **AVERAGE MIN/MAX X/Y/Z** - Average min or max point coordinates value along the axis X, Y or Z.

# Screenshot

<img src="https://user-images.githubusercontent.com/97401023/199076648-690a659c-124d-4529-ac56-097a2fa907d1.png">
