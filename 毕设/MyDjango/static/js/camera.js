     $(function (){
            $("#start_stop").click(function() {
                    var video = document.getElementById('video_camera');
                    if(video.paused)
                        getStream();
                    else
                        video.pause();

                    function getStream(){
                        var video = document.getElementById('video');
                        if (navigator.mediaDevices.getUserMedia) {
                            //最新的标准API
                            navigator.mediaDevices.getUserMedia({video : {width: 400, height: 400}}).then(success).catch(error);
                        } else if (navigator.webkitGetUserMedia) {
                            //webkit核心浏览器
                            navigator.webkitGetUserMedia({video : {width: 400, height: 400}},success, error)
                        } else if (navigator.mozGetUserMedia) {
                            //firfox浏览器
                            navigator.mozGetUserMedia({video : {width: 400, height: 400}}, success, error);
                        } else if (navigator.getUserMedia) {
                            //旧版API
                            navigator.getUserMedia({video : {width: 400, height: 400}}, success, error);
                        }
                    }
                    function success(stream) {
                        video.srcObject = stream;
                        video.play();
                        video.addEventListener("timeupdate", function (_event) {
                             var canvas = document.createElement("canvas");
                             canvas.width = video.videoWidth;
                             canvas.height = video.videoHeight;
                             canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
                             photoPath = canvas.toDataURL("image/png");
                             $.ajax({
                                    type: "POST",
                                    url: "camera_savePhotos",    //后台处理函数的url
                                    data: {'Path':photoPath},
                                    success:function (data) {
                                    }
                             });
                        });
                    }
                    function error(error) {
                        console.log(`访问用户媒体设备失败${error.name}, ${error.message}`);
                    }
            });

            $("#start_stop").click(function (){
                Highcharts.setOptions({
                    global: {
                        useUTC: false
                    }
                });
                var  time = (new Date()).getTime();
                var chart;
                $('#container_camera').highcharts({
                    chart: {
                        type: 'spline',
                        animation: Highcharts.svg, // don't animate in old IE
                        marginRight: 10,
                        events: {
                            load: function() {
                                var series = this.series[0];
                                var series1 = this.series[1];
                                // set up the updating of the chart each second
                                setInterval(function() {
                                    $.ajax({
                                           type: "POST",
                                           url: "camera_detect",    //后台处理函数的url
                                           async:false,  //false同步， ture异步
                                           data: {'Path':"photoPath"},
                                           processData:false,  //告诉浏览器不要对数据进行处理
                                           success:function (data) {
                                                data = JSON.parse(data);
                                                timeA = JSON.parse(data["timeA"]);
                                                timeB = JSON.parse(data["timeB"]);
                                                valueA = JSON.parse(data["valueA"]);
                                                valueB = JSON.parse(data["valueB"]);
                                                var i;
                                                for(i = 0; i < timeA.length; i++){
                                                    series.addPoint([timeA[i], valueA[i]], true, true);
                                                }
                                                for(i = 0; i < timeB.length; i++){
                                                    series1.addPoint([timeB[i], valueB[i]], true, true);
                                                }
                                           }
                                    });
                                }, 1000);
                            }
                        }
                    },
                    title: {
                        text: '容量检测曲线图'
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
                            var data = [],i;
                                for (i = 19; i >= 0; i--) {
                                    data.push({
                                        x: 0 - i * 1000,
                                        y: 0
                                    });
                                }
                            return data;
                        })()
                    },{
                        name: '桶B',
                        data: (function() {
                            // generate an array of random data
                            var data = [],i;
                                for (i = 19; i >= 0; i--) {
                                    data.push({
                                        x: 0 - i * 1000,
                                        y: 0
                                    });
                                }
                            return data;
                        })()
                    }]

                });

            });

     });
