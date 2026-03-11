import os
import csv

def main():
    # 获取当前所在目录和外层 data 目录
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_input_path = os.path.join(base_dir, 'MicroLens-50k_titles.csv')
    data_dir = os.path.join(base_dir, '..', 'data')
    csv_output_path = os.path.join(data_dir, 'videos.csv')

    # 确保 data 文件夹存在
    os.makedirs(data_dir, exist_ok=True)

    # 1. 读取当前文件夹下存在的视频的 ID (以 .mp4 结尾的文件)
    video_ids = set()
    for filename in os.listdir(base_dir):
        if filename.endswith(('.mp4', '.avi', '.mkv', '.mov')):  # 可以根据实际格式扩展
            vid = filename.rsplit('.', 1)[0]
            if vid.isdigit():
                video_ids.add(vid)

    # 2. 读取 MicroLens-50k_titles.csv 中所有视频的名称并形成字典
    title_map = {}
    if os.path.exists(csv_input_path):
        with open(csv_input_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            # 跳过表头 (item,title)
            next(reader, None)
            for row in reader:
                if len(row) >= 2:
                    item_id = row[0].strip()
                    full_title = row[1].strip()
                    title_map[item_id] = full_title
    else:
        print(f"找不到文件: {csv_input_path}")
        return

    # 3. 解析标题及Tag，并保存到 ../data/videos.csv 中
    with open(csv_output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'title', 'tag'])

        count = 0
        for vid in video_ids:
            if vid in title_map:
                full_title = title_map[vid]
                
                # 通过查找第一个 '#' 符号来分离 title 和 tag
                idx = full_title.find('#')
                if idx != -1:
                    title = full_title[:idx].strip()
                    tag = full_title[idx:].strip()
                else:
                    title = full_title.strip()
                    tag = ''
                
                writer.writerow([vid, title, tag])
                count += 1
                
    print(f"处理完成！成功分离并写入了 {count} 条视频数据到 {csv_output_path}")

if __name__ == '__main__':
    main()
