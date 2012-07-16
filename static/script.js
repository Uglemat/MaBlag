$(document).ready(function() {

    function FormatNumberLength(num, length) {
	var r = "" + num;
	while (r.length < length) {
            r = "0" + r;
	}
	return r;
    }

    var weekday=new Array(7);
    weekday[0]="Sunday";
    weekday[1]="Monday";
    weekday[2]="Tuesday";
    weekday[3]="Wednesday";
    weekday[4]="Thursday";
    weekday[5]="Friday";
    weekday[6]="Saturday";

    var month=new Array();
    month[0]="January";
    month[1]="February";
    month[2]="March";
    month[3]="April";
    month[4]="May";
    month[5]="June";
    month[6]="July";
    month[7]="August";
    month[8]="September";
    month[9]="October";
    month[10]="November";
    month[11]="December";

    $(".blogtext img").each(function() {
        var src = $(this).attr('src');
        var a = $('<a/>').attr('href', src);
        $(this).wrap(a);
    });
    
    $("span.time, span.draft_time").each(function() {
	var unixt = parseInt($(this).text());
	var tdate = new Date(unixt*1000); 
	var day = weekday[tdate.getDay()].substring(0,3);
	var themonth = month[tdate.getMonth()].substring(0,3);
	var date = tdate.getDate();
	var year = tdate.getFullYear();
	var hours = FormatNumberLength(tdate.getHours(),2);
	var minutes = FormatNumberLength(tdate.getMinutes(),2);
	$(this).html(day+" "+themonth+" "+date+" "+year+" "+hours+":"+minutes);
	$(this).attr("title","Unix timestamp: "+unixt)
    });
    
    if (document.URL.search("#ex_") === -1) {
	$(".entire_examples").css("display","none");
	
	$(".showexamples").html("<a id='clicktoshow'>Show examples of bbcode usage</a>");
	$("#clicktoshow").click(function () {
	    $(".showexamples").html("<h2 class=\"title showexlink\">bbcode examples: </h2>");
	    $(".entire_examples").css("display","block");
	});
    }

    $('#captcharefresh').click(function() {
	var newsrc = $("#captchaimage").attr('src').split("?")[0]+'?'+Math.random();
	$("#captchaimage").attr('src',newsrc);
	$("#captchainput").val("");
    })
    
});
