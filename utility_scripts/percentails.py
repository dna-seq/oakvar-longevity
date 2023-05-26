import sqlite3
import random
import scipy.stats as stat
from sqlite3 import Error
import time
import numpy as np


def select_one(conn, sql):
    try:
        c = conn.cursor()
        c.execute(sql)
        return c.fetchone()
    except Error as e:
        print(e)
        print(sql)

class DBHelper:
    sql_table_names = """ SELECT name FROM sqlite_master WHERE type='table'; """

    def __init__(self, conn_gnom, conn_dbsnp):
        self.conn_gnom = conn_gnom
        self.gnom_cursor = conn_gnom.cursor()
        self.conn_dbsnp = conn_dbsnp
        self.tables = self.getChromTables()

    def getChromTables(self):
        tables = []
        try:
            c = self.conn_dbsnp.cursor()
            c.execute(self.sql_table_names)
            res = c.fetchall()
            for item in res:
                tables.append(item[0])
        except Error as e:
            print(e)

        return tables

    def get_dbsnp_records(self, snp, alt):
        c = self.conn_dbsnp.cursor()
        try:
            sql = ""
            for i, table in enumerate(self.tables):
                sql += f"SELECT '{table}', * FROM {table} WHERE snp = {str(snp[2:])} AND alt = '{alt}'"
                if i < 24:
                    sql += " UNION "

            c.execute(sql)
        except Error as e:
            print(e)
        return c.fetchall()



    ALEL_FREQENCY = "af"
    AFRICAN = "af_afr"
    AMERICAN = "af_amr"
    ASHKENAZI = "af_asj"
    EASTERN_ASIAN = "af_eas"
    FINISH = "af_fin"
    NONFINISH = "af_nfe"
    OTHER = "af_oth"
    SOUTH_ASIAN = "af_sas"

    WEIGHT = "weight"

    freq_index_map = {}
    freq_index_map[ALEL_FREQENCY] = 0
    freq_index_map[AFRICAN] = 1
    freq_index_map[AMERICAN] = 2
    freq_index_map[ASHKENAZI] = 3
    freq_index_map[EASTERN_ASIAN] = 4
    freq_index_map[FINISH] = 5
    freq_index_map[NONFINISH] = 6
    freq_index_map[OTHER] = 7
    freq_index_map[SOUTH_ASIAN] = 8

    # should corуsspond to freq_index_map
    def select_freq(self, chrom, pos, ref, effect_allele):
        sql = f"SELECT ref, alt, af, af_afr, af_amr, af_asj, af_eas, af_fin, af_nfe, af_oth, af_sas " \
              f"FROM {chrom} WHERE pos = {pos}"

        self.gnom_cursor.execute(sql)
        records = self.gnom_cursor.fetchall()
        prob = np.zeros(9, dtype=np.float64)
        if ref == effect_allele:
            for record in records:
                prob += np.array(record[2:], dtype=np.float64)
            prob = np.ones(9) - prob
            prob = np.where(prob < 0, 0, prob)
        else:
            for record in records:
                if record[1] == effect_allele:
                    prob = np.array(record[2:], dtype=np.float64)
                    break

        prob = np.where(np.isnan(prob), 0, prob)

        return prob


    # def select_freq_snp(self, snp, alt):
    #     records = self.get_dbsnp_records(snp, alt)
    #     if len(records) == 0:
    #         return None
    #     chrom, pos, ref, alt, snp = records[0]
    #     return self.select_freq(chrom, pos, ref, alt)

    sql_select_prs = "SELECT chrom, pos, ref, effect_allele, weight FROM position, prs, weights " \
            "WHERE prs.id = weights.prsid AND weights.posid = position.id AND prs.name = '"

    def get_probabilities(self, conn_prs, prs_name, populations):
        prob = {}
        prob[self.WEIGHT] = []
        sql = self.sql_select_prs + prs_name+"'"
        for pop in populations:
            prob[pop] = []
        try:
            c = conn_prs.cursor()
            c.execute(sql)
            record = c.fetchone()
            while record != None:
                freq_record = helper.select_freq(record[0], record[1], record[2], record[3])

                if freq_record is not None:
                    prob[self.WEIGHT].append(record[4])
                    for pop in populations:
                        prob[pop].append(freq_record[self.freq_index_map[pop]])
                record = c.fetchone()
        except Error as e:
            print(e)
            print(sql)
        return prob

class PrsDbHelper:
    sql_select_prs_id = """ SELECT id FROM prs WHERE name = """
    sql_insert_percentiles = """ INSERT INTO percentiles (percent, value, prs_id) VALUES (?, ?, ?)"""

    def __init__(self, conn, prs_name):
        self.c = conn.cursor()
        self.prs_id = select_one(conn, self.sql_select_prs_id + f"'{prs_name}'")[0]

    def insert(self, percent, value):
        if type(percent) is list and type(value) is list:
            if len(percent) != len(value):
                raise IndexError("percent and value should be equale length lists or floats")
            for i in range(len(percent)):
                self.c.execute(self.sql_insert_percentiles, (percent[i], value[i], self.prs_id))
        else:
            self.c.execute(self.sql_insert_percentiles, (percent, value, self.prs_id))



def get_probabilities_from_PRS_catalog_format(file_path):
    weight_ind = -1
    freq_ind = -1
    res = {DBHelper.WEIGHT:[], DBHelper.ALEL_FREQENCY:[]}
    with open(file_path) as f:
        is_head = True
        for line in f:
            if line.startswith("#"):
                continue
            parts = line.strip().split("\t")
            if is_head:
                weight_ind = parts.index("effect_weight")
                freq_ind = parts.index("freq")
                is_head = False
                continue
            try:
                weight = float(parts[weight_ind])
                freq = float(parts[freq_ind])
                res[DBHelper.WEIGHT].append(weight)
                res[DBHelper.ALEL_FREQENCY].append(freq)
            except ValueError as e:
                print(e)
    return res


