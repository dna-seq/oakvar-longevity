import sqlite3
from sqlite3 import Error
from pathlib import Path

SUM = "sum"
TOTAL = "total"
COUNT = "count"
TITLE = "title"
INVERS = "invers"


class PrsReport:
    prs = {}
    prs_names = []
    # prs5_rsids = []
    sql_get_prs = """SELECT name, title, total, invers FROM prs;"""


    def init(self, reporter):
        self.parent = reporter


    def data_name(self):
        return "PRS"


    def data(self):
        return {"NAME":[], "TITLE":[], "SUM":[], "AVG":[], "COUNT":[], "TOTAL":[], "PERCENT":[], "FRACTION":[], "INVERS":[]}


    def setup(self):
        # sql_file = os.path.dirname(__file__) + "/data/prs.sqlite"
        sql_file = str(Path(__file__).parent) + "/data/prs.sqlite"
        if Path(sql_file).exists():
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
        ref = self.parent.get_value(row, 'base__ref_base')
        chrom = self.parent.get_value(row, 'base__chrom')

        query = f"SELECT prs.name, weights.weight, position.effect_allele FROM position, prs, weights WHERE chrom = '{chrom}'" \
                f" AND rsid = '{rsid}' AND weights.posid = position.id AND weights.prsid = prs.id"

        self.cursor.execute(query)
        rows = self.cursor.fetchall()

        if len(rows) == 0:
            return

        zygot = self.parent.get_value(row, 'vcfinfo__zygosity')
        for name, weight, allele in rows:
            if not (allele == alt or (allele == ref and zygot == 'het')):
                continue
            weight = float(weight)
            if allele == alt and zygot == 'hom':
                weight = 2*weight

            self.prs[name][SUM] += weight
            self.prs[name][COUNT] += 1
            # if name == "PRS5":
            #     self.prs5_rsids.append(rsid)


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
            if name == "PRS5":
                avg = 0
                if self.prs[name][COUNT] > 0:
                    avg = self.prs[name][SUM] / (self.prs[name][COUNT] * 2)
                self.parent.template_vars["PRS5NAME"] = name
                self.parent.template_vars["PRS5SUM"] = self.prs[name][SUM]
                self.parent.template_vars["PRS5AVG"] = avg
                self.parent.template_vars["PRS5COUNT"] = self.prs[name][COUNT]
                self.parent.template_vars["PRS5TITLE"] = self.prs[name][TITLE]
                self.parent.template_vars["PRS5TOTAL"] = self.prs[name][TOTAL]
                percent = self.get_percent(name, self.prs[name][SUM])
                if type(percent) is not float:
                    percent = 0.01
                self.parent.template_vars["PRS5PERCENT"] = int(percent * 100)
                self.parent.template_vars["PRS5FRACTION"] = percent
                self.parent.template_vars["PRS5INVERS"] = self.prs[name][INVERS]
            else:
                avg = 0
                if self.prs[name][COUNT] > 0:
                    avg = self.prs[name][SUM] / (self.prs[name][COUNT] * 2)
                parent_prs = self.parent.data["PRS"]
                parent_prs["NAME"].append(name)
                parent_prs["SUM"].append(self.prs[name][SUM])
                parent_prs["AVG"].append(avg)
                parent_prs["COUNT"].append(self.prs[name][COUNT])
                parent_prs["TITLE"].append(self.prs[name][TITLE])
                parent_prs["TOTAL"].append(self.prs[name][TOTAL])
                percent = self.get_percent(name, self.prs[name][SUM])
                if type(percent) is not float:
                    percent = 0.01
                parent_prs["PERCENT"].append(int(percent*100))
                parent_prs["FRACTION"].append(percent)
                parent_prs["INVERS"].append(self.prs[name][INVERS])

        # with open('C:/dev/python/openCravatPlugin/prs_files/rsids_oakvar_PRS5.txt', "w") as f:
        #     f.write("\n".join(self.prs5_rsids))
        #     f.flush()