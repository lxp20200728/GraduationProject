    $(document).ready(function () {

        $("#filePicker").change(function (file) {
                $("body").append(file.target.files[0]);
                var url = window.URL.createObjectURL(file.target.files[0]);
                $("#video_video")[0].src = url;
                $("#video_video")[0].onload = function () {
                    window.URL.revokeObjectURL(src);
                };
                button = document.getElementById("submit");
                button.removeAttribute("disabled");

        });

        $("#submit").click(function(){
              let formData = new FormData();
              // formData对象不仅可以传文件而且可以传普通的键值对
              formData.append('video',$('#filePicker')[0].files[0]);
              $.ajax({
                    type: "POST",
                    url: "video_detect",    //后台处理函数的url
                    data: formData,
                    processData:false,  //告诉浏览器不要对数据进行处理
                    contentType:false,  //告诉浏览器使用自带的formdata格式，不要编码
                    //回调函数
                    success:function (data) {
                        data = JSON.parse(data);
                        timeA = JSON.parse(data["timeA"]);
                        timeB = JSON.parse(data["timeB"]);
                        valueA = JSON.parse(data["valueA"]);
                        valueB = JSON.parse(data["valueB"]);
                        Highcharts.setOptions({
                            global: {
                                useUTC: false
                            }
                        });
                        chart = $('#container_video').highcharts({
                            chart: {
                                type: 'spline',
                                animation: Highcharts.svg, // don't animate in old IE
                                marginRight: 10,
                            },
                            title: {
                                text: '容量检测图'
                            },
                            xAxis: {
                                title: {
                                text: '时间'
                                },
                                type: 'datetime',
                                tickPixelInterval: 100
                            },
                            yAxis: {
                                title: {
                                    text: '容量'
                                },
                                plotLines: [{
                                    value: 0,
                                    width: 1,
                                    color: '#808080'
                                }]
                            },
                            tooltip: {
                                formatter: function() {
                                        return '<b>'+ this.series.name +'</b><br/>'+
                                        Highcharts.dateFormat('%H:%M:%S', this.x) +'<br/>'+
                                        Highcharts.numberFormat(this.y, 2);//点击显示
                                }
                            },
                            legend: {
                                enabled: true
                            },
                            exporting: {
                                enabled: false
                            },
                            series: [{
                                name: '桶A',
                                data: (function() {
                                    // generate an array of random data
                                    var data = [], i;
                                    for(i = 0; i < timeA.length; i++){
                                        data.push({
                                            x: timeA[i],
                                            y: valueA[i]
                                        })
                                    }
                                    return data;
                                })()
                            },{
                                name: '桶B',
                                data: (function() {
                                    // generate an array of random data
                                    var data = [], i;
                                    for(i = 0; i < timeB.length; i++){
                                        data.push({
                                            x: timeB[i],
                                            y: valueB[i]
                                        })
                                    }
                                    return data;
                                })()
                            }]

                        });
                    }
              });
        });


    });


