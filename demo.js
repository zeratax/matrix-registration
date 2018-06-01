// see https://stackoverflow.com/a/901144/3779427
function getParameterByName(name, url) {
  if (!url) url = window.location.href;
  name = name.replace(/[\[\]]/g, "\\$&");
  var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
    results = regex.exec(url);
  if (!results) return null;
  if (!results[2]) return '';
  return decodeURIComponent(results[2].replace(/\+/g, " "));
}

// set token input to "?token=" query parameter
document.getElementById('token').value = getParameterByName("token");

// html5 validators
var username = document.getElementById("username");
var password = document.getElementById("password");
var confirm_password = document.getElementById("confirm_password");
var token = document.getElementById("token");

username.addEventListener("input", function(event) {
  if (username.validity.typeMismatch) {
    username.setCustomValidity("format: @username:dmnd.sh");
  } else {
    username.setCustomValidity("");
  }
});

token.addEventListener("input", function(event) {
  if (token.validity.typeMismatch) {
    token.setCustomValidity("case-sensitive, e.g: SardineImpactReport");
  } else {
    token.setCustomValidity("");
  }
});

password.addEventListener("input", function(event) {
  if (password.validity.typeMismatch) {
    password.setCustomValidity("atleast 8 characters long");
  } else {
    password.setCustomValidity("");
  }
});

function validatePassword() {
  if (password.value != confirm_password.value) {
    confirm_password.setCustomValidity("passwords don't match");
  } else {
    confirm_password.setCustomValidity("");
  }
}

password.onchange = validatePassword;
confirm_password.onkeyup = validatePassword;

/*
instead of just a simple form http post, we can also use
make use of some javascript magic to get a more visually pleasing
feedback.
since we just overwrite the submit button we don't hinder any functionality
for users without javascript
*/

function createCORSRequest(method, url) {

  var xhr = new XMLHttpRequest();
  if ("withCredentials" in xhr) {

    // Check if the XMLHttpRequest object has a "withCredentials" property.
    // "withCredentials" only exists on XMLHTTPRequest2 objects.
    xhr.open(method, url, true);

  } else if (typeof XDomainRequest != "undefined") {

    // Otherwise, check if XDomainRequest.
    // XDomainRequest only exists in IE, and is IE's way of making CORS requests.
    xhr = new XDomainRequest();
    xhr.open(method, url);

  } else {

    // Otherwise, CORS is not supported by the browser.
    xhr = null;

  }
  return xhr;
}

function sendData(formData) {
  var XHR = createCORSRequest('POST', https://dmnd.sh/test-register);
  if (!XHR) {
    throw new Error('CORS not supported');
  }

  XHR.addEventListener('load', function(event) {
    alert('Yeah! Data sent and response loaded.');
    alert(xhr.responseText);
  });
  XHR.addEventListener('error', function(event) {
    alert('Oops! Something goes wrong.');
  });
  XHR.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
  XHR.send(formData);
}

function getForm(id) {
  var button = document.getElementById(id);
  while (button && (button = button.parentNode) && (button.nodeName !== 'FORM')) {}

  return button;
}

var form = getForm('register'),
  handler = function(ev) {
    ev = ev || window.event;
    if (ev.preventDefault) { //w3c browsers
      ev.preventDefault();
    } else { //IE old
      ev.returnValue = false;
    }
    sendData(form);
  };
if (form) {
  if (form.addEventListener) {
    form.addEventListener('submit', handler, false)
  } else if (form.attachEvent) {
    form.attachEvent('onsubmit', handler);
  }

}
