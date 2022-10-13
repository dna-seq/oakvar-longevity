import sqlite3
from sqlite3 import Error
import os
import longevity_ref_homo


class LongevitymapReport:
    _is_active = False
    ref_homo = longevity_ref_homo.RefHomoEdgecases()
    col_index = 0


    def init(self, reporter):
        self.parent = reporter
        self.ref_homo.init(self)


    def setActive(self):
        self._is_active = True
        self.ref_homo.setActive()


    def data_name(self):
        return "LONGEVITY"


    def data(self):
        return {"IND":[], "POPULATION":[], "SNP":[], "GENE":[], "DESCRIPTION":[],
                         "CODING":[], "REF":[], "ALT":[], "CDNACHANGE":[],
                         "DESEASES":[], "ZEGOT":[], "ALELFREQ":[], "NUCLEOTIDES":[], "PRIORITY":[], "NCBIDESC":[], "WEIGHT":[],
                        "WEIGHTCOLOR":[]}


    def setup(self):
        self.ref_homo.setup()


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
                html += "<td>" + part + "</td>"
            html += "</tr>"
        html += "</table>\n<br/>"
        return html


    def get_nucleotides(self, ref, alt, zygocity):
        if zygocity == 'hom':
            return alt+"/"+alt, {alt, alt}
        return alt+"/"+ref, {alt, ref}


    def get_alt_weight(self, allele, state, zygosity, weight, ref, nuq_set):
        if allele.find(",") != -1:
            allele = allele.split(",")
            state = state.split(",")
            zygosity = zygosity.split(",")
            weight = weight.split(",")
        else:
            allele = [allele]
            state = [state]
            zygosity = [zygosity]
            weight = [weight]

        for i in range(len(allele)):
            if state[i] != "alt":
                continue
            if zygosity[i] == "hom":
                if {allele[i], allele[i]} == nuq_set:
                    return weight[i]
            else:
                if {allele[i], ref} == nuq_set:
                    return weight[i]
        return 0


    def process_row(self, row):
        if not self._is_active:
            return

        self.ref_homo.process_row(row)

        if self.parent.get_value(row, 'longevitymap__association') != "significant":
            return

        snp = self.parent.get_value(row, 'longevitymap__rsid')
        allele_field = self.parent.get_value(row, 'longevitymap__allele')
        state_field = self.parent.get_value(row, 'longevitymap__state')
        zygosity_field = self.parent.get_value(row, 'longevitymap__zygosity')
        weight_field = self.parent.get_value(row, 'longevitymap__weight')
        alt = self.parent.get_value(row, 'base__alt_base')
        ref = self.parent.get_value(row, 'base__ref_base')
        zygot = self.parent.get_value(row, 'vcfinfo__zygosity')
        nuq, nuq_set = self.get_nucleotides(ref, alt, zygot)

        w = self.get_alt_weight(allele_field, state_field, zygosity_field, weight_field, ref, nuq_set)

        if w == 0:
            return

        self.col_index += 1
        self.parent.data["LONGEVITY"]["IND"].append(self.col_index)
        self.parent.data["LONGEVITY"]["WEIGHT"].append(w)
        color = self.parent.get_color(w, 1.5)
        self.parent.data["LONGEVITY"]["WEIGHTCOLOR"].append(color)
        self.parent.data["LONGEVITY"]["POPULATION"].append(self.parent.get_value(row, 'longevitymap__population'))
        self.parent.data["LONGEVITY"]["SNP"].append(snp)
        self.parent.data["LONGEVITY"]["GENE"].append(self.parent.get_value(row, 'longevitymap__genes'))
        temp = self._createSubTable(self.parent.get_value(row, 'longevitymap__info'))
        temp += self.parent.get_value(row, 'longevitymap__description').replace("____", "<br/>").replace("__", " ")
        self.parent.data["LONGEVITY"]["DESCRIPTION"].append(temp)
        self.parent.data["LONGEVITY"]["CODING"].append(self.parent.get_value(row, 'base__coding'))
        self.parent.data["LONGEVITY"]["REF"].append(ref)
        self.parent.data["LONGEVITY"]["ALT"].append(alt)
        self.parent.data["LONGEVITY"]["CDNACHANGE"].append(self.parent.get_value(row, 'base__cchange'))
        self.parent.data["LONGEVITY"]["DESEASES"].append(self.parent.get_value(row, 'clinvar__disease_names'))
        self.parent.data["LONGEVITY"]["ZEGOT"].append(zygot)
        self.parent.data["LONGEVITY"]["ALELFREQ"].append(self.parent.get_value(row, 'gnomad__af'))
        self.parent.data["LONGEVITY"]["NUCLEOTIDES"].append(nuq)
        self.parent.data["LONGEVITY"]["PRIORITY"].append(self.parent.get_value(row, 'longevitymap__priority'))
        self.parent.data["LONGEVITY"]["NCBIDESC"].append(self.parent.get_value(row, 'ncbigene__ncbi_desc'))


    def end(self):
        self.ref_homo.end(self.col_index)