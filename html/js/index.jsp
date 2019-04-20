<%@ page language="java" contentType="text/html; charset=UTF-8"
	pageEncoding="UTF-8"%>
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">

<%@ include file="../shared/taglib.jsp"%>

<html>

<!--[if IE 8]> <html lang="en" class="ie8 no-js"> <![endif]-->
<!--[if IE 9]> <html lang="en" class="ie9 no-js"> <![endif]-->
<!--[if !IE]><!-->
<html lang="en" class="no-js">
<!--<![endif]-->
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<title>首页</title>
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta content="width=device-width, initial-scale=1.0" name="viewport" />
<meta content="" name="description" />
<meta content="" name="author" />
<meta name="MobileOptimized" content="320">

<%@ include file="../shared/importJs.jsp"%>
<%@ include file="../shared/importCss.jsp"%>



<script type="text/javascript" src="<c:url value='/js/app.js'/>"></script>
<%-- <script type="text/javascript"
	src="http://api.map.baidu.com/api?key=rlj5rjDy8WsGoxPElXE0ZBkp&v=1.2&services=false"></script>--%>
<!-- BEGIN Report SCRIPTS -->
<script type="text/javascript"
	src="<c:url value='/plugins/highcharts/highcharts.js'/>"></script>
	

<link href="<c:url value='/css/bootstrap-responsive.min.css'/>"
	rel="stylesheet" type="text/css" />

<!-- END Report SCRIPTS -->
<style type="text/css">
#allmap {
	width: 100%;
	height: 500px;
}
.height157{
	height: 157px;
}
</style>


