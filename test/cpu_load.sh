#!/bin/bash
rrdtool graph cpu_load.png \
-n DEFAULT:9:'/home/max/.fonts/MSYH.TTF' \
--font-render-mode normal \
--graph-render-mode normal \
--slope-mode \
-t "CPU负载   6小时之前的数据   分别为5、10、15分钟" \
-v "CPU负载" \
-w 650 -h 120 \
--start  now-4h \
-x MINUTE:5:HOUR:1:HOUR:1:0:'%H:%M' \
DEF:value1=Current_Load.rrd:1:AVERAGE \
DEF:value2=Current_Load.rrd:2:AVERAGE \
DEF:value3=Current_Load.rrd:3:AVERAGE \
COMMENT:"\n" \
COMMENT:"\t\t\t当前值\t\t平均值\t\t最大值\t\t最小值\n" \
COMMENT:"\n" \
AREA:value1#00ff00:"5分钟负载" \
GPRINT:value1:LAST:%13.2lf \
GPRINT:value1:AVERAGE:%13.2lf \
GPRINT:value1:MAX:%13.2lf \
GPRINT:value1:MIN:%13.2lf \
COMMENT:"\n" \
LINE2:value2#ff0000:"10分钟负载" \
GPRINT:value2:LAST:%13.2lf \
GPRINT:value2:AVERAGE:%13.2lf \
GPRINT:value2:MAX:%13.2lf \
GPRINT:value2:MIN:%13.2lf \
COMMENT:"\n" \
LINE2:value3#000fff:"15分钟负载" \
GPRINT:value3:LAST:%13.2lf \
GPRINT:value3:AVERAGE:%13.2lf \
GPRINT:value3:MAX:%13.2lf \
GPRINT:value3:MIN:%13.2lf \
COMMENT:"\n" \
COMMENT:"最后更新时间 \:$(date '+%Y-%m-%d %H\:%M')\n" \
COMMENT:"\n" \
COMMENT:"\t\t\t\t\t\t\t\t\t\t\t\t\t嘉值云计算团队开发"  \
COMMENT:"\t\t\t\t\t\t\t\t\t\t\t\t\t嘉值云计算@2012 版权所有" 
#LINE2:value2#00ff00:"10分钟负载":STACK
