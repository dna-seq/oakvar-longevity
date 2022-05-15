
def replace_symbols(text, replacements):
    for key, value in replacements.items():
        text = text.replace("{"+key+"}", value)
    return text

def _replase_section(text, replacements):
    text_parts = []
    key = next(iter(replacements))
    l = len(replacements[key])
    for i in range(l):
        part = text
        for key in replacements:
            part = part.replace("{"+key+"}", str(replacements[key][i]))
        text_parts.append(part)

    return "".join(text_parts)

def replace_loop(text, replacements):
    text_parts = []
    last_index = 0
    text_len = len(text)
    for loop_key in replacements:
        start_tag = "{"+loop_key+"_START}"
        end_tag = "{"+loop_key+"_END}"
        start_ind = text.find(start_tag, last_index, text_len)
        if start_ind == -1:
            continue
        text_parts.append(text[last_index:start_ind])
        ind = start_ind + len(start_tag)
        end_ind = text.find(end_tag, ind, text_len)
        text_parts.append(_replase_section(text[ind:end_ind], replacements[loop_key]))
        last_index = end_ind + len(end_tag)
    text_parts.append(text[last_index:text_len])
    return "".join(text_parts)

if __name__ == "__main__":
    f = open("template.html")
    text = f.read()
    f.close()

    text = replace_symbols(text, {"DOCUMENT_TITLE":"Test title name"})
    text = replace_loop(text, {"GENES":{"GENE_NAME":["casc", "casc", "casdc"],
                                        "GENE_SNP_COUNT":[1, 2, 3],
                                        "GENE_DESCRIPTION":["fwefew w w c", "edefew fef af", "feff ec  cec "]}})
    f = open("test.html", 'w+')
    f.write(text)
    f.flush()
    f.close()
