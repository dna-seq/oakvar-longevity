import sqlite3
from sqlite3 import Error
from pathlib import Path
import coronary_ref_homo


class CoronaryReport:

    def init(self, reporter):
        self.parent = reporter
        self.ref_homo = coronary_ref_homo.CoronaryRefHomo()
        self.ref_homo.init(self)


    def data_name(self):
        return "CORONARY"


    def data(self):
        return {"IND":[], "RSID":[], "GENE":[], "RISK":[], "GENOTYPE":[], "CONCLUSION":[], "WEIGHT":[], "PMID":[], "POPULATION":[], "STUDYDESIGN":[], "PVALUE":[], "WEIGHTCOLOR":[]}


    def setup(self):
        self.col_index = 0
        modules_path = str(Path(__file__).parent)
        sql_file = modules_path + "/data/coronary.sqlite"
        if Path(sql_file).exists():
            conn = sqlite3.connect(sql_file)
            self.cursor = conn.cursor()
        self.ref_homo.setup()


    def process_row(self, row):
        self.ref_homo.process_row(row)
        rsid = self.parent.get_value(row, 'dbsnp__rsid')
        if rsid is None:
            return

        alt = self.parent.get_value(row, 'base__alt_base')
        ref = self.parent.get_value(row, 'base__ref_base')

        query = "SELECT Risk_allele, Gene, Genotype, Conclusion, Weight, PMID, Population, GWAS_study_design, P_value " \
                f"FROM coronary_disease WHERE rsID = '{rsid}';"

        self.cursor.execute(query)
        rows = self.cursor.fetchall()

        if len(rows) == 0:
            return

        zygot = self.parent.get_value(row, 'vcfinfo__zygosity')
        genome = alt + "/" + ref
        gen_set = {alt, ref}
        if zygot == 'hom':
            genome = alt + "/" + alt
            gen_set = {alt, alt}
        for row in rows:
            allele = row[0]
            row_gen = {row[2][0], row[2][1]}

            if gen_set == row_gen:
            # if allele == alt or (allele == ref and zygot == 'het'):
                self.col_index += 1
                self.parent.data["CORONARY"]["IND"].append(self.col_index)
                self.parent.data["CORONARY"]["RSID"].append(rsid)
                self.parent.data["CORONARY"]["GENE"].append(row[1])
                self.parent.data["CORONARY"]["RISK"].append(allele)
                self.parent.data["CORONARY"]["GENOTYPE"].append(genome)
                self.parent.data["CORONARY"]["CONCLUSION"].append(row[3])
                self.parent.data["CORONARY"]["WEIGHT"].append(row[4])
                self.parent.data["CORONARY"]["PMID"].append(row[5])
                self.parent.data["CORONARY"]["POPULATION"].append(row[6])
                self.parent.data["CORONARY"]["STUDYDESIGN"].append(row[7])
                self.parent.data["CORONARY"]["PVALUE"].append(row[8])
                self.parent.data["CORONARY"]["WEIGHTCOLOR"].append(self.parent.get_color(row[4], 0.6))


    def end(self):
        self.ref_homo.end(self.col_index)
        pass
