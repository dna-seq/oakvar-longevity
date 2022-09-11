class PrsReport:
    prs = {}
    prs_names = ["PGS001298",
                 "PGS001017",
                 "PGS001185",
                 "PGS001252",
                 "PGS001833"
                 ]

    def init(self, reporter):
        self.parent = reporter

    def data_name(self):
        return "PRS"

    def data(self):
        return {"NAME":[], "SUM":[], "AVG":[], "COUNT":[]}

    def setup(self):
        for name in self.prs_names:
            self.prs[name] = {"sum":0, "count":0}

    def process_row(self, row):
        zygot = self.parent.get_value(row, 'vcfinfo__zygosity')
        for name in self.prs_names:
            weight = self.parent.get_value(row, 'prs__'+name)
            if weight is None or weight == "":
                continue

            weight = float(weight)

            if zygot == 'hom':
                weight = 2*weight

            self.prs[name]["sum"] += weight
            self.prs[name]["count"] += 1

    def end(self):
        for name in self.prs_names:
            if self.prs[name]["count"] > 0:
                self.parent.data["PRS"]["NAME"].append(name)
                self.parent.data["PRS"]["SUM"].append(self.prs[name]["sum"])
                self.parent.data["PRS"]["AVG"].append(self.prs[name]["sum"] / (self.prs[name]["count"] * 2))
                self.parent.data["PRS"]["COUNT"].append(self.prs[name]["count"])