# collection<a name="ZH-CN_TOPIC_0213225908"></a>

## 功能描述<a name="section124121426195015"></a>

采集业务运行时系统的全局资源使用情况以及OS的各项状态信息，并将收集的结果保存到csv格式的输出文件中，作为模型训练的输入数据集。

>![](public_sys-resources/icon-note.gif) **说明：**   
>本命令依赖采样工具perf，mpstat，vmstat，iostat，sar。CPU型号目前仅支持鲲鹏920，可通过dmidecode -t processor检查CPU型号。  

## 命令格式<a name="section1019897115110"></a>

**atune-adm collection**  <OPTIONS\>

## 参数说明<a name="section143803239510"></a>

-   OPTIONS

    <a name="zh-cn_topic_0210923698_table960915119119"></a>
    <table><thead align="left"><tr id="zh-cn_topic_0210923698_row13645013114"><th class="cellrowborder" valign="top" width="23.87%" id="mcps1.1.3.1.1"><p id="zh-cn_topic_0210923698_p176451311914"><a name="zh-cn_topic_0210923698_p176451311914"></a><a name="zh-cn_topic_0210923698_p176451311914"></a>参数</p>
    </th>
    <th class="cellrowborder" valign="top" width="76.13%" id="mcps1.1.3.1.2"><p id="zh-cn_topic_0210923698_p1364511211"><a name="zh-cn_topic_0210923698_p1364511211"></a><a name="zh-cn_topic_0210923698_p1364511211"></a>描述</p>
    </th>
    </tr>
    </thead>
    <tbody><tr id="zh-cn_topic_0210923698_row19645141112"><td class="cellrowborder" valign="top" width="23.87%" headers="mcps1.1.3.1.1 "><p id="zh-cn_topic_0210923698_p2645611710"><a name="zh-cn_topic_0210923698_p2645611710"></a><a name="zh-cn_topic_0210923698_p2645611710"></a>--filename, -f</p>
    </td>
    <td class="cellrowborder" valign="top" width="76.13%" headers="mcps1.1.3.1.2 "><p id="zh-cn_topic_0210923698_p10645512017"><a name="zh-cn_topic_0210923698_p10645512017"></a><a name="zh-cn_topic_0210923698_p10645512017"></a>生成的用于训练的csv文件名：name-时间戳.csv</p>
    </td>
    </tr>
    <tr id="zh-cn_topic_0210923698_row564581117"><td class="cellrowborder" valign="top" width="23.87%" headers="mcps1.1.3.1.1 "><p id="zh-cn_topic_0210923698_p15645911616"><a name="zh-cn_topic_0210923698_p15645911616"></a><a name="zh-cn_topic_0210923698_p15645911616"></a>--output_path, -o</p>
    </td>
    <td class="cellrowborder" valign="top" width="76.13%" headers="mcps1.1.3.1.2 "><p id="zh-cn_topic_0210923698_p106451918120"><a name="zh-cn_topic_0210923698_p106451918120"></a><a name="zh-cn_topic_0210923698_p106451918120"></a>生成的csv文件的存放路径</p>
    </td>
    </tr>
    <tr id="zh-cn_topic_0210923698_row8645711115"><td class="cellrowborder" valign="top" width="23.87%" headers="mcps1.1.3.1.1 "><p id="zh-cn_topic_0210923698_p14645713117"><a name="zh-cn_topic_0210923698_p14645713117"></a><a name="zh-cn_topic_0210923698_p14645713117"></a>--disk, -b</p>
    </td>
    <td class="cellrowborder" valign="top" width="76.13%" headers="mcps1.1.3.1.2 "><p id="zh-cn_topic_0210923698_p464519116110"><a name="zh-cn_topic_0210923698_p464519116110"></a><a name="zh-cn_topic_0210923698_p464519116110"></a>业务运行时实际使用的磁盘，如/dev/sda</p>
    </td>
    </tr>
    <tr id="zh-cn_topic_0210923698_row6645111714"><td class="cellrowborder" valign="top" width="23.87%" headers="mcps1.1.3.1.1 "><p id="zh-cn_topic_0210923698_p106451817111"><a name="zh-cn_topic_0210923698_p106451817111"></a><a name="zh-cn_topic_0210923698_p106451817111"></a>--network, -n</p>
    </td>
    <td class="cellrowborder" valign="top" width="76.13%" headers="mcps1.1.3.1.2 "><p id="zh-cn_topic_0210923698_p206451911611"><a name="zh-cn_topic_0210923698_p206451911611"></a><a name="zh-cn_topic_0210923698_p206451911611"></a>业务运行时使用的网络接口，如eth0</p>
    </td>
    </tr>
    <tr id="zh-cn_topic_0210923698_row14645219112"><td class="cellrowborder" valign="top" width="23.87%" headers="mcps1.1.3.1.1 "><p id="zh-cn_topic_0210923698_p9645191811"><a name="zh-cn_topic_0210923698_p9645191811"></a><a name="zh-cn_topic_0210923698_p9645191811"></a>--workload_type, -t</p>
    </td>
    <td class="cellrowborder" valign="top" width="76.13%" headers="mcps1.1.3.1.2 "><p id="zh-cn_topic_0210923698_p16450117114"><a name="zh-cn_topic_0210923698_p16450117114"></a><a name="zh-cn_topic_0210923698_p16450117114"></a>标记业务的负载类型，作为后续训练的标签</p>
    </td>
    </tr>
    <tr id="zh-cn_topic_0210923698_row76452118115"><td class="cellrowborder" valign="top" width="23.87%" headers="mcps1.1.3.1.1 "><p id="zh-cn_topic_0210923698_p96451114116"><a name="zh-cn_topic_0210923698_p96451114116"></a><a name="zh-cn_topic_0210923698_p96451114116"></a>--duration, -d</p>
    </td>
    <td class="cellrowborder" valign="top" width="76.13%" headers="mcps1.1.3.1.2 "><p id="p3205204519273"><a name="p3205204519273"></a><a name="p3205204519273"></a>业务运行时采集数据的时间</p>
    </td>
    </tr>
    </tbody>
    </table>


## 使用示例<a name="section5961238145111"></a>

```
$ atune-adm collection --filename name --interval 5 --duration 1200 --output_path ./data –-disk sda --network eth0 --workload_type test_type 
```

