from oakvar import BasePostAggregator
from pathlib import Path
import sqlite3

class CravatPostAggregator (BasePostAggregator):
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

    def check(self):
        return True

    def setup (self):
        with open(str(Path(__file__).parent)+"/data/genes.txt") as f:
            self.genes = set(f.read().split("\n"))
        self.result_path = Path(self.output_dir, self.run_name + "_longevity.sqlite")
        self.longevity_conn = sqlite3.connect(self.result_path)
        self.longevity_cursor = self.longevity_conn.cursor()
        sql_create = """ CREATE TABLE IF NOT EXISTS cancer (
            id integer NOT NULL PRIMARY KEY,
            chrom text,
            pos text,
            gene text,
            rsid text,
            cdnachange text,
            zegot text,
            alelfreq text,
            phenotype text,
            significance text,
            ncbi text
            )"""
        self.longevity_cursor.execute(sql_create)
        self.longevity_cursor.execute("DELETE FROM cancer;")
        self.longevity_conn.commit()

    
    def cleanup (self):
        if self.longevity_cursor is not None:
            self.longevity_cursor.close()
        if self.longevity_conn is not None:
            self.longevity_conn.commit()
            self.longevity_conn.close()

        return

        
    def annotate (self, input_data):
        significance = input_data['clinvar__sig']

        if significance not in self.significance_filter:
            return

        gene = input_data['base__hugo']
        if gene not in self.genes:
            return

        isOk = False

        omim_id = input_data['omim__omim_id']
        if omim_id is not None and omim_id != '':
            isOk = True

        ncbi_desc = input_data['ncbigene__ncbi_desc']
        if ncbi_desc is not None and ncbi_desc != '':
            isOk = True

        clinvar_id = input_data['clinvar__id']
        if clinvar_id is not None and clinvar_id != '':
            isOk = True

        pubmed_n = input_data['pubmed__n']
        if pubmed_n is not None and pubmed_n != '':
            isOk = True

        if not isOk:
            return

        sql = """ INSERT INTO cancer (
            chrom,
            pos,
            gene,
            rsid,
            cdnachange,
            zegot,
            alelfreq,
            phenotype,
            significance,
            ncbi
        ) VALUES (?,?,?,?,?,?,?,?,?,?) """

        task = (input_data['base__chrom'], input_data['base__pos'], gene,
                input_data['dbsnp__rsid'], input_data['base__cchange'],
                input_data['vcfinfo__zygosity'], input_data['gnomad__af'],
                input_data['clinvar__disease_names'], significance, ncbi_desc)

        self.longevity_cursor.execute(sql, task)
        return {"col1":""}
