import sys
from cravat import BaseAnnotator
from cravat import InvalidData
import csv, sqlite3, pandas
import os


class CravatAnnotator(BaseAnnotator):

    dbsnp_base = 0 #object pointer
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

        self.dbsnp_base = sqlite3.connect('sqlite:///dbsnp.db') #where?

        assert os.path.isfile( self.csv_fn)
        assert isinstance(self.dbsnp_base, sqlite3.Connection)
        assert isinstance(self.dbconn, sqlite3.Connection)
        assert isinstance(self.cursor, sqlite3.Cursor)

        df = pandas.read_csv( self.csv_fn, header=0, names=self.col_names) # Read a comma-separated values (csv) file into DataFrame
        df.to_sql( self.table_name, self.dbconn, if_exists='replace', index=True, index_label= self.index_label ) #Write records stored in a DataFrame to a SQL database.

        # same by hand:
        #con = self.dbconn #pointer to instance of connection
        #cur = self.cursor #cursor pointer
        # cur.execute("CREATE TABLE t (id,Association,Population,Variants,Genes,PubMed);") # use your column names here
        # with open('data.csv','r') as fin: # `with` statement available in 2.5+
        #    # csv.DictReader uses first line in file for column headings by default
        #    dr = csv.DictReader(fin) # comma is default delimiter
        #    to_db = [(i['id'], i['Association'], i['Population'], i['Variant(s)']), i['Gene(s)']), i['PubMed']) for i in dr]
        # cur.executemany("INSERT INTO t (id,Association,Population,Variants,Genes,PubMed) VALUES (?, ?, ?, ?, ?, ?);", to_db)
        # con.commit()

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

        rsquery = 'select snp from {chrom} where pos = {pos} and ref = "{ref}" and alt = "{alt}"'.format(
            chrom=input_data["chrom"], pos=int(input_data["pos"]), ref=input_data["ref_base"], alt=input_data["alt_base"])

        self.dbsnp_base.cursor.execute(rsquery)
        row = self.dbsnp_base.cursor.fetchone()

        if row is not None:
            rsid = 'rs' + str(row[0]) #rsid from dbsnp base

            query = 'select id,association,population,genes,pmid from {id} where variants = {variants}'.format(
                id=self.table_name, variants=rsid)
            self.cursor.execute(query)
            result = self.cursor.fetchone()

            if result is not None:
                pldbid = result[0]
                association = result[1]
                population = result[2]
                #variants = result[3] #matches rsid by query
                genes = result[4] #todo: update csv using api query to ensembl
                pmid = result[5]
                col_names = ['id', 'association', 'population', 'variants', 'genes', 'pmid']
                return {
                    'longevitydb_id': pldbid,
                    'association': association,
                    'population': population,
                    'rsid': rsid,
                    'genes': genes,
                    'pmid': pmid,
                }
            else:
                return None
        else:
            return None

        out = {}
        out['placeholder_annotation'] = 'placeholder value'
        return out

    def cleanup(self):
        """
        cleanup is called after every input line has been processed. Use it to
        close database connections and file handlers. Automatically opened
        database connections are also automatically closed.
        """
        # con.close()
        dbsnp_base.close() #close connection to dbsnp

        pass


if __name__ == '__main__':
    annotator = CravatAnnotator(sys.argv)
    annotator.run()