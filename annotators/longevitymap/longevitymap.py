import sys
import os
import sqlite3
import time

from cravat import BaseAnnotator
from cravat import InvalidData

MULTIPLE_CONST = "multiple"
CONFLICTED_CONST = "conflicted"
CONFLICTED_INDEX = -1

class CravatAnnotator(BaseAnnotator):
    # start_counter = 0
    # end_counter = 0

    def setup(self):
        """
        Set up data sources.
        Cravat will automatically make a connection to
        data/longevitymap.sqlite using the sqlite3 python module. The
        sqlite3.Connection object is stored as self.dbconn, and the
        sqlite3.Cursor object is stored as self.cursor.
        """

        pass

    def merge_records(self, row, record):
        need_info = False
        if record is None:
            record = list(row)
            record[6] = ""
            record[7] = "Pubmed id:__" + row[5] + "____Study Design:__" + row[6] + "____Conclusions:__" + row[7]
        else:
            record[7] += "____Pubmed id:__" + row[5] + "____Study Design:__" + row[6] + "____Conclusions:__" + row[7]

        if len(record) < 8:
            print("Error les than 7 len ----------------------------------------")
        if len(record[7]) == 0:
            print("Error 7 is empty----------------------------------------------")

        record_text = "__".join(list(map(lambda i: str(i), record[0:-2])))
        # record_text = ";".join(record[1:-1])
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
            if len(record[6]) == 0:
                record[6] += record_text
            record[6] += "____" + str(row[0]) + "__" + row[1] + "__" + row[2] + "__" + \
                         row[3] + "__" + str(row[4]) + "__" + str(row[5])

        return record


    def merge_rows(self, rows):
        res = [str(el) for el in rows[0]]
        for i in range(1, len(rows)):
            for j, item in enumerate(rows[i]):
                res[j] += ",ov"+str(item)

        return res


    def annotate(self, input_data, secondary_data=None):
        """
        The annotator parent class will call annotate for each line of the
        input file. It takes one positional argument, input_data, and one
        keyword argument, secondary_data.

        input_data is a dictionary containing the data from the current input
        line. The keys depend on what what file is used as the input, which can
        be changed in the module_name.yml file.
        Variant level includes the following keys:
            ('uid', 'chrom', 'pos', 'ref_base', 'alt_base')
        Variant level crx files expand the key set to include:
            ('hugo', 'transcript','so','all_mappings')
        Gene level files include
            ('hugo', 'num_variants', 'so', 'all_so')

        secondary_data is used to allow an annotator to access the output of
        other annotators. It is described in more detail in the CRAVAT
        documentation.

        annotate should return a dictionary with keys matching the column names
        defined in example_annotator.yml. Extra column names will be ignored,
        and absent column names will be filled with None. Check your output
        carefully to ensure that your data is ending up where you intend.
        """

        # if secondary_data['dbsnp'] and secondary_data['dbsnp'][0] is not None:
        #     rsids = secondary_data['dbsnp'][0]['rsid'].split(',')
        # else:
        #     rsids = []
        #
        # if secondary_data['dbsnp_common'] and secondary_data['dbsnp_common'][0] is not None:
        #     rsids += secondary_data['dbsnp_common'][0]['rsid'].split(',') # concatenate lists
        #
        # if not rsids:
        #     return None
        # self.start_counter += 1
        # query = 'SELECT longevitydb_id, association, population, longevitymap.rsid, genes, pubmed_id, info ' \
        #         'FROM longevitymap, snps WHERE chrom = "{chrom}" AND pos = {pos} AND ref = "{ref}" AND alt = "{alt}" ' \
        #         'AND longevitymap.rsid = snps.rsid'.format(
        #     chrom = input_data["chrom"], pos = int(input_data["pos"]), ref = input_data["ref_base"], alt = input_data["alt_base"])

        if secondary_data['dbsnp'] and secondary_data['dbsnp'][0] is not None:
            rsid = secondary_data['dbsnp'][0]['rsid']
        else:
            return None

        # 'allele_weights.allele, allele_weights.state, allele_weights.zygosity, allele_weights.weight' \

        # query = 'SELECT variant.id, association, population.name, identifier, symbol, quickpubmed, study_design, conclusions ' \
        #         'FROM variant, snps, population, gene WHERE chrom = "{chrom}" AND pos = {pos} AND ref = "{ref}" AND alt = "{alt}" ' \
        #         'AND variant.identifier = snps.rsid AND variant.population_id = population.id AND variant.gene_id = gene.id'.format(
        #     chrom=input_data["chrom"], pos=int(input_data["pos"]), ref=input_data["ref_base"], alt=input_data["alt_base"])
        query = 'SELECT variant.id, association, population.name, identifier, symbol, quickpubmed, study_design, conclusions ' \
                'FROM variant, population, gene, allele_weights WHERE  '\
                'variant.identifier = "{rsid}" AND variant.population_id = population.id AND variant.gene_id = gene.id AND ' \
                'allele_weights.rsid = variant.identifier AND allele_weights.allele = "{alt}" GROUP BY variant.id'.format(
            rsid=rsid, alt=input_data["alt_base"])


        # start = time.time_ns()
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        # time_span = time.time_ns() - start

        if len(rows) == 0:
            return None

        # print(rsid, "time:", time_span)

        # start = time.time_ns()
        record = None
        for row in rows:
            record = self.merge_records(row, record)

        query2 = 'SELECT allele, state, zygosity, weight, priority FROM allele_weights WHERE rsid = "{rsid}"'.format(rsid=rsid)
        self.cursor.execute(query2)
        rows2 = self.cursor.fetchall()
        allel_row = rows2[0]
        priority = allel_row[4]
        if len(rows2) > 1:
            allel_row = self.merge_rows(rows2)

        # time_span = time.time_ns() - start
        # print("loop time:", time_span)
        # print("rows:", len(rows))

        return {
            'longevitydb_id': str(record[0]),
            'association': str(record[1]),
            'population': str(record[2]),
            'rsid': str(record[3]),
            'genes': str(record[4]),
            'pmid': str(record[5]),
            'info': str(record[6]),
            'description': str(record[7]),
            'allele': str(allel_row[0]),
            'state': str(allel_row[1]),
            'zygosity': str(allel_row[2]),
            'weight': str(allel_row[3]),
            'priority':str(priority)
        }

        pass

    def cleanup(self):
        # print("start_counter:", self.start_counter)
        # print("end_counter:", self.end_counter)
        """
        cleanup is called after every input line has been processed. Use it to
        close database connections and file handlers. Automatically opened
        database connections are also automatically closed.
        """
        pass


if __name__ == '__main__':
    annotator = CravatAnnotator(sys.argv)
    annotator.run()
