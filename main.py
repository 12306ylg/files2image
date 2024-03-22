
from PIL import Image


def file_to_image(file_path, output_image_path):
    # 读取文件内容
    with open(file_path, 'rb') as file:
        file_data = file.read()
    # 将文件内容转换为16进制
    hex_data = file_data.hex()
    # 确定图片尺寸
    # 每个像素的RGB通道可以存储6位16进制数据，所以每个像素可以存储18位文件数据
    pixel_count = len(hex_data) // 3
    width = int(pixel_count ** 0.5)
    height= (int(pixel_count / width)/2)+1
    width,height=round(width),round(height)
    # 创建一个新的图片
    img = Image.new('RGB', (width, height))
    # 将16进制数据编码到图片的RGB通道中
    pixel_index = 0
    for y in range(height):
        for x in range(width):
            if pixel_index < len(hex_data):
             try:
                r = int(hex_data[pixel_index:pixel_index+2], 16)
                g = int(hex_data[pixel_index+2:pixel_index+4], 16)
                b = int(hex_data[pixel_index+4:pixel_index+6], 16)
                img.putpixel((x, y), (r, g, b))
                pixel_index += 3*2
             except Exception:break;break
            else:
                img.putpixel((x, y), (0, 0, 0))

    # 保存图片
    img.save(output_image_path)
def image_to_file(image_path, output_file_path):
    # 加载图片
    img = Image.open(image_path)
    # 从图片的RGB通道中提取16进制数据
    hex_data = ''
    for pixel in img.getdata():
        r, g, b = pixel
        hex_data += f'{r:02x}{g:02x}{b:02x}'
    # 将16进制数据转换为原始文件数据
    hex_data=hex_data.rstrip('0')
    file_data = bytes.fromhex(hex_data)
    # 保存文件
    with open(output_file_path, 'wb') as file:
        file.write(file_data)
if __name__ == "__main__":
    pass