# Bili-Scraper
Scrape data of videos and users from Bilibili

## APIs

Regions:

- https://socialsisteryi.github.io/bilibili-API-collect/docs/video/video_zone.html

## Storage Structure

```sh
.
└── regions/
    ├── douga/
    │   ├── 2009/
    │   │   ├── 2009_06.parquet
    │   │   ├── 2009_07.parquet
    │   │   ├── ...
    │   │   └── 2009_12.parquet
    │   ├── 2010/
    │   │   ├── 2010_01.parquet
    │   │   ├── ...
    │   │   └── 2010_12.parquet
    │   ├── ...
    │   └── 2024/
    │       └── ...
    ├── anime/
    ├── guochuang/
    ├── music/
    ├── dance/
    ├── game/
    ├── ...
    └── tv/
```