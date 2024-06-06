# API format


## APIs

视频分区一览：
- https://socialsisteryi.github.io/bilibili-API-collect/docs/video/video_zone.html


获取视频详细信息(web端)：

- https://socialsisteryi.github.io/bilibili-API-collect/docs/video/info.html#%E8%8E%B7%E5%8F%96%E8%A7%86%E9%A2%91%E8%AF%A6%E7%BB%86%E4%BF%A1%E6%81%AF-web%E7%AB%AF

获取视频超详细信息(web端)：

- https://socialsisteryi.github.io/bilibili-API-collect/docs/video/info.html#%E8%8E%B7%E5%8F%96%E8%A7%86%E9%A2%91%E8%B6%85%E8%AF%A6%E7%BB%86%E4%BF%A1%E6%81%AF-web%E7%AB%AF

查询用户投稿视频明细：

- https://socialsisteryi.github.io/bilibili-API-collect/docs/user/space.html#%E6%9F%A5%E8%AF%A2%E7%94%A8%E6%88%B7%E6%8A%95%E7%A8%BF%E8%A7%86%E9%A2%91%E6%98%8E%E7%BB%86

## `x/web-interface/newlist`

API example:

- http://api.bilibili.com/x/web-interface/newlist
- params: `rid`, `pn`, `ps`

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

## `x/space/wbi/arc/search`

API example:

- https://api.bilibili.com/x/space/wbi/arc/search
- params: `mid`, `pn`, `ps`, `wts`, `w_rid`

```json
{
    "code": 0,
    "message": "0",
    "ttl": 1,
    "data": {
        "list": {
            "tlist": {
                ...,
                "160": {
                    "tid": 160,
                    "count": 85,
                    "name": "生活"
                },
                ...
            },
            "vlist": [
                // video without "meta"
                {
                    "comment": 916,
                    "typeid": 95,
                    "play": 295776,
                    "pic": "http://i0.hdslb.com/bfs/archive/96449f235cca9ede3a0f643623c0515153ceee20.jpg",
                    "subtitle": "",
                    "description": "时隔好几年，我们再次来到了法国！这一次我们探访了著名的雅顾摄影工作室，也亲身体验了一次价值2万元的人像拍摄。他们有什么拍摄秘诀？有哪些经验是可以学习的？欢迎和我们一起来看看～如果你喜欢这样的节目，请多多支持我们，并把视频分享给其他人看看！\n节目中拍摄的一些动态影像素材我们也已经上传到了影视飓风官网（ysjf.com），欢迎大家前往下载使用。",
                    "copyright": "1",
                    "title": "去了一趟法国。",
                    "review": 0,
                    "author": "影视飓风",
                    "mid": 946974,
                    "created": 1717416000,
                    "length": "20:51",
                    "video_review": 3603,
                    "aid": 1255271796,
                    "bvid": "BV1DJ4m137TV",
                    "hide_click": false,
                    "is_pay": 0,
                    "is_union_video": 0,
                    "is_steins_gate": 0,
                    "is_live_playback": 0,
                    "is_lesson_video": 0,
                    "is_lesson_finished": 0,
                    "lesson_update_info": "",
                    "jump_url": "",
                    "meta": null,
                    "is_avoided": 0,
                    "season_id": 0,
                    "attribute": 16768,
                    "is_charging_arc": false,
                    "vt": 0,
                    "enable_vt": 0,
                    "vt_display": "",
                    "playback_position": 0
                },
                ...
                // video with "meta"
                {
                    "comment": 1730,
                    "typeid": 21,
                    "play": 1972241,
                    "pic": "http://i2.hdslb.com/bfs/archive/21e2d168324d0e248b989244d438555a6420f89c.jpg",
                    "subtitle": "",
                    "description": "之前新场地介绍的节目中提过我们还有很多可以改进的地方，其中有些问题令我们很头大，恰好迷瞪搬来了我们隔壁，于是就有了这期改造视频～如果你喜欢这期视频，请多多支持我们，并将视频分享给其他有需要的朋友！",
                    "copyright": "1",
                    "title": "【UP主改我计划】影视飓风摸鱼新地点？",
                    "review": 0,
                    "author": "影视飓风",
                    "mid": 946974,
                    "created": 1706703000,
                    "length": "16:14",
                    "video_review": 8468,
                    "aid": 1800205549,
                    "bvid": "BV1at421H7dK",
                    "hide_click": false,
                    "is_pay": 0,
                    "is_union_video": 1,
                    "is_steins_gate": 0,
                    "is_live_playback": 0,
                    "is_lesson_video": 0,
                    "is_lesson_finished": 0,
                    "lesson_update_info": "",
                    "jump_url": "",
                    "meta": {
                        "id": 2159611,
                        "title": "UP主改我计划",
                        "cover": "https://archive.biliimg.com/bfs/archive/21e2d168324d0e248b989244d438555a6420f89c.jpg",
                        "mid": 946974,
                        "intro": "",
                        "sign_state": 0,
                        "attribute": 140,
                        "stat": {
                            "season_id": 2159611,
                            "view": 5848977,
                            "danmaku": 17297,
                            "reply": 4566,
                            "favorite": 61389,
                            "coin": 132094,
                            "share": 24511,
                            "like": 377199,
                            "mtime": 1717614337,
                            "vt": 0,
                            "vv": 0
                        },
                        "ep_count": 2,
                        "first_aid": 1800205549,
                        "ptime": 1710331425,
                        "ep_num": 2
                    },
                    "is_avoided": 0,
                    "season_id": 2159611,
                    "attribute": 16793984,
                    "is_charging_arc": false,
                    "vt": 0,
                    "enable_vt": 0,
                    "vt_display": "",
                    "playback_position": 0
                },
                ...
            ],
            "slist": []
        },
        "page": {
            "pn": 1,
            "ps": 3,
            "count": 702
        },
        "episodic_button": {
            "text": "播放全部",
            "uri": "//www.bilibili.com/medialist/play/946974?from=space"
        },
        "is_risk": false,
        "gaia_res_type": 0,
        "gaia_data": null
    }
}