import requests

cert_file_path = "C:\Users\win7_test\PycharmProjects\WebHookBot\webhook_cert.pem"
key_file_path = "C:\Users\win7_test\PycharmProjects\WebHookBot\webhook_pkey.pem"

cert = (cert_file_path, key_file_path)

url = "https://7f95526c.ngrok.io/548697540:AAHbO142Q-p98C0-uvqpvi2-eYnSd4RdWno/"
data = {"URL": "865d62ad.ngrok.io"}
req = requests.post(url, json=data, cert=cert, verify=False)
print req.status_code