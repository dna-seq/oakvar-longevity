from oakvar import BasePostAggregator
from pathlib import Path
import sqlite3

RSID_COL_NAME = "Variant/Haplotypes"
DRUGS_COL_NAME = "Drug(s)"
PHENCAT_COL_NAME = "Phenotype Category"
SIGNIFICANCE_COL_NAME = "Significance"
SENTENCE_COL_NAME = "Sentence"
FREQCASES_COL_NAME = "Allele Of Frequency In Cases"
FREQCONTROLS_COL_NAME = "Allele Of Frequency In Controls"
TYPE_COL_NAME = "Ratio Stat Type"
RATIOSTAT_COL_NAME = "Ratio Stat"

class CravatPostAggregator (BasePostAggregator):

    def check(self):
        return True

    def setup (self):
        with open(str(Path(__file__).parent) + "/data/annotation_tab.tsv") as f:
            self.annotation_tab = {}
            header = True
            head = None
            rsid_index = -1
            for line in f:
                if header:
                    head = line.split("\t")
                    rsid_index = head.index(RSID_COL_NAME)
                    self.annotation_tab["header"] = head
                    header = False
                else:
                    parts = line.split("\t")
                    self.annotation_tab[parts[rsid_index]] = parts
            self.head_index_map = {}
            for i, item in enumerate(head):
                self.head_index_map[item] = i

        self.result_path = Path(self.output_dir, self.run_name + "_longevity.sqlite")
        self.longevity_conn = sqlite3.connect(self.result_path)
        self.longevity_cursor = self.longevity_conn.cursor()
        sql_create = """ CREATE TABLE IF NOT EXISTS drugs (
            id integer NOT NULL PRIMARY KEY,
            rsid text,
            drugs text,
            phencat text,
            significance text,
            sentence text,
            freqcases text,
            freqcontrols text,
            type text,
            effect text            
            )"""
        self.longevity_cursor.execute(sql_create)
        self.longevity_conn.commit()
        self.longevity_cursor.execute("DELETE FROM drugs;")

    
    def cleanup (self):
        if self.longevity_cursor is not None:
            self.longevity_cursor.close()
        if self.longevity_conn is not None:
            self.longevity_conn.commit()
            self.longevity_conn.close()
        return

        
    def annotate (self, input_data):
        rsid = str(input_data['dbsnp__rsid'])
        if rsid == '':
            return
        if not rsid.startswith("rs"):
            rsid = 'rs' + rsid
        item = self.annotation_tab.get(rsid)
        if item is None:
            return

        freq_in_case = item[self.head_index_map[FREQCASES_COL_NAME]]
        effect = float(item[self.head_index_map[RATIOSTAT_COL_NAME]])
        alt = input_data['base__alt_base']
        if freq_in_case != alt:
            effect = round((1 / effect) * 1000) / 1000

        sql = """ INSERT INTO drugs (
            rsid,
            drugs,
            phencat,
            significance,
            sentence,
            freqcases,
            freqcontrols,
            type,
            effect  
        ) VALUES (?,?,?,?,?,?,?,?,?) """

        task = (rsid, item[self.head_index_map[DRUGS_COL_NAME]], item[self.head_index_map[PHENCAT_COL_NAME]],
                item[self.head_index_map[SIGNIFICANCE_COL_NAME]], item[self.head_index_map[SENTENCE_COL_NAME]],
                freq_in_case, item[self.head_index_map[FREQCONTROLS_COL_NAME]],
                item[self.head_index_map[TYPE_COL_NAME]], str(effect))

        self.longevity_cursor.execute(sql, task)
        return {"col1":""}
