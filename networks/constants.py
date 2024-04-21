REQUESTS_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}


# https://socialsisteryi.github.io/bilibili-API-collect/docs/video/video_zone.html
REGION_CODES = {
    "douga": {
        "name": "动画",
        "tid": 1,
        "children": {
            "mad": {
                "name": "MAD·AMV",
                "tid": 24,
            },
            "mmd": {
                "name": "MMD·3D",
                "tid": 25,
            },
            "handdrawn": {
                "name": "短片·手书",
                "tid": 47,
            },
            "voice": {
                "name": "配音",
                "tid": 257,
            },
            "garage_kit": {
                "name": "手办·模玩",
                "tid": 210,
            },
            "tokusatsu": {
                "name": "特摄",
                "tid": 86,
            },
            "acgntalks": {
                "name": "动漫杂谈",
                "tid": 253,
            },
            "other": {
                "name": "综合",
                "tid": 27,
            },
        },
    },
    "anime": {
        "name": "番剧",
        "tid": 13,
        "children": {
            "information": {
                "name": "资讯",
                "tid": 51,
            },
            "offical": {
                "name": "官方延伸",
                "tid": 152,
            },
            "finish": {
                "name": "完结动画",
                "tid": 32,
            },
            "serial": {
                "name": "连载动画",
                "tid": 33,
            },
        },
    },
    "guochuang": {
        "name": "国创",
        "tid": 167,
        "children": {
            "chinese": {
                "name": "国产动画",
                "tid": 153,
            },
            "original": {
                "name": "国产原创相关",
                "tid": 168,
            },
            "puppetry": {
                "name": "布袋戏",
                "tid": 169,
            },
            "information": {
                "name": "资讯",
                "tid": 170,
            },
            "motioncomic": {
                "name": "动态漫·广播剧",
                "tid": 195,
            },
        },
    },
    "music": {
        "name": "音乐",
        "tid": 3,
        "children": {
            "original": {
                "name": "原创音乐",
                "tid": 28,
            },
            "cover": {
                "name": "翻唱",
                "tid": 31,
            },
            "vocaloid": {
                "name": "VOCALOID·UTAU",
                "tid": 30,
            },
            "perform": {
                "name": "演奏",
                "tid": 59,
            },
            "mv": {
                "name": "MV",
                "tid": 193,
            },
            "live": {
                "name": "音乐现场",
                "tid": 29,
            },
            "other": {
                "name": "音乐综合",
                "tid": 130,
            },
            "commentary": {
                "name": "乐评盘点",
                "tid": 243,
            },
            "tutorial": {
                "name": "音乐教学",
                "tid": 244,
            },
            "electronic": {
                "name": "电音",
                "tid": 194,
                "status": "offline",
            },
        },
    },
    "dance": {
        "name": "舞蹈",
        "tid": 129,
        "children": {
            "otaku": {
                "name": "宅舞",
                "tid": 20,
            },
            "three_d": {
                "name": "舞蹈综合",
                "tid": 154,
            },
            "demo": {
                "name": "舞蹈教程",
                "tid": 156,
            },
            "hiphop": {
                "name": "街舞",
                "tid": 198,
            },
            "star": {
                "name": "明星舞蹈",
                "tid": 199,
            },
            "china": {
                "name": "国风舞蹈",
                "tid": 200,
            },
            "gestures": {
                "name": "手势·网红舞",
                "tid": 255,
            },
        },
    },
    "game": {
        "name": "游戏",
        "tid": 4,
        "children": {
            "stand_alone": {
                "name": "单机游戏",
                "tid": 17,
            },
            "esports": {
                "name": "电子竞技",
                "tid": 171,
            },
            "mobile": {
                "name": "手机游戏",
                "tid": 172,
            },
            "online": {
                "name": "网络游戏",
                "tid": 65,
            },
            "board": {
                "name": "桌游棋牌",
                "tid": 173,
            },
            "gmv": {
                "name": "GMV",
                "tid": 121,
            },
            "music": {
                "name": "音游",
                "tid": 136,
            },
            "mugen": {
                "name": "Mugen",
                "tid": 19,
            },
        },
    },
    "knowledge": {
        "name": "知识",
        "tid": 36,
        "children": {
            "science": {
                "name": "",
                "tid": 201,
            },
            "social_science": {
                "name": "",
                "tid": 124,
            },
            "humanity_history": {
                "name": "",
                "tid": 228,
            },
            "business": {
                "name": "",
                "tid": 207,
            },
            "campus": {
                "name": "",
                "tid": 208,
            },
            "career": {
                "name": "",
                "tid": 209,
            },
            "design": {
                "name": "",
                "tid": 229,
            },
            "skill": {
                "name": "",
                "tid": 122,
            },
            "speech_course": {
                "name": "",
                "tid": 39,
            },
            "military": {
                "name": "",
                "tid": 96,
            },
            "mechanical": {
                "name": "",
                "tid": 98,
            },
        },
    },
    "tech": {
        "name": "科技",
        "tid": 188,
        "children": {
            "digital": {
                "name": "",
                "tid": 95,
            },
            "application": {
                "name": "",
                "tid": 230,
            },
            "computer_tech": {
                "name": "",
                "tid": 231,
            },
            "industry": {
                "name": "",
                "tid": 232,
            },
            "design": {
                "name": "",
                "tid": 229,
            },
            "diy": {
                "name": "",
                "tid": 233,
            },
            "pc": {
                "name": "",
                "tid": 189,
            },
            "photography": {
                "name": "",
                "tid": 190,
            },
            "intelligence_av": {
                "name": "",
                "tid": 191,
            },
        },
    },
    "sports": {
        "name": "运动",
        "tid": 234,
        "children": {
            "basketball": {
                "name": "",
                "tid": 235,
            },
            "football": {
                "name": "",
                "tid": 249,
            },
            "aerobics": {
                "name": "",
                "tid": 164,
            },
            "athletic": {
                "name": "",
                "tid": 236,
            },
            "culture": {
                "name": "",
                "tid": 237,
            },
            "comprehensive": {
                "name": "",
                "tid": 238,
            },
        },
    },
    "car": {
        "name": "汽车",
        "tid": 223,
        "children": {
            "knowledge": {
                "name": "",
                "tid": 258,
            },
            "racing": {
                "name": "",
                "tid": 245,
            },
            "modifiedvehicle": {
                "name": "",
                "tid": 246,
            },
            "newenergyvehicle": {
                "name": "",
                "tid": 247,
            },
            "touringcar": {
                "name": "",
                "tid": 248,
            },
            "motorcycle": {
                "name": "",
                "tid": 240,
            },
            "strategy": {
                "name": "",
                "tid": 227,
            },
            "life": {
                "name": "",
                "tid": 176,
            },
            "culture": {
                "name": "",
                "tid": 224,
            },
            "geek": {
                "name": "",
                "tid": 225,
            },
            "smart": {
                "name": "",
                "tid": 226,
            },
        },
    },
    "life": {
        "name": "生活",
        "tid": 160,
        "children": {
            "funny": {
                "name": "",
                "tid": 138,
            },
            "travel": {
                "name": "",
                "tid": 250,
            },
            "rurallife": {
                "name": "",
                "tid": 251,
            },
            "home": {
                "name": "",
                "tid": 239,
            },
            "handmake": {
                "name": "",
                "tid": 161,
            },
            "painting": {
                "name": "",
                "tid": 162,
            },
            "daily": {
                "name": "",
                "tid": 21,
            },
            "parenting": {
                "name": "",
                "tid": 254,
            },
            "food": {
                "name": "",
                "tid": 76,
            },
            "animal": {
                "name": "",
                "tid": 75,
            },
            "sports": {
                "name": "",
                "tid": 163,
            },
            "automobile": {
                "name": "",
                "tid": 176,
            },
            "other": {
                "name": "",
                "tid": 174,
            },
        },
    },
    "food": {
        "name": "美食",
        "tid": 211,
        "children": {
            "make": {
                "name": "",
                "tid": 76,
            },
            "detective": {
                "name": "",
                "tid": 212,
            },
            "measurement": {
                "name": "",
                "tid": 213,
            },
            "rural": {
                "name": "",
                "tid": 214,
            },
            "record": {
                "name": "",
                "tid": 215,
            },
        },
    },
    "animal": {
        "name": "动物圈",
        "tid": 217,
        "children": {
            "cat": {
                "name": "",
                "tid": 218,
            },
            "dog": {
                "name": "",
                "tid": 219,
            },
            "second_edition": {
                "name": "",
                "tid": 220,
            },
            "wild_animal": {
                "name": "",
                "tid": 221,
            },
            "reptiles": {
                "name": "",
                "tid": 222,
            },
            "animal_composite": {
                "name": "",
                "tid": 75,
            },
        },
    },
    "kichiku": {
        "name": "鬼畜",
        "tid": 119,
        "children": {
            "guide": {
                "name": "",
                "tid": 22,
            },
            "mad": {
                "name": "",
                "tid": 26,
            },
            "manual_vocaloid": {
                "name": "",
                "tid": 126,
            },
            "theatre": {
                "name": "",
                "tid": 216,
            },
            "course": {
                "name": "",
                "tid": 127,
            },
        },
    },
    "fashion": {
        "name": "时尚",
        "tid": 155,
        "children": {
            "makeup": {
                "name": "",
                "tid": 157,
            },
            "cos": {
                "name": "",
                "tid": 252,
            },
            "clothing": {
                "name": "",
                "tid": 158,
            },
            "catwalk": {
                "name": "",
                "tid": 159,
            },
            "aerobics": {
                "name": "",
                "tid": 164,
            },
            "trends": {
                "name": "",
                "tid": 192,
            },
        },
    },
    "information": {
        "name": "资讯",
        "tid": 202,
        "children": {
            "hotspot": {
                "name": "",
                "tid": 203,
            },
            "global": {
                "name": "",
                "tid": 204,
            },
            "social": {
                "name": "",
                "tid": 205,
            },
            "multiple": {
                "name": "",
                "tid": 206,
            },
        },
    },
    "ad": {
        "name": "广告",
        "tid": 165,
        "children": {
            "ad": {
                "name": "",
                "tid": 166,
            },
        },
    },
    "ent": {
        "name": "娱乐",
        "tid": 5,
        "children": {
            "variety": {
                "name": "",
                "tid": 71,
            },
            "talker": {
                "name": "",
                "tid": 241,
            },
            "fans": {
                "name": "",
                "tid": 242,
            },
            "celebrity": {
                "name": "",
                "tid": 137,
            },
            "korea": {
                "name": "",
                "tid": 131,
            },
        },
    },
    "cinephile": {
        "name": "影视",
        "tid": 181,
        "children": {
            "cinecism": {
                "name": "",
                "tid": 182,
            },
            "montage": {
                "name": "",
                "tid": 183,
            },
            "shortplay": {
                "name": "",
                "tid": 85,
            },
            "trailer_info": {
                "name": "",
                "tid": 184,
            },
            "shortfilm": {
                "name": "",
                "tid": 256,
            },
        },
    },
    "documentary": {
        "name": "纪录片",
        "tid": 177,
        "children": {
            "history": {
                "name": "",
                "tid": 37,
            },
            "science": {
                "name": "",
                "tid": 178,
            },
            "military": {
                "name": "",
                "tid": 179,
            },
            "travel": {
                "name": "",
                "tid": 180,
            },
        },
    },
    "movie": {
        "name": "电影",
        "children": {
            "tid": {
                "name": "",
                "tid": 23,
            },
            "chinese": {
                "name": "",
                "tid": 147,
            },
            "west": {
                "name": "",
                "tid": 145,
            },
            "japan": {
                "name": "",
                "tid": 146,
            },
            "movie": {
                "name": "",
                "tid": 83,
            },
        },
    },
    "tv": {
        "name": "电视剧",
        "tid": 11,
        "children": {
            "mainland": {
                "name": "",
                "tid": 185,
            },
            "overseas": {
                "name": "",
                "tid": 187,
            },
        },
    },
}
