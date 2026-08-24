"""
转换数据集格式为项目标准格式
"""

import os
import json
from typing import List, Dict, Any


def convert_longmemeval_s(input_file: str, output_file: str):
    """转换LongMemEval-S格式"""
    print("=" * 60)
    print("转换 LongMemEval-S 数据集")
    print("=" * 60)

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    converted = []
    for item in data:
        # LongMemEval-S格式
        query = item.get("question", "")
        answer = item.get("answer", "")
        context = item.get("context", "")
        category = item.get("category", "unknown")

        # 提取敏感信息（如果有）
        sensitive_info = []
        if "sensitive" in str(item).lower():
            # 尝试从答案中提取
            if "密码" in query or "password" in query.lower():
                sensitive_info.append(answer)
            elif "卡号" in query or "card" in query.lower():
                sensitive_info.append(answer)

        converted.append({
            "query": query,
            "expected_output": answer,
            "context": context,
            "category": category,
            "sensitive_info": sensitive_info,
            "source": "longmemeval_s"
        })

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(converted, f, ensure_ascii=False, indent=2)

    print(f"转换完成！共 {len(converted)} 题")
    print(f"保存位置: {output_file}")

    # 统计各类别数量
    categories = {}
    for item in converted:
        cat = item["category"]
        categories[cat] = categories.get(cat, 0) + 1

    print("类别统计:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")

    return converted


def convert_locomo(input_file: str, output_file: str):
    """转换LoCoMo格式"""
    print("=" * 60)
    print("转换 LoCoMo 数据集")
    print("=" * 60)

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    converted = []
    for sample in data:
        sample_id = sample.get("sample_id", "")
        conversation = sample.get("conversation", {})

        # 提取对话文本
        context = ""
        for session_key in sorted(conversation.keys()):
            session = conversation[session_key]
            for dia_id in sorted(session.keys()):
                if dia_id.startswith("session_"):
                    continue
                dia = session[dia_id]
                speaker = dia.get("speaker", "")
                text = dia.get("text", "")
                context += f"{speaker}: {text}\n"

        # 处理每个QA对
        for qa in sample.get("qa", []):
            category = qa.get("category", 0)

            # 跳过Adversarial (category 5)
            if category == 5:
                continue

            query = qa.get("question", "")
            answer = qa.get("answer", "")

            # 提取敏感信息（如果有）
            sensitive_info = []
            if "密码" in query or "password" in query.lower():
                # 尝试从答案中提取
                if "密码" in answer or "password" in answer.lower():
                    sensitive_info.append(answer)
            elif "卡号" in query or "card" in query.lower():
                sensitive_info.append(answer)

            converted.append({
                "query": query,
                "expected_output": answer,
                "context": context,
                "category": category,
                "sample_id": sample_id,
                "sensitive_info": sensitive_info,
                "source": "locomo"
            })

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(converted, f, ensure_ascii=False, indent=2)

    print(f"转换完成！共 {len(converted)} 题")
    print(f"保存位置: {output_file}")

    # 统计各类别数量
    categories = {
        1: "Multi Hop",
        2: "Temporal",
        3: "Open Domain",
        4: "Single Hop",
    }
    cat_counts = {}
    for item in converted:
        cat = item["category"]
        cat_counts[cat] = cat_counts.get(cat, 0) + 1

    print("类别统计:")
    for cat, count in sorted(cat_counts.items()):
        cat_name = categories.get(cat, f"Unknown({cat})")
        print(f"  {cat_name}: {count}")

    return converted


def create_combined_dataset(
    longmemeval_file: str,
    locomo_file: str,
    sensitive_file: str,
    output_file: str
):
    """合并所有数据集"""
    print("=" * 60)
    print("合并数据集")
    print("=" * 60)

    all_data = []

    # 读取LongMemEval-S
    if os.path.exists(longmemeval_file):
        with open(longmemeval_file, 'r', encoding='utf-8') as f:
            longmemeval_data = json.load(f)
        all_data.extend(longmemeval_data)
        print(f"LongMemEval-S: {len(longmemeval_data)} 题")

    # 读取LoCoMo
    if os.path.exists(locomo_file):
        with open(locomo_file, 'r', encoding='utf-8') as f:
            locomo_data = json.load(f)
        all_data.extend(locomo_data)
        print(f"LoCoMo: {len(locomo_data)} 题")

    # 读取敏感信息测试
    if os.path.exists(sensitive_file):
        with open(sensitive_file, 'r', encoding='utf-8') as f:
            sensitive_data = json.load(f)
        all_data.extend(sensitive_data)
        print(f"敏感信息测试: {len(sensitive_data)} 题")

    # 保存合并后的数据
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print(f"\n合并完成！共 {len(all_data)} 题")
    print(f"保存位置: {output_file}")

    return all_data


def main():
    """主函数"""
    print("数据集转换工具")
    print("=" * 60)

    # 设置路径
    base_dir = os.path.join(os.path.dirname(__file__), "..")
    raw_dir = os.path.join(base_dir, "data", "raw")
    processed_dir = os.path.join(base_dir, "data", "processed")

    os.makedirs(processed_dir, exist_ok=True)

    # 转换LongMemEval-S
    longmemeval_input = os.path.join(raw_dir, "longmemeval_s.json")
    longmemeval_output = os.path.join(processed_dir, "longmemeval_s_converted.json")

    if os.path.exists(longmemeval_input):
        convert_longmemeval_s(longmemeval_input, longmemeval_output)
    else:
        print(f"文件不存在: {longmemeval_input}")
        print("请先运行 download_datasets.py 下载数据集")

    # 转换LoCoMo
    locomo_input = os.path.join(raw_dir, "locomo10.json")
    locomo_output = os.path.join(processed_dir, "locomo_converted.json")

    if os.path.exists(locomo_input):
        convert_locomo(locomo_input, locomo_output)
    else:
        print(f"文件不存在: {locomo_input}")
        print("请先运行 download_datasets.py 下载数据集")

    # 合并数据集
    sensitive_file = os.path.join(raw_dir, "sensitive_test.json")
    combined_output = os.path.join(processed_dir, "combined_dataset.json")

    create_combined_dataset(
        longmemeval_output,
        locomo_output,
        sensitive_file,
        combined_output
    )

    print("\n转换完成！")


if __name__ == "__main__":
    main()
