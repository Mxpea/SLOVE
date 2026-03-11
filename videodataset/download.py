import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed

def download_file(file_url, save_path, file_name, i, total):
    try:
        headers = {}
        mode = 'wb'
        initial_pos = 0
        
        # 如果文件已部分存在，获取当前大小，用于真正的断点续传
        if os.path.exists(save_path):
            initial_pos = os.path.getsize(save_path)
            headers['Range'] = f'bytes={initial_pos}-'

        with requests.get(file_url, headers=headers, stream=True, timeout=15) as r:
            # 416 Requested Range Not Satisfiable 表示已经下载完成
            if r.status_code == 416:
                print(f"[{i}/{total}] 文件已完整下载，跳过: {file_name}")
                return True
            elif r.status_code not in [200, 206]:
                print(f"[{i}/{total}] 下载失败 {file_name}: 状态码 {r.status_code}")
                return False
            
            # 如果服务器忽略了 Range 头返回 200，说明不支持续传，重新下载
            if r.status_code == 200 and initial_pos > 0:
                mode = 'wb'
                initial_pos = 0
            elif r.status_code == 206:
                mode = 'ab'

            if initial_pos == 0:
                print(f"[{i}/{total}] 正在下载: {file_name} ...")
            else:
                print(f"[{i}/{total}] 正在断点续传: {file_name} ...")

            with open(save_path, mode) as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        print(f"[{i}/{total}] 下载完成: {file_name}")
        return True
    except Exception as e:
        print(f"[{i}/{total}] 下载异常 {file_name}: {e}")
        return False

def download_videos(max_workers=5):
    url = "https://recsys.westlake.edu.cn/MicroLens-50k-Dataset/MicroLens-50k_videos/"
    
    # 获取当前 py 文件所在的目录
    save_dir = os.path.dirname(os.path.abspath(__file__))

    print(f"开始爬取: {url}\n保存目录: {save_dir}")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"获取网页失败: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 查找带有 .mp4 的 a 标签
    links = soup.find_all('a')
    mp4_links = [link.get('href') for link in links if link.get('href') and link.get('href').endswith('.mp4')]
    
    total = len(mp4_links)
    print(f"找到 {total} 个 .mp4 文件。开始多线程下载 (最大线程数: {max_workers})...")

    tasks = []
    # 使用 ThreadPoolExecutor 进行多线程下载
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for i, href in enumerate(mp4_links, 1):
            file_url = urljoin(url, href)
            file_name = href.split('/')[-1]
            save_path = os.path.join(save_dir, file_name)

            # 提交下载任务到线程池
            tasks.append(executor.submit(download_file, file_url, save_path, file_name, i, total))
            
        # 等待所有任务完成
        for future in as_completed(tasks):
            pass

if __name__ == '__main__':
    download_videos()
