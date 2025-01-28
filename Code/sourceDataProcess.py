# -*- coding: utf-8 -*-
import os
import json
import git
import yaml
import pandas as pd
import requests

analyse_type = "pytorch"
tf_dir = "../Github Repository/" + analyse_type
repo = git.Repo(tf_dir)

# get depdendency change info by github rest api
# if run this function, you need to replace the token with your own token
def getDependencyChangeInfo(analyse_type):
    last_pos = -1
    end_pos = 10000000
    batch_size = 5000
    commits = list(repo.iter_commits("master" if analyse_type == "tensorflow" else "main"))
    last_response = None
    token = "xxx"

    diff_result = []

    commits = list(reversed(commits))
    for index, commit in enumerate(commits):
        if last_pos != -1 and index < last_pos:
            continue
        if index >= end_pos:
            with open(
                "../Data/" + analyse_type + "/dependency change data/result_{}-{}.json".format(last_pos, index),
                "w",
            ) as f:
                json.dump(diff_result, f)
            diff_result = []
            break
        if index + 1 < len(commits):
            now_sha = commit.hexsha
            next_sha = commits[index + 1].hexsha
            url = "https://api.github.com/repos/{}/{}/dependency-graph/compare/{}...{}".format(
                analyse_type, analyse_type, now_sha, next_sha
            )
            print(url)
            while True:
                try:
                    response = requests.get(
                        url=url,
                        headers={
                            "Authorization": "token {}".format(token),
                            "X-GitHub-Api-Version": "2022-11-28",
                        },
                        verify=False,
                    )
                    if response.status_code == 200:
                        print("success: {} -> {}:".format(now_sha, next_sha))
                        print(
                            "basic information: {}/{} change_num: {}".format(
                                index, len(commits), len(response.json())
                            )
                        )
                        diff_item = {
                            "now_sha": now_sha,
                            "next_sha": next_sha,
                            "index": index,
                            "diff": response.json(),
                        }
                        if len(response.json()) != 0:
                            print("founded:")
                            print(diff_item)
                        diff_result.append(diff_item)
                        if response.json() != last_response:
                            last_response = response.json()
                            print("diff")
                        else:
                            print("same")
                        print("")
                        break
                except requests.RequestException:
                    print("error: {} -> {}:".format(now_sha, next_sha))
            if index % batch_size == 0:
                filepath = analyse_type + "/dependency change data/result_{}-{}.json".format(
                    index - batch_size, index
                )

                with open(filepath, "w") as f:
                    json.dump(diff_result, f)
                diff_result = []
    if index % batch_size != 0:
        filepath = analyse_type + "/dependency change data/result_{}-{}.json".format(index - batch_size, index)
        with open(
            filepath,
            "w",
        ) as f:
            json.dump(diff_result, f)
        diff_result = []

def getCommitInformation(sha):
    commit = repo.commit(sha)
    commitItem = {
        "commit_time": commit.committed_datetime.isoformat(),
        "commit_message": commit.message,
    }
    return commitItem

# simplify dependency change data, generate dependency change list
def generateDependencyChangeList(analyse_type):
    file_path = f"../Data/{analyse_type}/dependency change data"
    for filename in os.listdir(file_path):
        sourceData = []
        with open(os.path.join(file_path, filename)) as f:
            data = f.read()
        sourceData = yaml.safe_load(data)
        for item in sourceData:
            if len(item["diff"]) != 0:
                commitItem = getCommitInformation(item["next_sha"])
                for diffItem in item["diff"]:
                    result_item = {**item, **commitItem, **diffItem}
                    result_item.pop("diff")
                    json_data.append(result_item)
    def sort_fn(item):
        return item["index"]

    json_data = sorted(json_data, key=sort_fn)
    file_path = "../Data/" + analyse_type
    with open(file_path + "/dependencyChangeList.json", "w") as f:
        json.dump(json_data, f)

    df = pd.DataFrame(json_data)
    df.to_excel(file_path + "/dependencyChangeList.xlsx", index=False)

# transform version to number
def versionToNum(version):
    if isinstance(version, int):
        return version
    version = version.replace("dev", "").split("-")[0]
    verlist = version.split(".")
    if len(verlist) == 4:
        verlist = verlist[:3]
    scale = 1
    sum = 0
    for part in reversed(verlist):
        subsum = 0
        if len(part) > 4:
            part = part[0:3]
        for index, ch in enumerate(part):
            subsum = subsum * 10**index + ord(ch) - ord("0")
        sum += subsum * scale
        scale *= 1e3
    sum = int(sum)
    return sum

# judge the relationship between two versions
def compareVersion(ver1, ver2, type):
    num1 = versionToNum(ver1)
    num2 = versionToNum(ver2)
    if type == 1:
        return num1 > num2
    elif type == 2:
        return num1 < num2
    elif type == 3:
        return num1 >= num2
    elif type == 4:
        return num1 <= num2
    else:
        return False

# judge whether the version is in the range of the vulnerability according to the border and version range
def versionInRangeAcBorder(ver1, ver, border):
    lver = ver[0]
    rver = ver[1]
    if border[0] and border[1]:
        return compareVersion(ver1, lver, 3) and compareVersion(ver1, rver, 4)
    elif border[0]:
        return compareVersion(ver1, lver, 3) and compareVersion(ver1, rver, 2)
    elif border[1]:
        return compareVersion(ver1, lver, 1) and compareVersion(ver1, rver, 4)
    else:
        return compareVersion(ver1, lver, 1) and compareVersion(ver1, rver, 2)


