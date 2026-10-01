#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 一鍵重建所有客戶的檢視台。新客戶＝加一支 data_<slug>.py 並在這裡呼叫。
# 模板改 dashlib.py ＝ 所有客戶一起變。
import dashlib, data_demo

for slug in ("hearth", "loom"):
    dashlib.render(data_demo.build(slug))
print("all dashboards built")
