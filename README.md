# oakvar-longevity

Repository for longevity annotators for OakVar.

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

## setting up

Install conda environment
-------------------------
Annotation modules and dvc are included in the conda environment that goes with the project.
The environment can be setup either with Anaconda or micromamba (superior version of conda).
Here is installation instruction for micromamba:
```
wget -qO- https://micromamba.snakepit.net/api/micromamba/linux-64/latest | tar -xvj bin/micromamba
```
We can use ./micromamba shell init ... to initialize a shell (.bashrc) and a new root environment in ~/micromamba:
```
./bin/micromamba shell init -s bash -p ~/micromamba
source ~/.bashrc
```
To create a micromamba environment use:
```
micromamba create -f environment.yaml
micromamba activate oakvar-longevity
```

The instructions above are provided for Linux and MacOS (note: in MacOS you have to install wget).
For Windows you can either install Linux Subsystem or use Windows version of anaconda.


Installing modules
--------------------

First, read the [installation guide](https://rkimoakbioinformatics.github.io/oakvar/install_system/) about OakVar, launch system setup and locate the path to the modules directory:

```base
ov system setup
```

```base
ov config md
```

Change to the module folder, for example:
```bash
ov config md .
```

Then activate github [update script](https://github.com/dna-seq/opencravat-longevity/blob/main/utility_scripts/gh_update.py) to download modules to moduals path:
```bash
python gh_update.py --path YOUR_PATH
```

Run opencravat:
```bash
ov gui
```

