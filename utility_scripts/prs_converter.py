import sqlite3
import time
from sqlite3 import Error
import oakvar as ov

from pip import __main__

sql_create_position = """CREATE TABLE IF NOT EXISTS position (
   id integer NOT NULL PRIMARY KEY,
   rsid text NOT NULL,
   chrom text,
   pos integer,
   other_allele text,
   effect_allele text NOT NULL,
   ref text
);
"""

sql_create_wieghts = """CREATE TABLE IF NOT EXISTS weights (
   id integer NOT NULL PRIMARY KEY,
   weight real,
   posid integer,
   prsid integer
);
"""

sql_create_prs = """CREATE TABLE IF NOT EXISTS prs (
   id integer NOT NULL PRIMARY KEY,
   title text,
   name text,
   total integer,
   invers integer NOT NULL DEFAULT 0
);
"""

sql_create_prs_percentiles = """CREATE TABLE IF NOT EXISTS percentiles (
   id integer NOT NULL PRIMARY KEY,
   value float,
   percent float,
   prs_id integer
);
"""

sql_insert_position = """INSERT INTO position
(rsid,
 chrom,
 pos,
 other_allele,
 effect_allele,
 ref)
VALUES
(?,?,?,?,?,?);
"""

sql_insert_weights = """INSERT INTO weights
(weight,
 posid,
 prsid
)
VALUES
(?,?,?);
"""

sql_insert_prs = """INSERT INTO prs
(title,
 name,
 invers
)
VALUES
(?,?,?);
"""



sql_create_pos_index = """CREATE INDEX IF NOT EXISTS pos_index on position (chrom, pos, effect_allele);"""
sql_create_prsid_index = """CREATE INDEX IF NOT EXISTS prsid_index on weights (prsid);"""
sql_create_posid_index = """CREATE INDEX IF NOT EXISTS posid_index on weights (posid);"""

RSID = "rsID"
CHROM = "chr_name"
POSITION = "chr_position"
EFFECT_ALLELE = "effect_allele"
OTHER_ALLELE = "other_allele"
WEIGHT = "effect_weight"

wgs_reader = None

class InsertHelper:
    def __init__(self, header, parts):
        self.header = header
        self.parts = parts

    def get(self, key):
        ind = self.header.get(key)
        if ind is None:
            return ''
        else:
            return self.parts[ind]

def update_total(conn, total, prsid):
    sql = f"UPDATE prs SET total = {total} WHERE id = {prsid}"
    c = conn.cursor()
    c.execute(sql)

def select_one(conn, sql):
    c = conn.cursor()
    c.execute(sql)
    return c.fetchone()

def execute_sql(conn, sql):
    c = conn.cursor()
    c.execute(sql)

def insert_sql(conn, sql, task):
    c = conn.cursor()
    c.execute(sql, task)
    return c.lastrowid

def parse_header(line):
    header = line.split("\t")
    res = {}
    for i, key in enumerate(header):
        res[key] = i
    return res

def process_position(conn, ins, lifter):
    sql = f"SELECT id FROM position WHERE chrom = '{ins.get(CHROM)}' AND pos = {ins.get(POSITION)} AND effect_allele = '{ins.get(EFFECT_ALLELE)}'"
    id = select_one(conn, sql)
    if not id:
        chrom = ins.get(CHROM)
        if chrom == "X":
            chrom = "chrX"
        elif chrom == "XY":
            chrom = "chrY"
        elif chrom == "M":
            chrom = "chrM"
        else:
            chrom = f"chr{chrom}"

        pos = 0
        if ins.get(POSITION).strip() != "":
            try:
                pos = int(ins.get(POSITION))
            except ValueError as e:
                print(e)

        global wgs_reader

        if wgs_reader == None:
            wgs_reader = ov.get_wgs_reader(assembly="hg38")

        if lifter != None:
            [chrom, pos, ref, _] = ov.liftover(chrom, pos, lifter=lifter, get_ref=True, wgs_reader=wgs_reader)
        else:
            ref = wgs_reader.get_bases(chrom, pos)

        ref = ref.upper()

        id = insert_sql(conn, sql_insert_position, (ins.get(RSID), chrom, pos, ins.get(OTHER_ALLELE), ins.get(EFFECT_ALLELE), ref))
    else:
        id = id[0]
    return id

def parse_prs(file_path, conn, prs_title, prs_name, invers=0):
    print(prs_name, " Starts...")
    prsid = insert_sql(conn, sql_insert_prs, (prs_title, prs_name, invers))
    processed = 0
    total = 0
    lifter = None

    is_header = True
    header = None
    with open(file_path) as f:
        for line in f:
            if line.startswith("#"):
                if line.startswith("#genome_build"):
                    genome_build = line.split("=")[1].strip()
                    if genome_build == "GRCh37":
                        # lifter = ov.get_lifter("hg19", "hg38")
                        lifter = ov.get_lifter("hg19")
                    elif genome_build == "GRCh36":
                        # lifter = ov.get_lifter("hg18", "hg38")
                        lifter = ov.get_lifter("hg18")
                    elif genome_build != "GRCh38":
                        raise Exception("Error unsuported genome version, "+genome_build)

                continue
            line = line.strip()
            if is_header:
                header = parse_header(line)
                is_header = False
                continue
            total += 1
            parts = line.split("\t")
            if len(parts) < 6:
                continue
            ins = InsertHelper(header, parts)
            if ins.get(WEIGHT).strip() == "":
                continue
            # if ins.get(RSID).strip() == "" or not ins.get(RSID).startswith("rs"):
            #     continue
            try:
                posid = process_position(conn, ins, lifter)
                insert_sql(conn, sql_insert_weights, (float(ins.get(WEIGHT)), posid, prsid))
                processed += 1
                if processed % 10000 == 0:
                    print("procesed:", processed)

            except Exception as e:
                print("Error on line: ", line)
                print(e)
                continue
        update_total(conn, processed, prsid)
        print(prs_name)
        print("total:", total)
        print("processed:", processed)


if __name__ == "__main__":
    conn = sqlite3.connect(r"prs.sqlite")
    execute_sql(conn, sql_create_position)
    execute_sql(conn, sql_create_wieghts)
    execute_sql(conn, sql_create_prs)
    execute_sql(conn, sql_create_pos_index)
    execute_sql(conn, sql_create_posid_index)
    execute_sql(conn, sql_create_prsid_index)
    execute_sql(conn, sql_create_prs_percentiles)

    parse_prs("PGS000906_hmPOS_GRCh38.txt", conn, "Longevity PRS", "PRS5", 1)
    # parse_prs("PGS002724_rsid.txt", conn, "Ischemic stroke", "PGS002724")
    parse_prs("PGS000931.txt", conn, "Blood clot or deep vein thrombosis", "PGS000931")
    parse_prs("PGS000818.txt", conn, "Coronary heart disease", "PGS000818")
    parse_prs("PGS001839.txt", conn, "Coronary atherosclerosis", "PGS001839")
    parse_prs("PGS000314.txt", conn, "C-reactive protein measurement", "PGS000314")


    # parse_prs("PGS001298.txt", conn, "Obesity PRS", "PGS001298")
    # parse_prs("PGS001017.txt", conn, "Nervous measurement PRS", "PGS001017")
    # parse_prs("PGS001185.txt", conn, "Intraocular pressure PRS", "PGS001185")
    # parse_prs("PGS001252.txt", conn, "Hearing difficulty and deafness PRS", "PGS001252")
    # parse_prs("PGS001833.txt", conn, "Retinal detachments and defects PRS", "PGS001833")

    conn.commit()
    conn.close()
    print("Finish")