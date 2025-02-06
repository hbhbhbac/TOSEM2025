# Supplemental Materials

This repository contains the replication package for the paper "Securing the Foundation of AI： Securing the Foundation of AI: A Deep Dive into Dependency Management and Security in Deep Learning Frameworks".

## Introduction

We have organized the replication package into four main folders to provide a clear and systematic structure for reproducing our study:

The file directory tree is as follows:

```
Code
├─ 📄dataAnalysis.py
├─ 📄requirements.txt
└─ 📄sourceDataProcess.py
Data
├─ 📁pytorch
│  ├─ 📁dependency change data
│  ├─ 📄dependencyChangeList.json
│  ├─ 📄dependencyCves.json
│  └─ 📄dependencyVulsChangeList.json
└─ 📁tensorflow
   ├─ 📁dependency change data 
   ├─ 📄dependencyChangeList.json
   ├─ 📄dependencyCves.json
   └─ 📄dependencyVulsChangeList.json
Github Repository 
├─ 📁tensorflow
└─ 📁pytorch
Result
├─ 📁RQ1
│  ├─ 📁ChangeFrequence
│  │  ├─ 📄dependencyChangeFrequence.xlsx
│  │  ├─ 📄pt-dep-change-freq.pdf
│  │  └─ 📄tf-dep-change-freq.pdf
│  ├─ 📁ChangePattern
│  │  ├─ 📄dep-change-pattern.png
│  │  ├─ 📄pytorch_edge.txt
│  │  ├─ 📄pytorch_node.txt
│  │  ├─ 📄tensorflow_edge.txt
│  │  └─ 📄tensorflow_node.txt
│  ├─ 📁ChangeReason
│  │  ├─ 📄pytorch&tensorflow_reason.png
│  │  ├─ 📄pytorch_data.json
│  │  └─ 📄tensorflow_data.json
│  └─ 📁Type
│     ├─ 📄dependencyType.json
│     ├─ 📄dependencyType.xlsx
│     └─ 📄type.png
├─ 📁RQ2
│  ├─ 📁VulnerabilityChangePattern
│  │  └─ 📄changePatternData.txt
│  ├─ 📁VulnerabilitySeverity
│  │  ├─ 📄pytorch_introduceVuls.json
│  │  ├─ 📄pytorch_unrepairVuls.json
│  │  ├─ 📄tensorflow_introduceVuls.json
│  │  └─ 📄tensorflow_unrepairVuls.json
│  └─ 📁VulnerabilityType
│     └─ 📄cweDistribute.xlsx
└─ 📁RQ3
   ├─ 📁RepairPractice
   │  ├─ 📄repairPractice.xlsx
   │  └─ 📄tensorflow&pytorch_repair.png
   └─ 📁Survey
      └─ 📄surveyRessult.xlsx
```

**GitHub Repository**:
This folder contains the raw commit history data for TensorFlow and PyTorch, obtained by cloning their GitHub repositories locally using `git`.

**Data**:
This folder is divided into two subfolders, `tensorflow` and `pytorch`, which store all data collected through the GitHub REST API, CVE, and NVD. The file structure within both the `tensorflow` and `pytorch` folders is identical. It first contains a folder named `dependency change data`, which records raw dependency change data obtained through the GitHub REST API for commits between adjacent dependencies. The file `dependencyChangeList.json` contains preprocessed data derived from the raw data, while `dependencyCves.json` includes information about the project's dependencies along with associated vulnerabilities and their attributes. The file `dependencyVulsChangeList.json` represents the data obtained by mapping vulnerabilities to historical change data.

**Code**:

This folder contains two Python scripts for data processing and analysis, as well as dependency configuration files:

- **`sourceDataProcess.py`**: Retrieves raw data, pre-processes the data, and identifies vulnerabilities.
- **`dataAnalysis.py`**: Conducts data analysis on both the raw and pre-processed data to address each research question.

**Result**:
This folder is structured into three subfolders, `RQ1`, `RQ2`, and `RQ3`, each showcasing the findings and outputs for the respective research questions. 

## Usage/Examples

To execute our code, we first need to install the required dependencies. The following dependencies are necessary for our data analysis:

```
gitdb==4.0.11
GitPython==3.1.43
panda==0.3.1
pandas==2.2.3
PyYAML==6.0.2
requests==2.32.3
```

To install these dependencies, navigate to the `Code` folder and run the installation command:

```
cd Code
pip install -r requirements.txt
```

We have organized the data preprocessing and analysis scripts into **`sourceDataProcess.py`** and **`dataAnalysis.py`**, respectively. The necessary data for analysis has been placed in the `Data` folder. Additionally, **`sourceDataProcess.py`** can regenerate and preprocess the data.

To execute **`sourceDataProcess.py`**, follow these steps:

Clone the TensorFlow and PyTorch repositories:

```
cd "Github Repository"
git clone https://github.com/tensorflow/tensorflow.git
git clone https://github.com/pytorch/pytorch.git
```

Ensure data consistency by reverting repositories to the state as of January 9, 2024:

```
cd "Github Repository/tensorflow"
commit=$(git rev-list -n 1 --before="2024-01-09 23:59:59" master)
git checkout $commit
cd..
cd "Github Repository/pytorch"
commit=$(git rev-list -n 1 --before="2024-01-09 23:59:59" master)
git checkout $commit
```

Execute **`sourceDataProcess.py`**:

```
cd Code
python sourceDataProcess.py
```

At the beginning of the script, the variable **`analyse_type`** specifies the target project for analysis. You can modify its value to either `"tensorflow"` or `"pytorch"` to select the desired analysis target:

```
analyse_type = "pytorch" # pytorch/tensorflow
```

The script **`sourceDataProcess.py`** contains multiple functions, each of which is documented with comments explaining its purpose and any required inputs (e.g., filling in a GitHub REST API token for data retrieval). By modifying the **`main`** function, you can execute different tasks. For example, to locate vulnerabilities using the `locateCves()` function, update the `main` function as follows:

```
def main():
    # getDependencyChangeInfo(analyse_type)
    # generateDependencyChangeList(analyse_type)
    locateCves(analyse_type)
```

The script **`dataAnalysis.py`** contains various functions for analyzing the processed data. Each function is documented with comments explaining its purpose. Similar to `sourceDataProcess.py`, modifying the **`main`** function allows executing different analyses.

At the beginning of the script, set **`analyse_type`** to either `"tensorflow"` or `"pytorch"` to specify the target project. For example, to analyze the vulnerability distribution of TensorFlow, set:

```
analyse_type = "tensorflow"
```

Then, in the `main` function, configure the analysis by enabling the appropriate function, such as `analyseVulnerabilitySeverity()`:

```
def main():
    # analyseDepChangeFrequence()
    # analyseDependencyChangePattern()
    # analyseDependencyChangeWithReason()
    analyseVulnerabilitySeverity()
    # analyseVulnerabilityChangePattern()
```

