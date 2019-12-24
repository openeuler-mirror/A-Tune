# tuning<a name="ZH-CN_TOPIC_0213225933"></a>

## 功能描述<a name="section124121426195015"></a>

使用指定的项目文件对参数进行动态空间的搜索。

## 命令格式<a name="section1019897115110"></a>

**atune-adm tuning**  <PROJECT\_YAML\>

## 参数说明<a name="section16755152320311"></a>

PROJECT\_YAML 用户配置的用于动态参数搜索的yaml配置文件的路径。

**Yaml文件配置说明：**

<a name="zh-cn_topic_0210923703_table986567202610"></a>
<table><tbody><tr id="zh-cn_topic_0210923703_row12230533412"><td class="cellrowborder" valign="top" width="16.84%"><p id="zh-cn_topic_0210923703_p1922315520345"><a name="zh-cn_topic_0210923703_p1922315520345"></a><a name="zh-cn_topic_0210923703_p1922315520345"></a><strong id="zh-cn_topic_0210923703_b089417291387"><a name="zh-cn_topic_0210923703_b089417291387"></a><a name="zh-cn_topic_0210923703_b089417291387"></a>配置名称</strong></p>
</td>
<td class="cellrowborder" valign="top" width="19.97%"><p id="zh-cn_topic_0210923703_p2085616201345"><a name="zh-cn_topic_0210923703_p2085616201345"></a><a name="zh-cn_topic_0210923703_p2085616201345"></a><strong id="zh-cn_topic_0210923703_b99087294385"><a name="zh-cn_topic_0210923703_b99087294385"></a><a name="zh-cn_topic_0210923703_b99087294385"></a>配置说明</strong></p>
</td>
<td class="cellrowborder" valign="top" width="15.72%"><p id="zh-cn_topic_0210923703_p322320510341"><a name="zh-cn_topic_0210923703_p322320510341"></a><a name="zh-cn_topic_0210923703_p322320510341"></a><strong id="zh-cn_topic_0210923703_b990832915386"><a name="zh-cn_topic_0210923703_b990832915386"></a><a name="zh-cn_topic_0210923703_b990832915386"></a>参数类型</strong></p>
</td>
<td class="cellrowborder" valign="top" width="47.47%"><p id="zh-cn_topic_0210923703_p175251446113417"><a name="zh-cn_topic_0210923703_p175251446113417"></a><a name="zh-cn_topic_0210923703_p175251446113417"></a><strong id="zh-cn_topic_0210923703_b690902916384"><a name="zh-cn_topic_0210923703_b690902916384"></a><a name="zh-cn_topic_0210923703_b690902916384"></a>取值范围</strong></p>
</td>
</tr>
<tr id="zh-cn_topic_0210923703_row29621373265"><td class="cellrowborder" valign="top" width="16.84%"><p id="zh-cn_topic_0210923703_p1996216772611"><a name="zh-cn_topic_0210923703_p1996216772611"></a><a name="zh-cn_topic_0210923703_p1996216772611"></a>object</p>
</td>
<td class="cellrowborder" valign="top" width="19.97%"><p id="zh-cn_topic_0210923703_p19962379263"><a name="zh-cn_topic_0210923703_p19962379263"></a><a name="zh-cn_topic_0210923703_p19962379263"></a>需要调节的参数项及信息</p>
</td>
<td class="cellrowborder" valign="top" width="15.72%"><p id="zh-cn_topic_0210923703_p14608154717320"><a name="zh-cn_topic_0210923703_p14608154717320"></a><a name="zh-cn_topic_0210923703_p14608154717320"></a>-</p>
</td>
<td class="cellrowborder" valign="top" width="47.47%"><p id="zh-cn_topic_0210923703_p1252516467348"><a name="zh-cn_topic_0210923703_p1252516467348"></a><a name="zh-cn_topic_0210923703_p1252516467348"></a>-</p>
</td>
</tr>
<tr id="zh-cn_topic_0210923703_row1962777265"><td class="cellrowborder" valign="top" width="16.84%"><p id="zh-cn_topic_0210923703_p109622772615"><a name="zh-cn_topic_0210923703_p109622772615"></a><a name="zh-cn_topic_0210923703_p109622772615"></a>startworkload</p>
</td>
<td class="cellrowborder" valign="top" width="19.97%"><p id="zh-cn_topic_0210923703_p19962117162614"><a name="zh-cn_topic_0210923703_p19962117162614"></a><a name="zh-cn_topic_0210923703_p19962117162614"></a>待调服务的启动脚本</p>
</td>
<td class="cellrowborder" valign="top" width="15.72%"><p id="zh-cn_topic_0210923703_p15608124710329"><a name="zh-cn_topic_0210923703_p15608124710329"></a><a name="zh-cn_topic_0210923703_p15608124710329"></a>-</p>
</td>
<td class="cellrowborder" valign="top" width="47.47%"><p id="zh-cn_topic_0210923703_p752524613346"><a name="zh-cn_topic_0210923703_p752524613346"></a><a name="zh-cn_topic_0210923703_p752524613346"></a>-</p>
</td>
</tr>
<tr id="zh-cn_topic_0210923703_row139624782615"><td class="cellrowborder" valign="top" width="16.84%"><p id="zh-cn_topic_0210923703_p169628714260"><a name="zh-cn_topic_0210923703_p169628714260"></a><a name="zh-cn_topic_0210923703_p169628714260"></a>stopworkload</p>
</td>
<td class="cellrowborder" valign="top" width="19.97%"><p id="zh-cn_topic_0210923703_p99629742615"><a name="zh-cn_topic_0210923703_p99629742615"></a><a name="zh-cn_topic_0210923703_p99629742615"></a>待调服务的停止脚本</p>
</td>
<td class="cellrowborder" valign="top" width="15.72%"><p id="zh-cn_topic_0210923703_p86087477325"><a name="zh-cn_topic_0210923703_p86087477325"></a><a name="zh-cn_topic_0210923703_p86087477325"></a>-</p>
</td>
<td class="cellrowborder" valign="top" width="47.47%"><p id="zh-cn_topic_0210923703_p6525164610342"><a name="zh-cn_topic_0210923703_p6525164610342"></a><a name="zh-cn_topic_0210923703_p6525164610342"></a>-</p>
</td>
</tr>
<tr id="zh-cn_topic_0210923703_row296212752612"><td class="cellrowborder" valign="top" width="16.84%"><p id="zh-cn_topic_0210923703_p1596247102612"><a name="zh-cn_topic_0210923703_p1596247102612"></a><a name="zh-cn_topic_0210923703_p1596247102612"></a>iterations</p>
</td>
<td class="cellrowborder" valign="top" width="19.97%"><p id="zh-cn_topic_0210923703_p129621679265"><a name="zh-cn_topic_0210923703_p129621679265"></a><a name="zh-cn_topic_0210923703_p129621679265"></a>调优迭代次数</p>
</td>
<td class="cellrowborder" valign="top" width="15.72%"><p id="zh-cn_topic_0210923703_p19608164717325"><a name="zh-cn_topic_0210923703_p19608164717325"></a><a name="zh-cn_topic_0210923703_p19608164717325"></a>整型</p>
</td>
<td class="cellrowborder" valign="top" width="47.47%"><p id="zh-cn_topic_0210923703_p185251546143418"><a name="zh-cn_topic_0210923703_p185251546143418"></a><a name="zh-cn_topic_0210923703_p185251546143418"></a>&gt;=10</p>
</td>
</tr>
<tr id="zh-cn_topic_0210923703_row10962187122616"><td class="cellrowborder" valign="top" width="16.84%"><p id="zh-cn_topic_0210923703_p99621717264"><a name="zh-cn_topic_0210923703_p99621717264"></a><a name="zh-cn_topic_0210923703_p99621717264"></a>benchmark</p>
</td>
<td class="cellrowborder" valign="top" width="19.97%"><p id="zh-cn_topic_0210923703_p7962175269"><a name="zh-cn_topic_0210923703_p7962175269"></a><a name="zh-cn_topic_0210923703_p7962175269"></a>性能测试脚本</p>
</td>
<td class="cellrowborder" valign="top" width="15.72%"><p id="zh-cn_topic_0210923703_p10608184743220"><a name="zh-cn_topic_0210923703_p10608184743220"></a><a name="zh-cn_topic_0210923703_p10608184743220"></a>-</p>
</td>
<td class="cellrowborder" valign="top" width="47.47%"><p id="zh-cn_topic_0210923703_p552584603414"><a name="zh-cn_topic_0210923703_p552584603414"></a><a name="zh-cn_topic_0210923703_p552584603414"></a>-</p>
</td>
</tr>
<tr id="zh-cn_topic_0210923703_row119621676268"><td class="cellrowborder" valign="top" width="16.84%"><p id="zh-cn_topic_0210923703_p1896277112611"><a name="zh-cn_topic_0210923703_p1896277112611"></a><a name="zh-cn_topic_0210923703_p1896277112611"></a>evaluations</p>
</td>
<td class="cellrowborder" valign="top" width="19.97%"><p id="zh-cn_topic_0210923703_p179621871266"><a name="zh-cn_topic_0210923703_p179621871266"></a><a name="zh-cn_topic_0210923703_p179621871266"></a>性能测试评估指标</p>
</td>
<td class="cellrowborder" valign="top" width="15.72%"><p id="zh-cn_topic_0210923703_p26081547103218"><a name="zh-cn_topic_0210923703_p26081547103218"></a><a name="zh-cn_topic_0210923703_p26081547103218"></a>-</p>
</td>
<td class="cellrowborder" valign="top" width="47.47%"><p id="zh-cn_topic_0210923703_p18525846163413"><a name="zh-cn_topic_0210923703_p18525846163413"></a><a name="zh-cn_topic_0210923703_p18525846163413"></a>-</p>
</td>
</tr>
</tbody>
</table>

