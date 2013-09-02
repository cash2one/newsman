Procedures
-----------

1. `Change system alias`:

    - in **/etc/aliases** add root:xxx@xxx.com(sender) and ubuntu/work:yyy@yyy.com(receiver)

    - excute newaliases to update /etc/aliases

2. `Allow Google to validate request from EC2 servers`:

    - refers to ['cannot login gmail to send
      mail'](http://support.cloudfoundry.com/entries/25093507-cannot-login-gmail-to-send-email) and ['I'm having trouble logging in with my username and password'](https://support.google.com/mail/answer/78754)

    - Try [clearing the
      CAPTCHA](https://www.google.com/accounts/DisplayUnlockCaptcha)
