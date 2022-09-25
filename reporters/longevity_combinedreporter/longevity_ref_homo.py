import sqlite3
from sqlite3 import Error
import os

ALLELE = "allele"
EXIST = "exist"
WEIGHT = "weight"

MULTIPLE_CONST = "multiple"
CONFLICTED_CONST = "conflicted"
CONFLICTED_INDEX = -1

class RefHomoEdgecases:
    _is_active = False
    sql_ref_homozygot = """SELECT rsid, allele, weight FROM allele_weights WHERE state = 'ref' AND zygosity = 'hom'"""
    ref_homo_map = {}


    def init(self, reporter):
        self.parent = reporter


    def setActive(self):
        self._is_active = True


    def merge_records(self, row, record):
        need_info = False
        if record is None:
            record = list(row)
            record[6] = ""
            record[7] = "Pubmed id:__" + row[5] + "____Study Design:__" + row[6] + "____Conclusions:__" + row[7]
        else:
            record[7] += "____Pubmed id:__" + row[5] + "____Study Design:__" + row[6] + "____Conclusions:__" + row[7]

        if len(record) < 8:
            print("Error les than 7 len ----------------------------------------")
        if len(record[7]) == 0:
            print("Error 7 is empty----------------------------------------------")

        record_text = "__".join(list(map(lambda i: str(i), record[0:-2])))
        # record_text = ";".join(record[1:-1])
        #id
        if record[0] != row[0]:
            record[0] = MULTIPLE_CONST
            need_info = True

        #association
        if record[1] != row[1]:
            record[1] = CONFLICTED_CONST
            need_info = True

        #population
        if record[2] != row[2]:
            record[2] = MULTIPLE_CONST
            need_info = True
        #identifier
        if record[3] != row[3]:
            record[3] = CONFLICTED_INDEX
            need_info = True

        #symbol (GENE)
        if record[4] != row[4]:
            record[4] = MULTIPLE_CONST
            need_info = True

        #quickpubmed
        if record[5] != row[5]:
            record[5] = CONFLICTED_INDEX
            need_info = True

        if need_info:
            # print("Info--------------------------------------")
            if len(record[6]) == 0:
                record[6] += record_text
            record[6] += "____" + str(row[0]) + "__" + row[1] + "__" + row[2] + "__" + \
                         row[3] + "__" + str(row[4]) + "__" + str(row[5])

        return record


    def process_record(self, rsid, allele, w, index):
        if not self._is_active:
            return
        query = 'SELECT variant.id, association, population.name, identifier, symbol, quickpubmed, study_design, conclusions ' \
                'FROM variant, population, gene, allele_weights WHERE  ' \
                'variant.identifier = "{rsid}" AND variant.population_id = population.id AND variant.gene_id = gene.id AND ' \
                'allele_weights.rsid = variant.identifier AND allele_weights.allele = "{alt}" AND' \
                ' allele_weights.state = "ref" AND allele_weights.zygosity = "hom"' \
                ' GROUP BY variant.id'.format(
            rsid=rsid, alt=allele)

        self.cursor.execute(query)
        rows = self.cursor.fetchall()

        if len(rows) == 0:
            return

        record = None
        for row in rows:
            record = self.merge_records(row, record)

        alt = allele
        ref = allele
        zygot = "hom"
        nuq = allele + "/" + allele

        self.parent.parent.data["LONGEVITY"]["IND"].append(index)
        self.parent.parent.data["LONGEVITY"]["WEIGHT"].append(w)
        color = self.parent.get_color(w)
        self.parent.parent.data["LONGEVITY"]["WEIGHTCOLOR"].append(color)
        self.parent.parent.data["LONGEVITY"]["POPULATION"].append(record[2])
        self.parent.parent.data["LONGEVITY"]["SNP"].append(rsid)
        self.parent.parent.data["LONGEVITY"]["GENE"].append(record[4])
        temp = self.parent._createSubTable(record[6])
        temp += record[7].replace("____", "<br/>").replace("__", " ")
        self.parent.parent.data["LONGEVITY"]["DESCRIPTION"].append(temp)
        self.parent.parent.data["LONGEVITY"]["CODING"].append("")
        self.parent.parent.data["LONGEVITY"]["REF"].append(ref)
        self.parent.parent.data["LONGEVITY"]["ALT"].append(alt)
        self.parent.parent.data["LONGEVITY"]["CDNACHANGE"].append("")
        self.parent.parent.data["LONGEVITY"]["DESEASES"].append("")
        self.parent.parent.data["LONGEVITY"]["ZEGOT"].append(zygot)
        self.parent.parent.data["LONGEVITY"]["ALELFREQ"].append("")
        self.parent.parent.data["LONGEVITY"]["NUCLEOTIDES"].append(nuq)
        self.parent.parent.data["LONGEVITY"]["PRIORITY"].append("0")
        self.parent.parent.data["LONGEVITY"]["NCBIDESC"].append("")


    def setup(self):
        modules_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        sql_file = modules_path + "/annotators/longevitymap/data/longevitymap.sqlite"
        if os.path.exists(sql_file):
            longevitymap_conn = sqlite3.connect(sql_file)
            self.cursor = longevitymap_conn.cursor()
            try:
                self.cursor.execute(self.sql_ref_homozygot)
                ref_homozygots = self.cursor.fetchall()
                for row in ref_homozygots:
                    self.ref_homo_map[row[0]] = {ALLELE:row[1], WEIGHT:row[2], EXIST:True}

            except Error as e:
                print(e)


    def process_row(self, row):
        if not self._is_active:
            return
        if len(self.ref_homo_map) == 0:
            return
        rsid = self.parent.parent.get_value(row, 'longevitymap__rsid')
        item = self.ref_homo_map.get(rsid)
        if item:
            zygot = self.parent.parent.get_value(row, 'vcfinfo__zygosity')
            alt = self.parent.parent.get_value(row, 'base__alt_base')
            if item[ALLELE] != alt or zygot != "hom":
                self.ref_homo_map[rsid][EXIST] = False


    def end(self, index):
        if not self._is_active:
            return
        for rsid in self.ref_homo_map:
            if self.ref_homo_map[rsid][EXIST]:
                index += 1
                self.process_record(rsid, self.ref_homo_map[rsid][ALLELE], self.ref_homo_map[rsid][WEIGHT], index)