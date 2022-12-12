import sqlite3
from sqlite3 import Error
from pathlib import Path
import json

ALLELE = "allele"
EXIST = "exist"
WEIGHT = "weight"

MULTIPLE_CONST = "multiple"
CONFLICTED_CONST = "conflicted"
CONFLICTED_INDEX = -1

class RefHomoEdgecases:
    _is_active = True
    sql_ref_homozygot = """SELECT rsid, allele, weight FROM allele_weights WHERE state = 'ref' AND zygosity = 'hom'"""
    ref_homo_map = {}


    def init(self, parent, longevity_cursor, sql_insert):
        self.longevity_cursor = longevity_cursor
        self.sql_insert = sql_insert
        self.parent = parent


    def setActive(self, active):
        self._is_active = active

    def merge_records(self, row, record):
        need_info = False
        if record is None:
            record = list(row)
            record[6] = []
            record[7] = []

        record[7].append({"pubmedid": row[5], "study_design": row[6], "conclusions": row[7]})

        if len(record) < 8:
            print("Error les than 7 len ----------------------------------------")
        if len(record[7]) == 0:
            print("Error 7 is empty----------------------------------------------")

        # id
        if record[0] != row[0]:
            record[0] = MULTIPLE_CONST
            need_info = True

        # association
        if record[1] != row[1]:
            record[1] = CONFLICTED_CONST
            need_info = True

        # population
        if record[2] != row[2]:
            record[2] = MULTIPLE_CONST
            need_info = True
        # identifier
        if record[3] != row[3]:
            record[3] = CONFLICTED_INDEX
            need_info = True

        # symbol (GENE)
        if record[4] != row[4]:
            record[4] = MULTIPLE_CONST
            need_info = True

        # quickpubmed
        if record[5] != row[5]:
            record[5] = CONFLICTED_INDEX
            need_info = True

        if need_info:
            # print("Info--------------------------------------")
            record[6].append(
                {"id": row[0], "association": row[1], "population": row[2], "identifier": row[3], "gene": row[4],
                 "pubmedid": row[5]})

        return record


    def process_record(self, rsid, allele, w):
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
        color = self.parent.get_color(w, 1.5)

        task = (w, color, record[2], rsid, record[4], json.dumps(record[6]), json.dumps(record[7]), "", ref, alt, "", "", zygot, "", nuq, "0", "")

        self.longevity_cursor.execute(self.sql_insert, task)


    def setup(self):
        # modules_path = str(Path(__file__).parent.parent.parent)
        # sql_file = modules_path + "/annotators/longevitymap/data/longevitymap.sqlite"
        sql_file = Path(str(Path(__file__).parent), "data", "longevitymap.sqlite")
        if sql_file.exists():
            self.longevitymap_conn = sqlite3.connect(sql_file)
            self.cursor = self.longevitymap_conn.cursor()
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
        rsid = str(row['dbsnp__rsid'])
        if rsid == '':
            return
        if not rsid.startswith('rs'):
            rsid = "rs"+rsid
        item = self.ref_homo_map.get(rsid)
        if item:
            self.ref_homo_map[rsid][EXIST] = False
            # zygot = row['vcfinfo__zygosity']
            # alt = row['base__alt_base']
            # if item[ALLELE] != alt or zygot != "hom":
            #     self.ref_homo_map[rsid][EXIST] = False


    def end(self):
        if not self._is_active:
            return
        for rsid in self.ref_homo_map:
            if self.ref_homo_map[rsid][EXIST]:
                self.process_record(rsid, self.ref_homo_map[rsid][ALLELE], self.ref_homo_map[rsid][WEIGHT])

        if self.cursor is not None:
            self.cursor.close()
        if self.longevitymap_conn is not None:
            self.longevitymap_conn.close()