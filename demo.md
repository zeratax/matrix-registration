## demo registration

On this page you can try out the registration process for my homeserver [dmnd.sh](https://dmnd.sh).
No actual account will be created.


<form id="registration" action="https://dmnd.sh/test-register" method="post">
  <label for="username"> Enter your username:</label><br>
  <input id="username" name="username" type="text" required pattern="^@?[a-zA-Z_\-=\.\/0-9]+(:dmnd\.sh)?$" required minlength="1" maxlength="200">
  <br>
  <label for="password">Enter your password:</label><br>
  <input id="password" name="password" type="password" required minlength="8" maxlength="128">
  <br>
  <label for="confirm_password">Repeat your password:</label><br>
  <input id="confirm_password" name="confirm" type="password" required>
  <br>
  <label for="token">Enter your invite token:</label><br>
  <input id="token" name="token" type="text" required pattern="^([A-Z][a-z]+)+$">
  <br><br>
  <input id="register" type="submit" value="register">
</form>
<pre class="highlight">
  <code id="response">
 </code>
</pre>
<br>
You can get a token with a simple cURL request: [https://github.com/ZerataX/matrix-registration/wiki/api#curl](https://github.com/ZerataX/matrix-registration/wiki/api#curl)
Just use the endpoints `/test-token` and `/test-registration` and the SharedSecret `demopagesecret`.
E.g. to list all tokens:
```bash
curl -H "Authorization: SharedSecret demopagesecret" \
     https://dmnd.sh/test-token
```

This page is based on [https://github.com/ZerataX/matrix-registration/blob/master/resources/example.html](https://github.com/ZerataX/matrix-registration/blob/master/resources/example.html)

 <script src="demo.js"></script>
