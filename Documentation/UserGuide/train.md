# train<a name="ZH-CN_TOPIC_0213225909"></a>

## 功能描述<a name="section124121426195015"></a>

使用采集的数据进行模型的训练。训练时至少采集两种workload\_type的数据，否则会报错。

## 命令格式<a name="section1019897115110"></a>

**atune-adm train**  <OPTIONS\>

## 参数说明<a name="section4591487175"></a>

-   OPTIONS

    <a name="zh-cn_topic_0210923699_table847613161310"></a>
    <table><thead align="left"><tr id="zh-cn_topic_0210923699_row349814169120"><th class="cellrowborder" valign="top" width="23.87%" id="mcps1.1.3.1.1"><p id="zh-cn_topic_0210923699_p1549841614116"><a name="zh-cn_topic_0210923699_p1549841614116"></a><a name="zh-cn_topic_0210923699_p1549841614116"></a>参数</p>
    </th>
    <th class="cellrowborder" valign="top" width="76.13%" id="mcps1.1.3.1.2"><p id="zh-cn_topic_0210923699_p84988168119"><a name="zh-cn_topic_0210923699_p84988168119"></a><a name="zh-cn_topic_0210923699_p84988168119"></a>描述</p>
    </th>
    </tr>
    </thead>
    <tbody><tr id="zh-cn_topic_0210923699_row13499181612118"><td class="cellrowborder" valign="top" width="23.87%" headers="mcps1.1.3.1.1 "><p id="zh-cn_topic_0210923699_p24993163119"><a name="zh-cn_topic_0210923699_p24993163119"></a><a name="zh-cn_topic_0210923699_p24993163119"></a>--data_path, -d</p>
    </td>
    <td class="cellrowborder" valign="top" width="76.13%" headers="mcps1.1.3.1.2 "><p id="zh-cn_topic_0210923699_p134991316818"><a name="zh-cn_topic_0210923699_p134991316818"></a><a name="zh-cn_topic_0210923699_p134991316818"></a>存放模型训练所需的csv文件的目录</p>
    </td>
    </tr>
    <tr id="zh-cn_topic_0210923699_row149914161115"><td class="cellrowborder" valign="top" width="23.87%" headers="mcps1.1.3.1.1 "><p id="zh-cn_topic_0210923699_p14991516914"><a name="zh-cn_topic_0210923699_p14991516914"></a><a name="zh-cn_topic_0210923699_p14991516914"></a>--output_file, -o</p>
    </td>
    <td class="cellrowborder" valign="top" width="76.13%" headers="mcps1.1.3.1.2 "><p id="zh-cn_topic_0210923699_p049916166114"><a name="zh-cn_topic_0210923699_p049916166114"></a><a name="zh-cn_topic_0210923699_p049916166114"></a>训练生成的新模型</p>
    </td>
    </tr>
    </tbody>
    </table>


## 使用示例<a name="section5961238145111"></a>

使用data目录下的csv文件作为训练输入，生成的新模型new-model.m存放在model目录下。

```
$ atune-adm train --data_path ./data –output_file ./model/new-model.m 
```

