import sqlite3
from sqlite3 import Error
import pandas

MULTIPLE_CONST = "multiple"
CONFLICTED_CONST = "conflicted"
CONFLICTED_INDEX = -1

#id,Association,Population,Variant(s),Gene(s),PubMed
sql_create_longevitymap_table = """ CREATE TABLE IF NOT EXISTS longevitymap (
                                        id integer PRIMARY KEY,
                                        longevitydb_id text,
                                        association text,
                                        population text,
                                        rsid integer UNIQUE,
                                        genes text,
                                        pubmed_id integer,
                                        info text
                                    ); """

sql_create_snp_table = """ CREATE TABLE IF NOT EXISTS snps (
                                        id integer PRIMARY KEY,
                                        rsid integer,
                                        chrom text NOT NULL,
                                        pos integer,
                                        ref text,
                                        alt text
                                    ); """

sql_drop_longevitymap_table = """ DROP TABLE IF EXISTS longevitymap """
sql_drop_snps_table = """ DROP TABLE IF EXISTS snps """

sql_create_snps_index = "CREATE INDEX IF NOT EXISTS snps_search_index on snps (chrom, pos, ref, alt)"
sql_create_longevitymap_index = "CREATE INDEX IF NOT EXISTS longevitymap_rsid_index on longevitymap (rsid)"

sql_insert_into_longevitymap_table = """INSERT INTO longevitymap (
id, longevitydb_id, association, population, rsid, genes, pubmed_id, info)
 VALUES (?,?,?,?,?,?,?,?);"""

sql_insert_into_snp_table = """INSERT INTO snps (id, rsid, chrom, pos, ref, alt)
 VALUES (?,?,?,?,?,?);"""

sql_slect_longevitymap_by_rsid = """SELECT * FROM longevitymap WHERE rsid = """

sql_update_longevitymap_by_rsid = """UPDATE longevitymap SET longevitydb_id = '{dbid}', 
 association = '{assoc}', population = '{pop}', rsid = {rsid}, genes = '{gene}', pubmed_id = {pubmed}, info = '{info}' 
 WHERE id = {id}"""

sql_table_names = """ SELECT name FROM sqlite_master WHERE type='table'; """

tables = []

def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

def execute_sql(conn, sql):
    try:
        c = conn.cursor()
        c.execute(sql)
    except Error as e:
        print(e)

def initTables(conn, sql):
    global tables
    try:
        c = conn.cursor()
        c.execute(sql)
        res = c.fetchall()
        for item in res:
            tables.append(item[0])
    except Error as e:
        print(e)

def get_dbsnp_records(conn, snp):
    global tables

    c = conn.cursor()
    sql = ""
    for i, table in enumerate(tables):
        sql += "SELECT '"+table+"', * FROM "+table+" WHERE snp = "+str(snp);
        if i < 24:
            sql += " UNION "

    c.execute(sql)
    return c.fetchall()

def create_dbsnp_index(conn):
    global tables

    c = conn.cursor()
    for table in tables:
        sql = "CREATE INDEX "+table+"_index_snp on "+table+" (snp)"
        c.execute(sql)
        print(table)

def get_records_by_id(conn, sql, id):
    c = conn.cursor()
    c.execute(sql+str(id))
    return c.fetchall()

def merge_records(row, record):
    need_info = False
    record = list(record)
    record_text = "__".join(list(map(lambda i:str(i), record[1:-1])) )
    # record_text = ";".join(record[1:-1])
    if record[1] != row['id']:
        record[1] = MULTIPLE_CONST
        need_info = True

    if record[2] != row['association']:
        record[2] = CONFLICTED_CONST
        need_info = True

    if record[3] != row['population']:
        record[3] = MULTIPLE_CONST
        need_info = True

    if int(record[4]) != int(row['snp'][2:]):
        record[4] = CONFLICTED_INDEX
        need_info = True

    if record[5] != row['genes']:
        record[5] = MULTIPLE_CONST
        need_info = True

    if int(record[6]) != int(row['pubmed']):
        record[6] = CONFLICTED_INDEX
        need_info = True

    if need_info:
        if len(record[7]) == 0:
            record[7] += record_text
        record[7] += "_____" + str(row['id']) + "__" + row['association'] + "__" + row['population'] + "__" + \
                     row['snp'][2:] + "__" + row['genes'] + "__" + str(row['pubmed'])

    return record


