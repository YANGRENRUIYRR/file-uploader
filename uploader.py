import os
import base64
import requests # pip install requests
from datetime import datetime # pip install datetime

# 配置信息 - 请修改为你的信息
GITHUB_USERNAME = "your_username"
REPO_NAME = "your_repo"
GITHUB_TOKEN = "your_github_personal_token_here"
BRANCH = "main"
COMMIT_MESSAGE = f"Auto upload: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

# 忽略列表
IGNORE_FILES = [
    
]

# GitHub API 基础URL
BASE_URL = f"https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}"

def should_ignore(file_path):
    """检查文件是否应该被忽略"""
    for ignore in IGNORE_FILES:
        if ignore in file_path:
            return True
    return False

def get_file_content(file_path):
    """读取文件内容并进行Base64编码"""
    try:
        with open(file_path, 'rb') as file:
            content = file.read()
            return base64.b64encode(content).decode('utf-8')
    except Exception as e:
        print(f"无法读取文件 {file_path}: {str(e)}")
        return None

def get_current_file_sha(path):
    """获取文件在GitHub上的当前SHA值"""
    url = f"{BASE_URL}/contents/{path}?ref={BRANCH}"
    response = requests.get(url, headers={
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    })
    
    if response.status_code == 200:
        return response.json().get('sha')
    return None

def upload_file_to_github(file_path, content):
    """上传文件到GitHub"""
    relative_path = os.path.relpath(file_path)
    url = f"{BASE_URL}/contents/{relative_path}"
    
    sha = get_current_file_sha(relative_path)
    payload = {
        "message": COMMIT_MESSAGE,
        "content": content,
        "branch": BRANCH
    }
    
    if sha:
        payload["sha"] = sha
    
    method = "PUT"
    response = requests.request(
        method, url, 
        headers={'Authorization': f'token {GITHUB_TOKEN}'},
        json=payload
    )
    
    if response.status_code in (200, 201):
        print(f"成功上传: {relative_path}")
    else:
        print(f"上传失败: {relative_path}, 状态码: {response.status_code}, 响应: {response.text}")

def main():
    """主函数：遍历目录并上传文件"""
    print(f"开始上传文件到 GitHub 仓库: {REPO_NAME}")
    
    for root, _, files in os.walk('.'):
        for file in files:
            file_path = os.path.join(root, file)
            
            if should_ignore(file_path):
                print(f"忽略文件: {file_path}")
                continue
                
            content = get_file_content(file_path)
            if content:
                upload_file_to_github(file_path, content)
    
    print("上传完成!")

if __name__ == "__main__":
    main()    
