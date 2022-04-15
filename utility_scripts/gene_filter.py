import pandas
import requests, sys

csv_file = 'C:/dev/opencravat_longevity/annotators/longevitymap/data/longevitymap.csv'
url = "https://rest.ensembl.org/vep/human/id/"

col_names = ['id', 'association', 'population', 'snp', 'genes', 'pubmed']
df = pandas.read_csv(csv_file, header=0, names=col_names)
empty_counter = 0
multiple_counter = 0

for i in range(df.shape[0]):
    genes = str(df.loc[(i,'genes')])
    if genes.find(',') > 0:
        r = requests.get(url+df.loc[(i,'snp')], headers={"Content-Type": "application/json"})
        if not r.ok:
            r.raise_for_status()
            sys.exit()
        recieved_genes = set()
        old_genes = set(genes.split(','))

        json_data = r.json()
        for item1 in json_data:
            sequence = item1.get('transcript_consequences')
            if type(sequence) is list:
                for item2 in sequence:
                    g = item2.get('gene_symbol')
                    if g is not None:
                        recieved_genes.add(g)

        valid_genes = recieved_genes.intersection(old_genes)
        l = len(valid_genes)
        if l == 0:
            empty_counter += 1
        if l > 1:
            multiple_counter += 1

        genes_str = ','.join(valid_genes)
        df.loc[(i, 'genes')] = genes_str
        print(i,'/',df.shape[0]," ",genes_str)

print("Empty:", empty_counter)
print("Multiple:", multiple_counter)

df.to_csv('./longevitymap_fixed.csv')

print('Finish')