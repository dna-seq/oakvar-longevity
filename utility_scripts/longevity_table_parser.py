from email.policy import default
import pandas as pd
import sqlite3
from sqlite3 import Error
import click
from pathlib import Path

create_table = """ CREATE TABLE IF NOT EXISTS "allele_weights" (
	"id"	INTEGER NOT NULL UNIQUE,
	"allele"	TEXT NOT NULL,
	"state"	TEXT NOT NULL,
	"zygosity"	TEXT,
	"weight"	REAL DEFAULT 0,
	"rsid"	TEXT NOT NULL,
	"priority" TEXT NOT NULL,
	PRIMARY KEY("id")
);"""

sql_select_by_rsid = """SELECT ref, alt FROM snps WHERE rsid = """

sql_insert_alt_weights = """INSERT INTO allele_weights (id, allele, state, zygosity, weight, rsid, priority)
 VALUES (?,?,?,?,?,?,?);"""

sql_table_names = """ SELECT name FROM sqlite_master WHERE type='table'; """

sql_drop_allele_weights = """DROP TABLE allele_weights;"""

sql_create_population_id_index = """CREATE INDEX IF NOT EXISTS population_index ON population(id)"""
sql_create_gene_id_index = """CREATE INDEX IF NOT EXISTS gene_id_index ON gene(id)"""
sql_create_rsid_index = """CREATE INDEX IF NOT EXISTS allele_weights_rsid_index ON allele_weights(rsid)"""

HETEROZYGOTH = "het"
HOMOZYGOTH = "hom"
STATE_REF = "ref"
STATE_ALT = "alt"
STATE_SPECIAL = "spec"

def getChromTables(conn, sql):
    tables = []
    try:
        c = conn.cursor()
        c.execute(sql)
        res = c.fetchall()
        for item in res:
            tables.append(item[0])
    except Error as e:
        print(e)

    return tables

def get_dbsnp_records(conn, snp, tables):
    c = conn.cursor()
    try:
        sql = ""
        for i, table in enumerate(tables):
            sql += "SELECT ref, alt FROM "+table+" WHERE snp = "+ str(snp[2:]);
            if i < 24:
                sql += " UNION "

        c.execute(sql)
    except Error as e:
        print(e)
    return c.fetchall()

def filterVariants(variants, values, weight):
    var_parts = variants.upper().split(";")
    val_parts = values.split(";")
    val_res = []
    var_res = []

    for i, val in enumerate(val_parts):
        val = float(val.strip().replace(",", "."))
        if val == 0.0:
            continue
        val_res.append(val * weight)
        var_res.append(var_parts[i].strip())

    return var_res, val_res

def processVariants(cursor, variants, values, ref, rsid, idIndex, priority):
    for i, variant in enumerate(variants):
        state = STATE_ALT
        zygocity = HETEROZYGOTH
        allele = ""
        if variant[0] == variant[1]:
            allele = variant[0]
            zygocity = HOMOZYGOTH
            if variant[0] == ref:
                state = STATE_REF
        elif variant[0] != ref and variant[1] != ref:
            state = STATE_SPECIAL
            allele = variant
        else:
            if variant[0] != ref:
                allele = variant[0]
            if variant[1] != ref:
                allele = variant[1]

        task = (idIndex, allele, state, zygocity, values[i], rsid, priority)
        cursor.execute(sql_insert_alt_weights, task)
        idIndex += 1

    return idIndex

def create_dbsnp_index(conn, tables):
    c = conn.cursor()
    for table in tables:
        sql = "CREATE INDEX IF NOT EXISTS "+table+"_index_snp on "+table+" (snp)"
        c.execute(sql)
        print(table)


@click.command()
@click.option('--dbsnp', default='D:/dev/oakVar/modules/annotators/dbsnp/data/dbsnp.sqlite', help='Path to the dbSNP')
@click.option('--lmap', default='longevitymap.sqlite', help='Path to the LongevityMap')
@click.option('--tsv', default='longevitymap.tsv', help='Path to the longevitymap.tsv file')
def parser(dbsnp: str, lmap: str, tsv: str):
    dbsnp_conn = sqlite3.connect(dbsnp)
    dbsnp_tables = getChromTables(dbsnp_conn, sql_table_names)
    create_dbsnp_index(dbsnp_conn, dbsnp_tables)

    conn = sqlite3.connect(lmap)
    cursor = conn.cursor()
    cursor.execute(sql_drop_allele_weights)


    cursor.execute(create_table)
    cursor.execute(sql_create_population_id_index)
    cursor.execute(sql_create_gene_id_index)
    cursor.execute(sql_create_rsid_index)


    df = pd.read_csv(tsv, sep="\t")
    idIndex = 0
    length = df.shape[0] #628
    print("length:", length)
    errors = [
    norsids = []
    rsid_map = set()
    for i in range(length):
        variant_id, rsid, variants, values, priority, skip = df.loc[i, ["id", "identifier", "genotypes", "Genotype longevity weight", "Gene prioritization", "Skip"]]
        if skip == 1.0:
            continue

        if rsid in rsid_map:
            continue
        else:
            rsid_map.add(rsid)

        try:
            variants, values = filterVariants(variants, values, priority)
        except IndexError as e:
            errors.append({"num":i, "var":variants, "val":values})
            continue

        ref_alt = get_dbsnp_records(dbsnp_conn, rsid, dbsnp_tables)
        # cursor.execute(sql_select_by_rsid+"'"+rsid+"'")
        # ref_alt = cursor.fetchall()
        if len(ref_alt) == 0:
            norsids.append(rsid)
            continue

        ref = ref_alt[0][0]

        idIndex = processVariants(cursor, variants, values, ref, rsid, idIndex, priority)
        print(i,"/",length)

    if len(errors) > 0:
        print("Errors:")
        for error in errors:
            print(error)

    if len(norsids) > 0:
        print("No rsids:")
        for rsid in norsids:
            print(rsid)

    conn.commit()
    conn.close()
    print("Finish")

    # print(id, rsid, variants, values, weight, skip) # < 628

if __name__ == "__main__":
    parser()
