$(document).ready(function(){
	var currMapIndex = 0;
	var allMapObj = new Array();
	//西南经纬度
	var southWest = new AMap.LngLat(108.505, 19.0419);
	//东北经纬度
	var northEast = new AMap.LngLat(117.505, 26.0419);
	//控制替换图片
	var imagesNum = 0;
	//控制定时器
	var setInt;
	//暂停启动
	var stopOrStart = 1;
	//上一个特殊处理
	var lastInd = 1;
	
	//地图初始化
	function init(mapId, mapImages) {
		var currMapObj = new AMap.Map('' + mapId, {
			zooms: [6, 18],
			zoom: 6
		});
		//设置地图可视范围
		var bounds = currMapObj.setBounds(new AMap.Bounds(southWest, northEast));
		//设置比例尺
			 AMap.plugin([
			'AMap.Scale'
		], function(){
			// 在图面添加比例尺控件，展示地图在当前层级和纬度下的比例尺
			currMapObj.addControl(new AMap.Scale());
		});
		//设置初始图片
		var startImage = mapImages[0].url;
		//创建图层
		var currMapObjImages = new AMap.ImageLayer({
			bounds: bounds,
			url: startImage,
			opacity: 1,
			visible: true,
			map: currMapObj,
			zooms: [6, 18],
			zindex: 12
		});
		return [currMapObj, currMapObjImages];
	}
	//地图mapmove事件绑定
	function bindAll(mapObj, index) {
		mapObj[0].on('mapmove', function() {
			if(currMapIndex == index) {
				var length = allMapObj.length;
				var mapCenter = mapObj[0].getCenter();
				var mapZoom = mapObj[0].getZoom();
				for(var j = 0; j < length; j++) {
					if(currMapIndex != j) {
						var bindMapObj = allMapObj[j].mapObj[0];
						bindMapObj.setZoomAndCenter(mapZoom, mapCenter);
					}
				}
			}
		})
		//click事件绑定
		mapObj[0].on('mousemove', function(e) {
			if(currMapIndex == index) {
				var length = allMapObj.length;
				for(var j = 0; j < length; j++) {
					var bindMapObj = allMapObj[j].mapObj[0];
					//获取经度
					var mapLng = e.lnglat.getLng();
					//获取纬度
					var mapLat = e.lnglat.getLat();
					//调用mark创建函数
					initMark(bindMapObj, mapLng, mapLat);
				}
			}
		})
	}

	//mark创建
	function initMark(bindMapObj, mapLng, mapLat) {
		//获取mark
		var allmarker = bindMapObj.getAllOverlays('marker');
		if(allmarker == '') {
			//如果地图不存在mark则创建mark
			var marker = new AMap.Marker({
				position: new AMap.LngLat(mapLng, mapLat)
			})
			bindMapObj.add(marker);
		} else {
			//如果地图存在mark则先remove掉mark再创建mark
			bindMapObj.remove(allmarker);
			var marker = new AMap.Marker({
				position: new AMap.LngLat(mapLng, mapLat)
			})
			bindMapObj.add(marker);
		}
	}

	function initMap(maps) {
		var length = maps.maps.length;
		// init maps
		for(var i = 0; i < length; i++) {
			var mapId = maps.maps[i].mapId;
			var mapImages = maps.maps[i].images;
			$("#" + mapId).mouseover(function() {
				currMapIndex = $(this).attr("curr");
			});
			//初始化地图函数
			var mapObj = init(mapId, mapImages);
			var tempObj = new Object();
			tempObj.mapObj = mapObj;
			tempObj.images = mapImages;
			allMapObj.push(tempObj);
			//地图绑定事件函数
			bindAll(mapObj, i);
		}
		//启动定时器
		changeSetInterval();
	}

	//图片替换
	function imageChangeFun() {
		var length = allMapObj.length;
		var lengthOne = allMapObj[0].images.length;
		var lengthTwo = allMapObj[1].images.length;
		var lengthThree = allMapObj[2].images.length;
		var lengthFour = allMapObj[3].images.length;
		var lengthFive = allMapObj[4].images.length;
		var lengthSix = allMapObj[5].images.length;
		//取最大值
		var maxLength = Math.max(lengthOne, lengthTwo, lengthThree, lengthFour, lengthFive, lengthSix);
		for(var i = 0; i < length; i++) {
			var mapObj = allMapObj[i].mapObj[1];
			var images = allMapObj[i].images;
			
			// 处理特殊逻辑 各长度不同意情况下 根据自身length长度-1  imagesNum 8 length 9
			if(images.length < imagesNum + 1) {
				mapObj.setImageUrl(images[images.length - 1].url);
				var imageUrl = images[images.length - 1].url;
				subTimeString(imageUrl);
			} else {
				mapObj.setImageUrl(images[imagesNum].url);
				var imageUrl = images[imagesNum].url;
				subTimeString(imageUrl);
			}
		}
		
		//高亮显示改变
		$("#nav").find("div").css("background-color", "cornflowerblue");
		$("#d" + imagesNum).css("background-color", "orange");
		
		
		imagesNum = imagesNum + 1;
		if(imagesNum >= maxLength) {
			imagesNum = 0;
		}
		
	}
	
	
			//下一个按钮
	$("#next").click(function() {
		if(stopOrStart == 2) {
			imageChangeFun();
		}
	});
	
	//上一个按钮(需要特殊处理
	$("#last").click(function() {
		if(stopOrStart == 2) {
			if(lastInd == 1) {
				if(imagesNum > 1) {
					imagesNum = imagesNum - 2;
					lastInd = 2
				} else {
					imagesNum = imagesNum - 1;
					lastInd = 2
				}
			} else if(lastInd == 2) {
				imagesNum = imagesNum - 1;
			}
			
			var picLength = allMapObj[0].images.length;
			// 特殊处理上一个 如果<0 即为已经在最后一个节点 获取倒数第二个节点下标 add by eric
			if(imagesNum<0){
				imagesNum=picLength-2;
			}
		
			var length = allMapObj.length;
			

			for(var i = 0; i < length; i++) {
				var mapObj = allMapObj[i].mapObj[1];
				var images = allMapObj[i].images;
				
				mapObj.setImageUrl(images[imagesNum].url);
				// add by eric
				subTimeString(images[imagesNum].url);
			}
			$("#nav").find("div").css("background-color", "cornflowerblue");
			$("#d" + imagesNum).css("background-color", "orange");
			if(imagesNum == 0) {
				imagesNum = picLength;
			}
		}
	});
	

	//定时器
	function changeSetInterval() {
		setInt = setInterval(imageChangeFun, 500);
	}




	//更新
	$(".navgxbtn").click(function() {
		var dateStr;
		//获取日期时间
		var nowdate = $("#ks").val();
		//获取时间时间
		// var nowtime = $(".timeinput").val();
			var vall = $("#hh").val()
			var valll = $("#timePicker").val()
	        if(vall!=" "||valll!=" " ){
			var zong=$("#hh").val()+$("#timePicker").val()
	        console.log(zong)
	        var sdw=$('#ks').val();
	        $("#ks").find("option[value='"+sdw+"']").attr("value",zong);
	        console.log($("#ks").val())
			var chuanz = $("#ks").val()
			chuanz = chuanz.replace(/-/g, "");
			chuanz = chuanz.replace(/:/g, "");
			chuanz = chuanz.replace(/ /g, "");
			
			// dateStr = nowdate + nowtime;
			console.log(chuanz)
			dateTimeFun(chuanz);
			}

		// if(nowdate == "请选择时间") {
			// alert("请选择时间");
		 else {
			// 去除指定字符串
			nowdate = nowdate.replace(/-/g, "");
			nowdate = nowdate.replace(/:/g, "");
			nowdate = nowdate.replace(/ /g, "");
			// dateStr = nowdate + nowtime;
			console.log(nowdate)
			if($('#ks').val()=="请选择时间"){
			alert("请选择时间")
			return false
		    }
			dateTimeFun(nowdate);

		}
		//截取time最后两位
		imagesNum = 0;
	})
	
	//最新
	$(".navzxbtn").click(function() {
		//var newdate = new XDate();
		//var min = newdate.getMinutes();
		//if(min % 6 != 0) {
			//min = min - min % 6;
			//if(min.toString().length < 2) {
				//min = '0' + min.toString();
			//}
		//}
		//$(".timeinput").val(newdate.toString("HH:mm"));
		//$(".dateinput").val(newdate.toString("yyyy-MM-dd"));
		//var dateStr = newdate.toString("yyyyMMddHH") + min;
		//dateTimeFun(dateStr);
        var sele = document.getElementById("ks").options;
        sele[0].selected = true;
        var newdate = new XDate();
        var min = newdate.getMinutes();
        var hour = newdate.getHours();
        if(min % 6 != 0)
        {
            min = min - min % 6 - 18;
            if(min < 0)
            {
                min = 60 + min
                hour = parseInt(hour) - 1
            }
            else if(min.toString().length < 2)
            {
                min = '0' + min.toString();
            }
        }
        else
        {
            min = min - 18;
            if(min < 0)
            {
                min = 60 + min
                hour = parseInt(hour) - 1
            }
            else if(min.toString.length < 2)
            {
                min = '0' + min.toString();
            }
        }
        $(".timeinput").val(hour + ":" + min);
        $(".dateinput").val(newdate.toString("yyyy-MM-dd"));
        var dateStr = newdate.toString("yyyyMMdd") + hour + min;
        dateTimeFun(dateStr);
        imagesNum = 0;
	})
	
	
		//生成
	$("#shencheng1").click(function() {
			stopOrStart = 10;
			lastInd = 2;
		clearInterval(setInt);
		$("#stop").text("启动");
		var vall = $("#hh").val()
		var valll = $("#timePicker").val()
		if(vall==" "||valll==" " ){
        var a = document.getElementById("ks").value;
        a = a.replace(/-/g, "");
		a = a.replace(/:/g, "");
		a = a.replace(/ /g, "");
         var c = document.getElementById("cityChoice").value;
		var dated=parseFloat(a) - parseFloat(100);	
        var c = document.getElementById("cityChoice").value;

			// 获取图片
		console.log("maps",allMapObj);
		allMapObj[0].mapObj[1].setImageUrl("metric/model1/model1_"+c+"/img/"+a+".png");
		allMapObj[1].mapObj[1].setImageUrl("metric/model2/model2_"+c+"/img/"+a+".png");
		allMapObj[2].mapObj[1].setImageUrl("metric/model3/model3_"+c+"/img/"+a+".png");
		allMapObj[3].mapObj[1].setImageUrl("metric/model4/model4_"+c+"/img/"+a+".png");
		allMapObj[4].mapObj[1].setImageUrl("metric/realImg/"+c+"/img/"+a+".png");
		allMapObj[5].mapObj[1].setImageUrl("metric/realImg/"+c+"/img/"+dated+".png");
		
			
		}
		else{
		var dateStr;
		//获取日期时间
		var nowdate = $(".dateinput").val();
		//获取时间时间
		var nowtime = $(".timeinput").val();
				var ti =nowdate+"   "+nowtime;
        $("#autoMapSpanId").find("span").text(ti);
			nowdate = nowdate.replace(/-/g, "");
			nowtime = nowtime.replace(/:/g, "");
            dateStr = nowdate + nowtime;
		var dated=parseFloat(dateStr) - parseFloat(100);	
        var c = document.getElementById("cityChoice").value;

			// 获取图片
		console.log("maps",allMapObj);
		allMapObj[0].mapObj[1].setImageUrl("metric/model1/model1_"+c+"/img/"+dateStr+".png");
		allMapObj[1].mapObj[1].setImageUrl("metric/model2/model2_"+c+"/img/"+dateStr+".png");
		allMapObj[2].mapObj[1].setImageUrl("metric/model3/model3_"+c+"/img/"+dateStr+".png");
		allMapObj[3].mapObj[1].setImageUrl("metric/model4/model4_"+c+"/img/"+dateStr+".png");
		allMapObj[4].mapObj[1].setImageUrl("metric/realImg/"+c+"/img/"+dateStr+".png");
		allMapObj[5].mapObj[1].setImageUrl("metric/realImg/"+c+"/img/"+dated+".png");
		
		}
	})
		//暂停按钮
	$("#stop").click(function() {
		if(stopOrStart == 1) {
			//清除定时器
			clearInterval(setInt);
			$(this).text("启动");
			stopOrStart = 2;
			lastInd = 1
		} else if(stopOrStart == 2) {
			//启动定时器
			changeSetInterval();
			$(this).text("暂停");
			stopOrStart = 1;
			lastInd = 1;
		}
	});
	


	

	//字符串拼接
	function dateTimeFun(dateStr) {
		//截取分钟
		var minute = dateStr.substring(10, 12);
		//截取小时
		var hour = dateStr.substring(8, 10);
		//截取日期
		var days = dateStr.substring(6, 8);
		//月
		var months = dateStr.substring(4, 6);
		//年
		var year = dateStr.substring(0, 4);
		//文件路径循环
		var imageArray = new Array();
		for(var i = 1; i <= 6; i++) {
			var imageUrl = "";
			var picArray = new Array();
			if(i == 5) {
				imageUrl = 'image/radar/radarLive/${date}/';
			} else if(i == 6) {
				imageUrl = 'image/radar/future1hLive/${date}/';
			} else {
				imageUrl = "image/model" + i + "/${date}/";
			}
			picArray = getPicArray(year, months, days, hour, minute, imageUrl, "png", 10, "yyyyMMddHHmm", "yyyyMMdd");
			imageArray.push(picArray);
		}
		//销毁定时器
		clearInterval(setInt);
		$("#stop").text("启动");
		stopOrStart = 2;
		lastInd = 1
		
		//数组图片替换
		var length = allMapObj.length;
		var picLength = allMapObj[0].images.length;
		imagesNum = picLength - 1;
		for(var i = 0; i < length; i++) {
			allMapObj[i].images = imageArray[i].url;
		}
		imageChangeFun();
	}
		//生成拼接
	function dateTimeFun1(dateStr,c) {
		//截取分钟
		var minute = dateStr.substring(10, 12);
		//截取小时
		var hour = dateStr.substring(8, 10);
		//截取日期
		var days = dateStr.substring(6, 8);
		//月
		var months = dateStr.substring(4, 6);
		//年
		var year = dateStr.substring(0, 4);
		//文件路径循环
		var c = document.getElementById("cityChoice").value;
		var imageArray = new Array();
		for(var i = 1; i <= 6; i++) {
			var imageUrl = "";
			var picArray = new Array();
			
			if(i == 5) {
				imageUrl = "metric/realImg/"+c+"/img/${date}/";
			} else if(i == 6) {
				imageUrl = "metric/realImg/"+c+"/img$/${date}/";
			} else {
				imageUrl = "metric/model"+ i +"/model"+i+"_"+c+"/${date}/";
			}
              
			picArray = getPicArray(year, months, days, hour, minute, imageUrl, "png", 10, "yyyyMMddHHmm", "yyyyMMdd");
			imageArray.push(picArray);
		}
	}
	/**
	 *year 年
	 *month 月份
	 *date 日期
	 *hour 小时
	 *min 分钟
	 *imageUrl 图片目录
	 *imageType 图片类型
	 *picCount 图片张数
	 *format 日期转换规范
	 *urlFormat url日期格式format
	 **/
	function getPicArray(year, month, date, hour, min, imageUrl, imageType,
		picCount, format, urlFormat) {
		// 图片数组初始
		var picArray = new Array();
		var date = new XDate(year, (month - 1), date, hour, min, 0, 0);
		// 计算出开始时间
		var startTime = date;
		if(min != 0) {
			var time = -1 * (min % 6);
			startTime = date.addMinutes(time)
		}
		// 图片规则
		var obj =  new Object();
		console.log(imageUrl)
		obj.url = imageUrl.replace("${date}", startTime.toString(urlFormat)) + startTime.toString(format) + "." + imageType;
		// 排序规则 开始时间为最后一张图
		picArray[picCount - 1] = obj;
		// n张图片规则 每次-6分钟
		var n = picCount - 1;
		for(var i = 0; i < n; i++) {
			var tempDate = startTime.addMinutes(-6);
			obj = new Object();
			obj.url = imageUrl.replace("${date}", tempDate.toString(urlFormat)) + tempDate.toString(format) + "." + imageType;
			console.log(obj.url)
			picArray[picCount - 2 - i] = obj;
			// 赋值
			startTime = tempDate;
		};
		var currArray = new Object();
		currArray.url = picArray;
		console.log(currArray)
		return currArray;
	}
	//字符串截取
	function subTimeString(imageUrl) {
		var imageUrl = imageUrl
		var imageUrlIndex = imageUrl.lastIndexOf("\/");
		imageUrl = imageUrl.substring(imageUrlIndex + 1, imageUrl.length);
		imageUrl = imageUrl.substring(0, 12);
		//截取分钟
		var minute = imageUrl.substring(10, 12);
		//截取小时
		var hour = imageUrl.substring(8, 10);
		//截取日期
		var days = imageUrl.substring(6, 8);
		//月
		var months = imageUrl.substring(4, 6);
		//年
		var year = imageUrl.substring(0, 4);

		var newdate = new XDate(year, (months - 1), days, hour, minute, 0, 0);
		newdate = newdate.toString("yyyy-MM-dd HH:mm");
		$("#autoMapSpanId").find("span").text(newdate);
//		console.log("newdate", newdate);
	}

	//创建对象
	var maps = new initMap(mapsArray);
})