1）object项配置说明

<a name="zh-cn_topic_0210923703_table98739710266"></a>
<table><tbody><tr id="zh-cn_topic_0210923703_row2050178383"><td class="cellrowborder" valign="top" width="16.98%"><p id="zh-cn_topic_0210923703_p724413413819"><a name="zh-cn_topic_0210923703_p724413413819"></a><a name="zh-cn_topic_0210923703_p724413413819"></a><strong id="zh-cn_topic_0210923703_b52441134183819"><a name="zh-cn_topic_0210923703_b52441134183819"></a><a name="zh-cn_topic_0210923703_b52441134183819"></a>配置名称</strong></p>
</td>
<td class="cellrowborder" valign="top" width="20.18%"><p id="zh-cn_topic_0210923703_p824413419385"><a name="zh-cn_topic_0210923703_p824413419385"></a><a name="zh-cn_topic_0210923703_p824413419385"></a><strong id="zh-cn_topic_0210923703_b1424463413817"><a name="zh-cn_topic_0210923703_b1424463413817"></a><a name="zh-cn_topic_0210923703_b1424463413817"></a>配置说明</strong></p>
</td>
<td class="cellrowborder" valign="top" width="15.47%"><p id="zh-cn_topic_0210923703_p024483419389"><a name="zh-cn_topic_0210923703_p024483419389"></a><a name="zh-cn_topic_0210923703_p024483419389"></a><strong id="zh-cn_topic_0210923703_b1024463443811"><a name="zh-cn_topic_0210923703_b1024463443811"></a><a name="zh-cn_topic_0210923703_b1024463443811"></a>参数类型</strong></p>
</td>
<td class="cellrowborder" valign="top" width="47.370000000000005%"><p id="zh-cn_topic_0210923703_p102441234113810"><a name="zh-cn_topic_0210923703_p102441234113810"></a><a name="zh-cn_topic_0210923703_p102441234113810"></a><strong id="zh-cn_topic_0210923703_b182441934113818"><a name="zh-cn_topic_0210923703_b182441934113818"></a><a name="zh-cn_topic_0210923703_b182441934113818"></a>取值范围</strong></p>
</td>
</tr>
<tr id="zh-cn_topic_0210923703_row1596297112617"><td class="cellrowborder" valign="top" width="16.98%"><p id="zh-cn_topic_0210923703_p12962274268"><a name="zh-cn_topic_0210923703_p12962274268"></a><a name="zh-cn_topic_0210923703_p12962274268"></a>name</p>
</td>
<td class="cellrowborder" valign="top" width="20.18%"><p id="zh-cn_topic_0210923703_p4962187132616"><a name="zh-cn_topic_0210923703_p4962187132616"></a><a name="zh-cn_topic_0210923703_p4962187132616"></a>待调参数名称</p>
</td>
<td class="cellrowborder" valign="top" width="15.47%"><p id="zh-cn_topic_0210923703_p163811150173711"><a name="zh-cn_topic_0210923703_p163811150173711"></a><a name="zh-cn_topic_0210923703_p163811150173711"></a>字符串</p>
</td>
<td class="cellrowborder" valign="top" width="47.370000000000005%"><p id="zh-cn_topic_0210923703_p1873545493715"><a name="zh-cn_topic_0210923703_p1873545493715"></a><a name="zh-cn_topic_0210923703_p1873545493715"></a>-</p>
</td>
</tr>
<tr id="zh-cn_topic_0210923703_row39621676262"><td class="cellrowborder" valign="top" width="16.98%"><p id="zh-cn_topic_0210923703_p296212711262"><a name="zh-cn_topic_0210923703_p296212711262"></a><a name="zh-cn_topic_0210923703_p296212711262"></a>desc</p>
</td>
<td class="cellrowborder" valign="top" width="20.18%"><p id="zh-cn_topic_0210923703_p296216710269"><a name="zh-cn_topic_0210923703_p296216710269"></a><a name="zh-cn_topic_0210923703_p296216710269"></a>待调参数描述</p>
</td>
<td class="cellrowborder" valign="top" width="15.47%"><p id="zh-cn_topic_0210923703_p938195011376"><a name="zh-cn_topic_0210923703_p938195011376"></a><a name="zh-cn_topic_0210923703_p938195011376"></a>字符串</p>
</td>
<td class="cellrowborder" valign="top" width="47.370000000000005%"><p id="zh-cn_topic_0210923703_p47356546379"><a name="zh-cn_topic_0210923703_p47356546379"></a><a name="zh-cn_topic_0210923703_p47356546379"></a>-</p>
</td>
</tr>
<tr id="zh-cn_topic_0210923703_row18962575268"><td class="cellrowborder" valign="top" width="16.98%"><p id="zh-cn_topic_0210923703_p1896210782615"><a name="zh-cn_topic_0210923703_p1896210782615"></a><a name="zh-cn_topic_0210923703_p1896210782615"></a>get</p>
</td>
<td class="cellrowborder" valign="top" width="20.18%"><p id="zh-cn_topic_0210923703_p129621475264"><a name="zh-cn_topic_0210923703_p129621475264"></a><a name="zh-cn_topic_0210923703_p129621475264"></a>查询参数值的脚本</p>
</td>
<td class="cellrowborder" valign="top" width="15.47%"><p id="zh-cn_topic_0210923703_p238118508375"><a name="zh-cn_topic_0210923703_p238118508375"></a><a name="zh-cn_topic_0210923703_p238118508375"></a>-</p>
</td>
<td class="cellrowborder" valign="top" width="47.370000000000005%"><p id="zh-cn_topic_0210923703_p1773515473720"><a name="zh-cn_topic_0210923703_p1773515473720"></a><a name="zh-cn_topic_0210923703_p1773515473720"></a>-</p>
</td>
</tr>
<tr id="zh-cn_topic_0210923703_row199621079261"><td class="cellrowborder" valign="top" width="16.98%"><p id="zh-cn_topic_0210923703_p1996214742618"><a name="zh-cn_topic_0210923703_p1996214742618"></a><a name="zh-cn_topic_0210923703_p1996214742618"></a>set</p>
</td>
<td class="cellrowborder" valign="top" width="20.18%"><p id="zh-cn_topic_0210923703_p89625716260"><a name="zh-cn_topic_0210923703_p89625716260"></a><a name="zh-cn_topic_0210923703_p89625716260"></a>设置参数值的脚本</p>
</td>
<td class="cellrowborder" valign="top" width="15.47%"><p id="zh-cn_topic_0210923703_p6381105017374"><a name="zh-cn_topic_0210923703_p6381105017374"></a><a name="zh-cn_topic_0210923703_p6381105017374"></a>-</p>
</td>
<td class="cellrowborder" valign="top" width="47.370000000000005%"><p id="zh-cn_topic_0210923703_p1273512541375"><a name="zh-cn_topic_0210923703_p1273512541375"></a><a name="zh-cn_topic_0210923703_p1273512541375"></a>-</p>
</td>
</tr>
<tr id="zh-cn_topic_0210923703_row15962874265"><td class="cellrowborder" valign="top" width="16.98%"><p id="zh-cn_topic_0210923703_p996217711262"><a name="zh-cn_topic_0210923703_p996217711262"></a><a name="zh-cn_topic_0210923703_p996217711262"></a>needrestart</p>
</td>
<td class="cellrowborder" valign="top" width="20.18%"><p id="zh-cn_topic_0210923703_p159621715268"><a name="zh-cn_topic_0210923703_p159621715268"></a><a name="zh-cn_topic_0210923703_p159621715268"></a>参数生效是否需要重启业务</p>
</td>
<td class="cellrowborder" valign="top" width="15.47%"><p id="zh-cn_topic_0210923703_p11381165015371"><a name="zh-cn_topic_0210923703_p11381165015371"></a><a name="zh-cn_topic_0210923703_p11381165015371"></a>枚举</p>
</td>
<td class="cellrowborder" valign="top" width="47.370000000000005%"><p id="zh-cn_topic_0210923703_p6735125415375"><a name="zh-cn_topic_0210923703_p6735125415375"></a><a name="zh-cn_topic_0210923703_p6735125415375"></a>"true", "false"</p>
</td>
</tr>
<tr id="zh-cn_topic_0210923703_row39623714265"><td class="cellrowborder" valign="top" width="16.98%"><p id="zh-cn_topic_0210923703_p99621272261"><a name="zh-cn_topic_0210923703_p99621272261"></a><a name="zh-cn_topic_0210923703_p99621272261"></a>type</p>
</td>
<td class="cellrowborder" valign="top" width="20.18%"><p id="zh-cn_topic_0210923703_p396213732618"><a name="zh-cn_topic_0210923703_p396213732618"></a><a name="zh-cn_topic_0210923703_p396213732618"></a>参数的类型，目前支持discrete, continuous两种类型，对应离散型、连续型参数</p>
</td>
<td class="cellrowborder" valign="top" width="15.47%"><p id="zh-cn_topic_0210923703_p5381105014377"><a name="zh-cn_topic_0210923703_p5381105014377"></a><a name="zh-cn_topic_0210923703_p5381105014377"></a>枚举</p>
</td>
<td class="cellrowborder" valign="top" width="47.370000000000005%"><p id="zh-cn_topic_0210923703_p27351254143719"><a name="zh-cn_topic_0210923703_p27351254143719"></a><a name="zh-cn_topic_0210923703_p27351254143719"></a>"discrete", "continuous"</p>
</td>
</tr>
<tr id="zh-cn_topic_0210923703_row1822292018454"><td class="cellrowborder" valign="top" width="16.98%"><p id="zh-cn_topic_0210923703_p17222920164519"><a name="zh-cn_topic_0210923703_p17222920164519"></a><a name="zh-cn_topic_0210923703_p17222920164519"></a>dtype</p>
</td>
<td class="cellrowborder" valign="top" width="20.18%"><p id="zh-cn_topic_0210923703_p19222192014510"><a name="zh-cn_topic_0210923703_p19222192014510"></a><a name="zh-cn_topic_0210923703_p19222192014510"></a>type为discrete类型时的参数值类型，目前支持int和string两种</p>
</td>
<td class="cellrowborder" valign="top" width="15.47%"><p id="zh-cn_topic_0210923703_p13780291862"><a name="zh-cn_topic_0210923703_p13780291862"></a><a name="zh-cn_topic_0210923703_p13780291862"></a>枚举</p>
</td>
<td class="cellrowborder" valign="top" width="47.370000000000005%"><p id="zh-cn_topic_0210923703_p22221620184517"><a name="zh-cn_topic_0210923703_p22221620184517"></a><a name="zh-cn_topic_0210923703_p22221620184517"></a>int, string</p>
</td>
</tr>
<tr id="zh-cn_topic_0210923703_row032681314219"><td class="cellrowborder" valign="top" width="16.98%"><p id="zh-cn_topic_0210923703_p10326313194214"><a name="zh-cn_topic_0210923703_p10326313194214"></a><a name="zh-cn_topic_0210923703_p10326313194214"></a>scope</p>
</td>
<td class="cellrowborder" valign="top" width="20.18%"><p id="zh-cn_topic_0210923703_p203263132426"><a name="zh-cn_topic_0210923703_p203263132426"></a><a name="zh-cn_topic_0210923703_p203263132426"></a>参数设置范围，dtype为int时使用</p>
</td>
<td class="cellrowborder" valign="top" width="15.47%"><p id="zh-cn_topic_0210923703_p53261136426"><a name="zh-cn_topic_0210923703_p53261136426"></a><a name="zh-cn_topic_0210923703_p53261136426"></a>整型</p>
</td>
<td class="cellrowborder" valign="top" width="47.370000000000005%"><p id="zh-cn_topic_0210923703_p173261713184218"><a name="zh-cn_topic_0210923703_p173261713184218"></a><a name="zh-cn_topic_0210923703_p173261713184218"></a>用户自定义，取值在该参数的合法范围</p>
</td>
</tr>
<tr id="zh-cn_topic_0210923703_row20727521165917"><td class="cellrowborder" valign="top" width="16.98%"><p id="zh-cn_topic_0210923703_p872742119593"><a name="zh-cn_topic_0210923703_p872742119593"></a><a name="zh-cn_topic_0210923703_p872742119593"></a>step</p>
</td>
<td class="cellrowborder" valign="top" width="20.18%"><p id="zh-cn_topic_0210923703_p1996712111403"><a name="zh-cn_topic_0210923703_p1996712111403"></a><a name="zh-cn_topic_0210923703_p1996712111403"></a>参数值步长，dtype为int时使用</p>
</td>
<td class="cellrowborder" valign="top" width="15.47%"><p id="zh-cn_topic_0210923703_p2727721155920"><a name="zh-cn_topic_0210923703_p2727721155920"></a><a name="zh-cn_topic_0210923703_p2727721155920"></a>整型</p>
</td>
<td class="cellrowborder" valign="top" width="47.370000000000005%"><p id="zh-cn_topic_0210923703_p272782195920"><a name="zh-cn_topic_0210923703_p272782195920"></a><a name="zh-cn_topic_0210923703_p272782195920"></a>用户自定义</p>
</td>
</tr>
<tr id="zh-cn_topic_0210923703_row1775627175910"><td class="cellrowborder" valign="top" width="16.98%"><p id="zh-cn_topic_0210923703_p6775427195919"><a name="zh-cn_topic_0210923703_p6775427195919"></a><a name="zh-cn_topic_0210923703_p6775427195919"></a>items</p>
</td>
<td class="cellrowborder" valign="top" width="20.18%"><p id="zh-cn_topic_0210923703_p1577542775911"><a name="zh-cn_topic_0210923703_p1577542775911"></a><a name="zh-cn_topic_0210923703_p1577542775911"></a>参数值在选定范围之外的枚举值，dtype为int时使用</p>
</td>
<td class="cellrowborder" valign="top" width="15.47%"><p id="zh-cn_topic_0210923703_p187758270591"><a name="zh-cn_topic_0210923703_p187758270591"></a><a name="zh-cn_topic_0210923703_p187758270591"></a>整型</p>
</td>
<td class="cellrowborder" valign="top" width="47.370000000000005%"><p id="zh-cn_topic_0210923703_p9775132795916"><a name="zh-cn_topic_0210923703_p9775132795916"></a><a name="zh-cn_topic_0210923703_p9775132795916"></a>用户自定义，取值在该参数的合法范围</p>
</td>
</tr>
<tr id="zh-cn_topic_0210923703_row5454193811595"><td class="cellrowborder" valign="top" width="16.98%"><p id="zh-cn_topic_0210923703_p19454163845911"><a name="zh-cn_topic_0210923703_p19454163845911"></a><a name="zh-cn_topic_0210923703_p19454163845911"></a>options</p>
</td>
<td class="cellrowborder" valign="top" width="20.18%"><p id="zh-cn_topic_0210923703_p13455103835917"><a name="zh-cn_topic_0210923703_p13455103835917"></a><a name="zh-cn_topic_0210923703_p13455103835917"></a>参数值的枚举范围，dtype为string时使用</p>
</td>
<td class="cellrowborder" valign="top" width="15.47%"><p id="zh-cn_topic_0210923703_p9455173813593"><a name="zh-cn_topic_0210923703_p9455173813593"></a><a name="zh-cn_topic_0210923703_p9455173813593"></a>字符串</p>
</td>
<td class="cellrowborder" valign="top" width="47.370000000000005%"><p id="zh-cn_topic_0210923703_p144551338145910"><a name="zh-cn_topic_0210923703_p144551338145910"></a><a name="zh-cn_topic_0210923703_p144551338145910"></a>用户自定义，取值在该参数的合法范围</p>
</td>
</tr>
<tr id="zh-cn_topic_0210923703_row209629792616"><td class="cellrowborder" valign="top" width="16.98%"><p id="zh-cn_topic_0210923703_p1096207122612"><a name="zh-cn_topic_0210923703_p1096207122612"></a><a name="zh-cn_topic_0210923703_p1096207122612"></a>ref</p>
</td>
<td class="cellrowborder" valign="top" width="20.18%"><p id="zh-cn_topic_0210923703_p69629711266"><a name="zh-cn_topic_0210923703_p69629711266"></a><a name="zh-cn_topic_0210923703_p69629711266"></a>参数的推荐初始值</p>
</td>
<td class="cellrowborder" valign="top" width="15.47%"><p id="zh-cn_topic_0210923703_p12381150123716"><a name="zh-cn_topic_0210923703_p12381150123716"></a><a name="zh-cn_topic_0210923703_p12381150123716"></a>整型或字符串</p>
</td>
<td class="cellrowborder" valign="top" width="47.370000000000005%"><p id="zh-cn_topic_0210923703_p6735145483712"><a name="zh-cn_topic_0210923703_p6735145483712"></a><a name="zh-cn_topic_0210923703_p6735145483712"></a>用户自定义，取值在该参数的合法范围</p>
</td>
</tr>
</tbody>
</table>

