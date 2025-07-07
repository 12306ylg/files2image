import math
import os
from pathlib import Path
from typing import Union

from PIL import Image


def file_to_image(file_path: Union[str, Path], output_image_path: Union[str, Path]) -> None:
    """
    将任意文件编码为一张PNG图片。

    工作原理:
    1. 读取文件内容（二进制数据）。
    2. 将文件的原始大小（字节数）打包成一个8字节的头部。
    3. 将头部和文件内容拼接在一起。
    4. 将拼接后的二进制数据逐字节地填充到图片的RGB通道中。
    5. 计算能容纳所有数据的最小图片尺寸（接近正方形）。
    6. 生成并保存图片。

    Args:
        file_path (Union[str, Path]): 要编码的源文件路径。
        output_image_path (Union[str, Path]): 输出图片的保存路径。
    """
    try:
        # 1. 读取文件内容
        with open(file_path, 'rb') as file:
            file_data = file.read()

        # 2. 创建8字节的头部，用于存储原始文件大小
        # 'big'表示大端字节序，确保跨平台一致性
        file_size_bytes = len(file_data).to_bytes(8, 'big')

        # 3. 拼接头部和文件数据
        data_to_encode = file_size_bytes + file_data

        # 4. 计算所需的像素数量
        # 每个像素可以存储3个字节（R, G, B）
        # 使用math.ceil确保分配足够的像素来容纳所有数据
        num_pixels_needed = math.ceil(len(data_to_encode) / 3)

        # 5. 计算最佳图片尺寸（使其尽可能接近正方形）
        width = int(math.sqrt(num_pixels_needed)) + 1
        height = math.ceil(num_pixels_needed / width)

        # 6. 创建一个新的RGB图片
        img = Image.new('RGB', (width, height), color='black')
        pixels = img.load()  # 使用load()方法提高像素访问效率

        # 7. 将数据编码到图片的RGB通道中
        byte_iterator = iter(data_to_encode)
        for i in range(num_pixels_needed):
            # 从迭代器中取出3个字节，如果数据不足则用0填充
            r = next(byte_iterator, 0)
            g = next(byte_iterator, 0)
            b = next(byte_iterator, 0)
            
            # 使用divmod计算像素坐标，比嵌套循环更简洁
            x, y = divmod(i, width)
            pixels[x, y] = (r, g, b)

        # 8. 保存图片
        img.save(output_image_path, 'PNG')
        print(f"文件 '{file_path}' 已成功编码为图片 '{output_image_path}'.")

    except FileNotFoundError:
        print(f"错误: 文件 '{file_path}' 未找到。")
    except Exception as e:
        print(f"编码过程中发生错误: {e}")


def image_to_file(image_path: Union[str, Path], output_file_path: Union[str, Path]) -> None:
    """
    从编码后的图片中解码并恢复原始文件。

    工作原理:
    1. 加载图片并读取所有像素的RGB数据。
    2. 从前几个像素中提取前8个字节，解析出原始文件的确切大小。
    3. 根据文件大小，从像素数据中提取相应数量的字节。
    4. 将提取的字节写入新文件。

    Args:
        image_path (Union[str, Path]): 编码后的图片路径。
        output_file_path (Union[str, Path]): 恢复后文件的保存路径。
    """
    try:
        # 1. 加载图片
        img = Image.open(image_path)
        
        # 2. 从图片的RGB通道中提取所有字节数据
        extracted_bytes = bytearray()
        for pixel in img.getdata():
            extracted_bytes.extend(pixel)

        # 3. 提取前8个字节作为文件大小的头部
        if len(extracted_bytes) < 8:
            raise ValueError("图片数据不足，无法解析文件大小。")
        
        file_size_bytes = extracted_bytes[:8]
        original_file_size = int.from_bytes(file_size_bytes, 'big')

        # 4. 提取文件的实际内容
        # 内容紧跟在8字节的头部之后
        file_data_start = 8
        file_data_end = file_data_start + original_file_size
        
        if len(extracted_bytes) < file_data_end:
            raise ValueError("图片数据不完整，无法恢复完整文件。")
            
        file_data = extracted_bytes[file_data_start:file_data_end]

        # 5. 保存恢复的文件
        with open(output_file_path, 'wb') as file:
            file.write(file_data)
        print(f"图片 '{image_path}' 已成功解码为文件 '{output_file_path}'.")

    except FileNotFoundError:
        print(f"错误: 图片 '{image_path}' 未找到。")
    except Exception as e:
        print(f"解码过程中发生错误: {e}")


def main():
    """主函数，用于演示和测试编码与解码功能。"""
    # 定义测试用的文件名
    original_file = Path("original_test_file.txt")
    encoded_image = Path("encoded_image.png")
    restored_file = Path("restored_test_file.txt")

    # 1. 创建一个测试文件
    print("--- 步骤 1: 创建测试文件 ---")
    try:
        test_content = b"This is a test file.\nIt contains multiple lines and some special characters: !@#$%^&*()\x00\x01\x02"
        original_file.write_bytes(test_content)
        print(f"创建了测试文件: '{original_file}'")

        # 2. 将文件编码为图片
        print("\n--- 步骤 2: 文件 -> 图片 ---")
        file_to_image(original_file, encoded_image)

        # 3. 将图片解码回文件
        print("\n--- 步骤 3: 图片 -> 文件 ---")
        image_to_file(encoded_image, restored_file)

        # 4. 验证文件内容是否一致
        print("\n--- 步骤 4: 验证结果 ---")
        restored_content = restored_file.read_bytes()
        if test_content == restored_content:
            print("✅ 验证成功: 恢复的文件与原始文件完全一致！")
        else:
            print("❌ 验证失败: 文件内容不匹配。")
            print(f"Original len: {len(test_content)}, Restored len: {len(restored_content)}")
            print(f"Original: {test_content}")
            print(f"Restored: {restored_content}")

    finally:
        # 5. 清理测试文件
        print("\n--- 步骤 5: 清理 ---")
        for f in [original_file, encoded_image, restored_file]:
            if f.exists():
                os.remove(f)
                print(f"删除了临时文件: '{f}'")

if __name__ == "__main__":
    main()
