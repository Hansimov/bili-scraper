from tclogger import logger

from networks.constants import REGION_CODES


class WorkerParamsGenerator:
    def __init__(
        self, tid: int = None, pn: int = None, ps: int = None, mock: bool = False
    ):
        self.tid = tid
        self.pn = pn
        self.ps = ps
        self.mock = mock
        self.init_tids()

    def init_tids(self):
        self.tid_idx = 0
        self.region_codes = ["game", "knowledge", "tech"]
        main_regions = [REGION_CODES[region_code] for region_code in self.region_codes]
        self.tids = [
            sub_region["tid"]
            for main_region in main_regions
            for sub_region in main_region["children"].values()
        ]
        logger.note(f"> Regions: {self.region_codes} => {len(self.tids)} sub-regions")

    def next(self, archieve_len: int = 0):
        if archieve_len > 0:
            pn += 1
        else:
            self.tid_idx += 1
            if self.tid_idx < len(self.tids):
                tid = self.tids[self.tid_idx]
                pn = 1
            else:
                tid = -1
                pn = -1
        return tid, pn
