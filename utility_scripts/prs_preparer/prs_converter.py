import sqlite3
from sqlite3 import Cursor
from sqlite3 import Connection
import oakvar as ov
from prs_data_item import PrsDataItem
from liftover.chain_file import ChainFile
from typing import Optional

# For debug purpose
# class DbsnpResolver:
#     def __init__(self, path):
#         self.conn:Connection = sqlite3.connect(path)
#         self.cursor:Cursor = self.conn.cursor()
#
#     def get_rsid(self, chrom:str, pos:int, allele:str) -> str:
#         sql = f"SELECT rsid FROM {chrom} WHERE pos = {pos} AND alt = '{allele}'"
#         try:
#             self.cursor.execute(sql)
#             res = self.cursor.fetchone()
#             rsid = ""
#             if res:
#                 rsid = str(res[0])
#
#             return "rs"+rsid
#         except:
#             return ""
#
#     def close(self):
#         self.conn.close()


class InsertHelper:
    def __init__(self, header:dict[str, int], parts:list[str]) -> None:
        self.header:dict[str, int] = header
        self.parts:list[str] = parts

    def get(self, key:str) -> str:
        ind:int = self.header.get(key)
        if ind is None:
            return ''
        else:
            return self.parts[ind]


class PrsConverter:
    def __init__(self, db_path: str, verbos: bool = False) -> None:
        self.db_path: str = db_path
        self.verbos: bool = verbos
        # For debug purpose
        # self.rsid_resolver = DbsnpResolver("D:/dev/oakVar/modules/annotators/dbsnp/data/dbsnp.sqlite")


    sql_create_wieghts:str = """CREATE TABLE IF NOT EXISTS weights (
       id integer NOT NULL PRIMARY KEY,
       rsid text NOT NULL,
       chrom text,
       pos integer,
       other_allele text,
       effect_allele text NOT NULL,
       ref text,
       weight real,
       prsid integer,
       CONSTRAINT fk_weights_prs
        FOREIGN KEY (prsid)
        REFERENCES prs(id)
        ON DELETE CASCADE
    );
    """

    sql_create_prs:str = """CREATE TABLE IF NOT EXISTS prs (
       id integer NOT NULL PRIMARY KEY,
       title text,
       name text,
       total integer,
       invers integer NOT NULL DEFAULT 0
    );
    """

    sql_create_prs_percentiles:str = """CREATE TABLE IF NOT EXISTS percentiles (
       id integer NOT NULL PRIMARY KEY,
       value float,
       percent float,
       prs_id integer,
       CONSTRAINT fk_percentiles_prs
        FOREIGN KEY (prs_id)
        REFERENCES prs(id)
        ON DELETE CASCADE
    );
    """

    sql_delete_weights = "DELETE FROM weights"
    sql_delete_prs = "DELETE FROM prs"
    sql_delete_percentiles = "DELETE FROM percentiles"
    sql_delete_prs_by_name = "DELETE FROM prs WHERE name = "


    sql_insert_weights:str = """INSERT INTO weights
    (rsid,
     chrom,
     pos,
     other_allele,
     effect_allele,
     ref,
     weight,
     prsid
    )
    VALUES
    (?,?,?,?,?,?,?,?);
    """

    sql_insert_prs:str = """INSERT INTO prs
    (title,
     name,
     invers
    )
    VALUES
    (?,?,?);
    """

    sql_select_prs_names = """SELECT name FROM prs"""

    sql_create_pos_index:str = """CREATE INDEX IF NOT EXISTS pos_index on weights (chrom, pos, effect_allele);"""
    sql_create_prsid_index:str = """CREATE INDEX IF NOT EXISTS prsid_index on weights (prsid);"""

    RSID = "rsID"
    CHROM = "chr_name"
    POSITION = "chr_position"
    EFFECT_ALLELE = "effect_allele"
    OTHER_ALLELE = "other_allele"
    WEIGHT = "effect_weight"

    wgs_reader = None

    def clear_tables(self, cursor:Cursor):
        cursor.execute(self.sql_delete_weights)
        cursor.execute(self.sql_delete_prs)
        cursor.execute(self.sql_delete_percentiles)

    def parse_header(self, line) -> dict[str, int]:
        header:list[str] = line.split("\t")
        res:dict[str, int] = {}
        for i, key in enumerate(header):
            res[key] = i
        return res

    def add_weight(self, cursor:Cursor, ins:InsertHelper, lifter:Optional[ChainFile], prsid:int, weight:float):
        chrom:str = ins.get(self.CHROM)
        if chrom == "X":
            chrom = "chrX"
        elif chrom == "XY":
            chrom = "chrY"
        elif chrom == "M":
            chrom = "chrM"
        else:
            chrom = f"chr{chrom}"

        pos:int = 0
        if ins.get(self.POSITION).strip() != "":
            try:
                pos = int(ins.get(self.POSITION))
            except ValueError as e:
                print(e)

        if self.wgs_reader == None:
            self.wgs_reader = ov.get_wgs_reader(assembly="hg38")
        if lifter != None:
            [chrom, pos, ref, _] = ov.liftover(chrom, pos, lifter=lifter, get_ref=True, wgs_reader=self.wgs_reader)
        else:
            ref = self.wgs_reader.get_bases(chrom, pos)

        cursor.execute(self.sql_insert_weights, (ins.get(self.RSID), chrom, pos, ins.get(self.OTHER_ALLELE),
                                                 ins.get(self.EFFECT_ALLELE), ref.upper(), weight, prsid))
        # For debug purpose
        # rsid = self.rsid_resolver.get_rsid(chrom, int(pos), ins.get(self.EFFECT_ALLELE))
        # cursor.execute(self.sql_insert_position, (
        # rsid, chrom, pos, ins.get(self.OTHER_ALLELE), ins.get(self.EFFECT_ALLELE), ref.upper()))


    def get_lifter(self, line:str) -> Optional[ChainFile]:
        genome_build:str = line.split("=")[1].strip()
        lifter:Optional[ChainFile]
        if genome_build == "GRCh37":
            lifter = ov.get_lifter("hg19")
        elif genome_build == "GRCh36":
            lifter = ov.get_lifter("hg18")
        elif genome_build != "GRCh38":
            raise Exception("Error unsuported genome version, " + genome_build)
        return lifter

    def parse_prs(self, cursor:Cursor, file_path:str, prs_title:str, prs_name:str, invers:int = 0):
        if self.verbos:
            print(prs_name, " Starts...")
        cursor.execute(self.sql_insert_prs, (prs_title, prs_name, invers))
        prsid:int = cursor.lastrowid
        processed:int = 0
        total:int = 0
        lifter:Optional[ChainFile] = None
        is_header:bool = True
        header:dict[str, int] = None
        with open(file_path) as f:
            for line in f:
                if line.startswith("#"):
                    if line.startswith("#genome_build"):
                        lifter = self.get_lifter(line)
                    continue
                if is_header:
                    line = line.strip()
                    header = self.parse_header(line)
                    is_header = False
                    continue
                total += 1
                parts:list[str] = line.split("\t")
                parts = [i.strip() for i in parts]
                if len(parts) < 6:
                    continue
                ins:InsertHelper = InsertHelper(header, parts)
                if ins.get(self.WEIGHT).strip() == "":
                    continue
                try:
                    self.add_weight(cursor, ins, lifter, prsid, float(ins.get(self.WEIGHT)))
                    processed += 1
                    if self.verbos and (processed % 10000 == 0):
                        print("procesed:", processed)
                except Exception as e:
                    print("Error on line: ", line)
                    print(e)
                    continue
            sql:str = f"UPDATE prs SET total = {processed} WHERE id = {prsid}"
            cursor.execute(sql)
            if self.verbos:
                print(prs_name)
                print("total:", total)
                print("processed:", processed)
                print("missing:", total - processed, " percent:", (total - processed)/total)


    def process(self, data:list[PrsDataItem], reset:bool = True) -> list[str]:
        conn:Connection = sqlite3.connect(self.db_path) #r"prs.sqlite"
        cursor:Cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        prs_names = set()

        cursor.execute(self.sql_create_wieghts)
        cursor.execute(self.sql_create_prs)
        cursor.execute(self.sql_create_pos_index)
        cursor.execute(self.sql_create_prsid_index)
        cursor.execute(self.sql_create_prs_percentiles)

        if reset:
            self.clear_tables(cursor)
        else:
            cursor.execute(self.sql_select_prs_names)
            res = cursor.fetchall()
            prs_names = set([item[0] for item in res])

        for_deletion:list[str] = prs_names.copy()
        for item in data:
            if for_deletion.__contains__ (item.name):
                for_deletion.remove(item.name)
            if item.name not in prs_names:
                self.parse_prs(cursor, item.file, item.description, item.name, item.revers)

        for name in for_deletion:
            cursor.execute(self.sql_delete_prs_by_name + f"'{name}'")

        conn.commit()
        conn.close()
        return prs_names


# if __name__ == "__main__":
#     converter:PrsConverter = PrsConverter("prs.sqlite", True)
#     data = []
#     data.append(PrsDataItem("PGS000906_hmPOS_GRCh38.txt", "Longevity PRS", "PRS5", 1))
#     data.append(PrsDataItem("PGS000931.txt", "Blood clot or deep vein thrombosis", "PGS000931"))
#     data.append(PrsDataItem("PGS000818.txt", "Coronary heart disease", "PGS000818"))
#     data.append(PrsDataItem("PGS001839.txt", "Coronary atherosclerosis", "PGS001839"))
#     data.append(PrsDataItem("PGS000314.txt", "C-reactive protein measurement", "PGS000314"))
#     converter.process(data)
#     print("Finish")