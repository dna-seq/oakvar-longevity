from oakvar import BasePostAggregator
from pathlib import Path
import sys
cur_path = str(Path(__file__).parent)
sys.path.append(cur_path)
import sqlite3
import longevitymap_ref_homo
import json

MULTIPLE_CONST = "multiple"
CONFLICTED_CONST = "conflicted"
CONFLICTED_INDEX = -1

class CravatPostAggregator (BasePostAggregator):
    sql_insert = """ INSERT INTO longevitymap (
                weight,
                weightcolor,
                population,
                snp,
                gene,
                conflicted_rows,
                description,
                coding,
                ref,
                alt,
                cdnachange,
                deseases,
                zegot,
                alelfreq,
                nucleotides,
                priority,
                ncbidesc         
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) """

    ref_homo = longevitymap_ref_homo.RefHomoEdgecases()

    def check(self):
        return True


    def get_nucleotides(self, ref, alt, zygocity):
        if zygocity == 'hom':
            return alt+"/"+alt, {alt, alt}
        return alt+"/"+ref, {alt, ref}


    def get_color(self, w, scale = 1.5):
        w = float(w)
        if w < 0:
            w = w * -1
            w = 1 - w * scale
            if w < 0:
                w = 0
            color = format(int(w * 255), 'x')
            if len(color) == 1:
                color = "0" + color
            color = "ff" + color + color
        else:
            w = 1 - w * scale
            if w < 0:
                w = 0
            color = format(int(w * 255), 'x')
            if len(color) == 1:
                color = "0" + color
            color = color + "ff" + color

        return color


    def cleanup (self):
        if self.longevity_cursor is not None:
            self.longevity_cursor.close()
        if self.longevity_conn is not None:
            self.longevity_conn.commit()
            self.longevity_conn.close()
        return


    def setup (self):
        self.result_path = Path(self.output_dir, self.run_name + "_longevity.sqlite")
        self.longevity_conn = sqlite3.connect(self.result_path)
        self.longevity_cursor = self.longevity_conn.cursor()
        self.ref_homo.init(self, self.longevity_cursor, self.sql_insert)
        self.ref_homo.setup()
        sql_create = """ CREATE TABLE IF NOT EXISTS longevitymap (
            id integer NOT NULL PRIMARY KEY,
            weight float,
            weightcolor float,
            population text,
            snp text,
            gene text,
            conflicted_rows text,
            description text,
            coding text,
            ref text,
            alt text,
            cdnachange text,
            deseases text,
            zegot text,
            alelfreq text,
            nucleotides text,
            priority float,
            ncbidesc text          
            )"""
        self.longevity_cursor.execute(sql_create)
        self.longevity_cursor.execute("DELETE FROM longevitymap;")
        self.longevity_conn.commit()

        cur_path = str(Path(__file__).parent)
        self.data_conn = sqlite3.connect(Path(cur_path, "data", "longevitymap.sqlite"))
        self.data_cursor = self.data_conn.cursor()


    def merge_records(self, row, record):
        need_info = False
        if record is None:
            record = list(row)
            record[6] = []
            record[7] = []

        record[7].append({"pubmedid":row[5], "study_design":row[6], "conclusions":row[7]})

        if len(record) < 8:
            print("Error les than 7 len ----------------------------------------")
        if len(record[7]) == 0:
            print("Error 7 is empty----------------------------------------------")

        #id
        if record[0] != row[0]:
            record[0] = MULTIPLE_CONST
            need_info = True

        #association
        if record[1] != row[1]:
            record[1] = CONFLICTED_CONST
            need_info = True

        #population
        if record[2] != row[2]:
            record[2] = MULTIPLE_CONST
            need_info = True
        #identifier
        if record[3] != row[3]:
            record[3] = CONFLICTED_INDEX
            need_info = True

        #symbol (GENE)
        if record[4] != row[4]:
            record[4] = MULTIPLE_CONST
            need_info = True

        #quickpubmed
        if record[5] != row[5]:
            record[5] = CONFLICTED_INDEX
            need_info = True

        if need_info:
            # print("Info--------------------------------------")
            record[6].append({"id":row[0], "association":row[1], "population":row[2], "identifier":row[3], "gene":row[4], "pubmedid":row[5]})

        return record


    # 'longevitydb_id': str(record[0]),
    # 'association': str(record[1]),
    # 'population': str(record[2]),
    # 'rsid': str(record[3]),
    # 'genes': str(record[4]),
    # 'pmid': str(record[5]),
    # 'info': str(record[6]),
    # 'description': str(record[7]),
    # 'allele': str(allel_row[0]),
    # 'state': str(allel_row[1]),
    # 'zygosity': str(allel_row[2]),
    # 'weight': str(allel_row[3]),
    # 'priority': str(priority)

    def annotate (self, input_data):
        rsid = str(input_data['dbsnp__rsid'])
        if rsid == '':
            return

        if not rsid.startswith('rs'):
            rsid = "rs" + rsid
        query = 'SELECT variant.id, association, population.name, identifier, symbol, quickpubmed, study_design, conclusions ' \
                'FROM variant, population, gene, allele_weights WHERE  ' \
                'variant.identifier = "{rsid}" AND variant.population_id = population.id AND variant.gene_id = gene.id AND ' \
                'allele_weights.rsid = variant.identifier AND allele_weights.allele = "{alt}" GROUP BY variant.id'.format(
            rsid=rsid, alt=input_data['base__alt_base'])

        self.data_cursor.execute(query)
        rows = self.data_cursor.fetchall()

        if len(rows) == 0:
            return None

        record = None
        for row in rows:
            record = self.merge_records(row, record)

        zygot = input_data['vcfinfo__zygosity']
        if zygot is None or zygot == "":
            zygot = "het"

        alt = input_data['base__alt_base']
        ref = input_data['base__ref_base']

        query2 = f"SELECT weight, priority FROM allele_weights WHERE rsid = '{rsid}' AND zygosity = '{zygot}' AND allele = '{alt}'"
        self.data_cursor.execute(query2)
        rows2 = self.data_cursor.fetchall()
        if len(rows2) == 0:
            return
        allel_row = rows2[0]
        w = allel_row[0]
        priority = allel_row[1]

        if len(rows2) > 1:
            print("Worning unexpected number of rows in allel_row in longevitymap postagregator!!!____________________________________________")

        if record[1] != "significant":
            return

        self.ref_homo.process_row(input_data)
        nuq, nuq_set = self.get_nucleotides(ref, alt, zygot)

        if w == 0:
            return

        color = self.get_color(w, 1.5)
        # temp = self._createSubTable(record[6])
        # temp += record[7].replace("____", "<br/>").replace("__", " ")

        task = (w, color, record[2], rsid, record[4], json.dumps(record[6]), json.dumps(record[7]),
                input_data['base__coding'], ref, alt, input_data['base__cchange'], input_data['clinvar__disease_names'],
                zygot, input_data['gnomad__af'], nuq, priority, input_data['ncbigene__ncbi_desc'])

        self.longevity_cursor.execute(self.sql_insert, task)
        return {"col1":""}


    def postprocess(self):
        self.ref_homo.end()
