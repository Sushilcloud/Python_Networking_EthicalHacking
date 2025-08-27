import smtplib


server=smtplib.SMTP_SSL(smtp.gmail.com,465)
server.login("sushilgodiyal@gmail.com","romi24dec#")
server.sendmail("sushilgodiyal@gmail.com",
                "sushil_godiyal@hotmail.com",
                "Hello,How are you")
server.quit()