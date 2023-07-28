# 注册用户的issue存储到文件中，并发送邮件通知
import requests
import os
import base64
import json

from task.utils.sendMsg import send_email


def get_issue(keyword):
    print("获取issue内容")
    url = f"https://api.github.com/search/issues?q={keyword}+state:open+in:title+repo:Sjj1024/DataHub"
    headers = {
        'Authorization': f'Bearer {os.environ.get("TOKEN")}'
    }
    response = requests.request("GET", url, headers=headers).json()
    print(response)
    issue_list = response.get("items")
    for iss in issue_list:
        # 存储用户成功后，再关闭issue
        issNum = iss.get("number")
        # '[regist]userName:1024'
        if "regist" in iss.get("title"):
            userName = iss.get("title", "").replace("[regist]userName:", "")
            content = iss.get("body")
            res = save_user(userName, content)
            if res:
                # 关闭issue并且贴标签
                close_issue(issNum, "closed", ["user"])
                send_email(f"注册FileHub用户成功:{userName}", f"userName: {userName}")
            else:
                # 发送邮件
                send_email("注册FileHub用户失败:", f"userName: {userName}")
        # 通过分享
        elif "share" in iss.get("title"):
            # 获取类别，直接通过
            file_type = iss.get("title", "").split("FileHub:")[2]
            content = iss.get("body")
            # 暂时分享直接通过
            close_issue(issNum, "closed", [file_type, "share"])
            send_email(f"Filehub分享审核通过: {file_type}", f"FileLink: {content}")


def close_issue(num, state, labels):
    print("关闭issue")
    url = f"https://api.github.com/repos/Sjj1024/DataHub/issues/{num}"
    payload = json.dumps({
        "state": state,
        "labels": labels
    })
    headers = {
        'Authorization': f'Bearer {os.environ.get("TOKEN")}',
        'Content-Type': 'text/plain'
    }
    response = requests.request("PATCH", url, headers=headers, data=payload)
    print(response.text)


def save_user(userName, content):
    print("保存用户")
    url = f"https://api.github.com/repos/Sjj1024/DataHub/contents/FileData/users/{userName}.txt"
    base64_content = base64.b64encode(content.encode("utf-8"))
    payload = json.dumps({
        "message": "Register Filehub User",
        "content": base64_content.decode("utf-8")
    })
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': f'Bearer {os.environ.get("TOKEN")}',
        'X-GitHub-Api-Version': '2022-11-28',
        'Content-Type': 'text/plain'
    }
    response = requests.request("PUT", url, headers=headers, data=payload).json()
    print(response)
    if response.get("content"):
        return True
    else:
        return False


def run():
    print("开始执行")
    # 获取issue列表：open and user
    keywords = ["regist", "share"]
    for k in keywords:
        get_issue(k)


if __name__ == '__main__':
    run()
