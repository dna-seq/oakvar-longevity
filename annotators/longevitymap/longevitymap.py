import sys
import os
import sqlite3
import pandas

from cravat import BaseAnnotator
from cravat import InvalidData


class CravatAnnotator(BaseAnnotator):
    start_counter = 0
    end_counter = 0
    def setup(self):
        """
        Set up data sources.
        Cravat will automatically make a connection to
        data/longevitymap.sqlite using the sqlite3 python module. The
        sqlite3.Connection object is stored as self.dbconn, and the
        sqlite3.Cursor object is stored as self.cursor.
        """

        pass

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
        self.start_counter += 1
        query = 'SELECT longevitydb_id, association, population, longevitymap.rsid, genes, pubmed_id, info ' \
                'FROM longevitymap, snps WHERE chrom = "{chrom}" AND pos = {pos} AND ref = "{ref}" AND alt = "{alt}" ' \
                'AND longevitymap.rsid = snps.rsid'.format(
            chrom = input_data["chrom"], pos = int(input_data["pos"]), ref = input_data["ref_base"], alt = input_data["alt_base"])
        self.cursor.execute(query)
        row = self.cursor.fetchone()

        if row:
            self.end_counter += 1
            return {
                'longevitydb_id': str(row[0]),
                'association': str(row[1]),
                'population': str(row[2]),
                'rsid': str(row[3]),
                'genes': str(row[4]),
                'pmid': str(row[5]),
                'info': str(row[6])
            }

        return None # no rsid matches
        pass

    def cleanup(self):
        print("start_counter:", self.start_counter)
        print("end_counter:", self.end_counter)
        """
        cleanup is called after every input line has been processed. Use it to
        close database connections and file handlers. Automatically opened
        database connections are also automatically closed.
        """
        pass


if __name__ == '__main__':
    annotator = CravatAnnotator(sys.argv)
    annotator.run()
