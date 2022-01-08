import sys
import os
import sqlite3
import pandas

from cravat import BaseAnnotator
from cravat import InvalidData


class CravatAnnotator(BaseAnnotator):

    csv_fn = 'data/longevitymap.csv'
    table_name = 'longevitymap'
    index_label = 'lmid'
    col_names = ['id', 'association', 'population', 'variants', 'genes', 'pmid']

    def setup(self):
        """
        Set up data sources.
        Cravat will automatically make a connection to
        data/longevitymap.sqlite using the sqlite3 python module. The
        sqlite3.Connection object is stored as self.dbconn, and the
        sqlite3.Cursor object is stored as self.cursor.
        """

        assert os.path.isfile( self.csv_fn)
        assert isinstance(self.dbconn, sqlite3.Connection)
        assert isinstance(self.cursor, sqlite3.Cursor)

        df = pandas.read_csv(self.csv_fn, header=0, names=self.col_names) # Read a comma-separated values (csv) file into DataFrame
        df.to_sql(self.table_name, self.dbconn, if_exists='replace', index=True, index_label=self.index_label) #Write records stored in a DataFrame to a SQL database.

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

        if secondary_data['dbsnp'] and secondary_data['dbsnp'][0] is not None:
            rsids = secondary_data['dbsnp'][0]['rsid'].split(',')
        else:
            rsids = []

        if secondary_data['dbsnp_common'] and secondary_data['dbsnp_common'][0] is not None:
            rsids += secondary_data['dbsnp_common'][0]['rsid'].split(',') # concatenate lists

        if not rsids:
            return None

        for rsid in rsids:
            query = 'select id,association,population,genes,pmid from {table} where variants = {variants}'.format(
                table=self.table_name, variants=rsid)
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            if result is not None: # found match matches
                pldbid = result[0]
                association = result[1]
                population = result[2]
                genes = result[3] #todo: update csv using api query to ensembl
                pmid = result[4]
                return {
                    'longevitydb_id': pldbid,
                    'association': association,
                    'population': population,
                    'rsid': rsid,
                    'genes': genes,
                    'pmid': pmid,
                }

        return None # no rsid matches
        pass

    def cleanup(self):
        """
        cleanup is called after every input line has been processed. Use it to
        close database connections and file handlers. Automatically opened
        database connections are also automatically closed.
        """
        pass


if __name__ == '__main__':
    annotator = CravatAnnotator(sys.argv)
    annotator.run()
