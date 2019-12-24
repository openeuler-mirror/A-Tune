# train<a name="ZH-CN_TOPIC_0213225909"></a>

## 功能描述<a name="section124121426195015"></a>

使用采集的数据进行模型的训练。训练时至少采集两种业务类型的数据，否则训练出错。

## 命令格式<a name="section1019897115110"></a>

**atune-adm train**  <OPTIONS\>

## 参数说明<a name="section4591487175"></a>

-   OPTIONS

    <a name="zh-cn_topic_0210923699_table847613161310"></a>
    <table><tbody><tr id="zh-cn_topic_0210923699_row349814169120"><td class="cellrowborder" valign="top" width="23.87%"><p id="zh-cn_topic_0210923699_p1549841614116"><a name="zh-cn_topic_0210923699_p1549841614116"></a><a name="zh-cn_topic_0210923699_p1549841614116"></a>参数</p>
    </td>
    <td class="cellrowborder" valign="top" width="76.13%"><p id="zh-cn_topic_0210923699_p84988168119"><a name="zh-cn_topic_0210923699_p84988168119"></a><a name="zh-cn_topic_0210923699_p84988168119"></a>描述</p>
    </td>
    </tr>
    <tr id="zh-cn_topic_0210923699_row13499181612118"><td class="cellrowborder" valign="top" width="23.87%"><p id="zh-cn_topic_0210923699_p24993163119"><a name="zh-cn_topic_0210923699_p24993163119"></a><a name="zh-cn_topic_0210923699_p24993163119"></a>--data_path, -d</p>
    </td>
    <td class="cellrowborder" valign="top" width="76.13%"><p id="zh-cn_topic_0210923699_p134991316818"><a name="zh-cn_topic_0210923699_p134991316818"></a><a name="zh-cn_topic_0210923699_p134991316818"></a>用于存放模型训练的csv文件的目录</p>
    </td>
    </tr>
    <tr id="zh-cn_topic_0210923699_row149914161115"><td class="cellrowborder" valign="top" width="23.87%"><p id="zh-cn_topic_0210923699_p14991516914"><a name="zh-cn_topic_0210923699_p14991516914"></a><a name="zh-cn_topic_0210923699_p14991516914"></a>--output_file, -o</p>
    </td>
    <td class="cellrowborder" valign="top" width="76.13%"><p id="zh-cn_topic_0210923699_p049916166114"><a name="zh-cn_topic_0210923699_p049916166114"></a><a name="zh-cn_topic_0210923699_p049916166114"></a>产生的新的训练模型</p>
    </td>
    </tr>
    </tbody>
    </table>


## 使用示例<a name="section5961238145111"></a>

```
$ atune-adm train --data_path ./data –output_file ./model/new-model.m 
```

