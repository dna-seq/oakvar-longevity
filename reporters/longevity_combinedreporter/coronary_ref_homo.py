import sqlite3
from sqlite3 import Error
import os


class CoronaryRefHomo:

    rsid_map = {}

    def init(self, reporter):
        self.parent = reporter


    def setup(self):
        sql = "SELECT rsID, Risk_allele FROM coronary_disease WHERE Ref_allele = Risk_allele"
        self.parent.cursor.execute(sql)
        rows = self.parent.cursor.fetchall()
        for rsid, risk_allele in rows:
            self.rsid_map[rsid] = {'exist':True, 'risk':risk_allele}


    def process_row(self, row):
        rsid = self.parent.parent.get_value(row, 'dbsnp__rsid')
        if rsid is None:
            return

        item = self.rsid_map.get(rsid)
        if item:
            self.rsid_map[rsid]['exist'] = False


    def end(self, col_index):
        for rsid in self.rsid_map:
            if self.rsid_map[rsid]['exist']:
                risk = self.rsid_map[rsid]['risk']
                risk = risk+risk

                query = "SELECT Risk_allele, Gene, Genotype, Conclusion, Weight, PMID, Population, GWAS_study_design, P_value " \
                        f"FROM coronary_disease WHERE rsID = '{rsid}' AND Genotype = '{risk}';"

                self.parent.cursor.execute(query)
                row = self.parent.cursor.fetchone()
                if row:
                    col_index += 1
                    self.parent.parent.data["CORONARY"]["IND"].append(col_index)
                    self.parent.parent.data["CORONARY"]["RSID"].append(rsid)
                    self.parent.parent.data["CORONARY"]["GENE"].append(row[1])
                    self.parent.parent.data["CORONARY"]["RISK"].append(row[0])
                    self.parent.parent.data["CORONARY"]["GENOTYPE"].append(row[0]+"/"+row[0])
                    self.parent.parent.data["CORONARY"]["CONCLUSION"].append(row[3])
                    self.parent.parent.data["CORONARY"]["WEIGHT"].append(row[4])
                    self.parent.parent.data["CORONARY"]["PMID"].append(row[5])
                    self.parent.parent.data["CORONARY"]["POPULATION"].append(row[6])
                    self.parent.parent.data["CORONARY"]["STUDYDESIGN"].append(row[7])
                    self.parent.parent.data["CORONARY"]["PVALUE"].append(row[8])