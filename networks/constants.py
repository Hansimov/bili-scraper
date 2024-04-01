REQUESTS_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}


# https://socialsisteryi.github.io/bilibili-API-collect/docs/video/video_zone.html
REGION_CODES = {
    "动画": {
        # "douga": 1,
        "mad": 24,
        "mmd": 25,
        "handdrawn": 47,
        "voice": 257,
        "garage_kit": 210,
        "tokusatsu": 86,
        "acgntalks": 253,
        "other": 27,
    },
    "番剧": {
        # "anime": 13,
        "information": 51,
        "offical": 152,
        "finish": 32,
        "serial": 33,
    },
    "国创": {
        # "guochuang": 167,
        "chinese": 153,
        "original": 168,
        "puppetry": 169,
        "information": 170,
        "motioncomic": 195,
    },
    "音乐": {
        # "music": 3,
        "original": 28,
        "cover": 31,
        "vocaloid": 30,
        "perform": 59,
        "mv": 193,
        "live": 29,
        "other": 130,
        "commentary": 243,
        "tutorial": 244,
        "electronic": 194,  # dropped
    },
    "舞蹈": {
        # "dance": 129,
        "otaku": 20,
        "three_d": 154,
        "demo": 156,
        "hiphop": 198,
        "star": 199,
        "china": 200,
        "gestures": 255,
    },
    "游戏": {
        # "game": 4,
        "stand_alone": 17,
        "esports": 171,
        "mobile": 172,
        "online": 65,
        "board": 173,
        "gmv": 121,
        "music": 136,
        "mugen": 19,
    },
    "知识": {
        # "knowledge": 36,
        "science": 201,
        "social_science": 124,
        "humanity_history": 228,
        "business": 207,
        "campus": 208,
        "career": 209,
        "design": 229,
        "skill": 122,
        "speech_course": 39,  # dropped
        "military": 96,  # dropped
        "mechanical": 98,  # dropped
    },
    "科技": {
        "tech": 188,
        "digital": 95,
        "application": 230,
        "computer_tech": 231,
        "industry": 232,
        "design": 229,
        "diy": 233,
        "pc": 189,  # dropped
        "photography": 190,  # dropped
        "intelligence_av": 191,  # dropped
    },
    "运动": {
        # "sports": 234,
        "basketball": 235,
        "football": 249,
        "aerobics": 164,
        "athletic": 236,
        "culture": 237,
        "comprehensive": 238,
    },
    "汽车": {
        # "car": 223,
        "knowledge": 258,
        "racing": 245,
        "modifiedvehicle": 246,
        "newenergyvehicle": 247,
        "touringcar": 248,
        "motorcycle": 240,
        "strategy": 227,
        "life": 176,
        "culture": 224,  # dropped
        "geek": 225,  # dropped
        "smart": 226,  # dropped
    },
    "生活": {
        # "life": 160,
        "funny": 138,
        "travel": 250,
        "rurallife": 251,
        "home": 239,
        "handmake": 161,
        "painting": 162,
        "daily": 21,
        "parenting": 254,
        "food": 76,  # redirected
        "animal": 75,  # redirected
        "sports": 163,  # redirected
        "automobile": 176,  # redirected
        "other": 174,  # dropped
    },
    "美食": {
        # "food": 211,
        "make": 76,
        "detective": 212,
        "measurement": 213,
        "rural": 214,
        "record": 215,
    },
    "动物圈": {
        # "animal": 217,
        "cat": 218,
        "dog": 219,
        "second_edition": 220,
        "wild_animal": 221,
        "reptiles": 222,
        "animal_composite": 75,
    },
    "鬼畜": {
        # "kichiku": 119,
        "guide": 22,
        "mad": 26,
        "manual_vocaloid": 126,
        "theatre": 216,
        "course": 127,
    },
    "时尚": {
        # "fashion": 155,
        "makeup": 157,
        "cos": 252,
        "clothing": 158,
        "catwalk": 159,
        "aerobics": 164,  # redirected
        "trends": 192,  # dropped
    },
    "资讯": {
        # "information": 202,
        "hotspot": 203,
        "global": 204,
        "social": 205,
        "multiple": 206,
    },
    "广告": {
        # "ad": 165,
        "ad": 166,  # dropped
    },
    "娱乐": {
        # "ent": 5,
        "variety": 71,
        "talker": 241,
        "fans": 242,
        "celebrity": 137,
        "korea": 131,  # dropped
    },
    "影视": {
        # "cinephile": 181,
        "cinecism": 182,
        "montage": 183,
        "shortplay": 85,
        "trailer_info": 184,
        "shortfilm": 256,
    },
    "纪录片": {
        # "documentary": 177,
        "history": 37,
        "science": 178,
        "military": 179,
        "travel": 180,
    },
    "电影": {
        # "movie": 23,
        "chinese": 147,
        "west": 145,
        "japan": 146,
        "movie": 83,
    },
    "电视剧": {
        # "tv": 11,
        "mainland": 185,
        "overseas": 187,
    },
}
