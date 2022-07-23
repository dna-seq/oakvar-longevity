import sys
import time

from cravat import BaseAnnotator
from cravat import InvalidData

class CravatAnnotator(BaseAnnotator):
    # start_counter = 0
    # end_counter = 0
    sql_time = 0
    other_time = 0
    sql_count = 0
    other_count = 0

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

        if secondary_data['dbsnp'] and secondary_data['dbsnp'][0] is not None:
            rsid = secondary_data['dbsnp'][0]['rsid']
        else:
            return None

        # query = f"SELECT weight FROM position, prs, weights WHERE chrom = '{input_data['chrom']}' AND alt = '{input_data['alt_base']}'" \
        #         f" AND rsid = '{rsid}' AND weights.posid = position.id AND weights.prsid = prs.id AND prs.number = 'PGS001298'"

        query = f"SELECT prs.number, weights.weight FROM position, prs, weights WHERE chrom = '{input_data['chrom']}' AND alt = '{input_data['alt_base']}'" \
                    f" AND rsid = '{rsid}' AND weights.posid = position.id AND weights.prsid = prs.id"
        start = time.time_ns()
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sql_time += time.time_ns() - start
        self.sql_count += 1

        if rows is None or len(rows) == 0:
            return None

        result = {"PGS001298":"",
                  "PGS001017":"",
                  "PGS001185":"",
                  "PGS001252":"",
                  "PGS001833":""
                 }
        start = time.time_ns()
        for row in rows:
            result[row[0]] = str(row[1])
        self.other_time += time.time_ns() - start
        self.other_count += 1

        return result

        # return {
        #     'PGS001298': str(rows[0])
        # }

        pass

    def cleanup(self):
        print("sql_time sum:", self.sql_time)
        print("sql_time:", self.sql_time/self.sql_count)
        print("sql_count:", self.sql_count)

        print("other_time sum:", self.other_time)
        print("other_time:", self.other_time / self.other_count)
        print("other_count:", self.other_count)
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
