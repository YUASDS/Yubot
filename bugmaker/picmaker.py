from PIL import Image
from PIL import ImageDraw


def picmaker():
    #加载底图
    base_img = Image.open('.\Script\CLOUDS.PNG')
    # 可以查看图片的size和mode，常见mode有RGB和RGBA，RGBA比RGB多了Alpha透明度
    # print base_img.size, base_img.mode
    box = (6, 6)  # 底图上需要P掉的区域
    # img_mask = Image.new('1',(20,20))
    # 加载需要P上去的图片
    tmp_img = Image.open('.\Script\BA.GIF')
    # 这里可以选择一块区域或者整张图片
    # region = tmp_img.crop((0,0,304,546)) #选择一块区域
    # 或者使用整张图片
    region = tmp_img

    # 使用 paste(region, box) 方法将图片粘贴到另一种图片上去.
    # 注意，region的大小必须和box的大小完全匹配。但是两张图片的mode可以不同，合并的时候回自动转化。如果需要保留透明度，则使用RGMA mode
    # 提前将图片进行缩放，以适应box区域大小
    # region = region.rotate(180) #对图片进行旋转
    # region = region.resize((box[2] - box[0], box[3] - box[1]))
    r, g, b, a = base_img.split()
    base_img.paste(region, box, mask=a)
    base_img.show()  # 查看合成的图片
    base_img.save('./out.png')  #保存图片


def img():
    #加载中间透明的手机图片
    base_img = Image.open('.\Script\CLOUDS.GIF')
    #新建透明底图，大小和手机图一样，mode使用RGBA，保留Alpha透明度，颜色为透明
    #Image.new(mode, size, color=0)，color可以用tuple表示，分别表示RGBA的值
    target = Image.new('RGBA', base_img.size, (0, 0, 0, 0))
    box = (6, 6)  #区域
    # 加载需要狐狸像
    region = Image.open('.\Script\BA.GIF')
    #region = region.rotate(180) #旋转180度
    #确保图片是RGBA格式，大小和box区域一样
    region = region.convert("RGBA")
    region = region.resize((box[2] - box[0], box[3] - box[1]))
    #先将狐狸像合成到底图上
    target.paste(region, box)
    #将手机图覆盖上去，中间透明区域将狐狸像显示出来。
    target.paste(
        base_img, (0, 0),
        base_img)  #第一个参数表示需要粘贴的图像，中间的是坐标，最后是一个是mask图片，用于指定透明区域，将底图显示出来。
    target.show()
    target.save('./out.png')  # 保存图片


def make():
    pilim = Image.open('1.jpg')
    draw = ImageDraw.Draw(pilim)
    draw.rectangle([0, 0, 500, 500], fill=(255, 255, 255, 255))
    del draw
    pilim.save('2.jpg')


picmaker()