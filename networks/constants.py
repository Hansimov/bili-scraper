REQUESTS_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}

GET_VIDEO_PAGE_API = "http://api.bilibili.com/x/web-interface/newlist"

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
                "name": "科学科普",
                "tid": 201,
            },
            "social_science": {
                "name": "社科·法律·心理",
                "tid": 124,
            },
            "humanity_history": {
                "name": "人文历史",
                "tid": 228,
            },
            "business": {
                "name": "财经商业",
                "tid": 207,
            },
            "campus": {
                "name": "校园学习",
                "tid": 208,
            },
            "career": {
                "name": "职业职场",
                "tid": 209,
            },
            "design": {
                "name": "设计·创意",
                "tid": 229,
            },
            "skill": {
                "name": "野生技术协会",
                "tid": 122,
            },
            "speech_course": {
                "name": "演讲·公开课",
                "tid": 39,
                "status": "offline",
            },
            "military": {
                "name": "星海",
                "tid": 96,
                "status": "offline",
            },
            "mechanical": {
                "name": "机械",
                "tid": 98,
                "status": "offline",
            },
        },
    },
    "tech": {
        "name": "科技",
        "tid": 188,
        "children": {
            "digital": {
                "name": "数码",
                "tid": 95,
            },
            "application": {
                "name": "软件应用",
                "tid": 230,
            },
            "computer_tech": {
                "name": "计算机技术",
                "tid": 231,
            },
            "industry": {
                "name": "科工机械",
                "tid": 232,
            },
            "diy": {
                "name": "极客DIY",
                "tid": 233,
            },
            "pc": {
                "name": "电脑装机",
                "tid": 189,
                "status": "offline",
            },
            "photography": {
                "name": "摄影摄像",
                "tid": 190,
                "status": "offline",
            },
            "intelligence_av": {
                "name": "影音智能",
                "tid": 191,
                "status": "offline",
            },
        },
    },
    "sports": {
        "name": "运动",
        "tid": 234,
        "children": {
            "basketball": {
                "name": "篮球",
                "tid": 235,
            },
            "football": {
                "name": "足球",
                "tid": 249,
            },
            "aerobics": {
                "name": "健身",
                "tid": 164,
            },
            "athletic": {
                "name": "竞技体育",
                "tid": 236,
            },
            "culture": {
                "name": "运动文化",
                "tid": 237,
            },
            "comprehensive": {
                "name": "运动综合",
                "tid": 238,
            },
        },
    },
    "car": {
        "name": "汽车",
        "tid": 223,
        "children": {
            "knowledge": {
                "name": "汽车知识科普",
                "tid": 258,
            },
            "racing": {
                "name": "赛车",
                "tid": 245,
            },
            "modifiedvehicle": {
                "name": "改装玩车",
                "tid": 246,
            },
            "newenergyvehicle": {
                "name": "新能源车",
                "tid": 247,
            },
            "touringcar": {
                "name": "房车",
                "tid": 248,
            },
            "motorcycle": {
                "name": "摩托车",
                "tid": 240,
            },
            "strategy": {
                "name": "购车攻略",
                "tid": 227,
            },
            "life": {
                "name": "汽车生活",
                "tid": 176,
            },
            "culture": {
                "name": "汽车文化",
                "tid": 224,
                "status": "offline",
            },
            "geek": {
                "name": "汽车极客",
                "tid": 225,
                "status": "offline",
            },
            "smart": {
                "name": "智能出行",
                "tid": 226,
                "status": "offline",
            },
        },
    },
    "life": {
        "name": "生活",
        "tid": 160,
        "children": {
            "funny": {
                "name": "搞笑",
                "tid": 138,
            },
            "travel": {
                "name": "出行",
                "tid": 250,
            },
            "rurallife": {
                "name": "三农",
                "tid": 251,
            },
            "home": {
                "name": "家居房产",
                "tid": 239,
            },
            "handmake": {
                "name": "手工",
                "tid": 161,
            },
            "painting": {
                "name": "绘画",
                "tid": 162,
            },
            "daily": {
                "name": "日常",
                "tid": 21,
            },
            "parenting": {
                "name": "亲子",
                "tid": 254,
            },
            "food": {
                "name": "美食圈",
                "tid": 76,
                "status": "redirect",
            },
            "animal": {
                "name": "动物圈",
                "tid": 75,
                "status": "redirect",
            },
            "sports": {
                "name": "运动",
                "tid": 163,
                "status": "redirect",
            },
            "automobile": {
                "name": "汽车",
                "tid": 176,
                "status": "redirect",
            },
            "other": {
                "name": "其他",
                "tid": 174,
                "status": "offline",
            },
        },
    },
    "food": {
        "name": "美食",
        "tid": 211,
        "children": {
            "make": {
                "name": "美食制作",
                "tid": 76,
            },
            "detective": {
                "name": "美食侦探",
                "tid": 212,
            },
            "measurement": {
                "name": "美食测评",
                "tid": 213,
            },
            "rural": {
                "name": "田园美食",
                "tid": 214,
            },
            "record": {
                "name": "美食记录",
                "tid": 215,
            },
        },
    },
    "animal": {
        "name": "动物圈",
        "tid": 217,
        "children": {
            "cat": {
                "name": "喵星人",
                "tid": 218,
            },
            "dog": {
                "name": "汪星人",
                "tid": 219,
            },
            "second_edition": {
                "name": "动物二创",
                "tid": 220,
            },
            "wild_animal": {
                "name": "野生动物",
                "tid": 221,
            },
            "reptiles": {
                "name": "小宠异宠",
                "tid": 222,
            },
            "animal_composite": {
                "name": "动物综合",
                "tid": 75,
            },
        },
    },
    "kichiku": {
        "name": "鬼畜",
        "tid": 119,
        "children": {
            "guide": {
                "name": "鬼畜调教",
                "tid": 22,
            },
            "mad": {
                "name": "音MAD",
                "tid": 26,
            },
            "manual_vocaloid": {
                "name": "人力VOCALOID",
                "tid": 126,
            },
            "theatre": {
                "name": "鬼畜剧场",
                "tid": 216,
            },
            "course": {
                "name": "教程演示",
                "tid": 127,
            },
        },
    },
    "fashion": {
        "name": "时尚",
        "tid": 155,
        "children": {
            "makeup": {
                "name": "美妆护肤",
                "tid": 157,
            },
            "cos": {
                "name": "仿妆cos",
                "tid": 252,
            },
            "clothing": {
                "name": "穿搭",
                "tid": 158,
            },
            "catwalk": {
                "name": "时尚潮流",
                "tid": 159,
            },
            "aerobics": {
                "name": "健身",
                "tid": 164,
                "status": "redirect",
            },
            "trends": {
                "name": "风尚标",
                "tid": 192,
                "status": "offline",
            },
        },
    },
    "information": {
        "name": "资讯",
        "tid": 202,
        "children": {
            "hotspot": {
                "name": "热点",
                "tid": 203,
            },
            "global": {
                "name": "环球",
                "tid": 204,
            },
            "social": {
                "name": "社会",
                "tid": 205,
            },
            "multiple": {
                "name": "综合",
                "tid": 206,
            },
        },
    },
    "ad": {
        "name": "广告",
        "tid": 165,
        "children": {
            "ad": {
                "name": "广告",
                "tid": 166,
            },
        },
    },
    "ent": {
        "name": "娱乐",
        "tid": 5,
        "children": {
            "variety": {
                "name": "综艺",
                "tid": 71,
            },
            "talker": {
                "name": "娱乐杂谈",
                "tid": 241,
            },
            "fans": {
                "name": "粉丝创作",
                "tid": 242,
            },
            "celebrity": {
                "name": "明星综合",
                "tid": 137,
            },
            "korea": {
                "name": "Korea相关",
                "tid": 131,
                "status": "offline",
            },
        },
    },
    "cinephile": {
        "name": "影视",
        "tid": 181,
        "children": {
            "cinecism": {
                "name": "影视杂谈",
                "tid": 182,
            },
            "montage": {
                "name": "影视剪辑",
                "tid": 183,
            },
            "shortplay": {
                "name": "小剧场",
                "tid": 85,
            },
            "trailer_info": {
                "name": "预告·资讯",
                "tid": 184,
            },
            "shortfilm": {
                "name": "短片",
                "tid": 256,
            },
        },
    },
    "documentary": {
        "name": "纪录片",
        "tid": 177,
        "children": {
            "history": {
                "name": "人文·历史",
                "tid": 37,
            },
            "science": {
                "name": "科学·探索·自然",
                "tid": 178,
            },
            "military": {
                "name": "军事",
                "tid": 179,
            },
            "travel": {
                "name": "社会·美食·旅行",
                "tid": 180,
            },
        },
    },
    "movie": {
        "name": "电影",
        "tid": 23,
        "children": {
            "tid": {
                "name": "华语电影",
                "tid": 23,
            },
            "chinese": {
                "name": "欧美电影",
                "tid": 147,
            },
            "west": {
                "name": "欧美电影",
                "tid": 145,
            },
            "japan": {
                "name": "日本电影",
                "tid": 146,
            },
            "movie": {
                "name": "其他国家",
                "tid": 83,
            },
        },
    },
    "tv": {
        "name": "电视剧",
        "tid": 11,
        "children": {
            "mainland": {
                "name": "国产剧",
                "tid": 185,
            },
            "overseas": {
                "name": "海外剧",
                "tid": 187,
            },
        },
    },
}

REGION_GROUPS = {
    "animes": ["douga", "anime", "guochuang"],
    "arts": ["music", "dance"],
    "learns": ["knowledge", "tech", "documentary"],
    "mans": ["game", "sports", "car"],
    "lifes": ["life", "food", "animal"],
    "clips": ["kichiku", "cinephile"],
    "fashions": ["fashion", "ent"],
    "infos": ["information", "ad"],
    "tvs": ["movie", "tv"],
}
