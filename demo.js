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

var form = document.getElementById("registration");

function toggleValidate() {
    if (form.hasAttribute("novalidate")) {
      document.getElementById("registration").removeAttribute("novalidate")
    } else {
      document.getElementById("registration").setAttribute("novalidate", "novalidate")
    }
    console.log("form will not be validated")
}

/*
instead of just a simple form http post, we can also use
make use of some javascript magic to get a more visually pleasing
feedback.
since we just overwrite the submit button we don't hinder any functionality
for users without javascript
*/

function syntaxHighlight(json) {
    if (typeof json != 'string') {
         json = JSON.stringify(json, undefined, 2);
    }
    json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
        var cls = 'mi'; // number
        if (/^"/.test(match)) {
            if (/:$/.test(match)) {
                cls = 'nt'; // key
            } else {
                cls = 's2'; //string
            }
        } else if (/true|false/.test(match)) {
            cls = 'kc'; // boolean
        } else if (/null/.test(match)) {
            cls = 'kc'; // boolean
        }
        return '<span class="' + cls + '">' + match + '</span>';
    });
}

function sendData() {
    var XHR = new XMLHttpRequest();

    // Bind the FormData object and the form element
    var FD = new FormData(form);

    // Define what happens on successful data submission
    XHR.addEventListener("load", function(event) {
      console.log(XHR.responseText);
      var response = JSON.parse(XHR.responseText);
      var str = JSON.stringify(response, null, 4);
      console.log(response);
      document.getElementById("response").innerHTML = syntaxHighlight(str);
    });

    // Define what happens in case of error
    XHR.addEventListener("error", function(event) {
      alert('Oops! Something went wrong.');
    });

    // Set up our request
    XHR.open("POST", "https://dmnd.sh/test/register");

    // The data sent is what the user provided in the form
    XHR.send(FD);
  }

  // take over its submit event.
  form.addEventListener("submit", function (event) {
    event.preventDefault();

    sendData();
});
