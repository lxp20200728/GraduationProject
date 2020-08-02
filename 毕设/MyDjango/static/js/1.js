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
                        video.addEventListener("play", function (_event) {
                                 var canvas = document.createElement("canvas");
                                 canvas.width = video.videoWidth;
                                 canvas.height = video.videoHeight;
                                 console.log(video.videoWidth)
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
                                    var video = document.getElementById('video_camera');
                                    var timeA,timeB,valueA,valueB;

                                    $.ajax({
                                         type: "POST",
                                         url: "camera_detect",    //后台处理函数的url
                                         async:false,  //false同步， ture异步
                                         data: {'Path':"photoPath"},
                                         success:function (data) {
                                                data = JSON.parse(data);
                                                timeA = JSON.parse(data["timeA"]);
                                                timeB = JSON.parse(data["timeB"]);
                                                valueA = JSON.parse(data["valueA"]);
                                                valueB = JSON.parse(data["valueB"]);
                                          }
                                    });
                                    var i, lengthA = timeA.length(), lengthB = timeB.length();
                                    for(i = 0; i < lengthA; i++){
                                        series.addPoint([valueA[i], timeA[i]], true, true);
                                    }
                                    for(i = 0; i < lengthB; i++){
                                        series.addPoint([valueB[i], timeB[i]], true, true);
                                    }
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
                                Highcharts.dateFormat('%Y-%m-%d %H:%M:%S', this.x) +'<br/>'+
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
                            var data = [],
                                    time = (new Date()).getTime(),
                                    i;

                            return data;
                        })()
                    },{
                        name: '桶B',
                        data: (function() {
                            // generate an array of random data
                            var data = [],
                                    time = (new Date()).getTime(),
                                    i;

                            return data;
                        })()
                    }]

                });

            });

     });