2）evaluations项配置说明

<a name="zh-cn_topic_0210923703_table58847714266"></a>
<table><tbody><tr id="zh-cn_topic_0210923703_row96719161245"><td class="cellrowborder" valign="top" width="12.950000000000001%"><p id="zh-cn_topic_0210923703_p49973411241"><a name="zh-cn_topic_0210923703_p49973411241"></a><a name="zh-cn_topic_0210923703_p49973411241"></a><strong id="zh-cn_topic_0210923703_b1999714118410"><a name="zh-cn_topic_0210923703_b1999714118410"></a><a name="zh-cn_topic_0210923703_b1999714118410"></a>配置名称</strong></p>
</td>
<td class="cellrowborder" valign="top" width="24.23%"><p id="zh-cn_topic_0210923703_p119971941941"><a name="zh-cn_topic_0210923703_p119971941941"></a><a name="zh-cn_topic_0210923703_p119971941941"></a><strong id="zh-cn_topic_0210923703_b11997114111414"><a name="zh-cn_topic_0210923703_b11997114111414"></a><a name="zh-cn_topic_0210923703_b11997114111414"></a>配置说明</strong></p>
</td>
<td class="cellrowborder" valign="top" width="15.629999999999999%"><p id="zh-cn_topic_0210923703_p1899784117416"><a name="zh-cn_topic_0210923703_p1899784117416"></a><a name="zh-cn_topic_0210923703_p1899784117416"></a><strong id="zh-cn_topic_0210923703_b29983411244"><a name="zh-cn_topic_0210923703_b29983411244"></a><a name="zh-cn_topic_0210923703_b29983411244"></a>参数类型</strong></p>
</td>
<td class="cellrowborder" valign="top" width="47.19%"><p id="zh-cn_topic_0210923703_p1099814112416"><a name="zh-cn_topic_0210923703_p1099814112416"></a><a name="zh-cn_topic_0210923703_p1099814112416"></a><strong id="zh-cn_topic_0210923703_b19981411445"><a name="zh-cn_topic_0210923703_b19981411445"></a><a name="zh-cn_topic_0210923703_b19981411445"></a>取值范围</strong></p>
</td>
</tr>
<tr id="zh-cn_topic_0210923703_row159636710262"><td class="cellrowborder" valign="top" width="12.950000000000001%"><p id="zh-cn_topic_0210923703_p9963679262"><a name="zh-cn_topic_0210923703_p9963679262"></a><a name="zh-cn_topic_0210923703_p9963679262"></a>name</p>
</td>
<td class="cellrowborder" valign="top" width="24.23%"><p id="zh-cn_topic_0210923703_p10963378267"><a name="zh-cn_topic_0210923703_p10963378267"></a><a name="zh-cn_topic_0210923703_p10963378267"></a>评价指标名称</p>
</td>
<td class="cellrowborder" valign="top" width="15.629999999999999%"><p id="zh-cn_topic_0210923703_p86031433840"><a name="zh-cn_topic_0210923703_p86031433840"></a><a name="zh-cn_topic_0210923703_p86031433840"></a>字符串</p>
</td>
<td class="cellrowborder" valign="top" width="47.19%"><p id="zh-cn_topic_0210923703_p247112292045"><a name="zh-cn_topic_0210923703_p247112292045"></a><a name="zh-cn_topic_0210923703_p247112292045"></a>-</p>
</td>
</tr>
<tr id="zh-cn_topic_0210923703_row496313714269"><td class="cellrowborder" valign="top" width="12.950000000000001%"><p id="zh-cn_topic_0210923703_p696313782618"><a name="zh-cn_topic_0210923703_p696313782618"></a><a name="zh-cn_topic_0210923703_p696313782618"></a>get</p>
</td>
<td class="cellrowborder" valign="top" width="24.23%"><p id="zh-cn_topic_0210923703_p16963147102617"><a name="zh-cn_topic_0210923703_p16963147102617"></a><a name="zh-cn_topic_0210923703_p16963147102617"></a>获取性能评估结果的脚本</p>
</td>
<td class="cellrowborder" valign="top" width="15.629999999999999%"><p id="zh-cn_topic_0210923703_p360310338414"><a name="zh-cn_topic_0210923703_p360310338414"></a><a name="zh-cn_topic_0210923703_p360310338414"></a>-</p>
</td>
<td class="cellrowborder" valign="top" width="47.19%"><p id="zh-cn_topic_0210923703_p204715298417"><a name="zh-cn_topic_0210923703_p204715298417"></a><a name="zh-cn_topic_0210923703_p204715298417"></a>-</p>
</td>
</tr>
<tr id="zh-cn_topic_0210923703_row5963107142620"><td class="cellrowborder" valign="top" width="12.950000000000001%"><p id="zh-cn_topic_0210923703_p169631073264"><a name="zh-cn_topic_0210923703_p169631073264"></a><a name="zh-cn_topic_0210923703_p169631073264"></a>type</p>
</td>
<td class="cellrowborder" valign="top" width="24.23%"><p id="zh-cn_topic_0210923703_p29631478264"><a name="zh-cn_topic_0210923703_p29631478264"></a><a name="zh-cn_topic_0210923703_p29631478264"></a>评估结果的正负类型，positive代表最小化对应性能值，negative代表最大化对应性能</p>
</td>
<td class="cellrowborder" valign="top" width="15.629999999999999%"><p id="zh-cn_topic_0210923703_p76031331415"><a name="zh-cn_topic_0210923703_p76031331415"></a><a name="zh-cn_topic_0210923703_p76031331415"></a>枚举</p>
</td>
<td class="cellrowborder" valign="top" width="47.19%"><p id="zh-cn_topic_0210923703_p1647116291411"><a name="zh-cn_topic_0210923703_p1647116291411"></a><a name="zh-cn_topic_0210923703_p1647116291411"></a>"positive","negative"</p>
</td>
</tr>
<tr id="zh-cn_topic_0210923703_row59635792614"><td class="cellrowborder" valign="top" width="12.950000000000001%"><p id="zh-cn_topic_0210923703_p096320712268"><a name="zh-cn_topic_0210923703_p096320712268"></a><a name="zh-cn_topic_0210923703_p096320712268"></a>weight</p>
</td>
<td class="cellrowborder" valign="top" width="24.23%"><p id="zh-cn_topic_0210923703_p2096347192620"><a name="zh-cn_topic_0210923703_p2096347192620"></a><a name="zh-cn_topic_0210923703_p2096347192620"></a>该指标的权重百分比，0-100</p>
</td>
<td class="cellrowborder" valign="top" width="15.629999999999999%"><p id="zh-cn_topic_0210923703_p1666738163"><a name="zh-cn_topic_0210923703_p1666738163"></a><a name="zh-cn_topic_0210923703_p1666738163"></a>整型</p>
</td>
<td class="cellrowborder" valign="top" width="47.19%"><p id="zh-cn_topic_0210923703_p154712292047"><a name="zh-cn_topic_0210923703_p154712292047"></a><a name="zh-cn_topic_0210923703_p154712292047"></a>0-100</p>
</td>
</tr>
<tr id="zh-cn_topic_0210923703_row17963117152615"><td class="cellrowborder" valign="top" width="12.950000000000001%"><p id="zh-cn_topic_0210923703_p6963677267"><a name="zh-cn_topic_0210923703_p6963677267"></a><a name="zh-cn_topic_0210923703_p6963677267"></a>threshold</p>
</td>
<td class="cellrowborder" valign="top" width="24.23%"><p id="zh-cn_topic_0210923703_p19632712261"><a name="zh-cn_topic_0210923703_p19632712261"></a><a name="zh-cn_topic_0210923703_p19632712261"></a>该指标的最低性能要求</p>
</td>
<td class="cellrowborder" valign="top" width="15.629999999999999%"><p id="zh-cn_topic_0210923703_p36031331245"><a name="zh-cn_topic_0210923703_p36031331245"></a><a name="zh-cn_topic_0210923703_p36031331245"></a>整型</p>
</td>
<td class="cellrowborder" valign="top" width="47.19%"><p id="zh-cn_topic_0210923703_p447132914413"><a name="zh-cn_topic_0210923703_p447132914413"></a><a name="zh-cn_topic_0210923703_p447132914413"></a>用户指定</p>
</td>
</tr>
</tbody>
</table>

## 使用示例<a name="section5961238145111"></a>

```
$ atune-adm tuning example.yaml
```

