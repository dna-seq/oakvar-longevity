import sqlite3
import random
import scipy.stats as stat
from sqlite3 import Error
import time

class DBHelper:
    sql_table_names = """ SELECT name FROM sqlite_master WHERE type='table'; """

    def __init__(self, conn_gnom, conn_dbsnp):
        self.conn_gnom = conn_gnom
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

    def select_one(self, conn, sql):
        try:
            c = conn.cursor()
            c.execute(sql)
            return c.fetchone()
        except Error as e:
            print(e)
            print(sql)

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

    # should corsspond to freq_index_map
    def select_freq(self, chrom, pos, ref, alt):
        sql = f"SELECT af, af_afr, af_amr, af_asj, af_eas, af_fin, af_nfe, af_oth, af_sas " \
              f"FROM {chrom} WHERE pos = {pos} AND ref = '{ref}' AND alt = '{alt}'"
        return self.select_one(self.conn_gnom, sql)


    def select_freq_snp(self, snp, alt):
        records = self.get_dbsnp_records(snp, alt)
        if len(records) == 0:
            return None
        chrom, pos, ref, alt, snp = records[0]
        return self.select_freq(chrom, pos, ref, alt)

    sql_select_prs = "SELECT rsid, alt, weight FROM position, prs, weights " \
            "WHERE prs.id = weights.prsid AND weights.posid = position.id AND prs.number = '"

    def get_probabilities(self, conn_prs, prs_number, populations):
        prob = {}
        prob[self.WEIGHT] = []
        sql = self.sql_select_prs + prs_number+"'"
        for pop in populations:
            prob[pop] = []
        try:
            c = conn_prs.cursor()
            c.execute(sql)
            record = c.fetchone()
            while record != None:
                freq_record = helper.select_freq_snp(record[0], record[1])

                if freq_record is not None:
                    prob[self.WEIGHT].append(record[2])
                    for pop in populations:
                        prob[pop].append(freq_record[self.freq_index_map[pop]])
                record = c.fetchone()
        except Error as e:
            print(e)
            print(sql)
        return prob

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

def get_statistics(data, populations):
    ppf_val = [i / 10 for i in range(1, 10)]
    res = {"values": ppf_val}
    for pop in populations:
        loc, scale = stat.norm.fit(data[pop])
        # step = scale*6/10
        # start = loc - step*5
        # values10 = [i*step + start for i in range(10)]
        # percentile = stat.norm.cdf(values10, loc=loc, scale=scale)
        ppf = stat.norm.ppf(ppf_val, loc=loc, scale=scale)
        res[pop] = {"mean":loc, "sigma":scale, "percentile":ppf}

    return res


if __name__ == "__main__":
    db_file_gnom = r"C:\dev\python\openCravatPlugin\modules\annotators\gnomad\data\gnomad.sqlite"
    conn_gnom = sqlite3.connect(db_file_gnom)

    db_file_dbsnp = r"C:\dev\python\openCravatPlugin\modules\annotators\dbsnp\data\dbsnp.sqlite"
    conn_dbsnp = sqlite3.connect(db_file_dbsnp)

    db_file_prs = r"C:\dev\python\openCravatPlugin\modules\annotators\prs\data\prs.sqlite"
    conn_prs = sqlite3.connect(db_file_prs)

    helper = DBHelper(conn_gnom, conn_dbsnp)
    populations = [DBHelper.ALEL_FREQENCY, DBHelper.AFRICAN, DBHelper.AMERICAN, DBHelper.ASHKENAZI,
                   DBHelper.EASTERN_ASIAN, DBHelper.FINISH, DBHelper.NONFINISH, DBHelper.OTHER, DBHelper.SOUTH_ASIAN]

    start = time.time()
    prob = helper.get_probabilities(conn_prs, "PGS001298", populations)
    data = sample_distribution(prob, populations, 1000)
    res = get_statistics(data, populations)
    print(time.time() - start)
    print(res)

