const minPSWChars = 8;

window.onload = function() {
    $("input[type=text],input[type=email],input[type=password],textarea").on("blur", function(e) {
        var el = e.target;
        if (el.value.indexOf("'") > -1 || el.value.indexOf("\"") > -1) {
            addToErrorDisplay("You can't use neither of these characters: ' \"");
            el.value = "";
        }
    });
}

function passwordValidation(pswID, rpswID) {
	var psw = document.getElementById(pswID).value;
	var rpsw = document.getElementById(rpswID).value;
	
	var ret = (psw == rpsw) && psw.length > minPSWChars;
	if (!ret) addToErrorDisplay("The password must be at least 8 characters long, or it wasn\'t correctly copied.");
	
	return ret;
}

function createMessageElement(txt, author) {
	var msg = document.createElement("DIV");
	msg.className = "UserPost";
	var name = document.createElement("SPAN");
	name.className = "PosterName";
	name.innerHTML = author + " ";
	var body = document.createElement("SPAN");
	body.className = "MessageBody";
	body.innerHTML = txt;
	msg.appendChild(name);
	msg.appendChild(body);
	return msg;
}

function addToErrorDisplay(txt) {
	var err = document.getElementById("ErrorDisplay");
	err.innerHTML = txt;
	err.style.display = "initial";
	setTimeout( function() {document.getElementById("ErrorDisplay").style.display = "none";}, 7000);
}

function addToSuccessDisplay(txt) {
	var succ = document.getElementById("SuccessDisplay");
	succ.innerHTML = txt;
	succ.style.display = "initial";
	setTimeout( function() {document.getElementById("SuccessDisplay").style.display = "none";}, 7000);
}

function createMessageElement(txt, author) {
	var msg = document.createElement("DIV");
	msg.className = "UserPost";
	var name = document.createElement("SPAN");
	name.className = "PosterName";
	name.innerHTML = author + " ";
	var body = document.createElement("SPAN");
	body.className = "MessageBody";
	body.innerHTML = txt;
	msg.appendChild(name);
	msg.appendChild(body);
	return msg;
}