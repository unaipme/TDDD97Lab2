const minPSWChars = 8;

var token = null;
var loggedUser = null;
var browseUser = null;

function passwordValidation(pswID, rpswID) {
    console.log("Comprobando...");
	var psw = document.getElementById(pswID).value;
	var rpsw = document.getElementById(rpswID).value;
	
	var ret = (psw == rpsw) && psw.length > minPSWChars;
	if (!ret) addToErrorDisplay("The password must be at least 8 characters long, or it wasn\'t correctly copied.");
	
	return ret;
}

function postOnWall(user, search) {
	if (search) var txt = document.getElementById("OMessageContent").value;
	else var txt = document.getElementById("MessageContent").value;
	if (txt == "") {
		addToErrorDisplay("The posts can't be empty");
		return;
	}
	document.getElementById("MessageContent").value = "";
	var resp = serverstub.postMessage(token, txt, user.email);
	if (!resp.success) addToErrorDisplay(resp.message);
	else {
		addToSuccessDisplay(resp.message);
		refreshMessageWall(search, user);
	}
	return resp.success;
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
	console.log(txt);
	var err = document.getElementById("ErrorDisplay");
	err.innerHTML = txt;
	err.style.display = "initial";
	setTimeout( function() {document.getElementById("ErrorDisplay").style.display = "none";}, 7000);
}

function addToSuccessDisplay(txt) {
	console.log(txt);
	var succ = document.getElementById("SuccessDisplay");
	succ.innerHTML = txt;
	succ.style.display = "initial";
	setTimeout( function() {document.getElementById("SuccessDisplay").style.display = "none";}, 7000);
}