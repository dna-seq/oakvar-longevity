from pathlib import Path

class CancerReport:
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
    col_index = 0

    def init(self, reporter):
        self.parent = reporter

    def data_name(self):
        return "CANCER"

    def data(self):
        return {"IND":[], "CHROM":[], "POS":[], "GENE":[], "RSID":[], "CDNACHANGE":[], "ZEGOT":[], "ALELFREQ":[],
                      "PHENOTYPE":[], "SIGNIFICANCE":[], "NCBI":[]}

    def setup(self):
        with open(str(Path(__file__).parent)+"/data/genes.txt") as f:
            self.genes = set(f.read().split("\n"))

    def process_row(self, row):
        significance = self.parent.get_value(row, 'clinvar__sig')  # row[self.columns['clinvar__sig']['ind']]

        if significance not in self.significance_filter:
            return

        gene = self.parent.get_value(row, 'base__hugo')  # row[self.columns['base__hugo']['ind']]
        if gene not in self.genes:
            return

        isOk = False

        omim_id = self.parent.get_value(row, 'omim__omim_id')  # row[self.columns['omim__omim_id']['ind']]
        if omim_id is not None and omim_id != '':
            isOk = True

        ncbi_desc = self.parent.get_value(row, 'ncbigene__ncbi_desc')  # row[self.columns['ncbigene__ncbi_desc']['ind']]
        if ncbi_desc is not None and ncbi_desc != '':
            isOk = True

        clinvar_id = self.parent.get_value(row, 'clinvar__id')  # row[self.columns['clinvar__id']['ind']]
        if clinvar_id is not None and clinvar_id != '':
            isOk = True

        pubmed_n = self.parent.get_value(row, 'pubmed__n')  # row[self.columns['pubmed__n']['ind']]
        if pubmed_n is not None and pubmed_n != '':
            isOk = True

        if not isOk:
            return

        self.col_index += 1

        self.parent.data["CANCER"]["IND"].append(self.col_index)
        self.parent.data["CANCER"]["CHROM"].append(
            self.parent.get_value(row, 'base__chrom'))
        self.parent.data["CANCER"]["POS"].append(self.parent.get_value(row, 'base__pos'))
        self.parent.data["CANCER"]["GENE"].append(gene)
        self.parent.data["CANCER"]["RSID"].append(
            self.parent.get_value(row, 'dbsnp__rsid'))
        self.parent.data["CANCER"]["CDNACHANGE"].append(
            self.parent.get_value(row, 'base__cchange'))
        self.parent.data["CANCER"]["ZEGOT"].append(self.parent.get_value(row, 'vcfinfo__zygosity'))
        self.parent.data["CANCER"]["ALELFREQ"].append(
            self.parent.get_value(row, 'gnomad__af'))
        self.parent.data["CANCER"]["PHENOTYPE"].append(
            self.parent.get_value(row, 'clinvar__disease_names'))
        self.parent.data["CANCER"]["SIGNIFICANCE"].append(significance)
        self.parent.data["CANCER"]["NCBI"].append(ncbi_desc)


    def end(self):
        pass