# Bili-Scraper
Scrape data of videos and users from Bilibili

## APIs

Regions:

- https://socialsisteryi.github.io/bilibili-API-collect/docs/video/video_zone.html
- https://socialsisteryi.github.io/bilibili-API-collect/docs/video/info.html#%E8%8E%B7%E5%8F%96%E8%A7%86%E9%A2%91%E8%AF%A6%E7%BB%86%E4%BF%A1%E6%81%AF-web%E7%AB%AF


## APPs

Proxy App:
- http://127.0.0.1:19001

```sh
python -m apps.proxy_app
```

Worker App:
- http://127.0.0.1:19002

```sh
python -m apps.worker_app
```


## JSON format

JSON fields:

- http://api.bilibili.com/x/web-interface/newlist?rid=95&pn=1&ps=50

```json
{
  "code": 0,
  "message": "0",
  "ttl": 1,
  "data": {
    "archives": [
      {
        "aid": 1602543614,
        "videos": 1,
        "tid": 95,
        "tname": "数码",
        "copyright": 1,
        "pic": "http://i1.hdslb.com/bfs/archive/07e8c7c89a393e0a21aea407b49111b0e631a383.jpg",
        "title": "大型记录片之内存都去哪了",
        "pubdate": 1712072080,
        "ctime": 1712071277,
        "desc": "-",
        "state": 0,
        "duration": 43,
        "rights": {
          ...
        },
        "owner": {
          "mid": 456757463,
          "name": "缺氧XD",
          "face": "https://i2.hdslb.com/bfs/face/6eec4ebed3e4562f7285bc60923611c6a5ca44c7.jpg"
        },
        "stat": {
          "aid": 1602543614,
          "view": 0,
          "danmaku": 0,
          "reply": 0,
          "favorite": 0,
          "coin": 0,
          "share": 0,
          "now_rank": 0,
          "his_rank": 0,
          "like": 0,
          "dislike": 0,
          "vt": 0,
          "vv": 0
        },
        "dynamic": "",
        "cid": 1491380610,
        "dimension": {
          "width": 720,
          "height": 1600,
          "rotate": 0
        },
        "short_link_v2": "https://b23.tv/BV1hm421E7mD",
        "up_from_v2": 35,
        "first_frame": "http://i0.hdslb.com/bfs/storyff/n240402sa2gbxxrw72vvn3ple2vhoqbn_firsti.jpg",
        "pub_location": "山东",
        "cover43": "",
        "bvid": "BV1hm421E7mD",
        "season_type": 0,
        "is_ogv": false,
        "ogv_info": null,
        "rcmd_reason": "",
        "enable_vt": 0,
        "ai_rcmd": null
      },
      ...
    ],
    "page": {
      "count": 4464037,
      "num": 1,
      "size": 5
    }
  }
}
```