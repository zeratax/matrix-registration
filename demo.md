<section style="display:flex;justify-content:center;align-items:center;">
    <form action="https://dmnd.sh:5000/test-register" method="Post">
        <label for="username"> Enter your username:</label><br>
        <input id="username" name="username" type="text" required pattern="^@?[a-zA-Z_\-=\.\/0-9]+(:matrix\.org)?$" required minlength="1" maxlength="200">
        <label for="password">Enter your password:</label><br>
        <input id="password" name="password" type="password" required minlength="8" maxlength="128">
        <label for="confirm_password">Repeat your password:</label><br>
        <input id="confirm_password" name="confirm" type="password" required>
        <label for="token">Enter your invite token:</label><br>
        <input id="token" name="token" type="text" required pattern="^([A-Z][a-z]+)+$">
        <br><br>
        <input id="register" type="submit" value="register">
    </form>
</section>
<script>
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
      
    function sendData(formData) {
        var XHR = new XMLHttpRequest();

        XHR.addEventListener('load', function(event) {
          alert('Yeah! Data sent and response loaded.');
        });
        XHR.addEventListener('error', function(event) {
          alert('Oops! Something goes wrong.');
        });
        XHR.open('POST', 'https://dmnd.sh/register-test');
        XHR.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        XHR.send(formData);
    }
    
    
    // set token input to "?token=" query parameter
    document.getElementById('token').value = getParameterByName("token");
    
    // html5 validators
    var username = document.getElementById("username");
    var password = document.getElementById("password");
    var confirm_password = document.getElementById("confirm_password");
    var token = document.getElementById("token");
    
    username.addEventListener("input", function (event) {
      if (username.validity.typeMismatch) {
        username.setCustomValidity("format: @username:matrix.org");
      } else {
        username.setCustomValidity("");
      }
    });
    
    token.addEventListener("input", function (event) {
      if (token.validity.typeMismatch) {
        token.setCustomValidity("case-sensitive, e.g: SardineImpactReport");
      } else {
        token.setCustomValidity("");
      }
    });
    
    password.addEventListener("input", function (event) {
      if (password.validity.typeMismatch) {
        password.setCustomValidity("atleast 8 characters long");
      } else {
        password.setCustomValidity("");
      }
    });
    
    function validatePassword(){
      if(password.value != confirm_password.value) {
        confirm_password.setCustomValidity("passwords don't match");
      } else {
        confirm_password.setCustomValidity("");
      }
    }
    
    password.onchange = validatePassword;
    confirm_password.onkeyup = validatePassword;
    
    
    function getForm(id) {
      var button = document.getElementById(id);
      while(button && (button = button.parentNode)&&(button.nodeName !== 'FORM')){}
      
      return button;
      
    }
    
    var form = getForm('register'),
    handler = function(ev){
      ev = ev || window.event;
      if(ev.preventDefault) { //w3c browsers
          ev.preventDefault();    
      }
      else { //IE old
          ev.returnValue = false;    
      }
      alert('Custom logic goes here!'); 
      sendData(form);
    };
    if(form) {
      if(form.addEventListener) {
            form.addEventListener('submit', handler, false)   
      }
      else if(form.attachEvent) {
           form.attachEvent('onsubmit', handler);   
      }
         
    }
</script>
