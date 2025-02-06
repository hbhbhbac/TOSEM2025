import pandas as pd
import os
import json
import git
import re

analyse_type = "tensorflow"
tf_dir = "../Github Repository/" + analyse_type
repo = git.Repo(tf_dir)

def dealList(list, type="df"):
    list = sorted(list, key=lambda x: x["commit_time"])
    for item in list:
        item["year"] = int(item["commit_time"].split("-")[0])
        item["month"] = int(item["commit_time"].split("-")[1])
        item["day"] = int(item["commit_time"].split("-")[2].split("T")[0])
    if type == "list":
        return list
    columns = range(list[0]["year"], list[-1]["year"] + 1)

    index = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    data = [[0 for i in range(len(columns))] for j in range(12)]
    month_all = 0
    pre_month = 0
    pre_year = 0
    for item in list:
        if item["month"] == pre_month:
            month_all += len(item["diff"])
        elif pre_month != 0:
            data[pre_month - 1][pre_year - columns[0]] = month_all
            month_all = 0
        pre_month = int(item["month"])
        pre_year = int(item["year"])

    df = pd.DataFrame(data, index=index, columns=columns)
    if type == "df":
        return df
    if type == "dateList":
        datelist = []
        for col in df.columns:
            datelist += df[col].tolist()
        return datelist

def getCommitInformation(sha):
    commit = repo.commit(sha)
    commitItem = {
        "commit_time": commit.committed_datetime.isoformat(),
        "commit_message": commit.message,
    }
    return commitItem

