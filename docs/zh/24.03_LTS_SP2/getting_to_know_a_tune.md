# 认识A-Tune

## 简介

操作系统作为衔接应用和硬件的基础软件，如何调整系统和应用配置，充分发挥软硬件能力，从而使业务性能达到最优，对用户至关重要。然而，运行在操作系统上的业务类型成百上千，应用形态千差万别，对资源的要求各不相同。当前硬件和基础软件组成的应用环境涉及高达7000多个配置对象，随着业务复杂度和调优对象的增加，调优所需的时间成本呈指数级增长，导致调优效率急剧下降，调优成为了一项极其复杂的工程，给用户带来巨大挑战。

其次，操作系统作为基础设施软件，提供了大量的软硬件管理能力，每种能力适用场景不尽相同，并非对所有的应用场景都通用有益，因此，不同的场景需要开启或关闭不同的能力，组合使用系统提供的各种能力，才能发挥应用程序的最佳性能。

另外，实际业务场景成千上万，计算、网络、存储等硬件配置也层出不穷，实验室无法遍历穷举所有的应用和业务场景，以及不同的硬件组合。

为了应对上述挑战，openEuler推出了A-Tune。

A-Tune是一款基于AI开发的系统性能优化引擎，它利用人工智能技术，对业务场景建立精准的系统画像，感知并推理出业务特征，进而做出智能决策，匹配并推荐最佳的系统参数配置组合，使业务处于最佳运行状态。

![](./figures/zh-cn_image_0227497000.png)

## 架构

A-Tune核心技术架构如下图，主要包括智能决策、系统画像和交互系统三层。

- 智能决策层：包含感知和决策两个子系统，分别完成对应用的智能感知和对系统的调优决策。
- 系统画像层：主要包括自动特征工程和两层分类模型，自动特征工程用于业务特征的自动选择，两层分类模型用于业务模型的学习和分类。
- 交互系统层：用于各类系统资源的监控和配置，调优策略执行在本层进行。

![](./figures/zh-cn_image_0227497343.png)

## 支持特性与业务模型

### 支持特性

