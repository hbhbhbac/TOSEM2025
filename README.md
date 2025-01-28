# Supplemental Materials

This repository contains the replication package for the paper "Securing the Foundation of AI： Securing the Foundation of AI: A Deep Dive into Dependency Management and Security in Deep Learning Frameworks".

## Introduction

We have organized the replication package into four main folders to provide a clear and systematic structure for reproducing our study:

**GitHub Repository**:
This folder contains the raw commit history data for TensorFlow and PyTorch, obtained by cloning their GitHub repositories locally using `git`.

**Data**:
This folder is divided into two subfolders, `tensorflow` and `pytorch`, which store all data collected through the GitHub REST API. Each subfolder includes:

- Dependency change data.
- Processed dependency change summaries.
- Dependency vulnerability data.
- Mapped dependency change information related to identified vulnerabilities.

**Code**:
This folder contains two Python scripts for data processing and analysis:

- **`sourceDataProcess.py`**: Prepares and organizes raw data into a structured format for analysis.
- **`dataAnalysis.py`**: Conducts analyses on the processed data to answer the study’s research questions and generate the corresponding results.

**Result**:
This folder is structured into three subfolders, `RQ1`, `RQ2`, and `RQ3`, each showcasing the findings and outputs for the respective research questions. The results include processed data, visualizations, and summary files.

```
Code
├─ 📄dataAnalysis.py
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
│  │  ├─ 📄pt_introduceVuls.json
│  │  ├─ 📄pt_unrepairVuls.json
│  │  ├─ 📄tf_introduceVuls.json
│  │  └─ 📄tf_unrepairVuls.json
│  └─ 📁VulnerabilityType
│     └─ 📄cweDistribute.xlsx
└─ 📁RQ3
   ├─ 📁RepairPractice
   │  ├─ 📄repairPractice.xlsx
   │  └─ 📄tensorflow&pytorch_repair.png
   └─ 📁Survey
      └─ 📄surveyRessult.xlsx
```



