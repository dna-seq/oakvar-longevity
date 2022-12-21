# oakvar-longevity

**Oakvar-Longevity** is a module of OakVar which annotates user genome with longevity associated gene variants using the longevitymap annotator, and provides longevity PRS, variants, drugs and major risks(oncorisk) reports with longevity-combinedreporter.


The repository contains:
* postaggregators:

  **just_longevitymap** - postagregator for longevity report in oakvar
  
  **just_prs** -  postagregato for polygenic risk scores
  
  **just_cancer** and **just_coronary**-  postagregator for major health risks
* reporters:

  **longevity2reporter** - outputs prs, longevity report, major risks report (contains cancer and coronary arthery diseases)

* webviewerwidgets:

  **wglongevitymap** - widget for presenting a detailed view for longevity annotator

* other folders for preprocessing information for development purposes
* environment.yaml file for conda environment

# Setting up

First, git clone the repository and activate submodules:
```bash
git clone --recurse-submodules git@github.com:dna-seq/oakvar-longevity.git
```

Then, activate the environment. We provide environment.yaml that allows setting up the project quickly with Conda or [Micromamba](https://mamba.readthedocs.io/en/latest/user_guide/micromamba.html).
Here we describe instructions to install with micromamba, however conda/anaconda installation is the same.
You can either do it from bash or with graphical user interface of you IDE.
First, install [micromamba](https://mamba.readthedocs.io/en/latest/installation.html), then run:
```bash
micromamba create --file environment.yaml
micromamba activate oakvar-longevity
```
After installation OakVar will be available with ov command and you can install the modules with:
```bash
ov module install path_to_the_module
```

Then, you are ready to use.
Note: as the project contains submodules if changes happeneed inside any of them you can keep submodules updated with:
```bash
git submodule update --recursive --remote
```

# Documentation

You can learn how to install and use modules from this repository from [Just-DNA-Seq Documentation](https://just-dna-seq.readthedocs.io/en/oakvar/viewing-reports.html)

------------------
You can join our discord if you want to discuss the project or if you encountered any issue: https://discord.gg/5WU6aSANXy
