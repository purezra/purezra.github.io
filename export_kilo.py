#!/usr/bin/env python3
"""
export_kilo.py
将 Kilo Code 的 ui_messages.json 批量转换为 Markdown 文件
用法:
    python export_kilo.py                         # 自动扫描默认 tasks 目录
    python export_kilo.py --tasks <tasks目录路径>  # 指定 tasks 目录
    python export_kilo.py --file <ui_messages.json路径>  # 转换单个文件
    python export_kilo.py --out <输出目录>         # 指定输出目录（默认: ./kilo_exports）
"""

import json
import os
import sys
import argparse
from datetime import datetime, timezone


# ─── 默认 tasks 路径（Windows）───────────────────────────────────────────────
DEFAULT_TASKS_PATHS = [
    os.path.expandvars(r"%APPDATA%\Code\User\globalStorage\kilocode.kilo-code\tasks"),
    os.path.expandvars(r"%APPDATA%\Code - Insiders\User\globalStorage\kilocode.kilo-code\tasks"),
    os.path.expanduser(r"~/.config/Code/User/globalStorage/kilocode.kilo-code/tasks"),  # Linux
    os.path.expanduser(r"~/Library/Application Support/Code/User/globalStorage/kilocode.kilo-code/tasks"),  # macOS
]


def ts_to_time(ts):
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')


def parse_tool_text(text):
    try:
        obj = json.loads(text)
        tool = obj.get('tool', '未知工具')
        lines = [f"**工具**: `{tool}`"]
        if 'batchFiles' in obj:
            files = [f['path'] for f in obj['batchFiles']]
            lines.append("**读取文件**:\n" + '\n'.join(f"  - `{p}`" for p in files))
        elif 'todos' in obj:
            lines.append("**Todo 列表**:")
            for t in obj['todos']:
                status = '✅' if t['status'] == 'completed' else ('🔄' if t['status'] == 'in_progress' else '⬜')
                lines.append(f"  - {status} {t['content']}")
        elif 'command' in obj:
            lines.append(f"**命令**: `{obj['command']}`")
        else:
            for k, v in obj.items():
                if k != 'tool' and isinstance(v, str):
                    lines.append(f"**{k}**: `{v}`")
        return '\n'.join(lines)
    except Exception:
        return text


def convert(json_path, out_path, metadata_path=None):
    with open(json_path, 'r', encoding='utf-8') as f:
        messages = json.load(f)

    # 读取 task_metadata.json（如果存在）
    title = None
    if metadata_path and os.path.exists(metadata_path):
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            title = meta.get('taskText') or meta.get('name') or meta.get('title')
            if title and len(title) > 80:
                title = title[:80] + '...'
        except Exception:
            pass

    lines = []
    first_ts = messages[0]['ts'] if messages else 0
    heading = title if title else "Kilo Code 对话记录"
    lines.append(f"# {heading}\n")
    lines.append(f"**对话开始**: {ts_to_time(first_ts)}  ")
    lines.append(f"**导出时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    lines.append("---\n")

    SKIP = {'api_req_started', 'checkpoint_saved', 'api_req_retry_delayed', 'resume_task', 'condense_context'}

    for msg in messages:
        ts = msg.get('ts', 0)
        mtype = msg.get('type', '')
        subtype = msg.get('say') or msg.get('ask') or ''
        text = msg.get('text', '').strip()
        images = msg.get('images', [])

        if subtype in SKIP or not text:
            continue

        time_str = ts_to_time(ts)

        if mtype == 'say':
            if subtype == 'text':
                lines.append(f"## 🤖 AI 回复\n*{time_str}*\n")
                lines.append(text)
            elif subtype == 'reasoning':
                lines.append(f"### 💭 推理过程\n*{time_str}*\n")
                lines.append('> ' + text.replace('\n', '\n> '))
            elif subtype == 'completion_result':
                lines.append(f"## ✅ 任务完成\n*{time_str}*\n")
                lines.append(text)
            elif subtype == 'user_feedback':
                lines.append(f"## 👤 用户消息\n*{time_str}*\n")
                lines.append(text)
                if images:
                    lines.append(f"\n*（附带 {len(images)} 张图片）*")
            elif subtype == 'command':
                lines.append(f"### 💻 执行命令\n*{time_str}*\n")
                lines.append(f"```bash\n{text}\n```")
            elif subtype == 'command_output':
                lines.append(f"### 📤 命令输出\n*{time_str}*\n")
                lines.append(f"```\n{text}\n```")
            elif subtype == 'error':
                lines.append(f"### ❌ 错误\n*{time_str}*\n")
                lines.append(f"```\n{text}\n```")

        elif mtype == 'ask':
            if subtype == 'tool':
                lines.append(f"### 🔧 工具调用\n*{time_str}*\n")
                lines.append(parse_tool_text(text))
            elif subtype == 'followup':
                lines.append(f"### 💬 跟进问题\n*{time_str}*\n")
                lines.append(text)

        lines.append("")

    output = '\n'.join(lines)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(output)
    return len(messages)


def find_tasks_dir():
    for p in DEFAULT_TASKS_PATHS:
        if os.path.isdir(p):
            return p
    return None


def main():
    parser = argparse.ArgumentParser(description='将 Kilo Code 对话记录导出为 Markdown')
    parser.add_argument('--tasks', help='tasks 目录路径')
    parser.add_argument('--file', help='单个 ui_messages.json 路径')
    parser.add_argument('--out', default='./kilo_exports', help='输出目录（默认: ./kilo_exports）')
    args = parser.parse_args()

    out_dir = args.out

    # 单文件模式
    if args.file:
        task_dir = os.path.dirname(args.file)
        meta_path = os.path.join(task_dir, 'task_metadata.json')
        out_path = os.path.join(out_dir, 'conversation.md')
        count = convert(args.file, out_path, meta_path)
        print(f"✅ 已导出: {out_path}（共 {count} 条消息）")
        return

    # 批量模式
    tasks_dir = args.tasks or find_tasks_dir()
    if not tasks_dir:
        print("❌ 找不到 tasks 目录，请用 --tasks 参数指定路径")
        print("   示例: python export_kilo.py --tasks \"%APPDATA%\\Code\\User\\globalStorage\\kilocode.kilo-code\\tasks\"")
        sys.exit(1)

    print(f"📂 扫描目录: {tasks_dir}")
    task_ids = [d for d in os.listdir(tasks_dir) if os.path.isdir(os.path.join(tasks_dir, d))]

    if not task_ids:
        print("⚠️ 未找到任何对话记录")
        return

    success, skipped = 0, 0
    for task_id in sorted(task_ids):
        task_path = os.path.join(tasks_dir, task_id)
        json_path = os.path.join(task_path, 'ui_messages.json')
        meta_path = os.path.join(task_path, 'task_metadata.json')

        if not os.path.exists(json_path):
            skipped += 1
            continue

        out_path = os.path.join(out_dir, f"{task_id}.md")
        try:
            count = convert(json_path, out_path, meta_path)
            print(f"  ✅ {task_id} → {count} 条消息")
            success += 1
        except Exception as e:
            print(f"  ❌ {task_id} 失败: {e}")
            skipped += 1

    print(f"\n🎉 完成！成功 {success} 个，跳过 {skipped} 个")
    print(f"📁 输出目录: {os.path.abspath(out_dir)}")


if __name__ == '__main__':
    main()
