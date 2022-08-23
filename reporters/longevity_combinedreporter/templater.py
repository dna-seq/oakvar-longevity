
def replace_symbols(text, replacements):
    for key, value in replacements.items():
        text = text.replace("{"+key+"}", value)
    return text

def _replase_section(text, replacements, sort=None):
    text_parts = []
    key = next(iter(replacements))
    l = len(replacements[key])
    indeces = range(l)
    if sort is not None:
        seq = replacements[sort["key"]]
        reverse = False
        if sort.get("reverse") is not None:
            reverse = bool(sort["reverse"])
        if sort.get("type"):
            if sort["type"] == 'float':
                seq = [float(el) for el in seq]
            if sort["type"] == 'int':
                seq = [int(el) for el in seq]

        indeces = sorted(range(len(seq)), key=seq.__getitem__, reverse=reverse)
    for i in indeces:
        part = text
        for key in replacements:
            part = part.replace("{"+key+"}", str(replacements[key][i]))
        text_parts.append(part)

    return "".join(text_parts)

def replace_loop(text, replacements, sorts = {}):
    text_parts = []
    last_index = 0
    text_len = len(text)

    sorted_keys = []
    for loop_key in replacements:
        start_tag = "{" + loop_key + "_START}"
        start_ind = text.find(start_tag, 0, text_len)
        sorted_keys.append({"loop_key":loop_key, "start_tag":start_tag, "start_ind":start_ind})

    sorted_keys = sorted(sorted_keys, key=lambda x: x["start_ind"])

    for item in sorted_keys:
        loop_key = item["loop_key"]
        start_tag = item["start_tag"]
        end_tag = "{"+loop_key+"_END}"
        start_ind = item["start_ind"]
        if start_ind == -1:
            continue
        text_parts.append(text[last_index:start_ind])
        ind = start_ind + len(start_tag)
        end_ind = text.find(end_tag, ind, text_len)
        text_parts.append(_replase_section(text[ind:end_ind], replacements[loop_key], sorts.get(loop_key)))
        last_index = end_ind + len(end_tag)
    text_parts.append(text[last_index:text_len])
    return "".join(text_parts)

if __name__ == "__main__":
    f = open("test.html")
    text = f.read()
    f.close()
    sorts = {"DATA":{"key":"DATA_SNP_COUNT", "type":"int"}}
    text = replace_symbols(text, {"DOCUMENT_TITLE":"Test title name"})
    text = replace_loop(text, {"DATA": {"DATA_NAME": ["ca123sc", "cas43c", "casd12c"],
                                         "DATA_SNP_COUNT": [2, 1, 3],
                                         "DATA_DESCRIPTION": ["fwe22few w 3w c", "edefe44w fef af", "feff e2c  ce1c "]},
                               "GENES": {"GENE_NAME": ["casc", "casc", "casdc"],
                                         "GENE_SNP_COUNT": [1, 2, 3],
                                         "GENE_DESCRIPTION": ["fwefew w w c", "edefew fef af", "feff ec  cec "]}
                               }, sorts)
    f = open("test_test.html", 'w+')
    f.write(text)
    f.flush()
    f.close()
