# analysis<a name="ZH-CN_TOPIC_0213225932"></a>

## 功能描述<a name="section124121426195015"></a>

采集系统的实时统计数据进行负载类型识别，并进行自动优化。

## 命令格式<a name="section1019897115110"></a>

**atune-adm analysis**  \[OPTIONS\]

## 参数说明<a name="section16755152320311"></a>

-   OPTIONS

<a name="table531317574132"></a>
<table><tbody><tr id="row1031310575137"><td class="cellrowborder" valign="top" width="23.87%"><p id="p6313115718133"><a name="p6313115718133"></a><a name="p6313115718133"></a>参数</p>
</td>
<td class="cellrowborder" valign="top" width="76.13%"><p id="p16313157141312"><a name="p16313157141312"></a><a name="p16313157141312"></a>描述</p>
</td>
</tr>
<tr id="row7313105711139"><td class="cellrowborder" valign="top" width="23.87%"><p id="p203141657131315"><a name="p203141657131315"></a><a name="p203141657131315"></a>--model, -m</p>
</td>
<td class="cellrowborder" valign="top" width="76.13%"><p id="p13141157151316"><a name="p13141157151316"></a><a name="p13141157151316"></a>用户自训练产生的新模型</p>
</td>
</tr>
</tbody>
</table>

## 使用示例<a name="section5961238145111"></a>

-   使用默认的模型进行分类识别

    ```
    $ atune-adm analysis
    ```

-   使用自训练的模型进行识别

    ```
    $ atune-adm analysis --model ./model/new-model.m
    ```


