from cravat.cravat_report import CravatReport
import sys
import datetime
import re
import csv
import zipfile
import os
cur_path = os.path.dirname(__file__)
sys.path.append(cur_path)
import templater


class Reporter(CravatReport):
    col_count = 0
    last_col = 0
    is_longevitymap = False
    template_text = ""
    data = {"DATA":{"ID":[], "SIGNIFICANC":[], "POPULATION":[], "SNP":[], "GENE":[], "PUBMED":[]}}
    # data0 = data["DATA"]

    def setup(self):
        # setup is called first. Use it to open output files
        # Make output paths by appending to self.savepath
        outpath = f'{self.savepath}.report.html'
        self.outfile = open(outpath, 'w', encoding='utf-8')
        f = open(cur_path+"/template.html")
        self.template_text = f.read()
        f.close()

    def write_header(self, level):
        # write_header is called once per level. Use it to write
        # header lines, such as the top row of a csv, naming each column.
        # Use the self.colinfo object to get information about what
        # columns are present.
        # self.colinfo[level]['colgroups'] contains information about each
        # module (annotator) in the order it appears in the results.
        # self.colinfo[level]['columns'] contains information about each column
        # in the order it appears in the results

        for module in self.colinfo[level]['colgroups']:
            if module['name'] == 'longevitymap':
                self.col_count = module['count']
                self.last_col = module['lastcol']
                self.is_longevitymap = True

    def write_table_row(self, row):
        # write_table_row is called once for each variant. row is a list of
        # values. The order or row matches with self.colinfo[level]['columns']
        # Write the data to the output file here.
        start = self.last_col - self.col_count
        end = self.last_col - 2

        if len(row) >= end:
            if self.is_longevitymap and row[start + 1] == "significant":
                self.data["DATA"]["ID"].append(row[start])
                self.data["DATA"]["SIGNIFICANC"].append(row[start + 1])
                self.data["DATA"]["POPULATION"].append(row[start + 2])
                self.data["DATA"]["SNP"].append(row[start + 3])
                self.data["DATA"]["GENE"].append(row[start + 4])
                self.data["DATA"]["PUBMED"].append(row[start + 5])
                # str_row = [str(x) for x in row[start:end]]
                # line = '\t'.join(str_row)
                # self.outfile.write(line + '\n')

    def end(self):
        # end is called last. Use it to close the output file and
        # return a path to the output file.
        text = templater.replace_loop(self.template_text, self.data)
        self.outfile.write(text)
        self.outfile.close()
        return os.path.realpath(self.outfile.name)


### Don't edit anything below here ###
def main():
    reporter = Reporter(sys.argv)
    reporter.run()


if __name__ == '__main__':
    main()