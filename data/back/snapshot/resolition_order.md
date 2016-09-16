### Order Of Resolution

1. Visitor opens atyichu site in wechat.

2. If Visitor is not authenticated, it redirects to "/visitor/".

3. At "/visitor/" user authenticates with oauth2, and redirects to "visitor/openid/".
Also there cookies sets for angularjs auth service.

4. Server redirects visitor to mirror page or photo page.



1. Index page: there must be xhr request to unlock request and request to make a photo.
HOW IT IS IMPLEMENTS.

2. Mirror pages. It must represent a list of mirrors and it must bind a mirror. 

First of all on mirror page we need to load http://res.wx.qq.com/open/js/jweixin-1.0.0.js.
Then js_info signature must be received from server api. After it we must use it (wx.ready). 
But, as I saw, it is not used.

3. Photo pages. Represent photos, request goes to "/api/v1/photo/".


