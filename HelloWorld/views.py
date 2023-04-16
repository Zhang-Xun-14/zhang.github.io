from django.http import HttpResponse
from django.shortcuts import render


def weathers():
    import pyecharts.options as opts
    from pyecharts.charts import Line, Page
    from pyecharts.components import Table
    from pyecharts.globals import ThemeType

    from bs4 import BeautifulSoup
    from requests import get
    from lxml import etree

    data = get('https://tianqi.so.com/weather/101090501')
    data.encoding = data.apparent_encoding
    data = data.text

    html = BeautifulSoup(data, 'lxml')
    current_weather = html.select(
        "div.tab-pane.weather-today > div.g-clearfix.pane-top > div.cur-weather.g-fl > p"
    )
    future = html.select("div.weather-card > ul.weather-columns > li > div")

    first_data, second_data = zip(
        *[n.get_text().split('：', 1) for n in current_weather]
    )

    dates, weather, temperature, wind = [], [], [], []
    ds, wr, te, wd = dates.append, weather.append, temperature.append, wind.append
    count = -1
    for n in future:
        text2 = n.get_text()
        count += 1
        index = count % 7
        match index:
            case 0 | 2:
                pass
            case 1:
                ds(text2)
            case 3:
                wr(text2.replace('\\n', '').strip())
            case 4:
                te(text2)
            case 5:
                if '风' in text2:
                    wd(text2)
                    count += 1
            case _:
                wd(text2)

    days = [f"{ds}\n{wd}\n{wr}" for ds, wd, wr in zip(dates, wind, weather)]
    low, high = zip(*[z.split('/', 1) for z in temperature])
    high = [h.strip('℃') for h in high]

    today_index = etree.HTML(data).xpath(
        r"//div[@class='tabs-content']/div[1]/div[contains(@class,'tip-item')]/div/text()"
    )
    titles, today_data = [], []
    tes, tta = titles.append, today_data.append
    for title, data in zip(today_index[::2], today_index[1::2]):
        tes(title)
        tta(data)

    def table_first():
        table1 = Table()
        table1.add(first_data, [second_data[0:]])
        table1.set_global_opts(
            title_opts=opts.ComponentTitleOpts(
                title="天气信息"
            )
        )
        table1.render_notebook()
        return table1

    def table_second():
        table2 = Table()
        table2.add(titles, [today_data], attributes={
            "border": False,
            "style": "width:1500px; height:200px;"
        }
                   )
        table2.set_global_opts()
        table2.render_notebook()
        return table2

    def broken():
        weather_broken = (
            Line(init_opts=opts.InitOpts(
                width="1500px", theme=ThemeType.CHALK
            )).add_xaxis(
                xaxis_data=days
            ).add_yaxis(
                series_name="最高气温",
                y_axis=high,
                markpoint_opts=opts.MarkPointOpts(data=[
                    opts.MarkPointItem(type_="max", name="最大值"),
                    opts.MarkPointItem(type_="min", name="最小值")
                ]),
                markline_opts=opts.MarkLineOpts(
                    data=[opts.MarkLineItem(type_="average", name="平均值")]
                ),
            ).add_yaxis(
                series_name="最低气温",
                y_axis=low,
                markpoint_opts=opts.MarkPointOpts(
                    data=[opts.MarkPointItem(value=-2, name="周最低", x=1,
                                             y=-1.5)
                          ]
                ),
                markline_opts=opts.MarkLineOpts(data=[
                    opts.MarkLineItem(type_="average", name="平均值"),
                    opts.MarkLineItem(symbol="none", x="90%", y="max"),
                    opts.MarkLineItem(symbol="circle", type_="max",
                                      name="最高点"
                                      )
                ]),
            ).set_global_opts(
                title_opts=opts.TitleOpts(title="未来15天气温变化"),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
                toolbox_opts=opts.ToolboxOpts(),
                xaxis_opts=opts.AxisOpts(axislabel_opts={"interval": '0'},
                                         type_="category",
                                         boundary_gap=False
                                         ),
            )
        )
        weather_broken.render_notebook()
        return weather_broken

    html_big = Page(page_title='数据分析可视化展示')
    html_big.add(
        table_first(),
        table_second(),
        broken()
    )
    html_big.render('./templates/Weather_big.html')

    with open("./templates/Weather_big.html", "r+",
              encoding='utf-8') as html_big:
        html_yuan = str(BeautifulSoup(html_big, 'lxml')).replace(
            '<p class="title" style="font-size: 18px; font-weight:bold;"> </p>',
            ''
        ).replace(
            '<p class="subtitle" style="font-size: 12px;"> </p>', ''
        ).replace(
            '</head>', '<style>img {display:block;}</style></head>'
        ).replace('<br/> ', '')

        html_big.seek(0)  # 将光标移动到文件开头
        html_big.truncate()  # 删除光标后所有内容
        html_big.write(html_yuan)  # 写入经过去白边的源代码
        html_big.close()  # 保存关闭文件


def hello(request):
    # return HttpResponse("Hello world ! ")
    context = {'hello': 'Hello, welcome here!'}
    return render(request, 'zhx.html', context)


def weather_hello(request):
    weathers()
    return render(request, 'Weather_big.html')
