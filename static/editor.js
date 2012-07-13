/**
 * @file        :  editor.js
 * @version     :  1.0
 * @created     :  Apr 14, 2010, 00:00:16 PM
 * @author      :  Canberk BOLAT <canberk.bolat at gmail.com>
 * @description :  Insert selected tag to element which defined by user
 * @function    :  addtag
 * @parameters  :  elementName - which element you want to select
 *                 tag - which tag you want to add
 * @task        :  This function takes the selected text/word/char
 *                 between specified tags
 **/
function getURLParameter(name,where) {
    return decodeURIComponent((new RegExp('.*[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(where)||[,""])[1].replace(/\+/g, '%20'))||null;
}


function addtag(elementName, tag) {
    var obj = document.getElementById(elementName);
    
    beforeText = obj.value.substring(0, obj.selectionStart);
    selectedText = obj.value.substring(obj.selectionStart, obj.selectionEnd);
    afterText = obj.value.substring(obj.selectionEnd, obj.value.length);
    
    switch(tag) {
        
    case "bold":
        tagOpen = "[b]";
        tagClose = "[/b]";
	
        newText = beforeText + tagOpen + selectedText + tagClose + afterText;
        break;
	

    case "strikethrough":
        tagOpen = "[s]";
        tagClose = "[/s]";
	
        newText = beforeText + tagOpen + selectedText + tagClose + afterText;
        break;

    case "italic":
        tagOpen = "[i]";
        tagClose = "[/i]";
	
        newText = beforeText + tagOpen + selectedText + tagClose + afterText;
        break;
	
    case "underline":
        tagOpen = "[u]";
        tagClose = "[/u]";
	
        newText = beforeText + tagOpen + selectedText + tagClose + afterText;
        break;
	
    case "url":
        var patternHTTP = /http:\/\//i;
        url = prompt("Enter URL without http://\nExample: www.example.com", "");
        
        if (url == null) {
            break;
	} else if (url.match(patternHTTP)) {
            url = url.replace("http://", "");
        }
	
        tagOpen = "[url=" + url + "]";
        tagClose = "[/url]";
	
        newText = beforeText + tagOpen + selectedText + tagClose + afterText;
        break;
	
    case "img":
        imgURL = prompt("Enter image URL without http://\nExample: www.example.com/image.jpg", "");
	
        if (imgURL == null) {
            break;
        }
	
        tagOpen = "[img=" + imgURL + "]";
        tagClose = "[/img]";
	
        newText = beforeText + tagOpen + selectedText + tagClose + afterText;
        break;
	
    case "color":
        pickedcolor = $(".color").val();
	
        tagOpen = "[color "+pickedcolor+"]";
        tagClose = "[/color]";
	
        newText = beforeText + tagOpen + selectedText + tagClose + afterText;
        break;
    case "youtube":
        youtubeURL = prompt("Enter the URL of the youtube video\nExample: https://www.youtube.com/watch?v=7xf6mbtenyc&feature=g-hwr-e", "");

        if (youtubeURL === "") {
	    alert("You need to provide a URL")
            break;
        }

	videoID = getURLParameter("v",youtubeURL)

        if (videoID == null) {
            alert("I don't understand the URL you provided. Make sure it has a \"v\" parameter, like the example.");
	    break;
        }

        tagOpen = "[html]<span class=\"ytvideo\"><iframe width=640 height=400 src=\"http://www.youtube.com/embed/";
        tagClose = "\" frameborder=\“0\” allowfullscreen></iframe></span>[/html]";
	
        newText = beforeText + tagOpen + videoID + tagClose + afterText;
        break;

    case "list":
        tag = "[list]\n[*]A list item\n[/list]\n";
	
        newText = beforeText + tag + afterText;
        break;

    case "size":

	size = prompt("What size do you want? 8 is small, 15 is big. No letters, numbers only.");

	if (isNaN(Number(size))) {
	    alert("That is not a valid number... But do as you wish.");
	} else if (size === null) {
	    alert("You must enter a value.");
	    break;
	}

        tagOpen = "[size "+size+"]";
	tagClose = "[/size]";
	
        newText = beforeText + tagOpen + selectedText + tagClose + afterText;
        break;

    }

    obj.value = newText;
}

