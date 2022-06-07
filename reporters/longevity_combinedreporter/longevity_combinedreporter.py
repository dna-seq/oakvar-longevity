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
    template_text = ""
    data = {"CANCER":{"IND":[], "CHROM":[], "POS":[], "GENE":[], "RSID":[], "CDNACHANGE":[], "ZEGOT":[], "ALELFREQ":[],
                      "PHENOTYPE":[], "SIGNIFICANCE":[], "NCBI":[]},
            "LONGEVITY":{"ID":[], "SIGNIFICANCE":[], "POPULATION":[], "SNP":[], "GENE":[], "PUBMED":[], "DESCRIPTION":[],
                         "CODING":[], "SEQONTOLOGY":[], "PROTCHANGE":[], "REF":[], "ALT":[], "CDNACHANGE":[], "RANKSCOR":[],
                         "DESEASES":[], "ZEGOT":[]}}
    current_level = ""
    columns = None
    col_index = 0
    genes = set()
    significance_filter = [
              "Affects, risk factor",
              "Benign, risk factor",
              "Conflicting interpretations of pathogenicity",
              "Conflicting interpretations of pathogenicity, other",
              "Conflicting interpretations of pathogenicity, other, risk factor",
              "Conflicting interpretations of pathogenicity, risk factor",
              "Likely pathogenic",
              "Pathogenic",
              "Pathogenic, protective",
              "Uncertain significance",
              "association, risk factor",
              "protective, risk factor",
              "risk factor"
            ]
    flag = False
    is_longevitymap = False
    PGS001298_sum = 0
    PGS001298_count = 0

    def _createSubTable(self, text):
        if text is None:
            return ""
        html = "<table>\n"
        html += "<tr><td>ID</td><td>Significance</td><td>Population</td><td>RSID</td><td>Gene</td><td>PubMed Id</td></tr>"
        rows = text.split("____")
        for row in rows:
            html += "<tr>"
            parts = row.split("__")
            for part in parts:
                html += "<td>"+part+"</td>"
            html += "</tr>"
        html += "</table>\n<br/>"
        return html

    def col_info(self, level):
        columns_arr = self.colinfo[level]['columns']
        modules_arr = self.colinfo[level]['colgroups']
        columns = {}
        modules = {}
        for module in modules_arr:
            if module['name'] == 'base':
                module['start'] = module['lastcol'] - module['count']
            else:
                module['start'] = module['lastcol'] - module['count'] - 1
            modules[module['name']] = module

        for col in columns_arr:
            mod_name = col['col_name'].split("__")[0]
            ind = -1
            if modules.get(mod_name) != -1:
                if col['col_index'] is not None:
                    ind = modules[mod_name]['start'] + col['col_index']
                else:
                    ind = modules[mod_name]['start']

            column = {'name':col['col_name'], 'title':col['col_title'], 'ind':ind, 'col_index':col['col_index']}
            columns[col['col_name']] = column

        return columns

    def setup(self):
        # setup is called first. Use it to open output files
        # Make output paths by appending to self.savepath
        outpath = f'{self.savepath}.longevity_combined.html'
        self.outfile = open(outpath, 'w', encoding='utf-8')
        with open(cur_path+"/template.html") as f:
            self.template_text = f.read()

        with open(cur_path+"/genes.txt") as f:
            self.genes = set(f.read().split("\n"))


    def write_header(self, level):
        # write_header is called once per level. Use it to write
        # header lines, such as the top row of a csv, naming each column.
        # Use the self.colinfo object to get information about what
        # columns are present.
        # self.colinfo[level]['colgroups'] contains information about each
        # module (annotator) in the order it appears in the results.
        # self.colinfo[level]['columns'] contains information about each column
        # in the order it appears in the results
        self.current_level = level
        if level == 'variant':
            self.columns = self.col_info(level)
            self.columns['vcfinfo__zygosity']['ind'] += 3
            # print(self.colinfo[level]['colgroups'])
            # print(self.columns)

            for module in self.colinfo[level]['colgroups']:
                if module['name'] == 'longevitymap':
                    self.is_longevitymap = True
                    # print("Is longevity True")
            # fields = ['base__chrom', 'base__pos', 'base__hugo', 'dbsnp__rsid', 'base__cchange',
            #           'vcfinfo__zygosity', 'gnomad__af', 'clinvar__disease_names', 'clinvar__sig', 'ncbigene__ncbi_desc']
            # for field in fields:
            #     print(self.columns[field])

    def get_value(self, row, name):
        col = self.columns.get(name)
        if col is not None:
            ind = col["ind"]
            if ind == -1:
                return ''
            else:
                return row[ind]
        return ''

    def write_prs(self, row):
        weight = self.get_value(row, 'prs__PGS001298')
        if weight is None or weight == "":
            return

        weight = float(weight)
        zygot = self.get_value(row, 'vcfinfo__zygosity')
        if zygot == 'hom':
            weight = 2*weight

        self.PGS001298_sum += weight
        self.PGS001298_count += 1


    def write_longevity_row(self, row):
        if self.is_longevitymap and self.get_value(row, 'longevitymap__association') == "significant":
            self.data["LONGEVITY"]["ID"].append(self.get_value(row, 'longevitymap__longevitydb_id'))
            self.data["LONGEVITY"]["SIGNIFICANCE"].append(self.get_value(row, 'longevitymap__association'))
            self.data["LONGEVITY"]["POPULATION"].append(self.get_value(row, 'longevitymap__population'))
            self.data["LONGEVITY"]["SNP"].append(self.get_value(row, 'longevitymap__rsid'))
            self.data["LONGEVITY"]["GENE"].append(self.get_value(row, 'longevitymap__genes'))
            self.data["LONGEVITY"]["PUBMED"].append(self.get_value(row, 'longevitymap__pmid'))
            temp = self._createSubTable(self.get_value(row, 'longevitymap__info'))
            temp += self.get_value(row, 'longevitymap__description').replace("____", "<br/>").replace("__", " ")
            self.data["LONGEVITY"]["DESCRIPTION"].append(temp)
            self.data["LONGEVITY"]["CODING"].append(self.get_value(row, 'base__coding'))
            self.data["LONGEVITY"]["SEQONTOLOGY"].append(self.get_value(row, 'base__so'))
            self.data["LONGEVITY"]["PROTCHANGE"].append(self.get_value(row, 'base__achange'))
            self.data["LONGEVITY"]["REF"].append(self.get_value(row, 'base__ref_base'))
            self.data["LONGEVITY"]["ALT"].append(self.get_value(row, 'base__alt_base'))
            self.data["LONGEVITY"]["CDNACHANGE"].append(self.get_value(row, 'base__cchange'))
            self.data["LONGEVITY"]["RANKSCOR"].append(self.get_value(row, 'clinpred__rankscore'))
            self.data["LONGEVITY"]["DESEASES"].append(self.get_value(row, 'clinvar__disease_names'))
            self.data["LONGEVITY"]["ZEGOT"].append(self.get_value(row, 'vcfinfo__zygosity'))


    def write_cancer_row(self, row):
        significance = self.get_value(row, 'clinvar__sig')  # row[self.columns['clinvar__sig']['ind']]
        if significance not in self.significance_filter:
            return

        gene = self.get_value(row, 'base__hugo')  # row[self.columns['base__hugo']['ind']]
        if gene not in self.genes:
            return

        isOk = False

        omim_id = self.get_value(row, 'omim__omim_id')  # row[self.columns['omim__omim_id']['ind']]
        if omim_id is not None and omim_id != '':
            isOk = True

        ncbi_desc = self.get_value(row, 'ncbigene__ncbi_desc')  # row[self.columns['ncbigene__ncbi_desc']['ind']]
        if ncbi_desc is not None and ncbi_desc != '':
            isOk = True

        clinvar_id = self.get_value(row, 'clinvar__id')  # row[self.columns['clinvar__id']['ind']]
        if clinvar_id is not None and clinvar_id != '':
            isOk = True

        pubmed_n = self.get_value(row, 'pubmed__n')  # row[self.columns['pubmed__n']['ind']]
        if pubmed_n is not None and pubmed_n != '':
            isOk = True

        if not isOk:
            return

        self.col_index += 1

        self.data["CANCER"]["IND"].append(self.col_index)
        self.data["CANCER"]["CHROM"].append(
            self.get_value(row, 'base__chrom'))  # row[self.columns['base__chrom']['ind']])
        self.data["CANCER"]["POS"].append(self.get_value(row, 'base__pos'))  # row[self.columns['base__pos']['ind']])
        self.data["CANCER"]["GENE"].append(gene)
        self.data["CANCER"]["RSID"].append(
            self.get_value(row, 'dbsnp__rsid'))  # row[self.columns['dbsnp__rsid']['ind']])
        self.data["CANCER"]["CDNACHANGE"].append(
            self.get_value(row, 'base__cchange'))  # row[self.columns['base__cchange']['ind']])
        self.data["CANCER"]["ZEGOT"].append(self.get_value(row, 'vcfinfo__zygosity'))
        self.data["CANCER"]["ALELFREQ"].append(
            self.get_value(row, 'gnomad__af'))  # row[self.columns['gnomad__af']['ind']])
        self.data["CANCER"]["PHENOTYPE"].append(
            self.get_value(row, 'clinvar__disease_names'))  # row[self.columns['clinvar__disease_names']['ind']])
        self.data["CANCER"]["SIGNIFICANCE"].append(significance)
        self.data["CANCER"]["NCBI"].append(ncbi_desc)


    def write_table_row(self, row):
        # write_table_row is called once for each variant. row is a list of
        # values. The order or row matches with self.colinfo[level]['columns']
        # Write the data to the output file here.
        if self.current_level != 'variant':
            return

        # if not self.flag:
        #     print(row)
        #     self.flag = True
        self.write_longevity_row(row)
        self.write_cancer_row(row)
        self.write_prs(row)


    def end(self):
        # end is called last. Use it to close the output file and
        # return a path to the output file.
        # print(self.data)
        avg = 0
        if self.PGS001298_count > 0:
            avg = self.PGS001298_sum/(self.PGS001298_count*2)
        text = templater.replace_symbols(self.template_text,
            {"PGS001298SUM": str(self.PGS001298_sum), "PGS001298COUNT": str(self.PGS001298_count),
             "PGS001298AVG": str(avg)})
        text = templater.replace_loop(text, self.data)
        self.outfile.write(text)
        self.outfile.close()
        return os.path.realpath(self.outfile.name)


### Don't edit anything below here ###
def main():
    reporter = Reporter(sys.argv)
    reporter.run()


if __name__ == '__main__':
    main()