# rq1 analyse the frequency of dependency change
def analyseDepChangeFrequence():
    fileList = os.listdir("../Data/" + analyse_type + "/dependency change data")
    diffTimeList = []
    for file in fileList:
        with open("../Data/" + analyse_type + "/dependency change data/" + file) as f:
            data = f.read()
        sourceData = json.loads(data)
        for item in sourceData:
            commitItem = getCommitInformation(item["next_sha"])
            updateDiffList = []
            depDict = {}
            for diff in item["diff"]:
                name = diff["name"]
                if name in depDict:
                    depDict[name] = "update"
                else:
                    change_type = diff["change_type"]
                    depDict[name] = change_type
            for key, value in depDict.items():
                updateDiffList.append({"name": key, "change_type": value})

            diffTimeList.append(
                {
                    "index": item["index"],
                    "next_sha": item["next_sha"],
                    "commit_time": commitItem["commit_time"],
                    "diff": updateDiffList,
                }
            )
    df = dealList(diffTimeList, "df")

    changeType = ["added", "removed", "update"]
    ydatalist = []
    templist = []
    for ctype in changeType:
        templist = []
        for item in diffTimeList:
            tempitem = item.copy()
            tempitem["diff"] = [x for x in item["diff"] if x["change_type"] == ctype]
            templist.append(tempitem)
        datelist = dealList(templist, "dateList")
        ydatalist.append(datelist)
    datelist = dealList(diffTimeList, "dateList")
    ydatalist.append(datelist)
    xdatalist = []
    columns = df.columns
    for item in columns:
        xdatalist += [item] * 12
    changeType = ["added", "removed", "update", "all"]
    file_path = "../Result/RQ1/ChangeFrequence/dependencyChangeFrequence.xlsx"
    for index, item in enumerate(ydatalist):
        tempitem = []
        for i in range(0, len(item), 12):
            tempitem.append(sum(item[i : i + 12]))
        df = pd.DataFrame(tempitem, columns=["Number"])
        df.index = columns  
        sheet_name = f"{analyse_type}_{changeType[index]}"

        try:
            with pd.ExcelWriter(file_path, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
                df.to_excel(writer, sheet_name=sheet_name)
        except FileNotFoundError:
            with pd.ExcelWriter(file_path, engine="openpyxl", mode="w") as writer:
                df.to_excel(writer, sheet_name=sheet_name)

# rq1 generate dependency change pattern node and edge
def analyseDependencyChangePattern():
    fileList = os.listdir("../Data/" + analyse_type + "/dependency change data")
    diffTimeList = []
    for file in fileList:
        with open("../Data/" + analyse_type + "/dependency change data/" + file) as f:
            data = f.read()
        sourceData = json.loads(data)
        for item in sourceData:
            commitItem = getCommitInformation(item["next_sha"])
            updateDiffList = []
            depDict = {}
            for diff in item["diff"]:
                name = diff["name"]
                if name in depDict:
                    depDict[name] = "update"
                else:
                    change_type = diff["change_type"]
                    depDict[name] = change_type
            for key, value in depDict.items():
                updateDiffList.append({"name": key, "change_type": value})

            diffTimeList.append(
                {
                    "index": item["index"],
                    "next_sha": item["next_sha"],
                    "commit_time": commitItem["commit_time"],
                    "diff": updateDiffList,
                }
            )
    datalist = dealList(diffTimeList, "list")
    depNumList = [len(x["diff"]) for x in datalist if len(x["diff"]) != 0]
    filterdatalist = [x for x in datalist if len(x["diff"]) != 0]
    maxnum = max(depNumList)
    numdict = {}
    for i in range(1, maxnum + 1):
        if depNumList.count(i) > 0:
            for item in filterdatalist:
                if len(item["diff"]) == i:
                    deppair = ""
                    for dep in item["diff"]:
                        deppair += dep["name"] + " "
                    if deppair in numdict:
                        numdict[deppair] += 1
                    else:
                        numdict[deppair] = 1
    with open("../Result/RQ1/Type/dependencyType.json") as f:
        geneDict = json.load(f)
    dependency_dict = geneDict[analyse_type + "_dependency_dict"]
    node_dict = {}
    edge_dict = {}
    for key, value in numdict.items():
        deps = key.split(" ")
        if len(deps) == 2:
            if deps[0] in node_dict:
                node_dict[deps[0]]["single_count"] = value
            else:
                node_dict[deps[0]] = {"single_count": value, "edge_count": 0}
        else:
            for i in range(len(deps) - 1):
                if deps[i] in node_dict:
                    node_dict[deps[i]]["edge_count"] += value
                else:
                    node_dict[deps[i]] = {"single_count": 0, "edge_count": value}
                for j in range(i + 1, len(deps) - 1):
                    edge_pair = (
                        deps[i] + " " + deps[j]
                        if deps[i] < deps[j]
                        else deps[j] + " " + deps[i]
                    )
                    if edge_pair in edge_dict:
                        edge_dict[edge_pair] += value
                    else:
                        edge_dict[edge_pair] = value

    for key, value in node_dict.items():
        if key in dependency_dict:
            value["function"] = dependency_dict[key]["description"]
            value["category"] = dependency_dict[key]["category"]
        else:
            value["function"] = "None"
            value["category"] = "None"

        
    with open(
        f"../Result/RQ1/ChangePattern/{analyse_type}_node.txt", "w", encoding="utf-8"
    ) as f:
        f.write("Id,Label,single_count,edge_count,category\n")
        for index, (key, value) in enumerate(node_dict.items()):
            f.write(
                f"{index},\"{key}\",{value['single_count']},{value['edge_count']},{value['category']}\n"
            )
    with open(f"../Result/RQ1/ChangePattern/{analyse_type}_edge.txt", "w") as f:
        f.write("Source,Target,Weight\n")
        for index, (key, value) in enumerate(edge_dict.items()):
            nodes = list(node_dict.keys())
            if key.split(" ")[0] in nodes and key.split(" ")[1] in nodes:
                dep_pair = key.split(" ")
                source = list(node_dict.keys()).index(dep_pair[0])
                target = list(node_dict.keys()).index(dep_pair[1])
                f.write(f"{source},{target},{value}\n")

# rq1 filter dependency change with reason
def analyseDependencyChangeWithReason():
    difflist = []
    with open("../Data/" + analyse_type + "/dependencyChangeList.json", "r") as f:
        difflist = json.load(f)

    preindex = -1
    resultList = []
    tempData = []
    for index, item in enumerate(difflist):
        dep = {}
        if item["index"] != preindex:
            if preindex != -1:
                resultList.append({"index": preindex, "data": tempData})
            tempData = []
            preindex = item["index"]
            dep = {
                "name": item["name"],
                "version": item["version"],
                "change_type": item["change_type"],
                "commit_message": item["commit_message"],
                "type": ""
            }
            tempData.append(dep)
        else:
            nameList = [item["name"] for item in tempData]
            change_type = item["change_type"]
            dep = {
                "name": item["name"],
                "version": item["version"],
                "commit_message": item["commit_message"],
            }
            if item["name"] in nameList:
                sameItem = tempData[nameList.index(item["name"])]
                del tempData[nameList.index(item["name"])]
                preVersion = ""
                nowVersion = ""
                if sameItem["change_type"] == "removed":
                    preVersion = sameItem["version"]
                    nowVersion = item["version"]
                elif sameItem["change_type"] == "added":
                    preVersion = item["version"]
                    nowVersion = sameItem["version"]
                else:
                    preVersion = sameItem["pre_version"]
                    nowVersion = sameItem["now_version"]
                dep["pre_version"] = preVersion
                dep["now_version"] = nowVersion
                change_type = "updated"
            dep["change_type"] = change_type
            tempData.append(dep)
    resultList.append({"index": preindex, "data": tempData})

    data = []
    for item in resultList:
        for dep in item["data"]:
            data.append(
                {
                    "index": item["index"],
                    "name": dep["name"],
                    "change_type": dep["change_type"],
                    "commit_message": dep["commit_message"],
                    "type": ""
                }
            )

    filterdata = []
    for item in data:
        dep_name = item["name"]
        commit_message = item["commit_message"]
        name_pattern = dep_name + r"[^a-zA-Z]"
        if re.search(name_pattern, commit_message):
            filterdata.append({
                "name": item["name"],
                "commit_message": item["commit_message"],
                "change_type": item["change_type"],
                "type": item["type"]
            })

    with open("../Result/RQ1/ChangeReason/" + analyse_type + "_data.json", "w") as f:
        json.dump(filterdata, f)

# rq2 analyse introduced and repaired vulnerabilities
def analyseVulnerabilitySeverity():
    with open("../Data/" + analyse_type + "/dependencyVulsChangeList.json", "r") as f:
        cveCycleDatalist = json.load(f)
    introduceVulsIdSet = set()
    vulsChangeDict = {}
    for item in cveCycleDatalist:
        for vul in item["introduce"]:
            introduceVulsIdSet.add(vul['cve_id'])
            if vul['cve_id'] not in vulsChangeDict:
                vulsChangeDict[vul['cve_id']] = True
            else:
                vulsChangeDict[vul['cve_id']] = True
        for vul in item["repair"]:
            if vul['cve_id'] in vulsChangeDict:
                vulsChangeDict[vul['cve_id']] = False
    unrepairedVulsIdSet = set()
    for key, value in vulsChangeDict.items():
        if value:
            unrepairedVulsIdSet.add(key)
    dependencyCves = []
    with open("../Data/" + analyse_type + "/dependencyCves.json", "r") as f:
        dependencyCves = json.load(f)
    introlist, unrepairlist = [], []
    for cve_id in introduceVulsIdSet:
        for item in dependencyCves:
            for vul in item["vuls"]:
                if vul["cve_id"] == cve_id:
                    if vul.get("baseSeverity", None) != None and "cwe_id" in vul['baseSeverity']:
                        introlist.append({
                            "dependency": item["name"],
                            "cve_id": cve_id,
                            "baseSeverity": vul.get("baseSeverity", None),
                        })
    for cve_id in unrepairedVulsIdSet:
        for item in dependencyCves:
            for vul in item["vuls"]:
                if vul["cve_id"] == cve_id:
                    if vul.get("baseSeverity", None) != None and "cwe_id" in vul['baseSeverity']:
                        unrepairlist.append({
                            "dependency": item["name"],
                            "cve_id": cve_id,
                            "baseSeverity": vul.get("baseSeverity", None),
                        })

    introdict = {}
    unrepaireddict = {}
    for item in introlist:
        baseSeverity = item['baseSeverity']['baseSeverity']
        if baseSeverity in introdict:
            introdict[baseSeverity] += 1
        else:
            introdict[baseSeverity] = 1
    for item in unrepairlist:
        baseSeverity = item['baseSeverity']['baseSeverity']
        if baseSeverity in unrepaireddict:
            unrepaireddict[baseSeverity] += 1
        else:
            unrepaireddict[baseSeverity] = 1
    print("introduceVuls:")
    for key, value in introdict.items():
        print(key, value)
    print("unrepairVuls:")
    for key, value in unrepaireddict.items():
        print(key, value)
    with open("../Result/RQ2/VulnerabilitySeverity/" + analyse_type + "_introduceVuls.json", "w") as f:
        json.dump(introlist, f)  
    with open("../Result/RQ2/VulnerabilitySeverity/" + analyse_type + "_unrepairVuls.json", "w") as f:
        json.dump(unrepairlist, f)   

# rq2 analyse vulnerability change pattern
def analyseVulnerabilityChangePattern():
    with open("../Data/" + analyse_type + "/dependencyVulsChangeList.json", "r") as f:
        cveCycleDatalist = json.load(f)
    with open("../Data/" + analyse_type + "/dependencyChangeList.json", "r") as f:
        difflist = json.load(f)
    for item in cveCycleDatalist:
        for diff in difflist:
            if item["index"] == diff["index"]:
                item["next_sha"] = diff["next_sha"]
                break
    introNum, repairNum, upIntroNum, upRepNum = 0, 0, 0, 0
    addNum, removeNum, updateNum = 0, 0, 0
    addcomitset = set()
    removecomitset = set()
    uodatecomitset = set()
    allcommitset = set()
    upintroList, uprepList = [], []
    for item in cveCycleDatalist:
        if item["change_type"] == "added":
            introNum += len(item["introduce"])
            addcomitset.add(item['next_sha'])
        elif item["change_type"] == "removed":
            repairNum += len(item["repair"])
            removeNum += 1
            removecomitset.add(item['next_sha'])
        elif item["change_type"] == "updated":
            upIntroNum += len(item["introduce"])
            upRepNum += len(item["repair"])
            updateNum += 1
            uodatecomitset.add(item['next_sha'])
            upintroList.append(len(item["introduce"]))
            uprepList.append(len(item["repair"]))
        allcommitset.add(item['next_sha'])
    addNum = len(addcomitset)
    removeNum = len(removecomitset)
    updateNum = len(uodatecomitset)
        
    with open(
        f"../Result/RQ2/VulnerabilityChangePattern/changePatternData.txt", "a", encoding="utf-8"
    ) as f:
        f.write(f'{analyse_type:}\n')
        f.write(
            f"Accumulated vulnerabilities introduced due to new additions: {introNum}, Number of additions: {addNum}, Ratio: {introNum/addNum}\n"
        )
        f.write(
            f"Accumulated vulnerabilities removed due to deletions: {repairNum}, Number of deletions: {removeNum}, Ratio: {repairNum/removeNum}\n"
        )
        f.write(
            f"Accumulated vulnerabilities introduced due to updates: {upIntroNum}, Number of updates: {updateNum}, Ratio: {upIntroNum/updateNum}\n"
        )
        f.write(
            f"Accumulated vulnerabilities removed due to updates: {upRepNum}, Number of updates: {updateNum}, Ratio: {upRepNum/updateNum}\n"
        )
        f.write(
            f"Sum: {introNum + repairNum + upIntroNum + upRepNum}, Number of all commits: {len(allcommitset)}, Ratio: {(introNum + repairNum + upIntroNum + upRepNum)/len(allcommitset)}\n"
        )




def main():
    # analyseDepChangeFrequence()
    # analyseDependencyChangePattern()
    # analyseDependencyChangeWithReason()
    # analyseVulnerabilitySeverity()
    # analyseVulnerabilityChangePattern()
    


if __name__ == "__main__":
    main()
