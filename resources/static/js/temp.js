/**
 * @file help function for html
 *
 * Copyright (c) 2019 Huawei Technologies Co., Ltd.
 * A-Tune is licensed under the Mulan PSL v2.
 * You can use this software according to the terms and conditions of the Mulan PSL v2.
 * You may obtain a copy of Mulan PSL v2 at:
 *    http://license.coscl.org.cn/MulanPSL2
 * THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
 * PURPOSE.
 * See the Mulan PSL v2 for more details.
 * Create: 2020-08-17
*/


var socket;
var line;
var projectName;
var intervalId;
var timestamp;

function deleteOld() {
    var container = document.getElementById('tuning-chart');
    while (container.hasChildNodes()) {
        container.removeChild(container.firstChild);
    }
}

function initNdiv(list, name) {
    list.push('performance');
    list.push('best performance');
    var container = window.document.getElementById('tuning-chart');
    list.forEach(function (item) {
        var br = document.createElement('br');
        container.appendChild(br);

        var div = document.createElement('div');
        div.id = 'chart-' + item;
        div.className = 'performance-chart';
        container.appendChild(div);
        var chart = echarts.init(document.getElementById(div.id));
        var option = {
            title: {
                text: item
            },
            tooltip: {},
            xAxis: {
                name: 'times',
                data: []
            },
            yAxis: {
                name: 'value',
            },
            series: [{
                name: item,
                type: 'line',
                data: []
            }]
        };
        chart.setOption(option);
    });
    projectName = name;
}

function updateChart(name, times, value) {
    console.log(name, '-', times, '-', value);
    var id = 'chart-' + name;
    var chart = echarts.init(document.getElementById(id));
    var oldData = chart.getOption().series[0].data;
    var oldX = chart.getOption().xAxis[0].data;
    for (var i in times) {
        oldX.push(times[i]);
        if (name === 'best performance') {
            if (parseInt(value[i], 10) > parseInt(oldData[oldData.length - 1], 10) || oldData[0] === undefined) {
                oldData.push(value[i]);
            } else {
                oldData.push(oldData[oldData.length - 1]);
            }
        } else {
            oldData.push(value[i]);
        }
    }
    chart.setOption({
        xAxis: {data: oldX},
        series: [{data: oldData}]
    });
}

function appendPrjList(list, timestamp) {
    var container = document.getElementById('tuning-chart');
    console.log(list);
    var h4 = document.createElement('h4');
    h4.appendChild(document.createTextNode('Project:'));
    container.appendChild(h4);
    if (list.length === 0) {
        h4 = document.createElement('h4');
        h4.appendChild(document.createTextNode('No tuning project'));
        container.appendChild(h4);
        return;
    }
    var ul = document.createElement('ul');
    container.appendChild(ul);
    for (let i in list) {
        var li = document.createElement('li');
        li.id = 'project-name-' + list[i];
        li.appendChild(document.createTextNode(list[i]));
        ul.appendChild(li);
        li.style.cursor = 'pointer';

        li.onclick = function () {
            console.log(list[i]);
            socket.emit('inital_chart', {'prj_name': list[i]}, timestamp, namespace = '/tuning');
        };
    }
}

function updateChartInit(nameList, lineNum, value) {
    var lineList = [];
    nameList.push('performance');
    console.log(value, value.length);
    for (var i in value[0]) {
        lineList[i] = parseInt(lineNum, 10) + parseInt(i, 10);
    }
    for (var i in value) {
        updateChart(nameList[i], lineList, value[i]);
        if (nameList[i] === 'performance') {
            updateChart('best performance', lineList, value[i]);
        }
    }
}

function updateInterval() {
    socket.emit('update_chart', projectName, line, timestamp, namespace = '/tuning');
}

function setSocket() {
    $(document).ready(function () {
        console.log((new Date()).valueOf());
        var namespace = '/tuning';
        socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);
        timestamp = (new Date()).valueOf();
        socket.emit('show_page', timestamp, namespace = '/tuning');

        line = 0;
        socket.on('get_all_tuning_list', function (res) {
            if (res['timestamp'] === timestamp) {
                deleteOld();
                appendPrjList(res['prj_list'], res['timestamp']);
            }
        });

        socket.on('inital_chart', function (res) {
            if (res['timestamp'] === timestamp) {
                deleteOld();
                initNdiv(res['graph_list'], res['prj_name']);
                intervalId = setInterval(updateInterval, 2000);
            }
        });

        socket.on('update_chart', function (res) {
            if (res['timestamp'] === timestamp) {
                line = res['next_line'];
                if (line === -1) {
                    window.clearInterval(intervalId);
                }
                updateChartInit(res['name'], res['num'] + 1, res['value']);
            }
        });

        socket.on('file_removed', function (res) {
            if (res['timestamp'] === timestamp) {
                window.clearInterval(intervalId);
                var container = document.getElementById('tuning-chart');
                container.appendChild(document.createElement('br'));
                var h4 = document.createElement('h4');
                h4.appendChild(document.createTextNode('File ' + res['prj_name'] + ' has been delete'));
                container.appendChild(h4);
            }
        });
    });
}
