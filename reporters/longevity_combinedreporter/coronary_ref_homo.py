import sqlite3
from sqlite3 import Error


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
        rsid = str(self.parent.parent.get_value(row, 'dbsnp__rsid'))
        if rsid == '':
            return

        if not rsid.startswith('rs'):
            rsid = "rs"+rsid

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
                    coranary = self.parent.parent.data["CORONARY"]
                    coranary["IND"].append(col_index)
                    coranary["RSID"].append(rsid)
                    coranary["GENE"].append(row[1])
                    coranary["RISK"].append(row[0])
                    coranary["GENOTYPE"].append(row[0]+"/"+row[0])
                    coranary["CONCLUSION"].append(row[3])
                    coranary["WEIGHT"].append(row[4])
                    coranary["PMID"].append(row[5])
                    coranary["POPULATION"].append(row[6])
                    coranary["STUDYDESIGN"].append(row[7])
                    coranary["PVALUE"].append(row[8])
                    coranary["WEIGHTCOLOR"].append(self.parent.parent.get_color(row[4], 0.6))