</head>
<!-- END HEAD -->
<!-- BEGIN BODY -->
<body class="page-header-fixed">

	<form action="<c:url value='/home/index'/>" method="get" id="myform">
		<div class="clearfix"></div>
		<!-- BEGIN CONTAINER -->
		<div class="page-container">

			<%@ include file="../shared/sidebarMenu.jsp"%>


			<!-- BEGIN PAGE -->
			<div class="page-content">
				<%@ include file="../shared/pageHeader.jsp"%>
				<c:if test="${ sessionScope.accountAuth.companyId!=28}">
					<%-- include file="../shared/allRportSearch.jsp"--%>
					<%@ include file="../shared/styleSet.jsp"%>
					<!-- BEGIN PAGE HEADER-->
					<div class="row" id="rowHeard">
						<div class="col-md-12">
							<!-- BEGIN PAGE TITLE & BREADCRUMB-->
							<%@ include file="../shared/projectName.jsp"%>
							<!-- END PAGE TITLE & BREADCRUMB-->
						</div>
					</div>
					<!-- END PAGE HEADER-->
					<div class="clearfix"></div>
					<div class="row">
						<div class="col-md-12">
							<div class="panel wrapper">
								<div class="row height157">
									<div class="col-md-6 b-r b-light no-border-xs height157">
										<h4 class="font-thin m-t-none m-b-md text-muted">今日关键指标</h4>
										<div class="m-b" style="text-align: center;">
											<div class="col-md-4">
												<div class="levelOne" id="visiitorCount">
													<img src="<c:url value='/images'/>/loading.gif">
												</div>
												<div class="levelTwo">新增访客数</div>
												<div class="levelThree" id="visiitorCount2">
													<img src="<c:url value='/images'/>/loading.gif">
												</div>
												<br>
											</div>
											<div class="col-md-4">
												<div class="levelOne" id="weixinCount">
													<img src="<c:url value='/images'/>/loading.gif">
												</div>
												<div class="levelTwo">新增客户注册用户</div>
												<div class="levelThree" id="weixinCount2">
													<img src="<c:url value='/images'/>/loading.gif">
												</div>
												<br>
											</div>
											<div class="col-md-4">
												<div class="levelOne" id="oldCustomerCount">
													<img src="<c:url value='/images'/>/loading.gif">
												</div>
												<div class="levelTwo">老用户</div>
												<div class="levelThree" id="oldCustomerCount2">
													<img src="<c:url value='/images'/>/loading.gif">
												</div>
												<br>
											</div>
										</div>
									</div>
									<div class="col-md-2 height157"
										style="background-color: #428BCA; text-align: center; border-left: solid 1px #FFFFFF;">
										<div class="levelOne"
											style="color: #FFFFFF; padding-top: 40px;"
											id="weixinTotalCount">
											<img src="<c:url value='/images'/>/loading.gif">
										</div>
										<div class="levelTwo" style="color: #B0E1F1;">总客户</div>
										<div class="levelThree">&nbsp;</div>
										<br>
									</div>
									<div class="col-md-2 height157"
										style="background-color: #7266BA; text-align: center; border-left: solid 1px #FFFFFF;">
										<div class="levelOne"
											style="color: #FFFFFF; padding-top: 40px;"
											id="visiitorTotalCountaddweixinTotalCount">
											<img src="<c:url value='/images'/>/loading.gif">
										</div>
										<div class="levelTwo" style="color: #D6D3E6;">总访客人数</div>
										<div class="levelThree">&nbsp;</div>
										<br>
									</div>
									<div class="col-md-2 height157"
										style="background-color: #339900; text-align: center; border-left: solid 1px #FFFFFF;">
										<div class="levelOne"
											style="color: #FFFFFF; padding-top: 40px;"
											id="detectionTotalCount">
											<img src="<c:url value='/images'/>/loading.gif">
										</div>
										<div class="levelTwo" style="color: #C0EAAC;">总检查次数</div>
										<div class="levelThree">&nbsp;</div>
										<br>
									</div>
								</div>
							</div>
						</div>
					</div>
					
					<!-- map b2b none-->
					<%--<div class="row">
						<div class="col-md-12">
							<div class="panel wrapper">
								<div class="row">
									<div class="col-md-9 b-r b-light no-border-xs">
										<h4 class="font-thin m-t-none m-b-md text-muted" id="storetitle">店铺时图<img src="<c:url value='/images'/>/loading.gif"></h4>
										<div class="m-b" style="text-align: center;">
											<div id="allmap"></div>
										</div>
									</div>
									<div class="col-md-1">&nbsp;</div>
									<div class="col-md-3">
										<table class="table table-striped">
											<thead id="storetopten">
												<tr>
													<th style="color: #58666E; font-size: 20px;"><span
														style="font-weight: normal;">实时榜单</span>Top 10</th>
													<th
														style="color: #428BCA; font-size: 14px; font-weight: normal;">访客数</th>
												</tr>
											</thead>
										</table>
									</div>

								</div>
							</div>
						</div>
					</div> --%>
					
					<!-- map end -->
					
					<!-- report -->
					<div class="row">
						<div class="col-md-12">
							<div class="panel wrapper">
								<div class="row">
									<div class="col-md-12 b-r b-light no-border-xs">
										<h4 class="font-thin m-t-none m-b-md text-muted" id="maintitle">今日各时段检测次数<img src="<c:url value='/images'/>/loading.gif"></h4>
										<div class="m-b" style="text-align: center;">
											<div id="mainline" style="min-width: 700px; height: 250px"></div>
										</div>
									</div>
								</div>
							</div>
						</div>
					</div>
					<!-- end report -->

					<!-- top -->
					<!-- <div class="row">
		<div class="col-md-6">
		<div class="panel wrapper">
			        <div class="row">
			          <div class="col-md-12 b-r b-light no-border-xs">
			            <h4 class="font-thin m-t-none m-b-md text-muted">产品试用Top5</h4>
			            <div class="m-b" style="text-align: center;">
			            		<table class="table table-striped"
										id="data-table">
										<thead>
											<tr>
												<th>商品名称</th>
												<th>使用次数</th>
											</tr>
										</thead>
											<c:forEach items="${productVoList }" var="item">
											<tr class="odd gradeX px" style="text-align: left;">
												<td><img src="${item.photo }" style="width: 50px;height: 50px;"/>${item.name }</td>
												<td>${item.useCount }</td>
											</tr>
											</c:forEach>
									</table>
			            </div>
			          </div>
			          </div>
			      </div>
		</div> 
		<div class="col-md-6">
		<div class="panel wrapper">
			        <div class="row">
			          <div class="col-md-12 b-r b-light no-border-xs">
			            <h4 class="font-thin m-t-none m-b-md text-muted">导购活跃度Top5</h4>
			            <div class="m-b" style="text-align: center;">
			            		<table class="table table-striped"
										id="data-table">
										<thead>
											<tr>
												<th>姓名</th>
												<th>工号</th>
												<th>区域</th>
												<th>门店</th>
												<th>服务人数</th>
										</thead>
											<c:forEach items="${guideVoList }" var="item">
												<tr class="odd gradeX px" style="text-align: left;">
												<c:if test="${empty item.photo }">
													<td><img src="<c:url value='/images/user.jpg'/>" style="width: 50px;height: 50px;"/>${item.name }</td>
												</c:if>
												<c:if test="${item.photo }">
													<td><img src="${item.photo }" style="width: 50px;height: 50px;"/>${item.name }</td>
												</c:if>
													
													<td>${item.jobNumber }</td>
													<td>${item.city }</td>
													<td>${item.storeName }</td>
													<td>${item.serviceCount }</td>
												</tr>
											</c:forEach>
									</table>
			            </div>
			          </div>
			          </div>
			      </div>
		</div>
		</div>-->
					<!-- end top -->
					<!-- END PAGE -->
				</c:if>
			</div>
			<!-- END CONTAINER -->
			<!-- BEGIN FOOTER -->

			<!-- END FOOTER -->

			
			<!-- END PAGE LEVEL PLUGINS -->
			<!-- BEGIN PAGE LEVEL SCRIPTS -->
			<script src="<c:url value='/js/app.js'/>" type="text/javascript"></script>
			<script src="<c:url value='/js/index.js'/>" type="text/javascript"></script>

			<script src="<c:url value='/plugins/echart/src/echarts.min.js'/>?v=3"
				type="text/javascript"></script>
			<!-- END PAGE LEVEL SCRIPTS -->

			<script type="text/javascript">
				$(function() {
					App.init(); // initlayout and core plugins
					var options = "";

					$
							.ajax({
								type : 'POST',
								url : 'ajax/count',
								success : function(data) {
									$("#visiitorCount")
											.html(data.visiitorCount);
									$("#weixinCount").html(data.weixinCount);
									$("#oldCustomerCount").html(
											data.oldCustomerCount);
									$("#weixinTotalCount").html(
											data.weixinTotalCount);
									var visiitorTotalCountaddweixinTotalCount = Number(data.visiitorTotalCount)
											+ Number(data.weixinTotalCount);
									$("#visiitorTotalCountaddweixinTotalCount")
											.html(
													visiitorTotalCountaddweixinTotalCount);
									$("#detectionTotalCount").html(
											data.detectionTotalCount);

									var visiitorCount = Number(data.visiitorCount);
									var visiitorYesCount = Number(data.visiitorYesCount);
									var visiitorPercent = data.visiitorPercent;
									if (visiitorCount >= visiitorYesCount) {
										$("#visiitorCount2")
												.html(
														"昨日：上涨"
																+ visiitorPercent
																+ "%");
									} else {
										$("#visiitorCount2")
												.html(
														"昨日：下降"
																+ visiitorPercent
																+ "%");
									}

									var weixinCount = Number(data.weixinCount);
									var weixinYesCount = Number(data.weixinYesCount);
									var weixinPercent = data.weixinPercent;
									if (weixinCount >= weixinYesCount) {
										$("#weixinCount2").html(
												"昨日：上涨" + weixinPercent + "%");
									} else {
										$("#weixinCount2").html(
												"昨日：下降" + weixinPercent + "%");
									}

									var oldCustomerCount = Number(data.oldCustomerCount);
									var oldCustomerYesCount = Number(data.oldCustomerYesCount);
									var oldCustomerPercent = data.oldCustomerPercent;
									if (oldCustomerCount >= oldCustomerYesCount) {
										$("#oldCustomerCount2").html(
												"昨日：上涨" + oldCustomerPercent
														+ "%");
									} else {
										$("#oldCustomerCount2").html(
												"昨日：下降" + oldCustomerPercent
														+ "%");
									}

								}
							});
						
					<%--
					//map js
					var markerArr = new Array();
					$.ajax({
						type : 'POST',
						url : 'ajax/store',
						success : function(data) {
							for (var i = 0; i < data.length; i++) {
								var storeName = data[i].name;
								var visiteCount = data[i].visiteCount;
								if (i % 2 == 0) {
									$("#storetopten").append(
											"<tr class=\"active\"><td >"
													+ (i + 1) + " " + storeName
													+ "</td><td>" + visiteCount
													+ "</td></tr>");
								} else {
									$("#storetopten").append(
											"<tr><td>" + (i + 1) + " "
													+ storeName + "</td><td>"
													+ visiteCount
													+ "</td></tr>");
								}
								
								markerArr[i] = {
									title : "" + data[i].name + "",
									point : "" + data[i].longitude + ","
											+ data[i].latitude + "",
									count : "" + data[i].visiteCount + ""
								};
							}
							
							
							var map = new BMap.Map('allmap', {
								defaultCursor : 'default'
							});
							map.enableScrollWheelZoom(true);
							map
									.centerAndZoom(
											new BMap.Point(114.059809, 22.549065), 13);

							var ctrlNav = new window.BMap.NavigationControl({
								anchor : BMAP_ANCHOR_TOP_LEFT,
								type : BMAP_NAVIGATION_CONTROL_LARGE
							});
							map.addControl(ctrlNav);

							var point = new Array();
							var marker = new Array();
							for (var j = 0; j < markerArr.length; j++) {
								var p0 = markerArr[j].point.split(",")[0];
								var p1 = markerArr[j].point.split(",")[1];
								point[j] = new window.BMap.Point(p0, p1);
								marker[j] = new window.BMap.Marker(point[j]);
								marker[j].setAnimation(BMAP_ANIMATION_BOUNCE);
								var label = new window.BMap.Label("门店:"
										+ markerArr[j].title + "<br>访客:"
										+ markerArr[j].count, {
									offset : new window.BMap.Size(20, -10)
								});
								marker[j].setLabel(label);
								map.addOverlay(marker[j]);
							}
							;
							$("#storetitle").html("店铺时图");
						}
					}); --%>
					
					
					
					
					var timepersonOptions = {
						chart : {
							renderTo : 'mainline',
							type : 'areaspline'
						},
						title : {
							text : ''
						},
						xAxis : {
							categories : [ "0时", "1时", "2时", "3时", "4时", "5时",
									"6时", "7时", "8时", "9时", "10时", "11时",
									"12时", "13时", "14时", "15时", "16时", "17时",
									"18时", "19时", "20时", "21时", "22时", "23时" ],
							title : {
								text : '时间'
							}
						},
						  yAxis: {
					        	title: {
									text: '人数'
								}
					        },tooltip: {
					            shared: true,
					            valueSuffix: '人'
					        },
					        credits: {
					            enabled: false
					        },
					        plotOptions: {
					            areaspline: {
					                fillOpacity:0.5
					            }
					        }, legend: {
					        	align: "center", 
					        	verticalAlign: "top", 
					        	x: 0,
					        	y: 20 
					        },
						series : [ {
							name : '访客数'
						}, {
							name : '客户数'
						}]
					};
					
					$.ajax({
						url : 'ajax/timeperson',
						type : 'POST',
						success : function(data) {
							//init series arays
							select1_arr = [];
							select2_arr = [];
							
							var weixinHistoryList=data.weixinHistoryList;
							var visiitorHistoryList=data.visiitorHistoryList;
							
							for (i in weixinHistoryList) {
								//build
								var r = weixinHistoryList[i];
								select1_arr.push([r]);
								
							}
							
							for (i in visiitorHistoryList) {
								//build
								var r = visiitorHistoryList[i];
								select2_arr.push([r]);
								
							}
							
							timepersonOptions.series[0].data = select2_arr;
							timepersonOptions.series[1].data = select1_arr;
							
							//console.log(timepersonOptions);
							var chart = new Highcharts.Chart(
									timepersonOptions);
							$("#maintitle").html("今日各时段检测次数");
						},
						cache : false
					});

				});
			</script>
			<!-- END JAVASCRIPTS -->
	</form>

</body>

</html>