def sample(prob, populations):
    count = len(prob[DBHelper.WEIGHT])
    res = {}
    for pop in populations:
        res[pop] = 0
    for i in range(count):
        for pop in populations:
            p = prob[pop][i]
            if p is None:
                p = prob[DBHelper.ALEL_FREQENCY][i]
            if p is None:
                continue
            if random.uniform(0, 1) < p:
                res[pop] += prob[DBHelper.WEIGHT][i]
            if random.uniform(0, 1) < p:
                res[pop] += prob[DBHelper.WEIGHT][i]

    return res

def sample_distribution(prob, populations, dist_size):
    res = {}
    for pop in populations:
        res[pop] = []

    for i in range(dist_size):
        score = sample(prob, populations)
        if i % 100 == 0:
            print(i,"/",dist_size)
        for pop in populations:
            res[pop].append(score[pop])

    return res

def get_statistics(data, populations, prs_helper = None):
    count = 100
    ppf_val = [i / count for i in range(1, count)]
    res = {"values": ppf_val}
    for pop in populations:
        loc, scale = stat.norm.fit(data[pop])
        # step = scale*6/10
        # start = loc - step*5
        # values10 = [i*step + start for i in range(10)]
        # percentile = stat.norm.cdf(values10, loc=loc, scale=scale)
        ppf = stat.norm.ppf(ppf_val, loc=loc, scale=scale)
        if prs_helper is not None:
            prs_helper.insert(ppf_val, list(ppf))
        res[pop] = {"mean":loc, "sigma":scale, "percentile":ppf}

    return res


def parse_prs(helper, conn_prs, populations, prs_name):
    print("Start "+prs_name)
    prob = helper.get_probabilities(conn_prs, prs_name, populations)
    sum = 0
    for i in range(len(prob[DBHelper.WEIGHT])):
        if not np.isnan(prob[DBHelper.WEIGHT][i]) and not np.isnan(prob[DBHelper.ALEL_FREQENCY][i]):
            sum += float(prob[DBHelper.WEIGHT][i])*float(prob[DBHelper.ALEL_FREQENCY][i])
        else:
            print("something is nan:", prob[DBHelper.WEIGHT][i], prob[DBHelper.ALEL_FREQENCY][i], i)
    print(f"Math Expectation ({prs_name}):", sum*2)
    data = sample_distribution(prob, populations, 10000)
    get_statistics(data, populations, PrsDbHelper(conn_prs, prs_name))
    print("Finish " + prs_name)

if __name__ == "__main__":
    db_file_gnom = r"D:\dev\oakVar\modules\annotators\gnomad3\data\gnomad3.sqlite"
    conn_gnom = sqlite3.connect(db_file_gnom)

    db_file_dbsnp = r"D:\dev\oakVar\modules\annotators\dbsnp\data\dbsnp.sqlite"
    conn_dbsnp = sqlite3.connect(db_file_dbsnp)

    db_file_prs = r"C:\dev\python\openCravatPlugin\prs_files\prs.sqlite"
    conn_prs = sqlite3.connect(db_file_prs)

    helper = DBHelper(conn_gnom, conn_dbsnp)
    # populations = [DBHelper.ALEL_FREQENCY, DBHelper.AFRICAN, DBHelper.AMERICAN, DBHelper.ASHKENAZI,
    #                DBHelper.EASTERN_ASIAN, DBHelper.FINISH, DBHelper.NONFINISH, DBHelper.OTHER, DBHelper.SOUTH_ASIAN]

    populations = [DBHelper.ALEL_FREQENCY]

    start = time.time()

    prob = helper.get_probabilities(conn_prs, "PRS5", populations)

    # prob = get_probabilities_from_PRS_catalog_format("PRS5_pgscatalog_format.txt")
    data = sample_distribution(prob, populations, 10000)
    res = get_statistics(data, populations, PrsDbHelper(conn_prs, "PRS5"))

    # parse_prs(helper, conn_prs, populations, "PGS002724")
    parse_prs(helper, conn_prs, populations, "PGS000931")
    parse_prs(helper, conn_prs, populations, "PGS000818")
    parse_prs(helper, conn_prs, populations, "PGS001839")
    parse_prs(helper, conn_prs, populations, "PGS000314")

    # prob = helper.get_probabilities(conn_prs, "PGS000931", populations)
    # data = sample_distribution(prob, populations, 10000)
    # res = get_statistics(data, populations, PrsDbHelper(conn_prs, "PGS000931"))
    #
    # prob = helper.get_probabilities(conn_prs, "PGS000818", populations)
    # data = sample_distribution(prob, populations, 10000)
    # res = get_statistics(data, populations, PrsDbHelper(conn_prs, "PGS000818"))
    #
    # prob = helper.get_probabilities(conn_prs, "PGS001839", populations)
    # data = sample_distribution(prob, populations, 10000)
    # res = get_statistics(data, populations, PrsDbHelper(conn_prs, "PGS001839"))
    #
    # prob = helper.get_probabilities(conn_prs, "PGS000314", populations)
    # data = sample_distribution(prob, populations, 10000)
    # res = get_statistics(data, populations, PrsDbHelper(conn_prs, "PGS000314"))

    print(time.time() - start)
    print("Finish all!!!")
    conn_prs.commit()
    conn_prs.close()
    conn_dbsnp.close()
    conn_gnom.close()