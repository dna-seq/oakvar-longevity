import pymysql
import sqlite3
from sqlite3 import Error

sql_create_genes = """CREATE TABLE IF NOT EXISTS `gene` (
  `id` integer NOT NULL PRIMARY KEY,
  `name` text NOT NULL,
  `symbol` text NOT NULL,
  `alias` text DEFAULT NULL,
  `description` text,
  `omim` text DEFAULT NULL,
  `ensembl` text DEFAULT NULL,
  `uniprot` text DEFAULT NULL,
  `unigene` text DEFAULT NULL,
  `cytogenetic_location` text DEFAULT NULL
);
"""

sql_create_population = """CREATE TABLE IF NOT EXISTS `population` (
  `id` integer NOT NULL PRIMARY KEY,
  `name` text NOT NULL
);
"""

sql_create_variant = """CREATE TABLE IF NOT EXISTS `variant` (
  `id` integer NOT NULL PRIMARY KEY,
  `location` text DEFAULT NULL,
  `study_design` text NOT NULL,
  `conclusions` text NOT NULL,
  `association` text DEFAULT NULL,
  `gender` text NOT NULL,
  `quickref` text NOT NULL,
  `quickyear` integer NOT NULL,
  `quickpubmed` text NOT NULL,
  `identifier` text DEFAULT NULL,
  `gene_id` integer DEFAULT NULL,
  `population_id` integer NOT NULL
);
"""

sql_create_snp_table = """ CREATE TABLE IF NOT EXISTS snps (
    id integer PRIMARY KEY,
    rsid text,
    chrom text NOT NULL,
    pos integer,
    ref text,
    alt text
); """

sql_select_gene = """SELECT `gene`.`entrez_id`,
    `gene`.`name`,
    `gene`.`symbol`,
    `gene`.`alias`,
    `gene`.`description`,
    `gene`.`omim`,
    `gene`.`ensembl`,
    `gene`.`uniprot`,
    `gene`.`unigene`,
    `gene`.`cytogenetic_location`
FROM `longavitymap`.`gene`;
"""

sql_select_population = """SELECT `population`.`id`,
    `population`.`name`
FROM `longavitymap`.`population`;
"""

sql_select_variant = """SELECT
  `variant`.`id`,
  `variant`.`location`,
  `variant`.`study_design`,
  `variant`.`conclusions`,
  `variant`.`association`,
  `variant`.`gender`,
  `variant`.`quickref`,
  `variant`.`quickyear`,
  `variant`.`quickpubmed`,
  `variant`.`identifier`,
  `variant`.`gene_id`,
  `variant`.`population_id`
FROM `longavitymap`.`variant`;
"""

sql_create_index_snp = """CREATE INDEX identifier_index ON variant(identifier)"""

sql_select_distinct_identifire = """SELECT DISTINCT identifier FROM variant WHERE ( substr(identifier,1,2) = 'rs' );"""

sql_insert_gene = """INSERT INTO `gene`
(`id`,
`name`,
`symbol`,
`alias`,
`description`,
`omim`,
`ensembl`,
`uniprot`,
`unigene`,
`cytogenetic_location`)
VALUES
(?,?,?,?,?,?,?,?,?,?);
"""

sql_insert_population = """INSERT INTO `population`
(`id`,
`name`)
VALUES
(?,?);
"""

sql_insert_variant = """INSERT INTO `variant`
(`id`,
  `location`,
  `study_design`,
  `conclusions`,
  `association`,
  `gender`,
  `quickref`,
  `quickyear`,
  `quickpubmed`,
  `identifier`,
  `gene_id`,
  `population_id`)
VALUES
(?,?,?,?,?,?,?,?,?,?,?,?);
"""

sql_insert_into_snp_table = """INSERT INTO snps (id, rsid, chrom, pos, ref, alt)
 VALUES (?,?,?,?,?,?);"""

sql_table_names = """ SELECT name FROM sqlite_master WHERE type='table'; """

conn = sqlite3.connect(r"pedro_db.sqlite")

db = pymysql.connect(host="localhost",user="root",password="sndmsg4m",database="longavitymap")

cursor = db.cursor()

# cursor.execute("SELECT * FROM gene")
# data = cursor.fetchone()

def execute_sql(conn, sql):
    try:
        c = conn.cursor()
        c.execute(sql)
    except Error as e:
        print(e)
        print(sql)

def migrate_table(conn, cursor, select, insert):
    try:
        cursor.execute(select)
        rows = cursor.fetchall()
        c = conn.cursor()

        for row in rows:
            c.execute(insert, row)
    except Error as e:
        print(e)


execute_sql(conn, sql_create_genes)
execute_sql(conn, sql_create_population)
execute_sql(conn, sql_create_variant)
execute_sql(conn, sql_create_snp_table)
print("Create tabeles Finished")

migrate_table(conn, cursor, sql_select_gene, sql_insert_gene)
print("Migrate gene Finished")
migrate_table(conn, cursor, sql_select_population, sql_insert_population)
print("Migrate population Finished")
migrate_table(conn, cursor, sql_select_variant, sql_insert_variant)
print("Migrate variant Finished")

#-----------------------------------------------------------------------------------

f = open("fixes.sql")
sql_updates = f.read()
f.close()

try:
    c = conn.cursor()
    c.executescript(sql_updates)
    c.execute(sql_create_index_snp)
except Error as e:
    print(e)

print("SQL fixes Finished")

#--------------------------------------------------------------------------------------

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
            sql += "SELECT '"+table+"', * FROM "+table+" WHERE snp = "+str(snp[2:]);
            if i < 24:
                sql += " UNION "

        c.execute(sql)
    except Error as e:
        print(e)
    return c.fetchall()

conn_snp = sqlite3.connect(r"C:/dev/python/openCravatPlugin/modules/annotators/dbsnp/data/dbsnp.sqlite")

tables = getChromTables(conn_snp, sql_table_names)

try:
    snpId = 0
    c = conn.cursor()
    c.execute(sql_select_distinct_identifire)
    snps = c.fetchall()
    for snp in snps:
        snp = snp[0]
        records = get_dbsnp_records(conn_snp, snp, tables)
        for record in records:
            task = (snpId, snp, record[0], int(record[1]), record[2], record[3])
            c.execute(sql_insert_into_snp_table, task)
            snpId += 1
except Error as e:
    print(e)


db.close()
conn.commit()
conn.close()

print("Finish")