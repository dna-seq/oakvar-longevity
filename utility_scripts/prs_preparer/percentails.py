import sqlite3
import random
import scipy.stats as stat
from sqlite3 import Error
import time
import numpy as np
from prs_data_item import PrsDataItem
from sqlite3 import Cursor
from sqlite3 import Connection
from typing import Optional

class DBHelper:
    def __init__(self, conn_gnom:Connection):
        self.conn_gnom:Connection = conn_gnom
        self.gnom_cursor:Cursor = conn_gnom.cursor()

    ALEL_FREQENCY:str = "af"
    AFRICAN:str = "af_afr"
    AMERICAN:str = "af_amr"
    ASHKENAZI:str = "af_asj"
    EASTERN_ASIAN:str = "af_eas"
    FINISH:str = "af_fin"
    NONFINISH:str = "af_nfe"
    OTHER:str = "af_oth"
    SOUTH_ASIAN:str = "af_sas"

    WEIGHT:str = "weight"

    freq_index_map:dict[str, int] = {}
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
    def select_freq(self, chrom:str, pos:str, ref:str, effect_allele:str) -> np.ndarray:
        sql = f"SELECT ref, alt, af, af_afr, af_amr, af_asj, af_eas, af_fin, af_nfe, af_oth, af_sas " \
              f"FROM {chrom} WHERE pos = {pos}"

        self.gnom_cursor.execute(sql)
        records:list = self.gnom_cursor.fetchall()
        prob:np.ndarray = np.zeros(9, dtype=np.float64)
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


    sql_select_prs:str = "SELECT chrom, pos, ref, effect_allele, weight FROM prs, weights " \
            "WHERE prs.id = weights.prsid AND prs.name = '"

    def get_probabilities(self, conn_prs:Connection, prs_name:str, populations:list[str]) -> dict[str, list]:
        prob:dict[str, list] = {}
        prob[self.WEIGHT] = []
        sql = self.sql_select_prs + prs_name+"'"
        for pop in populations:
            prob[pop] = []
        try:
            c:Cursor = conn_prs.cursor()
            c.execute(sql)
            record:list = c.fetchone()
            while record != None:
                freq_record:np.ndarray = self.select_freq(record[0], record[1], record[2], record[3])

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
    sql_select_prs_id:str = """ SELECT id FROM prs WHERE name = """
    sql_insert_percentiles:str = """ INSERT INTO percentiles (percent, value, prs_id) VALUES (?, ?, ?)"""

    def __init__(self, conn:Connection, prs_name:str):
        self.c:Connection = conn.cursor()
        sql:str = self.sql_select_prs_id + f"'{prs_name}'"
        self.c.execute(sql)
        self.prs_id:int = self.c.fetchone()[0]

    def insert(self, percent:list[float], value:list[float]):
        if len(percent) != len(value):
            raise IndexError("percent and value should be equale length lists or floats")
        for i in range(len(percent)):
            self.c.execute(self.sql_insert_percentiles, (percent[i], value[i], self.prs_id))

class Percentails():
    def __init__(self, db_file_gnom:str, db_file_prs:str, n_samples:int = 10000, verbos:bool = False):
        self.db_file_gnom:str = db_file_gnom
        self.db_file_prs:str = db_file_prs
        self.n_samples:int = n_samples
        self.verbos:bool = verbos

    def sample(self, prob:dict[str, list], populations:list[str]) -> dict[str, float]:
        count:int = len(prob[DBHelper.WEIGHT])
        res:dict[str, float] = {}
        for pop in populations:
            res[pop] = 0
        for i in range(count):
            for pop in populations:
                p:Optional[float] = prob[pop][i]
                if p is None:
                    p = prob[DBHelper.ALEL_FREQENCY][i]
                if p is None:
                    continue
                if random.uniform(0, 1) < p:
                    res[pop] += prob[DBHelper.WEIGHT][i]
                if random.uniform(0, 1) < p:
                    res[pop] += prob[DBHelper.WEIGHT][i]
        return res


    def sample_distribution(self, prob:dict[str, list], populations:list[str], dist_size:int) -> dict[str, list]:
        res:dict[str, list] = {}
        for pop in populations:
            res[pop] = []
        for i in range(dist_size):
            score:dict[str, float] = self.sample(prob, populations)
            if self.verbos and (i % 100 == 0):
                print(i,"/",dist_size)
            for pop in populations:
                res[pop].append(score[pop])
        return res


    def get_statistics(self, data:dict[str, list], populations:list[str], prs_helper:PrsDbHelper = None) -> dict[str, list[float]]:
        count:int = 100
        ppf_val:list[float] = [i / count for i in range(1, count)]
        res:dict[str, list[float]] = {"values": ppf_val}
        for pop in populations:
            loc, scale = stat.norm.fit(data[pop])
            ppf = stat.norm.ppf(ppf_val, loc=loc, scale=scale)
            if prs_helper is not None:
                prs_helper.insert(ppf_val, list(ppf))
            res[pop] = {"mean":loc, "sigma":scale, "percentile":ppf}
        return res


    def parse_prs(self, helper:DBHelper, conn_prs:Connection, populations:list[str], prs_name:str):
        if self.verbos:
            print("Start "+prs_name)
        prob:dict[str, list] = helper.get_probabilities(conn_prs, prs_name, populations)
        # sum = 0
        # for i in range(len(prob[DBHelper.WEIGHT])):
        #     if not np.isnan(prob[DBHelper.WEIGHT][i]) and not np.isnan(prob[DBHelper.ALEL_FREQENCY][i]):
        #         sum += float(prob[DBHelper.WEIGHT][i])*float(prob[DBHelper.ALEL_FREQENCY][i])
        #     else:
        #         print("something is nan:", prob[DBHelper.WEIGHT][i], prob[DBHelper.ALEL_FREQENCY][i], i)
        # print(f"Math Expectation ({prs_name}):", sum*2)
        data:dict[str, list] = self.sample_distribution(prob, populations, self.n_samples)
        self.get_statistics(data, populations, PrsDbHelper(conn_prs, prs_name))
        if self.verbos:
            print("Finish " + prs_name)


    def process(self, data:list, prs_names:list[str], population:str = DBHelper.ALEL_FREQENCY):
        conn_gnom:Connection = sqlite3.connect(self.db_file_gnom)
        conn_prs:Connection = sqlite3.connect(self.db_file_prs)
        helper:DBHelper = DBHelper(conn_gnom)
        # populations:list[str] = [DBHelper.ALEL_FREQENCY]
        for item in data:
            if item.name not in prs_names:
                self.parse_prs(helper, conn_prs, [population], item.name)
        conn_prs.commit()
        conn_prs.close()
        conn_gnom.close()


# if __name__ == "__main__":
#     db_file_gnom = r"D:\dev\oakVar\modules\annotators\gnomad3\data\gnomad3.sqlite"
#     db_file_prs = r"C:\dev\python\openCravatPlugin\prs_files\prs.sqlite"
#     percentails = Percentails(db_file_gnom, db_file_prs, True)
#     data = [PrsDataItem(name = "PRS5"), PrsDataItem(name = "PGS000931"), PrsDataItem(name = "PGS000818"), PrsDataItem(name = "PGS001839"), PrsDataItem(name = "PGS000314")]
#     start = time.time()
#     percentails.process(data)
#     print(time.time() - start)
#     print("Finish all!!!")