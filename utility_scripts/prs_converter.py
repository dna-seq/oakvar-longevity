import sqlite3
from sqlite3 import Error

from pip import __main__

sql_create_position = """CREATE TABLE IF NOT EXISTS position (
   id integer NOT NULL PRIMARY KEY,
   rsid text NOT NULL,
   chrom text,
   pos integer,
   ref text,
   alt text NOT NULL
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
   number text
);
"""

sql_insert_position = """INSERT INTO position
(rsid,
 chrom,
 pos,
 ref,
 alt)
VALUES
(?,?,?,?,?);
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
 number
)
VALUES
(?,?);
"""

RSID = "rsID"
CHROM = "chr_name"
POSITION = "chr_position"
REF = "effect_allele"
ALT = "other_allele"
WEIGHT = "effect_weight"

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


def select_one(conn, sql):
    try:
        c = conn.cursor()
        c.execute(sql)
        return c.fetchone()
    except Error as e:
        print(e)
        print(sql)

def execute_sql(conn, sql):
    try:
        c = conn.cursor()
        c.execute(sql)
    except Error as e:
        print(e)
        print(sql)

def insert_sql(conn, sql, task):
    try:
        c = conn.cursor()
        c.execute(sql, task)
        return c.lastrowid
    except Error as e:
        print(e)
        print(sql)
        print(task)

def parse_header(line):
    header = line.split("\t")
    res = {}
    for i, key in enumerate(header):
        res[key] = i
    return res

def process_position(conn, ins):
    sql = f"SELECT id FROM position WHERE rsid = '{ins.get(RSID)}' AND alt = '{ins.get(ALT)}'"
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
        id = insert_sql(conn, sql_insert_position, (ins.get(RSID), chrom, int(ins.get(POSITION)), ins.get(REF), ins.get(ALT)))
    else:
        id = id[0]
    return id

def parse_prs(file_path, conn, prs_name, prs_number):
    prsid = insert_sql(conn, sql_insert_prs, (prs_name, prs_number))

    is_header = True
    header = None
    with open(file_path) as f:
        for line in f:
            if line.startswith("#"):
                continue
            line = line.strip()
            if is_header:
                header = parse_header(line)
                is_header = False
                continue
            parts = line.split("\t")
            if len(parts) < len(header):
                continue
            ins = InsertHelper(header, parts)
            if ins.get(WEIGHT).strip() == "":
                continue
            posid = process_position(conn, ins)
            insert_sql(conn, sql_insert_weights, (float(ins.get(WEIGHT)), posid, prsid))

if __name__ == "__main__":
    conn = sqlite3.connect(r"prs.sqlite")
    execute_sql(conn, sql_create_position)
    execute_sql(conn, sql_create_wieghts)
    execute_sql(conn, sql_create_prs)

    parse_prs("PGS001298.txt", conn, "Obesity PRS", "PGS001298")
    conn.commit()
    conn.close()
    print("Finish")