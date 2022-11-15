import sqlite3
from sqlite3 import Error


class CoronaryRefHomo:

    rsid_map = {}

    def init(self, reporter, sql_insert):
        self.parent = reporter
        self.sql_insert = sql_insert


    def setup(self):
        sql = "SELECT rsID, Risk_allele FROM coronary_disease WHERE Ref_allele = Risk_allele"
        self.parent.coronary_cursor.execute(sql)
        rows = self.parent.coronary_cursor.fetchall()
        for rsid, risk_allele in rows:
            self.rsid_map[rsid] = {'exist':True, 'risk':risk_allele}


    def process_row(self, row):
        rsid = str(row['dbsnp__rsid'])
        if rsid == '':
            return

        if not rsid.startswith('rs'):
            rsid = "rs"+rsid

        item = self.rsid_map.get(rsid)
        if item:
            self.rsid_map[rsid]['exist'] = False


    def end(self):
        for rsid in self.rsid_map:
            if self.rsid_map[rsid]['exist']:
                risk = self.rsid_map[rsid]['risk']
                risk = risk+risk

                query = "SELECT Risk_allele, Gene, Genotype, Conclusion, Weight, PMID, Population, GWAS_study_design, P_value " \
                        f"FROM coronary_disease WHERE rsID = '{rsid}' AND Genotype = '{risk}';"

                self.parent.coronary_cursor.execute(query)
                row = self.parent.coronary_cursor.fetchone()
                if row:
                    task = (rsid, row[1], row[0], row[0]+"/"+row[0], row[3], row[4], row[5], row[6], row[7], row[8],
                            self.parent.get_color(row[4], 0.6))
                    self.parent.longevity_cursor.execute(self.sql_insert, task)