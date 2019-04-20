$(document).ready(function() {
	    var g=0;
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
	//播放张数特殊处理
	var radioindex=2;
	//地图初始化
	var getdata=''
	var mydata=location.search
	console.log(mydata.length)
	if(mydata.length>20){
	$(".newdateinput").val("")
	$("#newtimePicker").val("")
	}
	else{
	mydata=mydata.replace('?','')
	hrefdata1=mydata.slice(0,10)
	hrefdata2=mydata.slice(10,15)
    mydata=mydata.replace(/-/g,"")
	mydata=mydata.replace(/:/g,"")
	$(".newdateinput").val(hrefdata1)
	$("#newtimePicker").val(hrefdata2)
	}
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
		dateTimeFun(mydata)
	}
	//图片替换
	function imageChangeFun() {
		console.log(imagesNum)
        g=g+6;
		if(radioindex==1&&g>60){
			g=6
		}
		if(radioindex==2&&g>120){
			g=6
		}
		console.log(g)
		var length = allMapObj.length;
		var lengthSeven = allMapObj[0].images.length;
		var lengthEight = allMapObj[1].images.length;
		//取最大值
		var maxLength = Math.max(lengthSeven, lengthEight);
		// var picLength = maxLength;
		// console.log(allMapObj);
		for(var i = 0; i < length; i++) {
		// for(var i = length-1; i > 0; i--) {
			var mapObj = allMapObj[i].mapObj[1];
			var images = allMapObj[i].images;
			if(images.length < imagesNum + 1) {
				mapObj.setImageUrl(images[images.length - 1].url);
				var imageUrl = images[images.length - 1].url;
				subTimeString(imageUrl,g);
			
			} 
			else {
				mapObj.setImageUrl(images[imagesNum].url);
				var imageUrl = images[imagesNum].url;					
				subTimeString(imageUrl,g);
			
			}

		}
				if(radioindex==2){
					for(i=10;i<20;i++){
                    console.log("newd"+i)
                    var dae = "#newd"+i
                    $(dae).css("display","block")
                }
				}
				if(radioindex==1){
					for(i=10;i<20;i++){
                    console.log("newd"+i)
                    var dae = "#newd"+i
                    $(dae).css("display","none")
                }
				}
		console.log(imagesNum)
		//高亮显示改变
		$("#newnav").find("div").css("background-color", "cornflowerblue");
		$("#newd" + imagesNum).css("background-color", "orange");
		imagesNum = imagesNum + 1;
		if(imagesNum >= maxLength) {
			imagesNum = 0;
		}
	}
	//定时器
	function changeSetInterval() {
		setInt = setInterval(imageChangeFun, 500);
	}
	//暂停按钮
	$("#newstop").click(function() {
		if(stopOrStart == 1) {
			//清除定时器
			clearInterval(setInt);
			$(this).text("启动");
			stopOrStart = 2;
			lastInd = 1
		} else if(stopOrStart == 2) {
		if(lastInd==2){
			g=g-6
		imageChangeFun();
		}
			//启动定时器
			changeSetInterval();
			$(this).text("暂停");
			stopOrStart = 1;
			lastInd = 1;
		}
	});
	//下一个按钮
	$("#newnext").click(function() {
		console.log(imagesNum)
		if(stopOrStart == 2) {
			imageChangeFun();
		}
		if(lastInd==2){
			g=g-6
		imageChangeFun();
		}
		lastInd=1
	});
	//上一个按钮(需要特殊处理
	$("#newlast").click(function() {
		if(stopOrStart == 2) {
			if(lastInd == 1) {
				if(imagesNum > 1) {
					imagesNum = imagesNum - 2;
					lastInd = 2
					console.log("触发1")
				} else {
					imagesNum = imagesNum - 1;
					lastInd = 2
					console.log("触发2")
				}
			} else if(lastInd == 2) {
				imagesNum = imagesNum - 1;
				console.log("触发3"+imagesNum)
			}
				if(imagesNum<=0){
				imagesNum=0;
			}
			var length = allMapObj.length;
			var picLength = allMapObj[0].images.length;
            g=g-6				        
		    if(radioindex==1&&g<=0){
			g=60
		    }
			if(radioindex==2&&g<=0){
			g=120
		    }
   			console.log(imagesNum)
			for(var i = 0; i < length; i++) {
				var mapObj = allMapObj[i].mapObj[1];
				var images = allMapObj[i].images;
				console.log(images[imagesNum].url)
				mapObj.setImageUrl(images[imagesNum].url);
				subTimeString(images[imagesNum].url,g);
			}
			if(imagesNum<0){
					imagesNum=0
				}
			$("#newnav").find("div").css("background-color", "cornflowerblue");
			$("#newd" + imagesNum).css("background-color", "orange");

			if(imagesNum == 0) {
				imagesNum = picLength;
			}
		}
	});
	//Radio控制张数
	// $('#optionsRadios4').click(function(){
	// radioindex=2
	// g=0
    // for(i=10;i<20;i++){
    // console.log("newd"+i)
    // var dae = "#newd"+i
    // $(dae).css("display","block")
    // }
	// $(".newnavgxbtn").trigger('click');
    // }
    // )
    // $('#optionsRadios3').click(function(){
	// radioindex=1
	// g=0
    // for(i=10;i<20;i++){
    // console.log("newd"+i)
    // var dae = "#newd"+i
    // $(dae).css("display","none")
    // }
	// $(".newnavgxbtn").trigger('click');
    // }
    // )
	    //跳转页面
    	$("#tiaozhuan").click(function(){
					var dateStr;
		//获取日期时间
		var nowdate = $("#kd").val();
		//获取时间时间
		// var nowtime = $(".timeinput").val();
			var vall = $(".newdateinput").val()
			var valll = $("#newtimePicker").val()
	        if(vall!=0||valll!=0 ){
			var zong=$(".newdateinput").val()+$("#newtimePicker").val()
	        console.log(zong)
	        var sdw=$('#kd').val();
	        $("#kd").find("option[value='"+sdw+"']").attr("value",zong);
	        console.log($("#kd").val())
			var chuanz = $("#kd").val()
			getdata=chuanz
			chuanz = chuanz.replace(/-/g, "");
			chuanz = chuanz.replace(/:/g, "");
			chuanz = chuanz.replace(/ /g, "");
			}

		// if(nowdate == "请选择时间") {
			// alert("请选择时间");
		 else {
			 nowdate = nowdate.replace(/ /g, "");
			 getdata=nowdate
			// 去除指定字符串
			nowdate = nowdate.replace(/-/g, "");
			nowdate = nowdate.replace(/:/g, "");
			nowdate = nowdate.replace(/ /g, "");
			// dateStr = nowdate + nowtime;
			
		}
        window.location.href="./index.html?"+getdata+""
        })
	//更新
	$(".newnavgxbtn").click(function update(){
		lastInd = 1;
		g=0;
		var dateStr;
		//获取日期时间
		var nowdate = $("#kd").val();
		//获取时间时间
		// var nowtime = $(".timeinput").val();
			var vall = $(".newdateinput").val()
			var valll = $("#newtimePicker").val()
	        if(vall!=0||valll!=0 ){
			var zong=$(".newdateinput").val()+$("#newtimePicker").val()
	        var sdw=$('#kd').val();
	        $("#kd").find("option[value='"+sdw+"']").attr("value",zong);
	        console.log($("#kd").val())
			var chuanz = $("#kd").val()
			chuanz = chuanz.replace(/-/g, "");
			chuanz = chuanz.replace(/:/g, "");
			chuanz = chuanz.replace(/ /g, "");
			// dateStr = nowdate + nowtime;
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
			if($('#kd').val()=="请选择时间"){
			alert("请选择时间")
			return false
		    }
			dateTimeFun(nowdate);
		}
		//截取time最后两位
		imagesNum = 0;
	})

	//最新
	$(".newnavzxbtn").click(function() {
		var newdate = new XDate();
		var min = newdate.getMinutes();
		if(min % 6 != 0) {
			min = min - min % 6;
			if(min.toString().length < 2) {
				min = '0' + min.toString();
			}
		}
		$(".newtimeinput").val(newdate.toString("HH:mm"));
		$(".newdateinput").val(newdate.toString("yyyy-MM-dd"));
		var dateStr = newdate.toString("yyyyMMddHH") + min;
		getdata=dateStr
		g=-6
		dateTimeFun(dateStr);
	})

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
		var imageLength = 0;
		for(var i = 1; i <= 2; i++) {
			var imageUrl = "";
			var picArray = new Array();
			if(i == 1) {
				imageUrl = 'image/model6/${date}/out';
			} else if(i == 2) {
				imageUrl = 'image/model6/${date}/pred';
			}
			if(radioindex==1){
			picArray = getPicArray(year, months, days, hour, minute, imageUrl, "png", 10, "yyyyMMddHHmm", "yyyyMMddHHmm");
			}
			else if(radioindex==2){
			picArray = getPicArray(year, months, days, hour, minute, imageUrl, "png", 20, "yyyyMMddHHmm", "yyyyMMddHHmm");
			}
			// imageArray.push(picArray);
			
			imageArray[imageLength++] = picArray;
		}
		// console.log('imageArray', imageArray)
		//销毁定时器
		clearInterval(setInt);
		$("#newstop").text("暂停");
		stopOrStart = 1;
		lastInd = 1
		//数组图片替换
		var length = allMapObj.length;
		var picLength = allMapObj[0].images.length;
		imagesNum = picLength-1;
        console.log(imagesNum)
		
		imageArray.reverse();
		for(var i = 0; i < length; i++) {
			allMapObj[i].images = imageArray[i].url;
			// console.log("id: "+i+" ,value:"+imageArray[i].url);
		}
		imagesNum = 0;
		changeSetInterval()	
		//imageChangeFun()
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
		var obj = new Object();
		obj.url = imageUrl.replace("${date}", startTime.toString(urlFormat)) + "/" + 10 + "." + imageType;
		// // 排序规则 开始时间为最后一张图
		// picArray[picCount - 1] = obj;
		// // n张图片规则 每次-6分钟
		// var n = picCount - 1;
		// for(var i = 1; i <= n; i++) {
		// 	//			var tempDate = startTime.addMinutes(-6);
		// 	obj = new Object();
		// 	obj.url = imageUrl.replace("${date}", startTime.toString(urlFormat)) + "/" + i + "." + imageType;
		// 	picArray[picCount - 1 - i] = obj;
		// 	// 赋值
		// 	//			startTime = tempDate;
		// };

		// n张图片规则 每次-6分钟
		for(var i = 0; i < picCount; i++) {
			//			var tempDate = startTime.addMinutes(-6);
			obj = new Object();
			obj.url = imageUrl.replace("${date}", startTime.toString(urlFormat)) + "/" + (i+1) + "." + imageType;
			picArray[i] = obj;
			// 赋值
			//			startTime = tempDate;
		};
		var currArray = new Object();
		currArray.url = picArray;
		return currArray;
	}

	//字符串截取
	function subTimeString(imageUrl,g) {
		var imageUrl = imageUrl
		imageUrl2=imageUrl.replace(/\..*/g,'');		
	
		var arr = imageUrl.split("/");
		imageUrl = arr[2]
		//截取分钟
		
		// var minute = g;
		//截取小时

        var minute = parseInt(imageUrl.substring(10, 12))+g;

		var hour = imageUrl.substring(8, 10);	
		
		//截取日期
		var days = imageUrl.substring(6, 8);
		//月
		var months = imageUrl.substring(4, 6);
		//年
		var year = imageUrl.substring(0, 4);
		var newdate = new XDate(year, (months - 1), days, hour, minute, 0, 0);
		newdate = newdate.toString("yyyy-MM-dd HH:mm");
		$("#newautoMapSpanId").find("span").text(newdate);
	}
	//创建对象
	var maps = new initMap(new_index_Maps);

})
