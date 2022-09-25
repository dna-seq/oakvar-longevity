import sqlite3
from sqlite3 import Error
import os

SUM = "sum"
TOTAL = "total"
COUNT = "count"
TITLE = "title"
INVERS = "invers"


class PrsReport:
    # "PGS001298",
    # "PGS001017",
    # "PGS001185",
    # "PGS001252",
    "PGS001833"
    prs = {}
    prs_names = []#["PRS5"]
    sql_get_prs = """SELECT name, title, total, invers FROM prs;"""
    # sql_get_percentiles = """SELECT name, percent, value FROM percentiles, prs WHERE percentiles.prs_id = prs.id ORDER BY name, value"""



    def init(self, reporter):
        self.parent = reporter


    def data_name(self):
        return "PRS"


    def data(self):
        return {"NAME":[], "TITLE":[], "SUM":[], "AVG":[], "COUNT":[], "TOTAL":[], "PERCENT":[], "FRACTION":[], "INVERS":[]}


    # def setup_percentile(self):
    #     self.cursor.execute(self.sql_get_percentiles)
    #     rows = self.cursor.fetchall()
    #     for row in rows:
    #         self.prs[row[0]][PERCENT].append(row[1])
    #         self.prs[row[0]][VALUE].append(row[2])


    def setup(self):
        modules_path = os.path.dirname(__file__)
        sql_file = modules_path + "/data/prs.sqlite"
        if os.path.exists(sql_file):
            conn = sqlite3.connect(sql_file)
            self.cursor = conn.cursor()
            self.cursor.execute(self.sql_get_prs)
            rows = self.cursor.fetchall()
            for row in rows:
                self.prs_names.append(row[0])
                self.prs[row[0]] = {SUM: 0, COUNT: 0, TITLE:row[1], TOTAL:int(row[2]), INVERS:int(row[3])}


    def process_row(self, row):
        rsid = self.parent.get_value(row, 'dbsnp__rsid')
        if rsid is None:
            return
        alt = self.parent.get_value(row, 'base__alt_base')
        chrom = self.parent.get_value(row, 'base__chrom')
        # print(rsid, alt, chrom)
        query = f"SELECT prs.name, weights.weight FROM position, prs, weights WHERE chrom = '{chrom}' AND alt = '{alt}'" \
                f" AND rsid = '{rsid}' AND weights.posid = position.id AND weights.prsid = prs.id"
        # start = time.time_ns()
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        # print(rows)
        if len(rows) == 0:
            return

        zygot = self.parent.get_value(row, 'vcfinfo__zygosity')
        for name, weight in rows:
            weight = float(weight)
            if zygot == 'hom':
                weight = 2*weight

            self.prs[name][SUM] += weight
            self.prs[name][COUNT] += 1


    def get_percent(self, name, value):
        sql_get_percent = f"SELECT 'min', percent, max(value) FROM percentiles, prs WHERE percentiles.prs_id = prs.id AND prs.name = '{name}' AND value <= {value} UNION " \
                        f"SELECT 'max', percent, min(value) FROM percentiles, prs WHERE percentiles.prs_id = prs.id AND prs.name = '{name}' AND value >= {value}"
        self.cursor.execute(sql_get_percent)
        rows = self.cursor.fetchall()
        for row in rows:
            if row[0] == 'min':
                min_percent = row[1]
                min_value = row[2]
            if row[0] == 'max':
                max_percent = row[1]
                max_value = row[2]

        if min_value is None:
            return max_percent

        if max_value is None:
            return min_percent

        if abs(min_value - value) > abs(max_value - value):
            return max_percent
        else:
            return min_percent


    def end(self):
        for name in self.prs_names:
            avg = 0
            if self.prs[name][COUNT] > 0:
                avg = self.prs[name][SUM] / (self.prs[name][COUNT] * 2)
            self.parent.data["PRS"]["NAME"].append(name)
            self.parent.data["PRS"]["SUM"].append(self.prs[name][SUM])
            self.parent.data["PRS"]["AVG"].append(avg)
            self.parent.data["PRS"]["COUNT"].append(self.prs[name][COUNT])
            self.parent.data["PRS"]["TITLE"].append(self.prs[name][TITLE])
            self.parent.data["PRS"]["TOTAL"].append(self.prs[name][TOTAL])
            percent = self.get_percent(name, self.prs[name][SUM])
            if type(percent) is not float:
                percent = 0.01
            self.parent.data["PRS"]["PERCENT"].append(int(percent*100))
            self.parent.data["PRS"]["FRACTION"].append(percent)
            self.parent.data["PRS"]["INVERS"].append(self.prs[name][INVERS])