# judge whether the version is in the range of the vulnerability according to the version range
def versionInRange(version, cveItem):
    verlist = version.replace(" ", "").split(",")
    if verlist[0] == "":
        return False
    cveVersion = cveItem["version"]
    if len(cveVersion) == 0:
        return False
    cveBorder = cveItem["border"]
    lborder = -1
    rborder = -1
    maxborder = 999999999999
    rclose = False
    nval = []
    for ver in verlist:
        if "||" in ver:
            nval.append(versionToNum(ver.split("||")[0]))
        if ver[0].isdigit():
            lborder = rborder = ver
        elif ver[0:2] == ">=":
            lborder = ver[2:]
        elif ver[0:2] == "<=":
            rborder = ver[2:]
            rclose = True
        elif ver[0] == "<":
            rborder = ver[1:]
        elif ver[0:2] == "~>":
            lborder = ver[2:]
        elif ver[0] == "~":
            lborder = ver[1:]
            firstNum = ver[1:].split(".")[0]
            secondNum = ver[1:].split(".")[1]
            rborder = firstNum + "." + str(int(secondNum) + 1) + ".0"
        elif ver[0] == "^":
            lborder = ver[1:]
            firstNum = ver[1:].split(".")[0]
            rborder = str(int(firstNum) + 1) + ".0.0"
        lborder = versionToNum(lborder)
        rborder = versionToNum(rborder)
        if rborder == -1:
            rborder = maxborder
        elif rclose:
            rborder = rborder + 1
        lborder = 0 if lborder == -1 else lborder

        if cveBorder[0] and compareVersion(rborder, cveVersion[0], 2):
            return False
        if not cveBorder[0] and compareVersion(rborder, cveVersion[0], 4):
            return False
        if cveBorder[1] and compareVersion(lborder, cveVersion[1], 1):
            return False
        if not cveBorder[1] and compareVersion(lborder, cveVersion[1], 3):
            return False

        return True
    return

# judge whether the vulnerability exists according to the name and version
def isCveExist(name, version):
    file_path = f"../Data/{analyse_type}/"
    with open(file_path + "dependencyCves.json", "r") as f:
        finalResult = json.load(f)
    for item in finalResult:
        if item["name"] == name:
            cves = []
            vuls = item["vuls"]
            for vul in vuls:
                if versionInRange(version, vul):
                    cves.append(vul)
            return cves
    return []


# analyse the vulnerability information of the updated dependency
def analyseUpdateChange(depitem):
    name, preversion, nowversion = (
        depitem["name"],
        depitem["pre_version"],
        depitem["now_version"],
    )
    precves, nowcves, decves, addcves = [], [], [], []
    with open("../Data/" + analyse_type + "/dependencyCves.json", "r") as f:
        finalResult = json.load(f)
    for item in finalResult:
        if item["name"] == name:
            vuls = item["vuls"]
            for vul in vuls:
                prehave = versionInRange(preversion, vul)
                nowhave = versionInRange(nowversion, vul)
                if prehave:
                    precves.append(vul)
                if nowhave:
                    nowcves.append(vul)
                if prehave and not nowhave:
                    decves.append(vul)
                if not prehave and nowhave:
                    addcves.append(vul)
    return {
        "index": depitem["index"],
        "name": name,
        "change_type": "updated",
        "pre_version": preversion,
        "now_version": nowversion,
        "introduce": addcves,
        "repair": decves,
        "pre_cves": precves,
        "now_cves": nowcves,
    }


# locate cves in dependency change list
def locateCves(analyse_type):
    difflist = []
    file_path = f"../Data/{analyse_type}"
    with open(file_path + "/dependencyChangeList.json", "r") as f:
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
            }
            tempData.append(dep)
        else:
            nameList = [item["name"] for item in tempData]
            change_type = item["change_type"]
            dep = {
                "name": item["name"],
                "version": item["version"],
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

    cveCycleData = []
    for index, item in enumerate(resultList):
        print(f"progress: {index}/{len(resultList)}")
        for depitem in item["data"]:
            depitem["index"] = item["index"]
            if depitem["name"] == "tensorflow":
                continue
            if depitem["change_type"] == "added":
                cves = isCveExist(depitem["name"], depitem["version"])
                if len(cves) > 0:
                    cveCycleData.append(
                        {
                            "index": item["index"],
                            "name": depitem["name"],
                            "version": depitem["version"],
                            "change_type": "added",
                            "introduce": cves,
                            "repair": [],
                        }
                    )
            elif depitem["change_type"] == "removed":
                cves = isCveExist(depitem["name"], depitem["version"])
                if len(cves) > 0:
                    cveCycleData.append(
                        {
                            "index": item["index"],
                            "name": depitem["name"],
                            "version": depitem["version"],
                            "change_type": "removed",
                            "introduce": [],
                            "repair": cves,
                        }
                    )
            elif depitem["change_type"] == "updated":
                ritem = analyseUpdateChange(depitem)
                if len(ritem["introduce"]) > 0 or len(ritem["repair"]) > 0:
                    cveCycleData.append(ritem)

    with open(file_path + "/dependencyChangeList.json", "r") as f:
        difflist = json.load(f)
    for item in cveCycleData:
        for diffitem in difflist:
            if item["index"] == diffitem["index"]:
                item["time"] = diffitem["commit_time"]
                break
    
    with open(file_path + "/dependencyVulsChangeList.json", "w") as f:
        json.dump(cveCycleData, f)

# console
def main():
    # getDependencyChangeInfo(analyse_type)
    # generateDependencyChangeList(analyse_type)
    locateCves(analyse_type)

if __name__ == "__main__":
    main()