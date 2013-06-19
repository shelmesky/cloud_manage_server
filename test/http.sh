#!/bin/bash
rrdtool graph http.png \
--font-render-mode normal \
--graph-render-mode normal \
--slope-mode \
-n DEFAULT:9:'/home/max/.fonts/MSYH.TTF' \
-t "HTTP响应时间   6小时之前的数据" \
-v "响应时间" \
-w 650 -h 200 \
--start  now-6h \
-x MINUTE:5:HOUR:1:HOUR:1:0:'%H:%M' \
DEF:value1=HTTP.rrd:1:AVERAGE \
COMMENT:"\n" \
COMMENT:"\t\t\t当前值\t\t\t平均值\t\t最大值\t\t最小值\n" \
COMMENT:"\n" \
AREA:value1#00ff00:"HTTP响应时间" \
GPRINT:value1:LAST:%13.2lf%s \
GPRINT:value1:AVERAGE:%13.2lf%s \
GPRINT:value1:MAX:%13.2lf%s \
GPRINT:value1:MIN:%13.2lf%s \
COMMENT:"\n" \
COMMENT:"m\: 毫秒 / u\:微秒\n" \
COMMENT:"最后更新时间 \:$(date '+%Y-%m-%d %H\:%M')\n" \
COMMENT:"\n" \
COMMENT:"\t\t\t\t\t\t\t\t\t\t\t\t\t嘉值云计算团队开发"  \
COMMENT:"\t\t\t\t\t\t\t\t\t\t\t\t\t嘉值云计算@2012 版权所有" 
#LINE2:value2#00ff00:"10分钟负载":STACK
#--upper-limit 4 \
#--rigid \
