import click
from prs_converter import PrsConverter
from percentails import Percentails, DBHelper
from prs_data_item import PrsDataItem

populations:dict[str,str] = {}
populations["all"] = DBHelper.ALEL_FREQENCY
populations["oth"] = DBHelper.OTHER
populations["fin"] = DBHelper.FINISH
populations["afr"] = DBHelper.AFRICAN
populations["amr"] = DBHelper.AMERICAN
populations["asj"] = DBHelper.ASHKENAZI
populations["eas"] = DBHelper.EASTERN_ASIAN
populations["nfe"] = DBHelper.NONFINISH
populations["sas"] = DBHelper.SOUTH_ASIAN

def pars_tsv(path):
    res = []
    with open(path) as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) == 0:
                continue
            revers = 0
            if len(parts) == 4:
                revers = int(parts[3])
            res.append(PrsDataItem(parts[0].strip(), parts[1].strip(), parts[2].strip(), revers))
    return res

@click.command()
@click.option('--prstsv', help='Path to tsv file with prs files data. 0 - path to file, 1 - description, 2 - name (unique), 3 - revers fag (1|0), optional')
@click.option('--prsdb', help='Path to sqlite database file which will be used for PRS postagregator.')
@click.option('--gnomdb', help='Path to sqlite database file of GNOM annotator.')
@click.option('--distsize', default=10000, help='Size of distribution to generate for percentails calculation. Rubust results from 100 000 but it is slow.')
@click.option('--verbos', default=1, help='Turn on 1 and off 0 messages to console')
@click.option('--population', default="all", help="Population for percentiles calulation. "
    "[all, oth - Other, Fin - Finish, afr - African, amr - American, asj - Ashkenzi, eas - Eastern Asia, nfe - non Finish, sas - South Asia]")
@click.option('--reset', default=1, help='1 - default, activate reset mode that deletes everething and create everething from scratch, '
                                         '0 - activate add, remove mode. Adds prs that nor in database and removes that exists but not in the list.')


def do_main(prstsv, prsdb, gnomdb, distsize, verbos, population, reset):
    global populations
    converter = PrsConverter(prsdb, verbos)
    percentails = Percentails(gnomdb, prsdb, distsize, verbos)
    prs_list = pars_tsv(prstsv)
    print("\n start converter\n")
    prs_names = converter.process(prs_list, reset == 1)
    print("\n start percentails\n")
    percentails.process(prs_list, prs_names, populations[population])
    print("Finish!")

if __name__ == "__main__":
    do_main()