A-Tune支持的主要特性、特性成熟度以及使用建议请参见[表1](#table1919220557576)。

**表 1**  特性成熟度

<a name="table1919220557576"></a>
<table><thead align="left"><tr id="row81921355135715"><th class="cellrowborder" valign="top" width="33.33333333333333%" id="mcps1.2.4.1.1"><p id="p1419275514576"><a name="p1419275514576"></a><a name="p1419275514576"></a><strong id="b175661223205512"><a name="b175661223205512"></a><a name="b175661223205512"></a>特性</strong></p>
</th>
<th class="cellrowborder" valign="top" width="33.33333333333333%" id="mcps1.2.4.1.2"><p id="p7192195520572"><a name="p7192195520572"></a><a name="p7192195520572"></a><strong id="b185678233555"><a name="b185678233555"></a><a name="b185678233555"></a>成熟度</strong></p>
</th>
<th class="cellrowborder" valign="top" width="33.33333333333333%" id="mcps1.2.4.1.3"><p id="p519205518573"><a name="p519205518573"></a><a name="p519205518573"></a><strong id="b1156872320553"><a name="b1156872320553"></a><a name="b1156872320553"></a>使用建议</strong></p>
</th>
</tr>
</thead>
<tbody><tr id="row519275518572"><td class="cellrowborder" valign="top" width="33.33333333333333%" headers="mcps1.2.4.1.1 "><p id="p1349454518111"><a name="p1349454518111"></a><a name="p1349454518111"></a>11大类15款应用负载类型自动优化</p>
</td>
<td class="cellrowborder" valign="top" width="33.33333333333333%" headers="mcps1.2.4.1.2 "><p id="p48001027191117"><a name="p48001027191117"></a><a name="p48001027191117"></a>已测试</p>
</td>
<td class="cellrowborder" valign="top" width="33.33333333333333%" headers="mcps1.2.4.1.3 "><p id="p15192195515715"><a name="p15192195515715"></a><a name="p15192195515715"></a>试用</p>
</td>
</tr>
<tr id="row919217552579"><td class="cellrowborder" valign="top" width="33.33333333333333%" headers="mcps1.2.4.1.1 "><p id="p519218559571"><a name="p519218559571"></a><a name="p519218559571"></a>自定义profile和业务模型</p>
</td>
<td class="cellrowborder" valign="top" width="33.33333333333333%" headers="mcps1.2.4.1.2 "><p id="p18192655115710"><a name="p18192655115710"></a><a name="p18192655115710"></a>已测试</p>
</td>
<td class="cellrowborder" valign="top" width="33.33333333333333%" headers="mcps1.2.4.1.3 "><p id="p71921655145717"><a name="p71921655145717"></a><a name="p71921655145717"></a>试用</p>
</td>
</tr>
<tr id="row71921155165711"><td class="cellrowborder" valign="top" width="33.33333333333333%" headers="mcps1.2.4.1.1 "><p id="p619217556575"><a name="p619217556575"></a><a name="p619217556575"></a>参数自调优</p>
</td>
<td class="cellrowborder" valign="top" width="33.33333333333333%" headers="mcps1.2.4.1.2 "><p id="p11192135595712"><a name="p11192135595712"></a><a name="p11192135595712"></a>已测试</p>
</td>
<td class="cellrowborder" valign="top" width="33.33333333333333%" headers="mcps1.2.4.1.3 "><p id="p2019235511575"><a name="p2019235511575"></a><a name="p2019235511575"></a>试用</p>
</td>
</tr>
</tbody>
</table>

### 支持业务模型

根据应用的负载特征，A-Tune将业务分为11大类，各类型的负载特征和A-Tune支持的应用请参见[表2](#table2819164611311)。

**表 2**  支持的业务类型和应用

<table class="MsoNormalTable" border="0" cellspacing="0" cellpadding="0" width="1440" style="width:1080.0pt;background:white;border-collapse:collapse">
 <thead>
  <tr>
   <td width="14%" valign="top" style="width:14.0%;border:solid #DFE2E5 1.0pt;
   padding:4.5pt 9.75pt 4.5pt 9.75pt">
   <p class="MsoNormal" align="center" style="margin-bottom:12.0pt;text-align:center;
   line-height:normal;text-autospace:ideograph-numeric ideograph-other"><b><span style="font-size:12.0pt;font-family:宋体;color:#24292E;layout-grid-mode:both">业务大类</span></b></p>
   </td>
   <td width="13%" valign="top" style="width:13.0%;border:solid #DFE2E5 1.0pt;
   border-left:none;padding:4.5pt 9.75pt 4.5pt 9.75pt">
   <p class="MsoNormal" align="center" style="margin-bottom:12.0pt;text-align:center;
   line-height:normal;text-autospace:ideograph-numeric ideograph-other"><a name="p953251510111"></a><a name="b11881145155715"></a><b><span style="font-size:12.0pt;font-family:宋体;color:#24292E;layout-grid-mode:both">业务类型</span></b></p>
   </td>
   <td width="28%" valign="top" style="width:28.0%;border:solid #DFE2E5 1.0pt;
   border-left:none;padding:4.5pt 9.75pt 4.5pt 9.75pt">
   <p class="MsoNormal" align="center" style="margin-bottom:12.0pt;text-align:center;
   line-height:normal;text-autospace:ideograph-numeric ideograph-other"><a name="p169111846181310"></a><a name="b1213516721612"></a><b><span style="font-size:12.0pt;font-family:宋体;color:#24292E;layout-grid-mode:both">瓶颈点</span></b></p>
   </td>
   <td width="22%" valign="top" style="width:22.0%;border:solid #DFE2E5 1.0pt;
   border-left:none;padding:4.5pt 9.75pt 4.5pt 9.75pt">
   <p class="MsoNormal" align="center" style="margin-bottom:12.0pt;text-align:center;
   line-height:normal;text-autospace:ideograph-numeric ideograph-other"><a name="p1591144617135"></a><a name="b31363721611"></a><b><span style="font-size:
   12.0pt;font-family:宋体;color:#24292E;layout-grid-mode:both">支持的应用</span></b></p>
   </td>
   <td width="20%" valign="top" style="width:20.0%;border:solid #DFE2E5 1.0pt;
   border-left:none;padding:4.5pt 9.75pt 4.5pt 9.75pt">
   <p class="MsoNormal" align="center" style="margin-bottom:12.0pt;text-align:center;
   line-height:normal;text-autospace:ideograph-numeric ideograph-other"><b><span style="font-size:12.0pt;font-family:宋体;color:#24292E;layout-grid-mode:both">待规划的应用</span></b></p>
   </td>
  </tr>
 </thead>
 <tbody><tr>
  <td width="14%" valign="top" style="width:14.0%;border:solid #DFE2E5 1.0pt;
  border-top:none;padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><a name="p1791124631317"></a><span lang="EN-US" style="font-size:12.0pt;font-family:&quot;Segoe UI&quot;,sans-serif;
  color:#24292E;layout-grid-mode:both">default</span></p>
  </td>
  <td width="13%" valign="top" style="width:13.0%;border-top:none;border-left:
  none;border-bottom:solid #DFE2E5 1.0pt;border-right:solid #DFE2E5 1.0pt;
  padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><a name="p45321515191120"></a><span style="font-size:12.0pt;font-family:宋体;color:#24292E;layout-grid-mode:both">默认类型</span></p>
  </td>
  <td width="28%" valign="top" style="width:28.0%;border-top:none;border-left:
  none;border-bottom:solid #DFE2E5 1.0pt;border-right:solid #DFE2E5 1.0pt;
  padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><a name="p691184671312"></a><span style="font-size:12.0pt;font-family:宋体;color:#24292E;layout-grid-mode:both">算力、内存、网络、</span><span lang="EN-US" style="font-size:12.0pt;font-family:&quot;Segoe UI&quot;,sans-serif;
  color:#24292E;layout-grid-mode:both">IO</span><span style="font-size:12.0pt;
  font-family:宋体;color:#24292E;layout-grid-mode:both">各维度资源使用率都不高</span></p>
  </td>
  <td width="22%" valign="top" style="width:22.0%;border-top:none;border-left:
  none;border-bottom:solid #DFE2E5 1.0pt;border-right:solid #DFE2E5 1.0pt;
  padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><a name="p69111946131318"></a><span lang="EN-US" style="font-size:12.0pt;font-family:&quot;Segoe UI&quot;,sans-serif;
  color:#24292E;layout-grid-mode:both">N/A</span></p>
  </td>
  <td width="20%" valign="top" style="width:20.0%;border-top:none;border-left:
  none;border-bottom:solid #DFE2E5 1.0pt;border-right:solid #DFE2E5 1.0pt;
  padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><span lang="EN-US" style="font-size:12.0pt;
  font-family:&quot;Segoe UI&quot;,sans-serif;color:#24292E;layout-grid-mode:both">&nbsp;N/A</span></p>
  </td>
 </tr>
 <tr>
  <td width="14%" valign="top" style="width:14.0%;border:solid #DFE2E5 1.0pt;
  border-top:none;background:#F6F8FA;padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><a name="p179110461137"></a><span lang="EN-US" style="font-size:12.0pt;font-family:&quot;Segoe UI&quot;,sans-serif;
  color:#24292E;layout-grid-mode:both">webserver</span></p>
  </td>
  <td width="13%" valign="top" style="width:13.0%;border-top:none;border-left:
  none;border-bottom:solid #DFE2E5 1.0pt;border-right:solid #DFE2E5 1.0pt;
  background:#F6F8FA;padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><a name="p20532111512117"></a><span lang="EN-US" style="font-size:12.0pt;font-family:&quot;Segoe UI&quot;,sans-serif;
  color:#24292E;layout-grid-mode:both">web</span><span style="font-size:12.0pt;
  font-family:宋体;color:#24292E;layout-grid-mode:both">应用</span></p>
  </td>
  <td width="28%" valign="top" style="width:28.0%;border-top:none;border-left:
  none;border-bottom:solid #DFE2E5 1.0pt;border-right:solid #DFE2E5 1.0pt;
  background:#F6F8FA;padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><a name="p1191117469133"></a><span style="font-size:12.0pt;font-family:宋体;color:#24292E;layout-grid-mode:both">算力瓶颈、网络瓶颈</span></p>
  </td>
  <td width="22%" valign="top" style="width:22.0%;border-top:none;border-left:
  none;border-bottom:solid #DFE2E5 1.0pt;border-right:solid #DFE2E5 1.0pt;
  background:#F6F8FA;padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><a name="p159111546161317"></a><span lang="EN-US" style="font-size:12.0pt;font-family:&quot;Segoe UI&quot;,sans-serif;
  color:#24292E;layout-grid-mode:both">Nginx</span><span style="font-size:12.0pt;
  font-family:宋体;color:#24292E;layout-grid-mode:both">、</span><span lang="EN-US" style="font-size:12.0pt;font-family:&quot;Segoe UI&quot;,sans-serif;color:#24292E;
  layout-grid-mode:both">Apache Traffic Server</span></p>
  </td>
  <td width="20%" valign="top" style="width:20.0%;border-top:none;border-left:
  none;border-bottom:solid #DFE2E5 1.0pt;border-right:solid #DFE2E5 1.0pt;
  background:#F6F8FA;padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><span lang="EN-US" style="font-size:12.0pt;
  font-family:&quot;Segoe UI&quot;,sans-serif;color:#24292E;layout-grid-mode:both">&nbsp;N/A</span></p>
  </td>
 </tr>
 <tr>
  <td width="14%" valign="top" style="width:14.0%;border:solid #DFE2E5 1.0pt;
  border-top:none;padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><a name="p2911164610134"></a><span lang="EN-US" style="font-size:12.0pt;font-family:&quot;Segoe UI&quot;,sans-serif;
  color:#24292E;layout-grid-mode:both">database</span></p>
  </td>
  <td width="13%" valign="top" style="width:13.0%;border-top:none;border-left:
  none;border-bottom:solid #DFE2E5 1.0pt;border-right:solid #DFE2E5 1.0pt;
  padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><a name="p4532111561119"></a><span style="font-size:12.0pt;font-family:宋体;color:#24292E;layout-grid-mode:both">数据库</span></p>
  </td>
  <td width="28%" valign="top" style="width:28.0%;border-top:none;border-left:
  none;border-bottom:solid #DFE2E5 1.0pt;border-right:solid #DFE2E5 1.0pt;
  padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><a name="ul3724104521013"></a><a name="p14911124612131"></a><span style="font-size:12.0pt;font-family:宋体;
  color:#24292E;layout-grid-mode:both">算力瓶颈、内存瓶颈、</span><span lang="EN-US" style="font-size:12.0pt;font-family:&quot;Segoe UI&quot;,sans-serif;color:#24292E;
  layout-grid-mode:both">IO</span><span style="font-size:12.0pt;font-family:
  宋体;color:#24292E;layout-grid-mode:both">瓶颈</span></p>
  </td>
  <td width="22%" valign="top" style="width:22.0%;border-top:none;border-left:
  none;border-bottom:solid #DFE2E5 1.0pt;border-right:solid #DFE2E5 1.0pt;
  padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><a name="p1091134671313"></a><span lang="EN-US" style="font-size:12.0pt;font-family:&quot;Segoe UI&quot;,sans-serif;
  color:#24292E;layout-grid-mode:both">Mongodb</span><span style="font-size:
  12.0pt;font-family:宋体;color:#24292E;layout-grid-mode:both">、</span><span lang="EN-US" style="font-size:12.0pt;font-family:&quot;Segoe UI&quot;,sans-serif;
  color:#24292E;layout-grid-mode:both">Mysql</span><span style="font-size:12.0pt;
  font-family:宋体;color:#24292E;layout-grid-mode:both">、</span><span lang="EN-US" style="font-size:12.0pt;font-family:&quot;Segoe UI&quot;,sans-serif;color:#24292E;
  layout-grid-mode:both">Postgresql</span><span style="font-size:12.0pt;
  font-family:宋体;color:#24292E;layout-grid-mode:both">、</span><span lang="EN-US" style="font-size:12.0pt;font-family:&quot;Segoe UI&quot;,sans-serif;color:#24292E;
  layout-grid-mode:both">Mariadb</span></p>
  </td>
  <td width="20%" valign="top" style="width:20.0%;border-top:none;border-left:
  none;border-bottom:solid #DFE2E5 1.0pt;border-right:solid #DFE2E5 1.0pt;
  padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><span lang="EN-US" style="font-size:12.0pt;
  font-family:&quot;Segoe UI&quot;,sans-serif;color:#24292E;layout-grid-mode:both">&nbsp;N/A</span></p>
  </td>
 </tr>
 <tr>
  <td width="14%" valign="top" style="width:14.0%;border:solid #DFE2E5 1.0pt;
  border-top:none;background:#F6F8FA;padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><a name="p491144611319"></a><span lang="EN-US" style="font-size:12.0pt;font-family:&quot;Segoe UI&quot;,sans-serif;
  color:#24292E;layout-grid-mode:both">big-data</span></p>
  </td>
  <td width="13%" valign="top" style="width:13.0%;border-top:none;border-left:
  none;border-bottom:solid #DFE2E5 1.0pt;border-right:solid #DFE2E5 1.0pt;
  background:#F6F8FA;padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><a name="p953261521112"></a><span style="font-size:12.0pt;font-family:宋体;color:#24292E;layout-grid-mode:both">大数据</span></p>
  </td>
  <td width="28%" valign="top" style="width:28.0%;border-top:none;border-left:
  none;border-bottom:solid #DFE2E5 1.0pt;border-right:solid #DFE2E5 1.0pt;
  background:#F6F8FA;padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><a name="p129111046151315"></a><span style="font-size:12.0pt;font-family:宋体;color:#24292E;layout-grid-mode:both">算力瓶颈、内存瓶颈</span></p>
  </td>
  <td width="22%" valign="top" style="width:22.0%;border-top:none;border-left:
  none;border-bottom:solid #DFE2E5 1.0pt;border-right:solid #DFE2E5 1.0pt;
  background:#F6F8FA;padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><a name="p119111946161317"></a><span lang="EN-US" style="font-size:12.0pt;font-family:&quot;Segoe UI&quot;,sans-serif;
  color:#24292E;layout-grid-mode:both">N/A</span></p>
  </td>
  <td width="20%" valign="top" style="width:20.0%;border-top:none;border-left:
  none;border-bottom:solid #DFE2E5 1.0pt;border-right:solid #DFE2E5 1.0pt;
  background:#F6F8FA;padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><span lang="EN-US" style="font-size:12.0pt;
  font-family:&quot;Segoe UI&quot;,sans-serif;color:#24292E;layout-grid-mode:both">Hadoop-hdfs</span><span style="font-size:12.0pt;font-family:宋体;color:#24292E;layout-grid-mode:both">、</span><span lang="EN-US" style="font-size:12.0pt;font-family:&quot;Segoe UI&quot;,sans-serif;
  color:#24292E;layout-grid-mode:both">Hadoop-spark</span></p>
  </td>
 </tr>
 <tr>
  <td width="14%" valign="top" style="width:14.0%;border:solid #DFE2E5 1.0pt;
  border-top:none;padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><a name="p1791104661313"></a><span lang="EN-US" style="font-size:12.0pt;font-family:&quot;Segoe UI&quot;,sans-serif;
  color:#24292E;layout-grid-mode:both">middleware</span></p>
  </td>
  <td width="13%" valign="top" style="width:13.0%;border-top:none;border-left:
  none;border-bottom:solid #DFE2E5 1.0pt;border-right:solid #DFE2E5 1.0pt;
  padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><a name="p453291517111"></a><span style="font-size:12.0pt;font-family:宋体;color:#24292E;layout-grid-mode:both">中间件框架</span></p>
  </td>
  <td width="28%" valign="top" style="width:28.0%;border-top:none;border-left:
  none;border-bottom:solid #DFE2E5 1.0pt;border-right:solid #DFE2E5 1.0pt;
  padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><a name="p591184671318"></a><span style="font-size:12.0pt;font-family:宋体;color:#24292E;layout-grid-mode:both">算力瓶颈、网络瓶颈</span></p>
  </td>
  <td width="22%" valign="top" style="width:22.0%;border-top:none;border-left:
  none;border-bottom:solid #DFE2E5 1.0pt;border-right:solid #DFE2E5 1.0pt;
  padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><a name="p2912846121315"></a><span lang="EN-US" style="font-size:12.0pt;font-family:&quot;Segoe UI&quot;,sans-serif;
  color:#24292E;layout-grid-mode:both">Dubbo</span></p>
  </td>
  <td width="20%" valign="top" style="width:20.0%;border-top:none;border-left:
  none;border-bottom:solid #DFE2E5 1.0pt;border-right:solid #DFE2E5 1.0pt;
  padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><span lang="EN-US" style="font-size:12.0pt;
  font-family:&quot;Segoe UI&quot;,sans-serif;color:#24292E;layout-grid-mode:both">&nbsp;N/A</span></p>
  </td>
 </tr>
 <tr>
  <td width="14%" valign="top" style="width:14.0%;border:solid #DFE2E5 1.0pt;
  border-top:none;background:#F6F8FA;padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><a name="p1391204619130"></a><span lang="EN-US" style="font-size:12.0pt;font-family:&quot;Segoe UI&quot;,sans-serif;
  color:#24292E;layout-grid-mode:both">in-memory-database</span></p>
  </td>
  <td width="13%" valign="top" style="width:13.0%;border-top:none;border-left:
  none;border-bottom:solid #DFE2E5 1.0pt;border-right:solid #DFE2E5 1.0pt;
  background:#F6F8FA;padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><a name="p65328153111"></a><span style="font-size:12.0pt;font-family:宋体;color:#24292E;layout-grid-mode:both">内存数据库</span></p>
  </td>
  <td width="28%" valign="top" style="width:28.0%;border-top:none;border-left:
  none;border-bottom:solid #DFE2E5 1.0pt;border-right:solid #DFE2E5 1.0pt;
  background:#F6F8FA;padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><a name="p3912164617133"></a><span style="font-size:12.0pt;font-family:宋体;color:#24292E;layout-grid-mode:both">内存瓶颈、</span><span lang="EN-US" style="font-size:12.0pt;font-family:&quot;Segoe UI&quot;,sans-serif;
  color:#24292E;layout-grid-mode:both">IO</span><span style="font-size:12.0pt;
  font-family:宋体;color:#24292E;layout-grid-mode:both">瓶颈</span></p>
  </td>
  <td width="22%" valign="top" style="width:22.0%;border-top:none;border-left:
  none;border-bottom:solid #DFE2E5 1.0pt;border-right:solid #DFE2E5 1.0pt;
  background:#F6F8FA;padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><a name="p1691254621313"></a><span lang="EN-US" style="font-size:12.0pt;font-family:&quot;Segoe UI&quot;,sans-serif;
  color:#24292E;layout-grid-mode:both">Redis</span></p>
  </td>
  <td width="20%" valign="top" style="width:20.0%;border-top:none;border-left:
  none;border-bottom:solid #DFE2E5 1.0pt;border-right:solid #DFE2E5 1.0pt;
  background:#F6F8FA;padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><span lang="EN-US" style="font-size:12.0pt;
  font-family:&quot;Segoe UI&quot;,sans-serif;color:#24292E;layout-grid-mode:both">&nbsp;N/A</span></p>
  </td>
 </tr>
 <tr>
  <td width="14%" valign="top" style="width:14.0%;border:solid #DFE2E5 1.0pt;
  border-top:none;padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><a name="p391214621312"></a><span lang="EN-US" style="font-size:12.0pt;font-family:&quot;Segoe UI&quot;,sans-serif;
  color:#24292E;layout-grid-mode:both">basic-test-suite</span></p>
  </td>
  <td width="13%" valign="top" style="width:13.0%;border-top:none;border-left:
  none;border-bottom:solid #DFE2E5 1.0pt;border-right:solid #DFE2E5 1.0pt;
  padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><a name="p55324155117"></a><span style="font-size:12.0pt;font-family:宋体;color:#24292E;layout-grid-mode:both">基础测试套</span></p>
  </td>
  <td width="28%" valign="top" style="width:28.0%;border-top:none;border-left:
  none;border-bottom:solid #DFE2E5 1.0pt;border-right:solid #DFE2E5 1.0pt;
  padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><a name="p1912164651319"></a><span style="font-size:12.0pt;font-family:宋体;color:#24292E;layout-grid-mode:both">算力瓶颈、内存瓶颈</span></p>
  </td>
  <td width="22%" valign="top" style="width:22.0%;border-top:none;border-left:
  none;border-bottom:solid #DFE2E5 1.0pt;border-right:solid #DFE2E5 1.0pt;
  padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><a name="p9912746121311"></a><span lang="EN-US" style="font-size:12.0pt;font-family:&quot;Segoe UI&quot;,sans-serif;
  color:#24292E;layout-grid-mode:both">SPECCPU2006</span><span style="font-size:12.0pt;font-family:宋体;color:#24292E;layout-grid-mode:both">、</span><span lang="EN-US" style="font-size:12.0pt;font-family:&quot;Segoe UI&quot;,sans-serif;
  color:#24292E;layout-grid-mode:both">SPECjbb2015</span></p>
  </td>
  <td width="20%" valign="top" style="width:20.0%;border-top:none;border-left:
  none;border-bottom:solid #DFE2E5 1.0pt;border-right:solid #DFE2E5 1.0pt;
  padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><span lang="EN-US" style="font-size:12.0pt;
  font-family:&quot;Segoe UI&quot;,sans-serif;color:#24292E;layout-grid-mode:both">&nbsp;N/A</span></p>
  </td>
 </tr>
 <tr>
  <td width="14%" valign="top" style="width:14.0%;border:solid #DFE2E5 1.0pt;
  border-top:none;background:#F6F8FA;padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><a name="p1391213464130"></a><span lang="EN-US" style="font-size:12.0pt;font-family:&quot;Segoe UI&quot;,sans-serif;
  color:#24292E;layout-grid-mode:both">hpc</span></p>
  </td>
  <td width="13%" valign="top" style="width:13.0%;border-top:none;border-left:
  none;border-bottom:solid #DFE2E5 1.0pt;border-right:solid #DFE2E5 1.0pt;
  background:#F6F8FA;padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><a name="p153210159118"></a><span style="font-size:12.0pt;font-family:宋体;color:#24292E;layout-grid-mode:both">人类基因组</span></p>
  </td>
  <td width="28%" valign="top" style="width:28.0%;border-top:none;border-left:
  none;border-bottom:solid #DFE2E5 1.0pt;border-right:solid #DFE2E5 1.0pt;
  background:#F6F8FA;padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><a name="p591214460137"></a><span style="font-size:12.0pt;font-family:宋体;color:#24292E;layout-grid-mode:both">算力瓶颈、内存瓶颈、</span><span lang="EN-US" style="font-size:12.0pt;font-family:&quot;Segoe UI&quot;,sans-serif;
  color:#24292E;layout-grid-mode:both">IO</span><span style="font-size:12.0pt;
  font-family:宋体;color:#24292E;layout-grid-mode:both">瓶颈</span></p>
  </td>
  <td width="22%" valign="top" style="width:22.0%;border-top:none;border-left:
  none;border-bottom:solid #DFE2E5 1.0pt;border-right:solid #DFE2E5 1.0pt;
  background:#F6F8FA;padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><a name="p391214619139"></a><span lang="EN-US" style="font-size:12.0pt;font-family:&quot;Segoe UI&quot;,sans-serif;
  color:#24292E;layout-grid-mode:both">Gatk4</span></p>
  </td>
  <td width="20%" valign="top" style="width:20.0%;border-top:none;border-left:
  none;border-bottom:solid #DFE2E5 1.0pt;border-right:solid #DFE2E5 1.0pt;
  background:#F6F8FA;padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><span lang="EN-US" style="font-size:12.0pt;
  font-family:&quot;Segoe UI&quot;,sans-serif;color:#24292E;layout-grid-mode:both">&nbsp;N/A</span></p>
  </td>
 </tr>
 <tr>
  <td width="14%" valign="top" style="width:14.0%;border:solid #DFE2E5 1.0pt;
  border-top:none;padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><a name="p5912154613139"><span lang="EN-US" style="font-size:12.0pt;font-family:&quot;Segoe UI&quot;,sans-serif;color:#24292E;
  layout-grid-mode:both">storage</span></a></p>
  </td>
  <td width="13%" valign="top" style="width:13.0%;border-top:none;border-left:
  none;border-bottom:solid #DFE2E5 1.0pt;border-right:solid #DFE2E5 1.0pt;
  padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><a name="p12532161561115"><span style="font-size:12.0pt;font-family:宋体;color:#24292E;layout-grid-mode:both">存储</span></a></p>
  </td>
  <td width="28%" valign="top" style="width:28.0%;border-top:none;border-left:
  none;border-bottom:solid #DFE2E5 1.0pt;border-right:solid #DFE2E5 1.0pt;
  padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><a name="p10912154631311"><span style="font-size:12.0pt;font-family:宋体;color:#24292E;layout-grid-mode:both">网络瓶颈、</span></a><span lang="EN-US" style="font-size:12.0pt;font-family:&quot;Segoe UI&quot;,sans-serif;
  color:#24292E;layout-grid-mode:both">IO</span><span style="font-size:12.0pt;
  font-family:宋体;color:#24292E;layout-grid-mode:both">瓶颈</span></p>
  </td>
  <td width="22%" valign="top" style="width:22.0%;border-top:none;border-left:
  none;border-bottom:solid #DFE2E5 1.0pt;border-right:solid #DFE2E5 1.0pt;
  padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><a name="p11912164617133"><span lang="EN-US" style="font-size:12.0pt;font-family:&quot;Segoe UI&quot;,sans-serif;color:#24292E;
  layout-grid-mode:both">N/A</span></a></p>
  </td>
  <td width="20%" valign="top" style="width:20.0%;border-top:none;border-left:
  none;border-bottom:solid #DFE2E5 1.0pt;border-right:solid #DFE2E5 1.0pt;
  padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><span lang="EN-US" style="font-size:12.0pt;
  font-family:&quot;Segoe UI&quot;,sans-serif;color:#24292E;layout-grid-mode:both">Ceph</span></p>
  </td>
 </tr>
 <tr>
  <td width="14%" valign="top" style="width:14.0%;border:solid #DFE2E5 1.0pt;
  border-top:none;background:#F6F8FA;padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><span lang="EN-US" style="font-size:12.0pt;
  font-family:&quot;Segoe UI&quot;,sans-serif;color:#24292E;layout-grid-mode:both">virtualization</span></p>
  </td>
  <td width="13%" valign="top" style="width:13.0%;border-top:none;border-left:
  none;border-bottom:solid #DFE2E5 1.0pt;border-right:solid #DFE2E5 1.0pt;
  background:#F6F8FA;padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><span style="font-size:12.0pt;font-family:
  宋体;color:#24292E;layout-grid-mode:both">虚拟化</span></p>
  </td>
  <td width="28%" valign="top" style="width:28.0%;border-top:none;border-left:
  none;border-bottom:solid #DFE2E5 1.0pt;border-right:solid #DFE2E5 1.0pt;
  background:#F6F8FA;padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><span style="font-size:12.0pt;font-family:
  宋体;color:#24292E;layout-grid-mode:both">算力瓶颈、内存瓶颈、</span><span lang="EN-US" style="font-size:12.0pt;font-family:&quot;Segoe UI&quot;,sans-serif;color:#24292E;
  layout-grid-mode:both">IO</span><span style="font-size:12.0pt;font-family:
  宋体;color:#24292E;layout-grid-mode:both">瓶颈</span></p>
  </td>
  <td width="22%" valign="top" style="width:22.0%;border-top:none;border-left:
  none;border-bottom:solid #DFE2E5 1.0pt;border-right:solid #DFE2E5 1.0pt;
  background:#F6F8FA;padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><span lang="EN-US" style="font-size:12.0pt;
  font-family:&quot;Segoe UI&quot;,sans-serif;color:#24292E;layout-grid-mode:both">Consumer-cloud</span><span style="font-size:12.0pt;font-family:宋体;color:#24292E;layout-grid-mode:both">、</span><span lang="EN-US" style="font-size:12.0pt;font-family:&quot;Segoe UI&quot;,sans-serif;
  color:#24292E;layout-grid-mode:both">Mariadb</span></p>
  </td>
  <td width="20%" valign="top" style="width:20.0%;border-top:none;border-left:
  none;border-bottom:solid #DFE2E5 1.0pt;border-right:solid #DFE2E5 1.0pt;
  background:#F6F8FA;padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><span lang="EN-US" style="font-size:12.0pt;
  font-family:&quot;Segoe UI&quot;,sans-serif;color:#24292E;layout-grid-mode:both">&nbsp;N/A</span></p>
  </td>
 </tr>
 <tr>
  <td width="14%" valign="top" style="width:14.0%;border:solid #DFE2E5 1.0pt;
  border-top:none;padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><span lang="EN-US" style="font-size:12.0pt;
  font-family:&quot;Segoe UI&quot;,sans-serif;color:#24292E;layout-grid-mode:both">docker</span></p>
  </td>
  <td width="13%" valign="top" style="width:13.0%;border-top:none;border-left:
  none;border-bottom:solid #DFE2E5 1.0pt;border-right:solid #DFE2E5 1.0pt;
  padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><span style="font-size:12.0pt;font-family:
  宋体;color:#24292E;layout-grid-mode:both">容器</span></p>
  </td>
  <td width="28%" valign="top" style="width:28.0%;border-top:none;border-left:
  none;border-bottom:solid #DFE2E5 1.0pt;border-right:solid #DFE2E5 1.0pt;
  padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><span style="font-size:12.0pt;font-family:
  宋体;color:#24292E;layout-grid-mode:both">算力瓶颈、内存瓶颈、</span><span lang="EN-US" style="font-size:12.0pt;font-family:&quot;Segoe UI&quot;,sans-serif;color:#24292E;
  layout-grid-mode:both">IO</span><span style="font-size:12.0pt;font-family:
  宋体;color:#24292E;layout-grid-mode:both">瓶颈</span></p>
  </td>
  <td width="22%" valign="top" style="width:22.0%;border-top:none;border-left:
  none;border-bottom:solid #DFE2E5 1.0pt;border-right:solid #DFE2E5 1.0pt;
  padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><span lang="EN-US" style="font-size:12.0pt;
  font-family:&quot;Segoe UI&quot;,sans-serif;color:#24292E;layout-grid-mode:both">Mariadb</span></p>
  </td>
  <td width="20%" valign="top" style="width:20.0%;border-top:none;border-left:
  none;border-bottom:solid #DFE2E5 1.0pt;border-right:solid #DFE2E5 1.0pt;
  padding:4.5pt 9.75pt 4.5pt 9.75pt">
  <p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal;text-autospace:
  ideograph-numeric ideograph-other"><span lang="EN-US" style="font-size:12.0pt;
  font-family:&quot;Segoe UI&quot;,sans-serif;color:#24292E;layout-grid-mode:both">&nbsp;N/A</span></p>
  </td>
 </tr>
</tbody></table>