def update_longevitymap(conn, record):
    sql = sql_update_longevitymap_by_rsid.format(id = record[0], dbid = record[1], assoc = record[2], pop = record[3],
                                           rsid = record[4], gene = record[5], pubmed = record[6], info = record[7])
    c = conn.cursor()
    c.execute(sql)


def fill_database(conn_snp, conn_longevity, csv_file):
    col_names = ['id', 'association', 'population', 'snp', 'genes', 'pubmed']
    df = pandas.read_csv(csv_file, header=0, names=col_names)
    c = conn_longevity.cursor()
    error_snp = []
    snpId = 0
    for i in range(df.shape[0]):
        snp = int(df.iloc[i]['snp'][2:])
        records = None
        try:
            records = get_dbsnp_records(conn_snp, snp)
        except Error as e:
            print(e)
            print(snp)
            continue

        if len(records) == 0:
            error_snp.append(snp)
            print("Error no snp found ", snp)
            continue
        task = (i, df.iloc[i]['id'], df.iloc[i]['association'], df.iloc[i]['population'], snp,
                df.iloc[i]['genes'], int(df.iloc[i]['pubmed']), "")
        need_snp_insert = False
        try:
            longevity_records = get_records_by_id(conn_longevity, sql_slect_longevitymap_by_rsid, snp)
            if len(longevity_records) < 1:
                c.execute(sql_insert_into_longevitymap_table, task)
                need_snp_insert = True
            else:
                longevity_record = merge_records(df.iloc[i], longevity_records[0])
                update_longevitymap(conn_longevity, longevity_record)

        except Error as e:
            print(e)
            print(task)
            continue
        if need_snp_insert:
            for record in records:
                task = (snpId, snp, record[0], int(record[1]), record[2], record[3])
                try:
                    c.execute(sql_insert_into_snp_table, task)
                except Error as e:
                    print(e)
                    print(task)
                    continue
                snpId += 1

        print(str(i)+"/"+str(df.shape[0]))
    print('Error snp:', error_snp)

    print("Finish")


if __name__ == '__main__':
    # conn_longevity = create_connection(r"data.db")
    # execute_sql(conn_longevity, sql_drop_table)
    # execute_sql(conn_longevity, sql_create_data_table)
    # conn_longevity.close()

    # conn_snp = create_connection(r"C:/dev/python/openCravatPlugin/modules/annotators/dbsnp/data/dbsnp.sqlite")
    # initTables(conn_snp, sql_table_names)
    # print(getRecord(conn_snp, 2542052))
    # conn_snp.close()

    # conn_snp_common = create_connection(r"C:/dev/python/openCravatPlugin/modules/annotators/dbsnp_common/data/dbsnp_common.sqlite")
    # initTables(conn_snp_common, sql_table_names)
    # create_dbsnp_index(conn_snp_common)

    csv_file = 'C:/dev/opencravat_longevity/annotators/longevitymap/data/longevitymap.csv'
    conn_longevity = create_connection(r"longevitymap.sqlite")
    conn_snp = create_connection(r"C:/dev/python/openCravatPlugin/modules/annotators/dbsnp/data/dbsnp.sqlite")

    execute_sql(conn_longevity, sql_drop_longevitymap_table)
    execute_sql(conn_longevity, sql_drop_snps_table)
    execute_sql(conn_longevity, sql_create_longevitymap_table)
    execute_sql(conn_longevity, sql_create_snp_table)

    initTables(conn_snp, sql_table_names)
    execute_sql(conn_longevity, sql_create_longevitymap_index)
    fill_database(conn_snp, conn_longevity, csv_file)
    execute_sql(conn_longevity, sql_create_snps_index)
    conn_longevity.commit()
    conn_longevity.close()
    conn_snp.close()

