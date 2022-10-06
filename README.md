# oakvar-longevity

**Oakvar-Longevity** is a module of OakVar which annotates user genome with longevity associated gene variants using the longevitymap annotator, and provides longevity PRS, variants, drugs and major risks(oncorisk) reports with longevity-combinedreporter.


The repository contains:
* annotators:

  **longevitymap** - for longevity related information, original data from [https://genomics.senescence.info](https://genomics.senescence.info/longevity/)
  
  **prs** - for polygenic risk scores
* reporters:

  **longevity_combinedreporter** - outputs prs, longevity report, cancer report
 
* webviewerwidgets:

  **wglongevitymap** - widget for presenting a detailed view for longevity annotator
 
* other folders for preprocessing information for development purposes
* environment.yaml file for conda environment

You can learn how to install and use this module in this documentation: https://just-dna-seq.readthedocs.io/en/oakvar/
