from django.shortcuts import render, redirect, HttpResponse
from app01 import models
from utils.pay import AliPay
import json
import time


def ali():
    # 沙箱环境地址：https://openhome.alipay.com/platform/appDaily.htm?tab=info
    app_id = "2016091500518677"
    # POST请求，用于最后的检测,用于修改订单状态的
    notify_url = "http://47.74.178.255:8000/page2/"
    # notify_url = "http://www.wupeiqi.com:8804/page2/"

    # GET请求，用于页面的跳转展示
    return_url = "http://47.74.178.255:8000/page3/"
    # return_url = "http://www.wupeiqi.com:8804/page2/"

    merchant_private_key_path = "keys/app_private_2048.txt"
    alipay_public_key_path = "keys/alipay_public_2048.txt"

    alipay = AliPay(
        appid=app_id,
        app_notify_url=notify_url,
        return_url=return_url,
        app_private_key_path=merchant_private_key_path,
        alipay_public_key_path=alipay_public_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥
        debug=True,  # 默认False,
    )
    return alipay


def page1(request):
    if request.method == "GET":
        return render(request, 'page1.html')
    else:
        money = float(request.POST.get('money'))
        order_num = 'xxxxx'+str(time.time())
        alipay = ali()
        # 生成支付的url
        query_params = alipay.direct_pay(
            subject="充气式韩红",  # 商品简单描述
            out_trade_no=order_num,  # 商户订单号
            total_amount=money,  # 交易金额(单位: 元 保留俩位小数)
        )

        pay_url = "https://openapi.alipaydev.com/gateway.do?{}".format(query_params)
        # ==================== 在数据库中添加订单 ====================
        models.Order.objects.create(num=order_num, price=money)

        return redirect(pay_url)


def page2(request):
    alipay = ali()
    if request.method == "POST":
        # 检测是否支付成功
        # 去请求体中获取所有返回的数据：状态/订单号
        # 检验数据是否合法
        from urllib.parse import parse_qs
        body_str = request.body.decode('utf-8')
        post_data = parse_qs(body_str)

        post_dict = {}
        for k, v in post_data.items():
            post_dict[k] = v[0]
        print(post_dict)

        sign = post_dict.pop('sign', None)
        status = alipay.verify(post_dict, sign)
        # 如果status为True就是成功了
        print('POST验证', status)
        if status:
            num = post_dict.get('out_trade_no')
            models.Order.objects.filter(num=num).update(status=2)
        return HttpResponse('POST返回')


def page3(request):
    alipay = ali()
    params = request.GET.dict()
    sign = params.pop('sign', None)
    status = alipay.verify(params, sign)
    print('GET验证', status)
    if status:
        return HttpResponse('支付成功')
    else:
        return HttpResponse('支付失败')


def page4(request):
    order_list = models.Order.objects.all()
    return render(request, 'page4.html', {'order_list': order_list})
